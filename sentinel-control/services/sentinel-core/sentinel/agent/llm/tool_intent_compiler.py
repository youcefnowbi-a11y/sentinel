from __future__ import annotations

import json
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from pydantic import Field

from sentinel.agent.events import AgentEventType
from sentinel.agent.llm.context_pack import (
    ContextPack,
    ContextPackInjectionRisk,
    hash_context_pack_payload,
)
from sentinel.agent.browser.v3_authority import BrowserV3AuthorityClass, find_browser_v3_authority_grant
from sentinel.agent.phases import AgentPhase
from sentinel.agent.tool_call_protocol import CanonicalToolCall, ToolCallProtocol
from sentinel.capabilities.risk import BLACK_ZONE_SIDE_EFFECTS, ToolSideEffect
from sentinel.shared.models import SentinelModel, new_id

if TYPE_CHECKING:
    from sentinel.agent.event_bus import EventBus
    from sentinel.capabilities.registry import ToolRegistry
    from sentinel.mission.models import MissionAuthorityEnvelope


NON_DELEGATED_BROWSER_ACTION_TOKENS = (
    "submit",
    "post",
    "send",
    "publish",
    "upload",
    "download",
    "login",
    "cookie",
    "storage",
    "private_session",
    "credential",
    "payment",
    "arbitrary_js",
    "javascript",
    "js_evaluate",
    "evaluate",
)


class ToolIntentCompilationStatus(StrEnum):
    COMPILED = "compiled"
    REJECTED = "rejected"


class ToolIntentCompilationStage(StrEnum):
    PARSE = "parse"
    CANONICALIZE = "canonicalize"
    SCHEMA = "schema"
    SEMANTIC = "semantic"
    AUTHORITY = "authority"
    PROVENANCE = "provenance"
    PRE_ACTION = "pre_action"
    REGISTRY = "registry"


class CompiledToolIntent(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("cti"))
    context_pack_id: str
    context_pack_sha256: str
    canonical_call: CanonicalToolCall
    provenance_ref_ids: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    compilation_hash: str
    trace_refs: list[str] = Field(default_factory=list)


class ToolIntentCompilationResult(SentinelModel):
    accepted: bool
    status: ToolIntentCompilationStatus
    failed_stage: ToolIntentCompilationStage | None = None
    compiled_intent: CompiledToolIntent | None = None
    canonical_call: CanonicalToolCall | None = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    trace_event_id: str | None = None
    canonicalization_trace_id: str | None = None


