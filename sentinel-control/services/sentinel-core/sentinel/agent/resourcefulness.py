from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any

from pydantic import Field, model_validator

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.mission.models import MissionAction, MissionAuthorityEnvelope
from sentinel.shared.models import SentinelModel


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return f"{prefix}_{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]}"


class DebrouilleLevel(StrEnum):
    D0_OBEY = "D0_obey"
    D1_REPAIR = "D1_repair"
    D2_SUBSTITUTE = "D2_substitute"
    D3_REPLAN = "D3_replan"
    D4_EXPLORE = "D4_explore"
    D5_PROPOSE_EXTENSION = "D5_propose_extension"


class FallbackPlanSet(SentinelModel):
    id: str = ""
    mission_id: str
    level: DebrouilleLevel
    plans: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    bounded: bool = True
    execution_started: bool = False
    authority_expansion: bool = False

    @model_validator(mode="after")
    def _validate(self) -> FallbackPlanSet:
        if not self.id:
            self.id = _stable_id("fallback", {"mission_id": self.mission_id, "level": self.level.value, "plans": self.plans, "evidence_refs": self.evidence_refs})
        return self


class ToolSubstitutionDecision(SentinelModel):
    id: str = ""
    mission_id: str
    original_tool: str
    original_action: str
    substitute_tool: str
    substitute_action: str
    authorized: bool
    reason: str
    execution_started: bool = False
    authority_expansion: bool = False

    @model_validator(mode="after")
    def _validate(self) -> ToolSubstitutionDecision:
        if not self.id:
            self.id = _stable_id(
                "tsub",
                {
                    "mission_id": self.mission_id,
                    "original_tool": self.original_tool,
                    "original_action": self.original_action,
                    "substitute_tool": self.substitute_tool,
                    "substitute_action": self.substitute_action,
                    "authorized": self.authorized,
                },
            )
        return self


class PartialSuccessReport(SentinelModel):
    id: str = ""
    mission_id: str
    summary: str
    completed_outputs: list[str] = Field(default_factory=list)
    missing_authority: list[str] = Field(default_factory=list)
    evidence_refs: list[str]
    full_success: bool = False
    authority_expansion: bool = False

    @model_validator(mode="after")
    def _validate(self) -> PartialSuccessReport:
        if not self.evidence_refs:
            raise ValueError("PartialSuccessReport requires evidence refs.")
        if not self.id:
            self.id = _stable_id(
                "psuccess",
                {
                    "mission_id": self.mission_id,
                    "summary": self.summary,
                    "completed_outputs": self.completed_outputs,
                    "missing_authority": self.missing_authority,
                    "evidence_refs": self.evidence_refs,
                },
            )
        return self


class AuthorityExtensionProposal(SentinelModel):
    id: str = ""
    mission_id: str
    requested_authority: list[str]
    reason: str
    risk_summary: str
    scope_limit: str
    expiry: str
    evidence_refs: list[str] = Field(default_factory=list)
    proposal_only: bool = True
    activated: bool = False
    authority_expansion: bool = False

    @model_validator(mode="after")
    def _validate(self) -> AuthorityExtensionProposal:
        if not self.id:
            self.id = _stable_id(
                "authprop",
                {
                    "mission_id": self.mission_id,
                    "requested_authority": self.requested_authority,
                    "reason": self.reason,
                    "risk_summary": self.risk_summary,
                    "scope_limit": self.scope_limit,
                    "expiry": self.expiry,
                },
            )
        return self


