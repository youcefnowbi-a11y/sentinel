from __future__ import annotations

from pathlib import Path

from sentinel.agent import (
    ActionEvaluator,
    AgentEventType,
    AgentRuntime,
    ContextBuilder,
    EffortLevel,
    EffortRouter,
    EventBus,
    HypothesisStatus,
    HypothesisVerificationResult,
    MissionHypothesis,
    ToolSelectionResult,
)
from sentinel.agent.state import AgentState
from sentinel.agent.uncertainty import Question
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


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
        "mission_title": "P1F effort router test",
        "mission_objective": "Route cognitive effort before planning.",
        "success_criteria": ["Effort routing trace exists"],
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


def test_effort_router_routes_low_when_hypotheses_are_verified():
    env = envelope()
    context = ContextBuilder().build(env, evidence_refs=["ev_wtp"])
    state = AgentState(mission_id=env.id)
    bus = EventBus(env.id)
    hypothesis_result = HypothesisVerificationResult(
        hypotheses=[verified_hypothesis(env)],
        verified_hypotheses=[verified_hypothesis(env)],
    )
    tool_selection = ToolSelectionResult(selected_tools=["safe_file_writer"])
    action_result = ActionEvaluator().evaluate(context, state, tool_selection, hypothesis_result, event_bus=bus)

    route = EffortRouter().route(context, state, tool_selection, hypothesis_result, action_result, event_bus=bus)

    assert route.level == EffortLevel.LOW
    assert route.recommended_cycles == 0
    assert 0.0 <= route.score <= 1.0
    assert route.trace_refs
    assert AgentEventType.EFFORT_ROUTED in [event.event_type for event in bus.events()]


def test_effort_router_increases_effort_when_hypotheses_are_unverified():
    env = envelope()
    context = ContextBuilder().build(env)
    state = AgentState(mission_id=env.id)
    bus = EventBus(env.id)
    hypothesis_result = HypothesisVerificationResult()
    tool_selection = ToolSelectionResult(selected_tools=["safe_file_writer"])
    action_result = ActionEvaluator().evaluate(context, state, tool_selection, hypothesis_result, event_bus=bus)

    route = EffortRouter().route(context, state, tool_selection, hypothesis_result, action_result, event_bus=bus)

    assert route.level in {EffortLevel.MEDIUM, EffortLevel.HIGH}
    assert route.recommended_cycles >= 1
    assert "hypotheses_need_verification" in route.reason
    assert route.max_parallel_workers == 1


def test_effort_router_can_route_extreme_without_parallel_workers_or_execution():
    env = envelope(max_actions=50)
    context = ContextBuilder().build(env)
    state = AgentState(
        mission_id=env.id,
        open_questions=[
            Question(question="What evidence proves WTP?", blocks_completion=True),
            Question(question="What competitor gap survives review?", blocks_completion=True),
            Question(question="What channel can reach buyers?", blocks_completion=True),
        ],
    )
    bus = EventBus(env.id)
    weak_hypothesis = MissionHypothesis(
        mission_id=env.id,
        statement="The market will pay for this launch workflow.",
        source="test",
        status=HypothesisStatus.NEEDS_EVIDENCE,
    )
    hypothesis_result = HypothesisVerificationResult(hypotheses=[weak_hypothesis])
    tool_selection = ToolSelectionResult(
        selected_tools=["safe_file_writer"],
        blocked_tools=["blocked_shell", "blocked_email", "blocked_browser", "blocked_payment"],
    )
    action_result = ActionEvaluator().evaluate(context, state, tool_selection, hypothesis_result, event_bus=bus)

    route = EffortRouter().route(context, state, tool_selection, hypothesis_result, action_result, event_bus=bus)

    assert route.level == EffortLevel.EXTREME
    assert route.recommended_cycles == 3
    assert route.max_parallel_workers == 1
    assert "hypotheses_need_verification" in route.reason


def test_runtime_records_effort_route_before_planning(tmp_path: Path):
    env = envelope()

    result = AgentRuntime(project_root=tmp_path).run(env, {"idea": "Sentinel Launch"}, evidence_refs=["ev_wtp"])
    event_types = [event.event_type for event in result.trace]

    assert result.success is True
    assert result.effort_route is not None
    assert result.effort_route.level in {EffortLevel.LOW, EffortLevel.MEDIUM, EffortLevel.HIGH, EffortLevel.EXTREME}
    assert event_types.index(AgentEventType.OBJECTIVE_SCORED) < event_types.index(AgentEventType.EFFORT_ROUTED)
    assert event_types.index(AgentEventType.EFFORT_ROUTED) < event_types.index(AgentEventType.PLAN_CREATED)
    plan_event = next(event for event in result.trace if event.event_type == AgentEventType.PLAN_CREATED)
    assert plan_event.payload["effort_level"] == result.effort_route.level
    assert plan_event.payload["effort_score"] == result.effort_route.score


def test_effort_router_is_consultative_and_does_not_execute_external_powers(tmp_path: Path):
    env = envelope()

    result = AgentRuntime(project_root=tmp_path).run(env, {"idea": "No external execution"}, evidence_refs=["ev_wtp"])
    event_types = [event.event_type for event in result.trace]

    assert result.effort_route is not None
    assert AgentEventType.EFFORT_ROUTED in event_types
    assert all("browser" not in event.event_type for event in result.trace)
    assert all("shell" not in str(event.payload).lower() for event in result.trace if event.event_type == AgentEventType.EFFORT_ROUTED)
