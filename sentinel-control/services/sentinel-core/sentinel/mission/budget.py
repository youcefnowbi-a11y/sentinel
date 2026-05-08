from __future__ import annotations

from dataclasses import dataclass, field

from sentinel.mission.models import MissionAction, MissionAuthorityEnvelope, MissionState
from sentinel.mission.trace_timeline import MissionTraceTimeline
from sentinel.shared.enums import MissionTraceEventType


@dataclass(frozen=True)
class BudgetDecision:
    allowed: bool
    exceeded: bool = False
    warning: bool = False
    reasons: list[str] = field(default_factory=list)


class MissionBudgetController:
    def evaluate(
        self,
        envelope: MissionAuthorityEnvelope,
        state: MissionState,
        action: MissionAction,
        timeline: MissionTraceTimeline | None = None,
    ) -> BudgetDecision:
        reasons: list[str] = []
        projected_cost = state.cost_used + action.estimated_cost

        if state.action_count >= envelope.max_actions:
            reasons.append("Mission max_actions limit has been reached.")
            return BudgetDecision(allowed=False, exceeded=True, reasons=reasons)

        if envelope.max_cost_usd > 0 and projected_cost > envelope.max_cost_usd:
            reasons.append("Mission max_cost_usd budget would be exceeded.")
            if timeline:
                timeline.emit(
                    MissionTraceEventType.BUDGET_EXCEEDED,
                    "Mission budget would be exceeded by this action.",
                    action_id=action.id,
                    result={
                        "cost_used": state.cost_used,
                        "estimated_cost": action.estimated_cost,
                        "max_cost_usd": envelope.max_cost_usd,
                    },
                )
            return BudgetDecision(allowed=False, exceeded=True, reasons=reasons)

        warning = False
        if envelope.max_cost_usd > 0 and projected_cost >= envelope.max_cost_usd * 0.8:
            warning = True
            reasons.append("Mission cost is at or above 80 percent of budget.")
            if timeline:
                timeline.emit(
                    MissionTraceEventType.BUDGET_WARNING,
                    "Mission cost is approaching budget limit.",
                    action_id=action.id,
                    result={
                        "cost_used": state.cost_used,
                        "estimated_cost": action.estimated_cost,
                        "max_cost_usd": envelope.max_cost_usd,
                    },
                )

        return BudgetDecision(allowed=True, warning=warning, reasons=reasons)

    def record_usage(self, state: MissionState, action: MissionAction) -> MissionState:
        return state.model_copy(
            update={
                "action_count": state.action_count + 1,
                "cost_used": state.cost_used + action.estimated_cost,
            }
        )
