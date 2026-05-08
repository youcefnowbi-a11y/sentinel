from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import Field

from sentinel.agent.artifact_capture import ArtifactCaptureResult, ArtifactCaptureSandbox, ArtifactCaptureStatus
from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.agent.phases import AgentPhase
from sentinel.agent.tool_call_protocol import CanonicalToolCall
from sentinel.capabilities.models import ToolInvocation
from sentinel.capabilities.registry import ToolRegistry
from sentinel.capabilities.risk import ToolExecutionStatus, ToolSideEffect
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.shared.models import SentinelModel, new_id


class ControlledCapabilityStatus(StrEnum):
    EXECUTED = "executed"
    REJECTED = "rejected"


class ControlledCapabilityReceipt(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("crec"))
    mission_id: str
    tool_call_id: str
    canonical_call_hash: str
    tool_id: str
    action: str
    policy_status: ToolExecutionStatus
    policy_trace_id: str
    capture_trace_id: str
    artifact_id: str
    artifact_path: str
    artifact_sha256: str
    reversible: bool = True
    rollback_strategy: str = "delete_captured_artifact_if_hash_matches"
    scope: str = "mission_capture_root"
    trace_refs: list[str] = Field(default_factory=list)


class ControlledCapabilityResult(SentinelModel):
    accepted: bool
    status: ControlledCapabilityStatus
    tool_id: str
    action: str
    reason: str
    policy_status: ToolExecutionStatus | None = None
    policy_trace_id: str | None = None
    artifact_result: ArtifactCaptureResult | None = None
    receipt: ControlledCapabilityReceipt | None = None
    trace_event_id: str | None = None