class ResourcefulnessDecision(SentinelModel):
    id: str = ""
    mission_id: str
    level: DebrouilleLevel
    reason: str
    fallback_plan_set: FallbackPlanSet | None = None
    tool_substitution_decision: ToolSubstitutionDecision | None = None
    partial_success_report: PartialSuccessReport | None = None
    authority_extension_proposal: AuthorityExtensionProposal | None = None
    advisory_only: bool = True
    execution_started: bool = False
    authority_expansion: bool = False
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> ResourcefulnessDecision:
        if not self.id:
            self.id = _stable_id(
                "rdec",
                {
                    "mission_id": self.mission_id,
                    "level": self.level.value,
                    "reason": self.reason,
                    "fallback": self.fallback_plan_set.id if self.fallback_plan_set else None,
                    "substitution": self.tool_substitution_decision.id if self.tool_substitution_decision else None,
                    "partial": self.partial_success_report.id if self.partial_success_report else None,
                    "proposal": self.authority_extension_proposal.id if self.authority_extension_proposal else None,
                },
            )
        return self


class ResourcefulnessEngine:
    """Routes tactical resourcefulness inside a fixed authority envelope."""

    def route(
        self,
        envelope: MissionAuthorityEnvelope,
        *,
        blocked_action: MissionAction | None = None,
        failure_type: str = "none",
        substitute_tool: str | None = None,
        substitute_action: str | None = None,
        uncertain_branches: int = 0,
        missing_authority: list[str] | None = None,
        partial_outputs: list[str] | None = None,
        evidence_refs: list[str] | None = None,
        event_bus: EventBus | None = None,
    ) -> ResourcefulnessDecision:
        refs = evidence_refs or []
        if blocked_action is not None and blocked_action.mission_id != envelope.id:
            raise ValueError("Blocked action mission_id must match envelope id.")

        substitution = None
        if blocked_action is not None and substitute_tool and substitute_action:
            authorized = self._is_authorized(envelope, substitute_tool, substitute_action)
            substitution = ToolSubstitutionDecision(
                mission_id=envelope.id,
                original_tool=blocked_action.tool,
                original_action=blocked_action.action_type,
                substitute_tool=substitute_tool,
                substitute_action=substitute_action,
                authorized=authorized,
                reason="authorized_substitution" if authorized else "substitution_outside_authority",
            )
            if authorized:
                decision = ResourcefulnessDecision(
                    mission_id=envelope.id,
                    level=DebrouilleLevel.D2_SUBSTITUTE,
                    reason="authorized_substitution_available",
                    tool_substitution_decision=substitution,
                )
                return self._record(decision, event_bus)

        if missing_authority:
            proposal = AuthorityExtensionProposal(
                mission_id=envelope.id,
                requested_authority=missing_authority,
                reason="mission_blocked_by_missing_authority",
                risk_summary="Requires explicit user approval before activation.",
                scope_limit="limited_to_requested_authority_for_this_mission",
                expiry="single_mission_or_short_expiry_required",
                evidence_refs=refs,
            )
            partial = None
            if partial_outputs:
                partial = PartialSuccessReport(
                    mission_id=envelope.id,
                    summary="Partial useful result produced before authority boundary.",
                    completed_outputs=partial_outputs,
                    missing_authority=missing_authority,
                    evidence_refs=refs,
                )
            decision = ResourcefulnessDecision(
                mission_id=envelope.id,
                level=DebrouilleLevel.D5_PROPOSE_EXTENSION,
                reason="authority_extension_proposal_required",
                tool_substitution_decision=substitution,
                partial_success_report=partial,
                authority_extension_proposal=proposal,
            )
            return self._record(decision, event_bus)

        if failure_type == "repair":
            fallback = FallbackPlanSet(mission_id=envelope.id, level=DebrouilleLevel.D1_REPAIR, plans=["repair_same_plan"], evidence_refs=refs)
            return self._record(ResourcefulnessDecision(mission_id=envelope.id, level=DebrouilleLevel.D1_REPAIR, reason="repair_same_plan", fallback_plan_set=fallback), event_bus)

        if failure_type == "replan":
            fallback = FallbackPlanSet(mission_id=envelope.id, level=DebrouilleLevel.D3_REPLAN, plans=["create_alternate_plan_inside_envelope"], evidence_refs=refs)
            return self._record(ResourcefulnessDecision(mission_id=envelope.id, level=DebrouilleLevel.D3_REPLAN, reason="replan_inside_envelope", fallback_plan_set=fallback), event_bus)

        if uncertain_branches > 1:
            plans = [f"explore_authorized_branch_{index + 1}" for index in range(min(uncertain_branches, 5))]
            fallback = FallbackPlanSet(mission_id=envelope.id, level=DebrouilleLevel.D4_EXPLORE, plans=plans, evidence_refs=refs)
            return self._record(ResourcefulnessDecision(mission_id=envelope.id, level=DebrouilleLevel.D4_EXPLORE, reason="bounded_exploration_inside_envelope", fallback_plan_set=fallback), event_bus)

        if substitution is not None:
            return self._record(
                ResourcefulnessDecision(
                    mission_id=envelope.id,
                    level=DebrouilleLevel.D2_SUBSTITUTE,
                    reason="unauthorized_substitution_rejected",
                    tool_substitution_decision=substitution,
                ),
                event_bus,
            )

        return self._record(ResourcefulnessDecision(mission_id=envelope.id, level=DebrouilleLevel.D0_OBEY, reason="no_block_detected"), event_bus)

    @staticmethod
    def _is_authorized(envelope: MissionAuthorityEnvelope, tool: str, action: str) -> bool:
        forbidden = {item.lower() for item in envelope.forbidden_actions}
        return tool in envelope.allowed_tools and action in envelope.allowed_actions and tool.lower() not in forbidden and action.lower() not in forbidden

    @staticmethod
    def _record(decision: ResourcefulnessDecision, event_bus: EventBus | None) -> ResourcefulnessDecision:
        if event_bus is None:
            return decision
        trace_refs = []
        route_event = event_bus.append(
            AgentEventType.RESOURCEFULNESS_ROUTED,
            "Resourcefulness routed advisably inside the mission authority envelope.",
            payload={
                "decision_id": decision.id,
                "level": decision.level.value,
                "reason": decision.reason,
                "advisory_only": True,
                "execution_started": False,
                "authority_expansion": False,
            },
        )
        trace_refs.append(route_event.id)
        if decision.fallback_plan_set is not None:
            event = event_bus.append(
                AgentEventType.FALLBACK_PLAN_CREATED,
                "Fallback plan created without execution.",
                payload={"decision_id": decision.id, "fallback_plan_set_id": decision.fallback_plan_set.id, "plans": decision.fallback_plan_set.plans, "execution_started": False, "authority_expansion": False},
                trace_refs=trace_refs,
            )
            trace_refs.append(event.id)
        if decision.tool_substitution_decision is not None:
            event = event_bus.append(
                AgentEventType.TOOL_SUBSTITUTION_PROPOSED,
                "Tool substitution proposed without activating new authority.",
                payload={
                    "decision_id": decision.id,
                    "substitution_id": decision.tool_substitution_decision.id,
                    "authorized": decision.tool_substitution_decision.authorized,
                    "execution_started": False,
                    "authority_expansion": False,
                },
                trace_refs=trace_refs,
            )
            trace_refs.append(event.id)
        if decision.partial_success_report is not None:
            event = event_bus.append(
                AgentEventType.PARTIAL_SUCCESS_DECLARED,
                "Partial success declared with evidence refs.",
                payload={"decision_id": decision.id, "partial_success_report_id": decision.partial_success_report.id, "full_success": False, "authority_expansion": False},
                trace_refs=trace_refs,
            )
            trace_refs.append(event.id)
        if decision.authority_extension_proposal is not None:
            event = event_bus.append(
                AgentEventType.AUTHORITY_EXTENSION_PROPOSED,
                "Authority extension proposed without activation.",
                payload={
                    "decision_id": decision.id,
                    "proposal_id": decision.authority_extension_proposal.id,
                    "proposal_only": True,
                    "activated": False,
                    "authority_expansion": False,
                },
                trace_refs=trace_refs,
            )
            trace_refs.append(event.id)
        return decision.model_copy(update={"trace_refs": trace_refs})
