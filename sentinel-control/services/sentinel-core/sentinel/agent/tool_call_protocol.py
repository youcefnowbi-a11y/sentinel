from __future__ import annotations

import hashlib
import json
import re
from enum import StrEnum
from html import unescape
from typing import Any

from pydantic import Field

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.agent.phases import AgentPhase
from sentinel.capabilities.models import ToolInvocation
from sentinel.capabilities.risk import ToolSideEffect
from sentinel.shared.models import SentinelModel, new_id


MAX_RAW_TOOL_CALL_CHARS = 50_000
MAX_TOOL_ARGUMENT_KEYS = 128

_IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")
_XML_TAG_RE = re.compile(r"<(?P<tag>[a-zA-Z_][a-zA-Z0-9_-]*)>(?P<value>.*?)</(?P=tag)>", re.DOTALL)
_REGEX_FIELD_RE = re.compile(
    r"(?P<key>tool_id|tool|action|operation|capability|target|arguments|args|input|side_effects|requested_side_effects)"
    r"\s*[:=]\s*"
    r"(?P<value>\{.*?\}|\[[^\]]*\]|\"[^\"]*\"|'[^']*'|[^\n;,]+)",
    re.IGNORECASE | re.DOTALL,
)
_TOOL_ID_ALIASES = ("tool_id", "tool", "name")
_ACTION_ALIASES = ("action", "operation")
_ARGUMENT_ALIASES = ("arguments", "args", "input")
_SIDE_EFFECT_ALIASES = ("requested_side_effects", "side_effects")


class ToolCallParseMethod(StrEnum):
    JSON = "json"
    XML = "xml"
    REGEX = "regex"
    REJECTED = "rejected"


class ToolCallParseStatus(StrEnum):
    CANONICAL = "canonical"
    RECOVERED = "recovered"
    REJECTED = "rejected"


class CanonicalToolCall(SentinelModel):
    """Typed tool-call intention. This object is never an execution grant."""

    id: str = Field(default_factory=lambda: new_id("tcall"))
    tool_id: str
    action: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    capability: str | None = None
    target: str | None = None
    requested_side_effects: list[ToolSideEffect] = Field(default_factory=list)
    canonical_hash: str

    def to_invocation(self) -> ToolInvocation:
        return ToolInvocation(
            tool_id=self.tool_id,
            action=self.action,
            requested_side_effects=self.requested_side_effects,
            capability=self.capability,
            target=self.target,
        )


class ToolCallCanonicalizationResult(SentinelModel):
    accepted: bool
    status: ToolCallParseStatus
    method: ToolCallParseMethod
    raw_sha256: str
    call: CanonicalToolCall | None = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    trace_event_id: str | None = None


