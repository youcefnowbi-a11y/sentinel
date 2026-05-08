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


class ActionClass(StrEnum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class CognitiveAction(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("cact"))
    mission_id: str
    name: str
    action_class: ActionClass
    intent: str
    source: str = "p1e_action_builder"
    tool_id: str | None = None
    capability_name: str | None = None
    trace_refs: list[str] = Field(default_factory=list)


class WorldModelPrediction(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("wpred"))
    mission_id: str
    action_id: str
    predicted_progress_gain: float = Field(ge=0.0, le=1.0)
    predicted_uncertainty_reduction: float = Field(ge=0.0, le=1.0)
    predicted_risk: float = Field(ge=0.0, le=1.0)
    predicted_cost: float = Field(ge=0.0, le=1.0)
    predicted_side_effects: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class ObjectiveScore(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("oscore"))
    mission_id: str
    action_id: str
    pragmatic_value: float = Field(ge=0.0, le=1.0)
    epistemic_value: float = Field(ge=0.0, le=1.0)
    risk_penalty: float = Field(ge=0.0, le=1.0)
    cost_penalty: float = Field(ge=0.0, le=1.0)
    total_score: float
    trace_refs: list[str] = Field(default_factory=list)


class ActionEvaluation(SentinelModel):
    action: CognitiveAction
    prediction: WorldModelPrediction
    score: ObjectiveScore


class ActionEvaluationResult(SentinelModel):
    actions: list[CognitiveAction] = Field(default_factory=list)
    predictions: list[WorldModelPrediction] = Field(default_factory=list)
    scores: list[ObjectiveScore] = Field(default_factory=list)
    evaluations: list[ActionEvaluation] = Field(default_factory=list)
    selected_action_id: str | None = None
    selected_action_name: str | None = None
    trace_refs: list[str] = Field(default_factory=list)


class CognitiveActionBuilder:
    def build(
        self,
        context: AgentContext,
        state: AgentState,
        tool_selection: ToolSelectionResult,
        hypothesis_result: HypothesisVerificationResult,
    ) -> list[CognitiveAction]:
        actions = [
            CognitiveAction(
                mission_id=context.mission.id,
                name="proceed_to_planning",
                action_class=ActionClass.INTERNAL,
                intent="Proceed to mission planning using only verified hypotheses and selected safe tools.",
            ),
            CognitiveAction(
                mission_id=context.mission.id,
                name="seek_more_evidence",
                action_class=ActionClass.INTERNAL,
                intent="Prefer an internal evidence-gathering or clarification step before committing more effort.",
            ),
            CognitiveAction(
                mission_id=context.mission.id,
                name="compress_operational_context",
                action_class=ActionClass.INTERNAL,
                intent="Preserve trace references and reduce working context before further planning.",
            ),
        ]
        for tool_id in tool_selection.selected_tools:
            actions.append(
                CognitiveAction(
                    mission_id=context.mission.id,
                    name=f"use_safe_worker_tool:{tool_id}",
                    action_class=ActionClass.EXTERNAL,
                    intent="Represent a future safe-worker path; P1E scores it but does not execute it.",
                    tool_id=tool_id,
                )
            )
        return actions


class WorldModel:
    def predict(
        self,
        context: AgentContext,
        state: AgentState,
        action: CognitiveAction,
        hypothesis_result: HypothesisVerificationResult,
    ) -> WorldModelPrediction:
        verified_count = len(hypothesis_result.verified_hypotheses)
        uncertainty_pressure = min(1.0, (len(state.open_questions) * 0.2) + (0.45 if verified_count == 0 else 0.0))

        if action.name == "seek_more_evidence":
            return WorldModelPrediction(
                mission_id=context.mission.id,
                action_id=action.id,
                predicted_progress_gain=0.25,
                predicted_uncertainty_reduction=0.75 if uncertainty_pressure else 0.25,
                predicted_risk=0.0,
                predicted_cost=0.08,
                notes=["Internal action; no external tool execution."],
            )
        if action.name == "compress_operational_context":
            return WorldModelPrediction(
                mission_id=context.mission.id,
                action_id=action.id,
                predicted_progress_gain=0.15,
                predicted_uncertainty_reduction=0.25,
                predicted_risk=0.0,
                predicted_cost=0.02,
                notes=["Internal context action; preserves trace references."],
            )
        if action.action_class == ActionClass.EXTERNAL:
            return WorldModelPrediction(
                mission_id=context.mission.id,
                action_id=action.id,
                predicted_progress_gain=0.8,
                predicted_uncertainty_reduction=0.1,
                predicted_risk=0.2,
                predicted_cost=0.0,
                predicted_side_effects=["local_draft_write"],
                notes=["External path remains gated by MissionRunner and SafeExecutors."],
            )
        return WorldModelPrediction(
            mission_id=context.mission.id,
            action_id=action.id,
            predicted_progress_gain=min(0.9, 0.65 + (0.05 * verified_count)),
            predicted_uncertainty_reduction=0.2 if verified_count else 0.05,
            predicted_risk=0.05,
            predicted_cost=0.03,
            notes=["Internal planning action constrained by verified hypotheses."],
        )


class ObjectiveFunctionV2:
    def score(self, context: AgentContext, action: CognitiveAction, prediction: WorldModelPrediction) -> ObjectiveScore:
        risk_weight = 1.3 if action.action_class == ActionClass.EXTERNAL else 1.0
        cost_weight = 0.7
        total = (
            prediction.predicted_progress_gain
            + prediction.predicted_uncertainty_reduction
            - (prediction.predicted_risk * risk_weight)
            - (prediction.predicted_cost * cost_weight)
        )
        return ObjectiveScore(
            mission_id=context.mission.id,
            action_id=action.id,
            pragmatic_value=prediction.predicted_progress_gain,
            epistemic_value=prediction.predicted_uncertainty_reduction,
            risk_penalty=min(1.0, prediction.predicted_risk * risk_weight),
            cost_penalty=min(1.0, prediction.predicted_cost * cost_weight),
            total_score=round(total, 6),
        )


class ActionEvaluator:
    def __init__(
        self,
        *,
        builder: CognitiveActionBuilder | None = None,
        world_model: WorldModel | None = None,
        objective: ObjectiveFunctionV2 | None = None,
    ) -> None:
        self.builder = builder or CognitiveActionBuilder()
        self.world_model = world_model or WorldModel()
        self.objective = objective or ObjectiveFunctionV2()

    def evaluate(
        self,
        context: AgentContext,
        state: AgentState,
        tool_selection: ToolSelectionResult,
        hypothesis_result: HypothesisVerificationResult,
        *,
        event_bus: EventBus,
    ) -> ActionEvaluationResult:
        actions = self.builder.build(context, state, tool_selection, hypothesis_result)
        simulated_event = event_bus.append(
            AgentEventType.WORLD_MODEL_SIMULATED,
            "World model simulated cognitive action candidates without executing them.",
            payload={
                "actions": [
                    {"id": action.id, "name": action.name, "class": action.action_class, "tool_id": action.tool_id}
                    for action in actions
                ]
            },
        )

        actions = [action.model_copy(update={"trace_refs": [simulated_event.id]}) for action in actions]
        evaluations: list[ActionEvaluation] = []
        for action in actions:
            prediction = self.world_model.predict(context, state, action, hypothesis_result)
            prediction = prediction.model_copy(update={"trace_refs": [simulated_event.id]})
            score = self.objective.score(context, action, prediction)
            score = score.model_copy(update={"trace_refs": [simulated_event.id]})
            evaluations.append(ActionEvaluation(action=action, prediction=prediction, score=score))

        selected = max(evaluations, key=lambda item: item.score.total_score) if evaluations else None
        scored_event = event_bus.append(
            AgentEventType.OBJECTIVE_SCORED,
            "Objective function v2 scored simulated cognitive actions.",
            payload={
                "scores": [
                    {"action_id": item.action.id, "name": item.action.name, "score": item.score.total_score}
                    for item in evaluations
                ],
                "selected_action_id": selected.action.id if selected else None,
                "selected_action_name": selected.action.name if selected else None,
            },
            trace_refs=[simulated_event.id],
        )
        return ActionEvaluationResult(
            actions=[item.action for item in evaluations],
            predictions=[item.prediction for item in evaluations],
            scores=[item.score for item in evaluations],
            evaluations=evaluations,
            selected_action_id=selected.action.id if selected else None,
            selected_action_name=selected.action.name if selected else None,
            trace_refs=[simulated_event.id, scored_event.id],
        )
