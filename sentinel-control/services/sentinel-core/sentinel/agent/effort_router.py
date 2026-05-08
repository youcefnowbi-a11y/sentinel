from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import Field

from sentinel.agent.events import AgentEventType
from sentinel.shared.models import SentinelModel, new_id

if TYPE_CHECKING:
    from sentinel.agent.event_bus import EventBus
    from sentinel.agent.hypothesis import HypothesisVerificationResult
    from sentinel.agent.models import AgentContext, ToolSelectionResult
    from sentinel.agent.state import AgentState
    from sentinel.agent.world_model import ActionEvaluationResult


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


class EffortLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class EffortRoute(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("effort"))
    mission_id: str
    level: EffortLevel
    score: float = Field(ge=0.0, le=1.0)
    uncertainty_pressure: float = Field(ge=0.0, le=1.0)
    verification_pressure: float = Field(ge=0.0, le=1.0)
    risk_pressure: float = Field(ge=0.0, le=1.0)
    budget_pressure: float = Field(ge=0.0, le=1.0)
    recommended_cycles: int = Field(ge=0)
    max_parallel_workers: int = Field(ge=1)
    reason: str
    trace_refs: list[str] = Field(default_factory=list)


class EffortRouter:
    """Routes cognitive effort, not execution.

    The P1F equation is deliberately bounded and deterministic:

        effort = 0.35U + 0.30V + 0.20R + 0.15A - 0.20B

    U = unresolved uncertainty pressure
    V = hypothesis verification pressure
    R = risk pressure from simulated actions and blocked tools
    A = action pressure when the selected action asks for more evidence
    B = budget scarcity pressure
    """

    def route(
        self,
        context: AgentContext,
        state: AgentState,
        tool_selection: ToolSelectionResult,
        hypothesis_result: HypothesisVerificationResult,
        action_result: ActionEvaluationResult,
        *,
        event_bus: EventBus,
    ) -> EffortRoute:
        uncertainty_pressure = self._uncertainty_pressure(state, hypothesis_result, action_result)
        verification_pressure = self._verification_pressure(hypothesis_result)
        risk_pressure = self._risk_pressure(tool_selection, action_result)
        budget_pressure = self._budget_pressure(context)
        action_pressure = 1.0 if action_result.selected_action_name == "seek_more_evidence" else 0.0

        score = _clamp01(
            (0.35 * uncertainty_pressure)
            + (0.30 * verification_pressure)
            + (0.20 * risk_pressure)
            + (0.15 * action_pressure)
            - (0.20 * budget_pressure)
        )
        level, recommended_cycles = self._classify(score)
        reason = self._reason(
            level,
            uncertainty_pressure,
            verification_pressure,
            risk_pressure,
            budget_pressure,
            action_pressure,
        )
        event = event_bus.append(
            AgentEventType.EFFORT_ROUTED,
            "Cognitive effort routed deterministically without selecting or executing tools.",
            payload={
                "level": level,
                "score": round(score, 6),
                "uncertainty_pressure": round(uncertainty_pressure, 6),
                "verification_pressure": round(verification_pressure, 6),
                "risk_pressure": round(risk_pressure, 6),
                "budget_pressure": round(budget_pressure, 6),
                "recommended_cycles": recommended_cycles,
                "max_parallel_workers": 1,
            },
            trace_refs=list(dict.fromkeys([*hypothesis_result.trace_refs, *action_result.trace_refs, *tool_selection.trace_refs])),
        )
        return EffortRoute(
            mission_id=context.mission.id,
            level=level,
            score=round(score, 6),
            uncertainty_pressure=round(uncertainty_pressure, 6),
            verification_pressure=round(verification_pressure, 6),
            risk_pressure=round(risk_pressure, 6),
            budget_pressure=round(budget_pressure, 6),
            recommended_cycles=recommended_cycles,
            max_parallel_workers=1,
            reason=reason,
            trace_refs=[event.id],
        )

    @staticmethod
    def _uncertainty_pressure(
        state: AgentState,
        hypothesis_result: HypothesisVerificationResult,
        action_result: ActionEvaluationResult,
    ) -> float:
        pressure = min(0.55, len(state.open_questions) * 0.18)
        if not hypothesis_result.verified_hypotheses:
            pressure += 0.30
        if action_result.selected_action_name == "seek_more_evidence":
            pressure += 0.15
        return _clamp01(pressure)

    @staticmethod
    def _verification_pressure(hypothesis_result: HypothesisVerificationResult) -> float:
        hypotheses = hypothesis_result.hypotheses
        if not hypotheses:
            return 0.50
        verified_count = len(hypothesis_result.verified_hypotheses)
        return _clamp01(1.0 - (verified_count / len(hypotheses)))

    @staticmethod
    def _risk_pressure(tool_selection: ToolSelectionResult, action_result: ActionEvaluationResult) -> float:
        simulated_risk = max((score.risk_penalty for score in action_result.scores), default=0.0)
        tool_pressure = (0.08 * len(tool_selection.blocked_tools)) + (0.04 * len(tool_selection.candidate_tools))
        return _clamp01(simulated_risk + tool_pressure)

    @staticmethod
    def _budget_pressure(context: AgentContext) -> float:
        action_budget = context.mission.max_actions
        if action_budget <= 5:
            pressure = 0.75
        elif action_budget <= 10:
            pressure = 0.45
        else:
            pressure = 0.15

        cost_budget = context.mission.max_cost_usd
        if 0.0 < cost_budget < 0.25:
            pressure = max(pressure, 0.65)
        elif 0.0 < cost_budget < 1.0:
            pressure = max(pressure, 0.35)
        return _clamp01(pressure)

    @staticmethod
    def _classify(score: float) -> tuple[EffortLevel, int]:
        if score < 0.25:
            return EffortLevel.LOW, 0
        if score < 0.55:
            return EffortLevel.MEDIUM, 1
        if score < 0.80:
            return EffortLevel.HIGH, 2
        return EffortLevel.EXTREME, 3

    @staticmethod
    def _reason(
        level: EffortLevel,
        uncertainty_pressure: float,
        verification_pressure: float,
        risk_pressure: float,
        budget_pressure: float,
        action_pressure: float,
    ) -> str:
        factors: list[str] = []
        if uncertainty_pressure >= 0.50:
            factors.append("uncertainty_high")
        if verification_pressure >= 0.50:
            factors.append("hypotheses_need_verification")
        if risk_pressure >= 0.35:
            factors.append("simulated_risk_or_blocked_tools")
        if action_pressure:
            factors.append("selected_action_requests_more_evidence")
        if budget_pressure >= 0.45:
            factors.append("budget_limits_effort")
        if not factors:
            factors.append("bounded_low_uncertainty_path")
        return f"effort={level}; factors={','.join(factors)}"