class ToolCallProtocol:
    """Canonicalizes fragile model tool-call text without executing anything."""

    def canonicalize(
        self,
        raw: str,
        *,
        event_bus: EventBus | None = None,
        phase: AgentPhase = AgentPhase.TOOL_SELECTING,
    ) -> ToolCallCanonicalizationResult:
        raw_text = raw if isinstance(raw, str) else str(raw)
        raw_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
        if not raw_text.strip():
            return self._finish(
                ToolCallCanonicalizationResult(
                    accepted=False,
                    status=ToolCallParseStatus.REJECTED,
                    method=ToolCallParseMethod.REJECTED,
                    raw_sha256=raw_hash,
                    errors=["empty_tool_call"],
                ),
                event_bus,
                phase,
            )
        if len(raw_text) > MAX_RAW_TOOL_CALL_CHARS:
            return self._finish(
                ToolCallCanonicalizationResult(
                    accepted=False,
                    status=ToolCallParseStatus.REJECTED,
                    method=ToolCallParseMethod.REJECTED,
                    raw_sha256=raw_hash,
                    errors=["tool_call_too_large"],
                ),
                event_bus,
                phase,
            )

        last_rejected_result: ToolCallCanonicalizationResult | None = None
        for method, extractor in (
            (ToolCallParseMethod.JSON, self._extract_json),
            (ToolCallParseMethod.XML, self._extract_xml),
            (ToolCallParseMethod.REGEX, self._extract_regex),
        ):
            fields, warnings = extractor(raw_text)
            if fields is None:
                continue
            result = self._canonicalize_fields(fields, raw_hash, method, warnings)
            if result.accepted:
                return self._finish(result, event_bus, phase)
            last_rejected_result = result

        if last_rejected_result is not None:
            return self._finish(last_rejected_result, event_bus, phase)

        return self._finish(
            ToolCallCanonicalizationResult(
                accepted=False,
                status=ToolCallParseStatus.REJECTED,
                method=ToolCallParseMethod.REJECTED,
                raw_sha256=raw_hash,
                errors=["tool_call_not_parseable"],
            ),
            event_bus,
            phase,
        )

    @staticmethod
    def _extract_json(raw: str) -> tuple[dict[str, Any] | None, list[str]]:
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError:
            extracted = ToolCallProtocol._first_json_object(raw)
            if extracted is None:
                return None, []
            try:
                decoded = json.loads(extracted)
            except json.JSONDecodeError:
                return None, []
            warnings = ["recovered_embedded_json_object"]
        else:
            warnings = []
        if not isinstance(decoded, dict):
            return None, []
        return decoded, warnings

    @staticmethod
    def _extract_xml(raw: str) -> tuple[dict[str, Any] | None, list[str]]:
        if "<tool_call" not in raw and "<tool>" not in raw and "<tool_id>" not in raw:
            return None, []
        fields: dict[str, Any] = {}
        xml_fragment = re.sub(r"</?tool_call[^>]*>", "", raw, flags=re.IGNORECASE)
        for match in _XML_TAG_RE.finditer(xml_fragment):
            key = match.group("tag").strip().lower().replace("-", "_")
            value = unescape(match.group("value").strip())
            if key in fields and fields[key] != value:
                fields.setdefault("__field_errors__", []).append(f"duplicate_field:{key}")
                continue
            fields[key] = value
        if not fields:
            return None, []
        return fields, ["recovered_from_xml_tags"]

    @staticmethod
    def _extract_regex(raw: str) -> tuple[dict[str, Any] | None, list[str]]:
        fields: dict[str, Any] = {}
        for match in _REGEX_FIELD_RE.finditer(raw):
            key = match.group("key").strip().lower()
            value = match.group("value").strip().strip(",;")
            if key in fields and fields[key] != value:
                fields.setdefault("__field_errors__", []).append(f"duplicate_field:{key}")
                continue
            fields[key] = value
        if not fields:
            return None, []
        return fields, ["recovered_from_regex_fields"]

    def _canonicalize_fields(
        self,
        fields: dict[str, Any],
        raw_hash: str,
        method: ToolCallParseMethod,
        warnings: list[str],
    ) -> ToolCallCanonicalizationResult:
        normalized = {str(key).strip().lower(): value for key, value in fields.items()}
        tool_id = self._string_field(normalized, "tool_id", "tool", "name")
        action = self._string_field(normalized, "action", "operation")
        errors: list[str] = list(normalized.get("__field_errors__", []))
        errors.extend(self._conflicting_alias_errors(normalized, "tool_id", _TOOL_ID_ALIASES))
        errors.extend(self._conflicting_alias_errors(normalized, "action", _ACTION_ALIASES))
        errors.extend(self._conflicting_alias_errors(normalized, "arguments", _ARGUMENT_ALIASES))
        errors.extend(self._conflicting_alias_errors(normalized, "requested_side_effects", _SIDE_EFFECT_ALIASES))

        if not tool_id:
            errors.append("missing_tool_id")
        elif not _IDENTIFIER_RE.match(tool_id):
            errors.append("invalid_tool_id")

        if not action:
            errors.append("missing_action")
        elif not _IDENTIFIER_RE.match(action):
            errors.append("invalid_action")

        arguments, argument_warnings, argument_errors = self._arguments(normalized)
        warnings = [*warnings, *argument_warnings]
        errors.extend(argument_errors)

        requested_side_effects, side_effect_errors = self._requested_side_effects(normalized)
        errors.extend(side_effect_errors)

        if errors:
            return ToolCallCanonicalizationResult(
                accepted=False,
                status=ToolCallParseStatus.REJECTED,
                method=method,
                raw_sha256=raw_hash,
                errors=errors,
                warnings=warnings,
            )

        capability = self._string_field(normalized, "capability")
        target = self._string_field(normalized, "target")
        canonical_data = {
            "tool_id": tool_id,
            "action": action,
            "arguments": arguments,
            "capability": capability,
            "target": target,
            "requested_side_effects": [effect.value for effect in requested_side_effects],
        }
        canonical_hash = hashlib.sha256(
            json.dumps(canonical_data, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        call = CanonicalToolCall(
            tool_id=tool_id or "",
            action=action or "",
            arguments=arguments,
            capability=capability,
            target=target,
            requested_side_effects=requested_side_effects,
            canonical_hash=canonical_hash,
        )
        status = ToolCallParseStatus.CANONICAL if method == ToolCallParseMethod.JSON and not warnings else ToolCallParseStatus.RECOVERED
        return ToolCallCanonicalizationResult(
            accepted=True,
            status=status,
            method=method,
            raw_sha256=raw_hash,
            call=call,
            warnings=warnings,
        )

    @staticmethod
    def _string_field(fields: dict[str, Any], *aliases: str) -> str | None:
        for alias in aliases:
            value = fields.get(alias)
            if value is None:
                continue
            if isinstance(value, str):
                stripped = value.strip().strip("\"'")
                return stripped or None
            if isinstance(value, int | float):
                return str(value)
        return None

    @staticmethod
    def _conflicting_alias_errors(fields: dict[str, Any], canonical_name: str, aliases: tuple[str, ...]) -> list[str]:
        present = [alias for alias in aliases if alias in fields]
        if len(present) < 2:
            return []
        fingerprints = {ToolCallProtocol._field_fingerprint(fields[alias]) for alias in present}
        if len(fingerprints) <= 1:
            return []
        return [f"conflicting_{canonical_name}_fields"]

    @staticmethod
    def _field_fingerprint(value: Any) -> str:
        if isinstance(value, str):
            return value.strip().strip("\"'")
        return json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))

    @staticmethod
    def _arguments(fields: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
        value: Any = None
        for alias in ("arguments", "args", "input"):
            if alias in fields:
                value = fields[alias]
                break
        if value is None:
            return {}, [], []
        warnings: list[str] = []
        errors: list[str] = []
        if isinstance(value, dict):
            arguments = value
        elif isinstance(value, str):
            text = value.strip()
            try:
                decoded = json.loads(text)
            except json.JSONDecodeError:
                arguments = {"raw": text}
                warnings.append("arguments_preserved_as_raw_text")
            else:
                if isinstance(decoded, dict):
                    arguments = decoded
                else:
                    arguments = {"value": decoded}
                    warnings.append("arguments_wrapped_non_object_json")
        else:
            arguments = {"value": value}
            warnings.append("arguments_wrapped_non_object_value")

        if len(arguments) > MAX_TOOL_ARGUMENT_KEYS:
            errors.append("too_many_argument_keys")
        return arguments, warnings, errors

    @staticmethod
    def _requested_side_effects(fields: dict[str, Any]) -> tuple[list[ToolSideEffect], list[str]]:
        value: Any = None
        for alias in ("requested_side_effects", "side_effects"):
            if alias in fields:
                value = fields[alias]
                break
        if value is None:
            return [], []
        if isinstance(value, str):
            text = value.strip()
            try:
                decoded = json.loads(text)
            except json.JSONDecodeError:
                decoded = [item.strip() for item in re.split(r"[,|]", text) if item.strip()]
        elif isinstance(value, list):
            decoded = value
        else:
            return [], ["invalid_requested_side_effects"]

        effects: list[ToolSideEffect] = []
        errors: list[str] = []
        for item in decoded:
            try:
                effects.append(ToolSideEffect(str(item).strip().strip("\"'")))
            except ValueError:
                errors.append(f"unknown_side_effect:{item}")
        return list(dict.fromkeys(effects)), errors

    @staticmethod
    def _first_json_object(raw: str) -> str | None:
        start: int | None = None
        depth = 0
        in_string = False
        escaped = False
        for index, char in enumerate(raw):
            if start is None:
                if char == "{":
                    start = index
                    depth = 1
                continue
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return raw[start : index + 1]
        return None

    @staticmethod
    def _finish(
        result: ToolCallCanonicalizationResult,
        event_bus: EventBus | None,
        phase: AgentPhase,
    ) -> ToolCallCanonicalizationResult:
        if event_bus is None:
            return result
        call_payload = {}
        if result.call is not None:
            call_payload = {
                "tool_id": result.call.tool_id,
                "action": result.call.action,
                "capability": result.call.capability,
                "target": result.call.target,
                "argument_keys": sorted(result.call.arguments),
                "requested_side_effects": [effect.value for effect in result.call.requested_side_effects],
                "canonical_hash": result.call.canonical_hash,
            }
        event = event_bus.append(
            AgentEventType.TOOL_CALL_CANONICALIZED,
            "Raw tool-call text canonicalized without execution.",
            phase_before=phase,
            phase_after=phase,
            payload={
                "accepted": result.accepted,
                "status": result.status,
                "method": result.method,
                "raw_sha256": result.raw_sha256,
                "errors": result.errors,
                "warnings": result.warnings,
                **call_payload,
            },
        )
        return result.model_copy(update={"trace_event_id": event.id})