class ToolIntentCompiler:
    """Compiles LLM draft intent into a canonical call under brain authority."""

    def __init__(self, *, protocol: ToolCallProtocol | None = None, registry: ToolRegistry | None = None) -> None:
        self.protocol = protocol or ToolCallProtocol()
        self.registry = registry

    def compile(
        self,
        raw_intent: str | dict[str, Any],
        context_pack: ContextPack,
        envelope: MissionAuthorityEnvelope,
        *,
        event_bus: EventBus | None = None,
        phase: AgentPhase = AgentPhase.TOOL_SELECTING,
    ) -> ToolIntentCompilationResult:
        raw = json.dumps(raw_intent, sort_keys=True, default=str, separators=(",", ":")) if isinstance(raw_intent, dict) else raw_intent
        canonicalization = self.protocol.canonicalize(raw, event_bus=event_bus, phase=phase)
        if not canonicalization.accepted or canonicalization.call is None:
            return self._finish(
                ToolIntentCompilationResult(
                    accepted=False,
                    status=ToolIntentCompilationStatus.REJECTED,
                    failed_stage=ToolIntentCompilationStage.CANONICALIZE,
                    errors=[*canonicalization.errors],
                    warnings=[*canonicalization.warnings],
                    canonicalization_trace_id=canonicalization.trace_event_id,
                ),
                context_pack,
                event_bus,
                phase,
            )

        call = canonicalization.call
        errors: list[str] = []
        warnings: list[str] = list(canonicalization.warnings)

        expected_hash = hash_context_pack_payload(context_pack.model_dump(mode="json"))
        if context_pack.context_pack_sha256 != expected_hash:
            errors.append("context_pack_hash_invalid")
        if call.arguments.get("context_pack_id") != context_pack.context_pack_id:
            errors.append("missing_or_mismatched_context_pack_id")
        if call.arguments.get("context_pack_sha256") != context_pack.context_pack_sha256:
            errors.append("missing_or_mismatched_context_pack_sha256")

        if call.tool_id not in envelope.allowed_tools:
            errors.append("tool_outside_mission_authority")
        if call.action not in envelope.allowed_actions:
            errors.append("action_outside_mission_authority")
        if call.action in envelope.forbidden_actions:
            errors.append("action_forbidden_by_mission")

        available_actions = {intent.kind for intent in context_pack.available_action_intents}
        if call.action not in available_actions:
            errors.append("action_not_available_in_context_pack")

        form_submit_grant = find_browser_v3_authority_grant(
            envelope.browser_v3_authority_grants,
            BrowserV3AuthorityClass.FORM_SUBMIT,
            grant_id=str(call.arguments.get("authority_grant_id") or "") or None,
        )
        download_grant = find_browser_v3_authority_grant(
            envelope.browser_v3_authority_grants,
            BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE,
            grant_id=str(call.arguments.get("authority_grant_id") or "") or None,
        )
        upload_grant = find_browser_v3_authority_grant(
            envelope.browser_v3_authority_grants,
            BrowserV3AuthorityClass.UPLOAD_AUTHORIZED,
            grant_id=str(call.arguments.get("authority_grant_id") or "") or None,
        )
        private_session_grant = find_browser_v3_authority_grant(
            envelope.browser_v3_authority_grants,
            BrowserV3AuthorityClass.PRIVATE_SESSION,
            grant_id=str(call.arguments.get("authority_grant_id") or "") or None,
        )
        login_grant = find_browser_v3_authority_grant(
            envelope.browser_v3_authority_grants,
            BrowserV3AuthorityClass.LOGIN_AUTHORITY,
            grant_id=str(call.arguments.get("authority_grant_id") or "") or None,
        )
        cookie_storage_grant = find_browser_v3_authority_grant(
            envelope.browser_v3_authority_grants,
            BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT,
            grant_id=str(call.arguments.get("authority_grant_id") or "") or None,
        )
        js_grant = find_browser_v3_authority_grant(
            envelope.browser_v3_authority_grants,
            BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED,
            grant_id=str(call.arguments.get("authority_grant_id") or "") or None,
        )
        har_grant = find_browser_v3_authority_grant(
            envelope.browser_v3_authority_grants,
            BrowserV3AuthorityClass.HAR_BODY_CAPTURE,
            grant_id=str(call.arguments.get("authority_grant_id") or "") or None,
        )
        delegated_tokens: set[str] = set()
        if call.action == BrowserV3AuthorityClass.FORM_SUBMIT.value and form_submit_grant is not None:
            delegated_tokens.update({"submit", "post", "send", "publish"})
        if call.action == BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value and download_grant is not None:
            delegated_tokens.add("download")
        if call.action == BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value and upload_grant is not None:
            delegated_tokens.add("upload")
        if call.action == BrowserV3AuthorityClass.PRIVATE_SESSION.value and private_session_grant is not None:
            delegated_tokens.add("private_session")
        if call.action == BrowserV3AuthorityClass.LOGIN_AUTHORITY.value and login_grant is not None:
            delegated_tokens.add("login")
        if call.action == BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value and cookie_storage_grant is not None:
            delegated_tokens.update({"cookie", "storage"})
        if call.action == BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value and js_grant is not None:
            delegated_tokens.update({"javascript", "js_evaluate", "evaluate"})
        non_delegated = self._non_delegated_tokens(call, delegated_tokens=delegated_tokens)
        if non_delegated:
            errors.append(f"non_delegated_browser_power:{','.join(non_delegated)}")

        requested_effects = set(call.requested_side_effects)
        allowed_black_effects = set()
        if call.action == BrowserV3AuthorityClass.FORM_SUBMIT.value and form_submit_grant is not None:
            allowed_black_effects.add(ToolSideEffect.BROWSER_SUBMIT)
        if call.action == BrowserV3AuthorityClass.LOGIN_AUTHORITY.value and login_grant is not None:
            allowed_black_effects.add(ToolSideEffect.CREDENTIAL_ACCESS)
        if requested_effects & (BLACK_ZONE_SIDE_EFFECTS - allowed_black_effects):
            errors.append("non_delegated_side_effect_requested")
        if call.action == BrowserV3AuthorityClass.FORM_SUBMIT.value and form_submit_grant is None:
            errors.append("browser_v3_authority_grant_missing")
        if call.action == BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value and download_grant is None:
            errors.append("browser_v3_authority_grant_missing")
        if call.action == BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value and upload_grant is None:
            errors.append("browser_v3_authority_grant_missing")
        if call.action == BrowserV3AuthorityClass.PRIVATE_SESSION.value and private_session_grant is None:
            errors.append("browser_v3_authority_grant_missing")
        if call.action == BrowserV3AuthorityClass.LOGIN_AUTHORITY.value and login_grant is None:
            errors.append("browser_v3_authority_grant_missing")
        if call.action == BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value and cookie_storage_grant is None:
            errors.append("browser_v3_authority_grant_missing")
        if call.action == BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value and js_grant is None:
            errors.append("browser_v3_authority_grant_missing")
        if call.action == BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value and har_grant is None:
            errors.append("browser_v3_authority_grant_missing")
        errors.extend(self._sensitive_browser_v3_payload_errors(call))

        ref_ids = self._runtime_ref_ids(call.arguments)
        ref_errors, ref_warnings = self._verify_refs(ref_ids, call.arguments, context_pack)
        errors.extend(ref_errors)
        warnings.extend(ref_warnings)

        injection_errors = self._verify_prompt_injection_boundaries(ref_ids, context_pack)
        errors.extend(injection_errors)

        if errors:
            return self._finish(
                ToolIntentCompilationResult(
                    accepted=False,
                    status=ToolIntentCompilationStatus.REJECTED,
                    failed_stage=self._failed_stage(errors),
                    canonical_call=call,
                    errors=errors,
                    warnings=warnings,
                    canonicalization_trace_id=canonicalization.trace_event_id,
                ),
                context_pack,
                event_bus,
                phase,
            )

        if self.registry is not None and event_bus is not None:
            decision = self.registry.decide(call.to_invocation(), envelope, event_bus=event_bus)
            if not decision.allowed:
                return self._finish(
                    ToolIntentCompilationResult(
                        accepted=False,
                        status=ToolIntentCompilationStatus.REJECTED,
                        failed_stage=ToolIntentCompilationStage.REGISTRY,
                        canonical_call=call,
                        errors=[f"registry_rejected:{decision.reason}"],
                        warnings=warnings,
                        canonicalization_trace_id=canonicalization.trace_event_id,
                    ),
                    context_pack,
                    event_bus,
                    phase,
                )

        compilation_payload = {
            "context_pack_id": context_pack.context_pack_id,
            "context_pack_sha256": context_pack.context_pack_sha256,
            "canonical_hash": call.canonical_hash,
            "provenance_ref_ids": sorted(ref_ids),
            "evidence_refs": sorted(self._evidence_refs(call.arguments)),
        }
        compiled = CompiledToolIntent(
            context_pack_id=context_pack.context_pack_id,
            context_pack_sha256=context_pack.context_pack_sha256,
            canonical_call=call,
            provenance_ref_ids=sorted(ref_ids),
            evidence_refs=sorted(self._evidence_refs(call.arguments)),
            compilation_hash=hash_context_pack_payload(compilation_payload),
            trace_refs=[canonicalization.trace_event_id] if canonicalization.trace_event_id else [],
        )
        return self._finish(
            ToolIntentCompilationResult(
                accepted=True,
                status=ToolIntentCompilationStatus.COMPILED,
                compiled_intent=compiled,
                canonical_call=call,
                warnings=warnings,
                canonicalization_trace_id=canonicalization.trace_event_id,
            ),
            context_pack,
            event_bus,
            phase,
        )

    @staticmethod
    def _runtime_ref_ids(arguments: dict[str, Any]) -> set[str]:
        keys = {"ref", "ref_id", "stable_ref_id", "runtime_ref_id", "target_ref", "source_ref_id", "upload_ref_id", "form_ref_id"}
        list_keys = {"refs", "ref_ids", "stable_ref_ids", "runtime_ref_ids", "required_ref_ids"}
        result: set[str] = set()

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    key_name = str(key)
                    if key_name in keys and item is not None:
                        result.add(str(item))
                    elif key_name in list_keys and isinstance(item, list):
                        result.update(str(ref) for ref in item)
                    else:
                        visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)

        visit(arguments)
        return result

    @staticmethod
    def _evidence_refs(arguments: dict[str, Any]) -> set[str]:
        value = arguments.get("evidence_refs", arguments.get("evidenceRefIds", []))
        if not isinstance(value, list):
            return set()
        return {str(item) for item in value}

    @staticmethod
    def _verify_refs(ref_ids: set[str], arguments: dict[str, Any], context_pack: ContextPack) -> tuple[list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []
        refs = {ref.id: ref for ref in context_pack.browser_stable_refs}
        page_sha256 = arguments.get("page_sha256") or arguments.get("expected_page_sha256")
        snapshot_sha256 = arguments.get("snapshot_sha256") or arguments.get("expected_snapshot_sha256")
        for ref_id in sorted(ref_ids):
            ref = refs.get(ref_id)
            if ref is None:
                errors.append(f"runtime_ref_not_found:{ref_id}")
                continue
            if page_sha256 and ref.page_sha256 and page_sha256 != ref.page_sha256:
                errors.append(f"runtime_ref_stale_page:{ref_id}")
            if snapshot_sha256 and ref.snapshot_sha256 and snapshot_sha256 != ref.snapshot_sha256:
                errors.append(f"runtime_ref_stale_snapshot:{ref_id}")
        if not ref_ids and "browser" in str(arguments).lower():
            warnings.append("browser_intent_without_runtime_ref")
        return errors, warnings

    @staticmethod
    def _verify_prompt_injection_boundaries(ref_ids: set[str], context_pack: ContextPack) -> list[str]:
        refs = {ref.id: ref for ref in context_pack.browser_stable_refs}
        high_sources = {
            flag.source_id
            for flag in context_pack.prompt_injection_flags
            if flag.risk == ContextPackInjectionRisk.HIGH or str(flag.risk) == ContextPackInjectionRisk.HIGH.value
        }
        errors: list[str] = []
        for ref_id in sorted(ref_ids):
            ref = refs.get(ref_id)
            if ref is not None and ref.source_id in high_sources:
                errors.append(f"runtime_ref_from_injection_source:{ref_id}")
        return errors

    @staticmethod
    def _non_delegated_tokens(call: CanonicalToolCall, *, delegated_tokens: set[str] | None = None) -> list[str]:
        haystack = json.dumps(
            {
                "tool_id": call.tool_id,
                "action": call.action,
                "target": call.target,
                "arguments": call.arguments,
                "requested_side_effects": [effect.value for effect in call.requested_side_effects],
            },
            sort_keys=True,
            default=str,
        ).lower()
        tokens = {token for token in NON_DELEGATED_BROWSER_ACTION_TOKENS if token in haystack}
        tokens -= delegated_tokens or set()
        return sorted(tokens)

    @staticmethod
    def _sensitive_browser_v3_payload_errors(call: CanonicalToolCall) -> list[str]:
        """Reject LLM-authored payloads that try to smuggle raw secrets/state."""

        forbidden_key_markers: dict[str, tuple[str, ...]] = {
            BrowserV3AuthorityClass.LOGIN_AUTHORITY.value: (
                "password",
                "credential",
                "credential_value",
                "secret",
                "token",
                "cookie_value",
                "api_key",
                "access_token",
                "refresh_token",
            ),
            BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value: (
                "raw_cookie",
                "cookie_value",
                "storage_value",
                "raw_storage",
                "local_storage_value",
                "session_storage_value",
            ),
            BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value: (
                "raw_body",
                "unredacted_body",
                "credential_body",
                "secret_body",
                "authorization",
                "api_key",
                "access_token",
            ),
        }
        forbidden_value_markers: dict[str, tuple[str, ...]] = {
            BrowserV3AuthorityClass.LOGIN_AUTHORITY.value: (
                "password=",
                "bearer ",
                "secret=",
                "credential=",
                "api_key=",
                "access_token=",
            ),
            BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value: (
                "set-cookie:",
                "document.cookie",
                "localstorage[",
                "sessionstorage[",
            ),
            BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value: (
                "authorization:",
                "set-cookie:",
                "password=",
                "bearer ",
                "api_key=",
                "access_token=",
            ),
        }
        key_markers = forbidden_key_markers.get(call.action, ())
        value_markers = forbidden_value_markers.get(call.action, ())
        if not key_markers and not value_markers:
            return []

        errors: set[str] = set()

        def visit(value: Any, path: str) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    child_path = f"{path}.{key}" if path else str(key)
                    lowered_key = str(key).lower()
                    if any(marker in lowered_key for marker in key_markers):
                        if call.action == BrowserV3AuthorityClass.LOGIN_AUTHORITY.value:
                            errors.add(f"credential_payload_not_allowed:{child_path}")
                        elif call.action == BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value:
                            errors.add(f"raw_cookie_storage_value_not_allowed:{child_path}")
                        else:
                            errors.add(f"raw_har_body_value_not_allowed:{child_path}")
                    visit(item, child_path)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    visit(item, f"{path}[{index}]")
            elif isinstance(value, str):
                lowered_value = value.lower()
                if any(marker in lowered_value for marker in value_markers):
                    if call.action == BrowserV3AuthorityClass.LOGIN_AUTHORITY.value:
                        errors.add(f"credential_payload_not_allowed:{path}")
                    elif call.action == BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value:
                        errors.add(f"raw_cookie_storage_value_not_allowed:{path}")
                    else:
                        errors.add(f"raw_har_body_value_not_allowed:{path}")

        visit(call.arguments, "arguments")
        return sorted(errors)

    @staticmethod
    def _failed_stage(errors: list[str]) -> ToolIntentCompilationStage:
        if any("context_pack" in error for error in errors):
            return ToolIntentCompilationStage.SEMANTIC
        if any("authority" in error or "forbidden" in error or "non_delegated" in error for error in errors):
            return ToolIntentCompilationStage.AUTHORITY
        if any("runtime_ref" in error for error in errors):
            return ToolIntentCompilationStage.PROVENANCE
        return ToolIntentCompilationStage.PRE_ACTION

    @staticmethod
    def _finish(
        result: ToolIntentCompilationResult,
        context_pack: ContextPack,
        event_bus: EventBus | None,
        phase: AgentPhase,
    ) -> ToolIntentCompilationResult:
        if event_bus is None:
            return result
        compiled_payload: dict[str, Any] = {}
        if result.compiled_intent is not None:
            compiled_payload = {
                "compiled_intent_id": result.compiled_intent.id,
                "compilation_hash": result.compiled_intent.compilation_hash,
                "provenance_ref_ids": result.compiled_intent.provenance_ref_ids,
                "evidence_refs": result.compiled_intent.evidence_refs,
            }
        if result.canonical_call is not None:
            compiled_payload.update(
                {
                    "tool_id": result.canonical_call.tool_id,
                    "action": result.canonical_call.action,
                    "canonical_hash": result.canonical_call.canonical_hash,
                }
            )
        event = event_bus.append(
            AgentEventType.TOOL_INTENT_COMPILED if result.accepted else AgentEventType.TOOL_INTENT_COMPILATION_REJECTED,
            "LLM tool intent compiled." if result.accepted else "LLM tool intent rejected by compiler.",
            phase_before=phase,
            phase_after=phase,
            payload={
                "accepted": result.accepted,
                "status": result.status,
                "failed_stage": result.failed_stage,
                "context_pack_id": context_pack.context_pack_id,
                "context_pack_sha256": context_pack.context_pack_sha256,
                "canonicalization_trace_id": result.canonicalization_trace_id,
                "errors": result.errors,
                "warnings": result.warnings,
                **compiled_payload,
            },
            trace_refs=[ref for ref in [result.canonicalization_trace_id, *context_pack.trace_refs] if ref],
        )
        trace_refs = list(result.compiled_intent.trace_refs) if result.compiled_intent is not None else []
        if result.compiled_intent is not None:
            result = result.model_copy(update={"compiled_intent": result.compiled_intent.model_copy(update={"trace_refs": [*trace_refs, event.id]})})
        return result.model_copy(update={"trace_event_id": event.id})
