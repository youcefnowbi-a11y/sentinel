from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import Field

from sentinel.agent.effort_router import EffortLevel
from sentinel.agent.events import AgentEventType
from sentinel.agent.phases import ABSORBING_PHASES, AgentPhase
from sentinel.shared.models import SentinelModel, new_id

if TYPE_CHECKING:
    from sentinel.agent.effort_router import EffortRoute
    from sentinel.agent.event_bus import EventBus
    from sentinel.agent.hypothesis import AdversarialFinding
    from sentinel.agent.models import AgentContext, ReviewFinding
    from sentinel.agent.state import AgentState
    from sentinel.agent.world_model import ObjectiveScore


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


class RepairDecisionType(StrEnum):
    NO_REPAIR_NEEDED = "no_repair_needed"
    REPAIR_ALLOWED = "repair_allowed"
    REPAIR_BLOCKED = "repair_blocked"
    ESCALATE = "escalate"


class RepairInstruction(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("repair"))
    mission_id: str
    target: str
    reason: str
    allowed_scope: str = "internal_cognitive_repair_only"
    forbidden_actions: list[str] = Field(default_factory=list)
    expected_fix: str
    trace_refs: list[str] = Field(default_factory=list)


class RepairDecision(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("rdec"))
    mission_id: str
    decision: RepairDecisionType
    repair_pressure: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    findings_used: list[str] = Field(default_factory=list)
    max_repair_cycles: int = Field(ge=0)
    current_repair_cycles: int = Field(ge=0)
    can_continue: bool
    instructions: list[RepairInstruction] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class CognitiveRepairLoop:
    """Bounded controller that decides whether internal repair is permitted.

    P1G is a control barrier, not a retry loop:

        pressure = 0.35F + 0.25A + 0.20C + 0.15E + 0.05M - 0.20B

    F = review finding severity pressure
    A = adversarial finding severity pressure
    C = confidence deficit
    E = cognitive effort pressure
    M = required missing capability pressure
    B = bounded remaining repair budget bonus
    """

    def decide(
        self,
        context: AgentContext,
        state: AgentState,
        *,
        review_findings: list[ReviewFinding],
        adversarial_findings: list[AdversarialFinding],
        objective_scores: list[ObjectiveScore],
        effort_route: EffortRoute,
        event_bus: EventBus,
    ) -> RepairDecision:
        findings_used = self._finding_ids(review_findings, adversarial_findings)
        required_missing = [need.name for need in state.missing_capabilities if need.required]
        has_error_signal = bool(review_findings or adversarial_findings or required_missing)

        if state.phase in ABSORBING_PHASES:
            return self._emit(
                context,
                state,
                event_bus,
                decision=RepairDecisionType.REPAIR_BLOCKED,
                pressure=0.0,
                reasons=["terminal_phase_cannot_be_repaired"],
                findings_used=findings_used,
                instructions=[],
            )
        if not has_error_signal:
            return self._emit(
                context,
                state,
                event_bus,
                decision=RepairDecisionType.NO_REPAIR_NEEDED,
                pressure=0.0,
                reasons=["no_review_or_adversarial_findings"],
                findings_used=[],
                instructions=[],
            )

        finding_pressure = self._review_finding_pressure(review_findings)
        adversarial_pressure = self._adversarial_pressure(adversarial_findings)
        confidence_pressure = _clamp01(1.0 - state.confidence_score)
        effort_pressure = self._effort_pressure(effort_route)
        missing_capability_pressure = 1.0 if required_missing else 0.0
        budget_bonus = self._repair_budget_bonus(state)
        objective_pressure = self._objective_pressure(objective_scores)

        pressure = _clamp01(
            (0.35 * finding_pressure)
            + (0.25 * adversarial_pressure)
            + (0.20 * confidence_pressure)
            + (0.15 * effort_pressure)
            + (0.05 * missing_capability_pressure)
            + (0.05 * objective_pressure)
            - (0.20 * budget_bonus)
        )
        reasons = self._reasons(
            finding_pressure=finding_pressure,
            adversarial_pressure=adversarial_pressure,
            confidence_pressure=confidence_pressure,
            effort_pressure=effort_pressure,
            missing_capability_pressure=missing_capability_pressure,
            budget_bonus=budget_bonus,
            objective_pressure=objective_pressure,
        )
        if state.repair_cycles >= state.max_repair_cycles:
            return self._emit(
                context,
                state,
                event_bus,
                decision=RepairDecisionType.REPAIR_BLOCKED,
                pressure=pressure,
                reasons=[*reasons, "max_repair_cycles_exhausted"],
                findings_used=findings_used,
                instructions=[],
            )
        if pressure >= 0.85:
            return self._emit(
                context,
                state,
                event_bus,
                decision=RepairDecisionType.ESCALATE,
                pressure=pressure,
                reasons=[*reasons, "repair_pressure_exceeds_escalation_threshold"],
                findings_used=findings_used,
                instructions=[],
            )
        if pressure < 0.25:
            return self._emit(
                context,
                state,
                event_bus,
                decision=RepairDecisionType.NO_REPAIR_NEEDED,
                pressure=pressure,
                reasons=[*reasons, "pressure_below_repair_threshold"],
                findings_used=findings_used,
                instructions=[],
            )
        return self._emit(
            context,
            state,
            event_bus,
            decision=RepairDecisionType.REPAIR_ALLOWED,
            pressure=pressure,
            reasons=[*reasons, "bounded_internal_repair_allowed"],
            findings_used=findings_used,
            instructions=self._instructions(context, review_findings, adversarial_findings, required_missing),
        )

    def _emit(
        self,
        context: AgentContext,
        state: AgentState,
        event_bus: EventBus,
        *,
        decision: RepairDecisionType,
        pressure: float,
        reasons: list[str],
        findings_used: list[str],
        instructions: list[RepairInstruction],
    ) -> RepairDecision:
        phase_after = state.phase
        if decision == RepairDecisionType.REPAIR_ALLOWED:
            phase_after = AgentPhase.REPAIRING
        elif decision == RepairDecisionType.ESCALATE:
            phase_after = AgentPhase.ESCALATED
        event = event_bus.append(
            AgentEventType.REPAIR_DECIDED,
            "Bounded cognitive repair decision computed without executing tools.",
            phase_before=state.phase,
            phase_after=phase_after,
            payload={
                "decision": decision,
                "repair_pressure": round(pressure, 6),
                "reasons": reasons,
                "findings_used": findings_used,
                "current_repair_cycles": state.repair_cycles,
                "max_repair_cycles": state.max_repair_cycles,
                "instruction_count": len(instructions),
            },
        )
        instructions = [item.model_copy(update={"trace_refs": [event.id]}) for item in instructions]
        return RepairDecision(
            mission_id=context.mission.id,
            decision=decision,
            repair_pressure=round(pressure, 6),
            reasons=reasons,
            findings_used=findings_used,
            max_repair_cycles=state.max_repair_cycles,
            current_repair_cycles=state.repair_cycles,
            can_continue=decision == RepairDecisionType.REPAIR_ALLOWED,
            instructions=instructions,
            trace_refs=[event.id],
        )

    @staticmethod
    def _review_finding_pressure(findings: list[ReviewFinding]) -> float:
        return max((CognitiveRepairLoop._severity_pressure(finding.severity) for finding in findings), default=0.0)

    @staticmethod
    def _adversarial_pressure(findings: list[AdversarialFinding]) -> float:
        return max((CognitiveRepairLoop._severity_pressure(finding.severity) for finding in findings), default=0.0)

    @staticmethod
    def _severity_pressure(severity: str) -> float:
        return {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.45,
            "low": 0.20,
        }.get(severity.lower(), 0.30)

    @staticmethod
    def _effort_pressure(effort_route: EffortRoute) -> float:
        return {
            EffortLevel.LOW: 0.10,
            EffortLevel.MEDIUM: 0.35,
            EffortLevel.HIGH: 0.65,
            EffortLevel.EXTREME: 1.0,
        }[effort_route.level]

    @staticmethod
    def _repair_budget_bonus(state: AgentState) -> float:
        if state.max_repair_cycles <= 0:
            return 0.0
        remaining_ratio = max(0.0, (state.max_repair_cycles - state.repair_cycles) / state.max_repair_cycles)
        return 0.35 * remaining_ratio

    @staticmethod
    def _objective_pressure(scores: list[ObjectiveScore]) -> float:
        if not scores:
            return 0.0
        best_score = max(score.total_score for score in scores)
        if best_score >= 0.50:
            return 0.0
        return _clamp01(0.50 - best_score)

    @staticmethod
    def _finding_ids(review_findings: list[ReviewFinding], adversarial_findings: list[AdversarialFinding]) -> list[str]:
        review_ids = [finding.code for finding in review_findings]
        adversarial_ids = [finding.id for finding in adversarial_findings]
        return list(dict.fromkeys([*review_ids, *adversarial_ids]))

    @staticmethod
    def _reasons(
        *,
        finding_pressure: float,
        adversarial_pressure: float,
        confidence_pressure: float,
        effort_pressure: float,
        missing_capability_pressure: float,
        budget_bonus: float,
        objective_pressure: float,
    ) -> list[str]:
        reasons: list[str] = []
        if finding_pressure >= 0.75:
            reasons.append("review_findings_high_or_critical")
        if adversarial_pressure >= 0.75:
            reasons.append("adversarial_findings_high_or_critical")
        if confidence_pressure >= 0.45:
            reasons.append("confidence_deficit")
        if effort_pressure >= 0.65:
            reasons.append("high_effort_route")
        if missing_capability_pressure:
            reasons.append("required_capability_missing")
        if objective_pressure:
            reasons.append("objective_score_weak")
        if budget_bonus:
            reasons.append("repair_budget_available")
        return reasons

    @staticmethod
    def _instructions(
        context: AgentContext,
        review_findings: list[ReviewFinding],
        adversarial_findings: list[AdversarialFinding],
        required_missing: list[str],
    ) -> list[RepairInstruction]:
        instructions: list[RepairInstruction] = []
        for finding in review_findings:
            instructions.append(
                RepairInstruction(
                    mission_id=context.mission.id,
                    target=finding.code,
                    reason=finding.message,
                    forbidden_actions=list(context.mission.forbidden_actions),
                    expected_fix="Run an internal bounded correction or convert the issue into a learning proposal.",
                )
            )
        for finding in adversarial_findings:
            instructions.append(
                RepairInstruction(
                    mission_id=context.mission.id,
                    target=finding.target_artifact,
                    reason=finding.finding,
                    forbidden_actions=list(context.mission.forbidden_actions),
                    expected_fix=finding.suggested_repair,
                )
            )
        for capability in required_missing:
            instructions.append(
                RepairInstruction(
                    mission_id=context.mission.id,
                    target=capability,
                    reason="Required capability is unavailable inside current mission authority.",
                    forbidden_actions=list(context.mission.forbidden_actions),
                    expected_fix="Do not fabricate availability; preserve the missing capability for learning proposal.",
                )
            )
        return instructions
