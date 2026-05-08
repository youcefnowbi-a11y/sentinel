from __future__ import annotations

from sentinel.agent.hypothesis import HypothesisStatus, MissionHypothesis
from sentinel.agent.models import AgentContext, CapabilityNeed, MethodRef, ToolSelectionResult
from sentinel.mission.models import MissionPlan
from sentinel.mission.registry import MissionRegistry, default_mission_registry


class PlannerBridge:
    def __init__(self, registry: MissionRegistry | None = None, project_root: str | None = None) -> None:
        self.registry = registry or default_mission_registry(project_root)

    def create_plan(
        self,
        context: AgentContext,
        methods: list[MethodRef],
        capabilities: list[CapabilityNeed],
        tool_selection: ToolSelectionResult | None = None,
        verified_hypotheses: list[MissionHypothesis] | None = None,
    ) -> MissionPlan:
        if any(hypothesis.status != HypothesisStatus.VERIFIED for hypothesis in verified_hypotheses or []):
            raise ValueError("PlannerBridge only accepts verified mission hypotheses.")
        definition = self.registry.get(context.mission.mission_type)
        idea = context.user_input.get("idea")
        plan = definition.planner.create_plan(context.mission, idea=idea, evidence_refs=context.evidence_refs)
        return self._attach_verified_hypotheses(plan, verified_hypotheses or [])

    @staticmethod
    def _attach_verified_hypotheses(
        plan: MissionPlan,
        verified_hypotheses: list[MissionHypothesis],
    ) -> MissionPlan:
        if not verified_hypotheses:
            return plan

        hypothesis_refs = [f"hypothesis:{hypothesis.id}" for hypothesis in verified_hypotheses]
        hypothesis_payload = [
            {
                "id": hypothesis.id,
                "statement": hypothesis.statement,
                "confidence": hypothesis.confidence,
                "evidence_refs": hypothesis.evidence_refs,
            }
            for hypothesis in verified_hypotheses
        ]

        steps = []
        for step in plan.steps:
            action_input = {
                **step.action.input,
                "verified_hypotheses": hypothesis_payload,
            }
            action = step.action.model_copy(
                update={
                    "input": action_input,
                    "evidence_refs": _dedupe([*step.action.evidence_refs, *hypothesis_refs]),
                }
            )
            steps.append(
                step.model_copy(
                    update={
                        "action": action,
                        "required_evidence_refs": _dedupe([*step.required_evidence_refs, *hypothesis_refs]),
                    }
                )
            )
        return plan.model_copy(update={"steps": steps})


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))
