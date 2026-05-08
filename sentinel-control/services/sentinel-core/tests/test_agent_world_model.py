from __future__ import annotations

from pathlib import Path

from sentinel.agent import (
    ActionClass,
    ActionEvaluator,
    AgentEventType,
    AgentRuntime,
    ContextBuilder,
    EventBus,
    HypothesisStatus,
    HypothesisVerificationResult,
    MissionHypothesis,
    ToolSelectionResult,
)
from sentinel.agent.state import AgentState
from sentinel.shared.enums import MissionMode, MissionType
from sentinel.mission import MissionAuthorityEnvelope


SAFE_ACTIONS = [
    "create_project_folder",
    "create_markdown_file",
    "export_json",
    "generate_gtm_pack",
    "generate_landing_copy",
    "generate_outreach_drafts_without_sending",
    "create_watchlist",
    "generate_research_questions",
    "write_trace",
]


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "P1E world model test",
        "mission_objective": "Score internal cognitive actions before planning.",
        "success_criteria": ["Objective score trace exists"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer"],
        "allowed_actions": SAFE_ACTIONS,
        "forbidden_actions": ["send_email", "run_shell_command", "browser_submit_form", "credential_access"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 20,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def verified_hypothesis(env: MissionAuthorityEnvelope) -> MissionHypothesis:
    return MissionHypothesis(
        mission_id=env.id,
        statement="A focused launch pack is more immediately valuable than a broad dashboard.",
        source="test",
        confidence=0.9,
        status=HypothesisStatus.VERIFIED,
        evidence_refs=["ev_wtp"],
    )


def test_action_evaluator_prefers_evidence_when_hypotheses_are_not_verified():
    env = envelope()
    context = ContextBuilder().build(env)
    state = AgentState(mission_id=env.id)
    bus = EventBus(env.id)

    result = ActionEvaluator().evaluate(
        context,
        state,
        ToolSelectionResult(selected_tools=["safe_file_writer"]),
        HypothesisVerificationResult(),
        event_bus=bus,
    )

    assert result.selected_action_name == "seek_more_evidence"
    assert all(0.0 <= score.risk_penalty <= 1.0 for score in result.scores)
    assert all(0.0 <= score.cost_penalty <= 1.0 for score in result.scores)
    assert {event.event_type for event in bus.events()} == {
        AgentEventType.WORLD_MODEL_SIMULATED,
        AgentEventType.OBJECTIVE_SCORED,
    }


def test_action_evaluator_prefers_planning_when_hypotheses_are_verified():
    env = envelope()
    context = ContextBuilder().build(env, evidence_refs=["ev_wtp"])
    state = AgentState(mission_id=env.id)
    bus = EventBus(env.id)

    result = ActionEvaluator().evaluate(
        context,
        state,
        ToolSelectionResult(selected_tools=["safe_file_writer"]),
        HypothesisVerificationResult(verified_hypotheses=[verified_hypothesis(env)]),
        event_bus=bus,
    )

    assert result.selected_action_name == "proceed_to_planning"
    selected_score = next(score.total_score for score in result.scores if score.action_id == result.selected_action_id)
    assert selected_score == max(score.total_score for score in result.scores)
    safe_worker = next(action for action in result.actions if action.name == "use_safe_worker_tool:safe_file_writer")
    assert safe_worker.action_class == ActionClass.EXTERNAL


def test_runtime_records_world_model_and_objective_before_planning(tmp_path: Path):
    env = envelope()

    result = AgentRuntime(project_root=tmp_path).run(env, {"idea": "Sentinel Launch"}, evidence_refs=["ev_wtp"])
    event_types = [event.event_type for event in result.trace]

    assert result.success is True
    assert result.cognitive_actions
    assert result.world_model_predictions
    assert result.objective_scores
    assert result.action_evaluations
    assert result.selected_action_name == "proceed_to_planning"
    assert event_types.index(AgentEventType.WORLD_MODEL_SIMULATED) < event_types.index(AgentEventType.PLAN_CREATED)
    assert event_types.index(AgentEventType.OBJECTIVE_SCORED) < event_types.index(AgentEventType.PLAN_CREATED)
    plan_event = next(event for event in result.trace if event.event_type == AgentEventType.PLAN_CREATED)
    assert plan_event.payload["selected_action_name"] == result.selected_action_name


def test_runtime_keeps_more_evidence_recommendation_consultative(tmp_path: Path):
    env = envelope()

    result = AgentRuntime(project_root=tmp_path).run(env, {"idea": "No evidence launch"})

    assert result.success is True
    assert result.verified_hypotheses == []
    assert result.selected_action_name == "seek_more_evidence"
    assert any(action.name == "proceed_to_planning" for action in result.cognitive_actions)