class LocalControlledCapabilityRunner:
    """Executes the first P2 local capability through registry policy and capture."""

    SUPPORTED_ACTIONS = frozenset({"create_markdown_file", "export_json"})

    def __init__(
        self,
        *,
        registry: ToolRegistry,
        capture_root: str | Path,
    ) -> None:
        self.registry = registry
        self.capture_root = Path(capture_root).resolve()

    def run(
        self,
        call: CanonicalToolCall,
        envelope: MissionAuthorityEnvelope,
        *,
        event_bus: EventBus,
    ) -> ControlledCapabilityResult:
        if event_bus.mission_id != envelope.id:
            raise ValueError("Controlled capability trace mission_id must match the mission authority envelope.")

        manifest = self.registry.maybe_get(call.tool_id)
        manifest_effects = manifest.side_effects if manifest is not None else []
        requested_effects = self._unique_effects([*manifest_effects, *call.requested_side_effects])
        policy_decision = self.registry.decide(
            ToolInvocation(
                tool_id=call.tool_id,
                action=call.action,
                requested_side_effects=requested_effects,
                capability=call.capability,
                target=call.target,
            ),
            envelope,
            event_bus=event_bus,
        )
        if not policy_decision.allowed:
            return self._rejected(
                call,
                reason=policy_decision.reason,
                event_bus=event_bus,
                policy_status=policy_decision.status,
                policy_trace_id=policy_decision.trace_event_id,
            )

        if call.action not in self.SUPPORTED_ACTIONS:
            return self._rejected(
                call,
                reason="action_not_supported_by_p2a_runner",
                event_bus=event_bus,
                policy_status=policy_decision.status,
                policy_trace_id=policy_decision.trace_event_id,
            )

        sandbox = ArtifactCaptureSandbox(mission_id=envelope.id, capture_root=self.capture_root)
        if call.action == "create_markdown_file":
            artifact_result = self._capture_markdown(call, sandbox, event_bus)
        else:
            artifact_result = self._capture_json(call, sandbox, event_bus)

        if not artifact_result.accepted:
            return self._rejected(
                call,
                reason=artifact_result.reason,
                event_bus=event_bus,
                policy_status=policy_decision.status,
                policy_trace_id=policy_decision.trace_event_id,
                artifact_result=artifact_result,
            )
        if artifact_result.artifact is None or not artifact_result.trace_event_id or not policy_decision.trace_event_id:
            return self._rejected(
                call,
                reason="artifact_receipt_incomplete",
                event_bus=event_bus,
                policy_status=policy_decision.status,
                policy_trace_id=policy_decision.trace_event_id,
                artifact_result=artifact_result,
            )

        receipt = ControlledCapabilityReceipt(
            mission_id=envelope.id,
            tool_call_id=call.id,
            canonical_call_hash=call.canonical_hash,
            tool_id=call.tool_id,
            action=call.action,
            policy_status=policy_decision.status,
            policy_trace_id=policy_decision.trace_event_id,
            capture_trace_id=artifact_result.trace_event_id,
            artifact_id=artifact_result.artifact.id,
            artifact_path=artifact_result.artifact.relative_path,
            artifact_sha256=artifact_result.artifact.sha256,
            trace_refs=[policy_decision.trace_event_id, artifact_result.trace_event_id],
        )

        event = event_bus.append(
            AgentEventType.CONTROLLED_CAPABILITY_EXECUTED,
            "Controlled local capability executed after policy approval.",
            phase_before=AgentPhase.EXECUTING,
            phase_after=AgentPhase.EXECUTING,
            payload={
                "tool_id": call.tool_id,
                "tool_call_id": call.id,
                "canonical_call_hash": call.canonical_hash,
                "action": call.action,
                "policy_status": policy_decision.status,
                "policy_trace_id": policy_decision.trace_event_id,
                "capture_trace_id": artifact_result.trace_event_id,
                "receipt_id": receipt.id,
                "artifact_id": artifact_result.artifact.id if artifact_result.artifact else None,
                "artifact_path": artifact_result.artifact.relative_path if artifact_result.artifact else None,
                "artifact_sha256": artifact_result.artifact.sha256 if artifact_result.artifact else None,
                "reversible": receipt.reversible,
                "rollback_strategy": receipt.rollback_strategy,
                "scope": receipt.scope,
            },
            trace_refs=[ref for ref in [policy_decision.trace_event_id, artifact_result.trace_event_id] if ref],
        )
        receipt = receipt.model_copy(update={"trace_refs": [*receipt.trace_refs, event.id]})
        return ControlledCapabilityResult(
            accepted=True,
            status=ControlledCapabilityStatus.EXECUTED,
            tool_id=call.tool_id,
            action=call.action,
            reason="controlled_capability_executed",
            policy_status=policy_decision.status,
            policy_trace_id=policy_decision.trace_event_id,
            artifact_result=artifact_result,
            receipt=receipt,
            trace_event_id=event.id,
        )

    @staticmethod
    def _capture_markdown(
        call: CanonicalToolCall,
        sandbox: ArtifactCaptureSandbox,
        event_bus: EventBus,
    ) -> ArtifactCaptureResult:
        relative_path = str(call.arguments.get("filename") or call.arguments.get("path") or "")
        content = call.arguments.get("content")
        if not relative_path or content is None:
            return ArtifactCaptureResult(
                accepted=False,
                status=ArtifactCaptureStatus.REJECTED,
                reason="missing_markdown_path_or_content",
            )
        return sandbox.capture_text(
            relative_path=relative_path,
            content=str(content),
            artifact_type=str(call.arguments.get("artifact_type") or "markdown"),
            event_bus=event_bus,
            provenance_refs=[call.id],
            phase=AgentPhase.EXECUTING,
        )

    @staticmethod
    def _capture_json(
        call: CanonicalToolCall,
        sandbox: ArtifactCaptureSandbox,
        event_bus: EventBus,
    ) -> ArtifactCaptureResult:
        relative_path = str(call.arguments.get("filename") or call.arguments.get("path") or "")
        payload = call.arguments.get("payload")
        if not relative_path or not isinstance(payload, (dict, list)):
            return ArtifactCaptureResult(
                accepted=False,
                status=ArtifactCaptureStatus.REJECTED,
                reason="missing_json_path_or_payload",
            )
        return sandbox.capture_json(
            relative_path=relative_path,
            payload=payload,
            artifact_type=str(call.arguments.get("artifact_type") or "json_export"),
            event_bus=event_bus,
            provenance_refs=[call.id],
            phase=AgentPhase.EXECUTING,
        )

    @staticmethod
    def _unique_effects(effects: Iterable[ToolSideEffect]) -> list[ToolSideEffect]:
        return list(dict.fromkeys(effects))

    @staticmethod
    def _rejected(
        call: CanonicalToolCall,
        *,
        reason: str,
        event_bus: EventBus,
        policy_status: ToolExecutionStatus | None = None,
        policy_trace_id: str | None = None,
        artifact_result: ArtifactCaptureResult | None = None,
    ) -> ControlledCapabilityResult:
        event = event_bus.append(
            AgentEventType.CONTROLLED_CAPABILITY_REJECTED,
            "Controlled local capability rejected before execution.",
            phase_before=AgentPhase.EXECUTING,
            phase_after=AgentPhase.EXECUTING,
            payload={
                "tool_id": call.tool_id,
                "action": call.action,
                "reason": reason,
                "policy_status": policy_status,
                "policy_trace_id": policy_trace_id,
                "artifact_reason": artifact_result.reason if artifact_result else None,
            },
            trace_refs=[ref for ref in [policy_trace_id, artifact_result.trace_event_id if artifact_result else None] if ref],
        )
        return ControlledCapabilityResult(
            accepted=False,
            status=ControlledCapabilityStatus.REJECTED,
            tool_id=call.tool_id,
            action=call.action,
            reason=reason,
            policy_status=policy_status,
            policy_trace_id=policy_trace_id,
            artifact_result=artifact_result,
            trace_event_id=event.id,
        )
