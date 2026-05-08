from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from sentinel.agent.events import AgentEventType
from sentinel.agent.llm.context_pack import ContextPack
from sentinel.agent.phases import AgentPhase
from sentinel.shared.models import SentinelModel, new_id


class LLMRole(StrEnum):
    BROWSER_PLANNER = "browser_planner"
    BROWSER_VERIFIER = "browser_verifier"


class LLMReasoningOutput(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("llmout"))
    role: LLMRole
    context_pack_id: str
    context_pack_sha256: str
    drafted_intent: dict[str, Any] = Field(default_factory=dict)
    reasoning_summary: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    trace_event_id: str | None = None


class LLMVerificationOutput(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("llmver"))
    role: LLMRole = LLMRole.BROWSER_VERIFIER
    before_context_pack_id: str
    after_context_pack_id: str
    accepted: bool
    findings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    trace_event_id: str | None = None


class BrowserPlannerRole:
    """Bounded planner role: drafts intent JSON, never executes it."""

    def draft(
        self,
        context_pack: ContextPack,
        drafted_intent: dict[str, Any],
        *,
        reasoning_summary: str = "",
        event_bus=None,
        phase: AgentPhase = AgentPhase.TOOL_SELECTING,
    ) -> LLMReasoningOutput:
        output = LLMReasoningOutput(
            role=LLMRole.BROWSER_PLANNER,
            context_pack_id=context_pack.context_pack_id,
            context_pack_sha256=context_pack.context_pack_sha256,
            drafted_intent={
                **drafted_intent,
                "arguments": {
                    **dict(drafted_intent.get("arguments") or {}),
                    "context_pack_id": context_pack.context_pack_id,
                    "context_pack_sha256": context_pack.context_pack_sha256,
                },
            },
            reasoning_summary=reasoning_summary,
            evidence_refs=list(drafted_intent.get("evidence_refs", [])),
        )
        if event_bus is None:
            return output
        event = event_bus.append(
            AgentEventType.LLM_REASONING_DRAFTED,
            "Bounded LLM planner drafted a tool intent for compiler review.",
            phase_before=phase,
            phase_after=phase,
            payload={
                "role": output.role,
                "context_pack_id": output.context_pack_id,
                "context_pack_sha256": output.context_pack_sha256,
                "draft_argument_keys": sorted(output.drafted_intent.get("arguments", {})),
                "evidence_refs": output.evidence_refs,
            },
            trace_refs=context_pack.trace_refs,
        )
        return output.model_copy(update={"trace_event_id": event.id})


class BrowserVerifierRole:
    """Bounded verifier role: checks grounding shape, never grants authority."""

    def verify(
        self,
        before_pack: ContextPack,
        after_pack: ContextPack,
        receipt: dict[str, Any],
        *,
        event_bus=None,
        phase: AgentPhase = AgentPhase.ARTIFACT_REVIEWING,
    ) -> LLMVerificationOutput:
        findings: list[str] = []
        if before_pack.mission_id != after_pack.mission_id:
            findings.append("context_pack_mission_changed")
        if not receipt.get("context_pack_id"):
            findings.append("receipt_missing_context_pack_id")
        if not receipt.get("trace_refs"):
            findings.append("receipt_missing_trace_refs")
        if not receipt.get("evidence_refs"):
            findings.append("receipt_missing_evidence_refs")
        if receipt.get("context_pack_id") and receipt.get("context_pack_id") != before_pack.context_pack_id:
            findings.append("receipt_context_pack_mismatch")
        output = LLMVerificationOutput(
            before_context_pack_id=before_pack.context_pack_id,
            after_context_pack_id=after_pack.context_pack_id,
            accepted=not findings,
            findings=findings,
            evidence_refs=list(receipt.get("evidence_refs", [])),
        )
        if event_bus is None:
            return output
        event = event_bus.append(
            AgentEventType.LLM_VERIFICATION_DRAFTED,
            "Bounded LLM verifier drafted a grounding verdict.",
            phase_before=phase,
            phase_after=phase,
            payload={
                "accepted": output.accepted,
                "before_context_pack_id": output.before_context_pack_id,
                "after_context_pack_id": output.after_context_pack_id,
                "findings": output.findings,
                "evidence_refs": output.evidence_refs,
            },
            trace_refs=[*before_pack.trace_refs, *after_pack.trace_refs],
        )
        return output.model_copy(update={"trace_event_id": event.id})
