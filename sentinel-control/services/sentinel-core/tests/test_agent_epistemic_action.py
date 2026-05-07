from __future__ import annotations

from sentinel.agent import AgentEventType, EpistemicActionEvaluator, EventBus
from sentinel.mission import MissionAction, MissionAuthorityEnvelope
from sentinel.shared.enums import ConfidenceLevel, ExternalityLevel, MissionMode, MissionType, ReversibilityLevel, SensitivityLevel


SAFE_ACTIONS = ["create_markdown_file", "export_json", "write_trace", "generate_research_questions"]


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_p5h",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P5H epistemic action fixture",
        "mission_objective": "Score candidate actions without execution.",
        "success_criteria": ["Score exists"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer", "research_planner"],
        "allowed_actions": SAFE_ACTIONS,
        "forbidden_actions": ["payment", "spend_money", "credential_access", "send_email"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 30,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def action(env: MissionAuthorityEnvelope, **overrides) -> MissionAction:
    data = {
        "mission_id": env.id,
        "action_type": "generate_research_questions",
        "tool": "research_planner",
        "intent": "validate uncertainty with a safe research probe",
        "expected_output": "questions",
        "estimated_cost": 0.05,
        "confidence": ConfidenceLevel.HIGH,
        "risk_score": 5.0,
        "reversibility": ReversibilityLevel.DRAFT,
        "externality": ExternalityLevel.INTERNAL_LOCAL,
        "sensitivity": SensitivityLevel.INTERNAL,
    }
    data.update(overrides)
    return MissionAction(**data)


def test_informative_safe_action_preferred_and_traced():
    env = envelope()
    bus = EventBus(env.id)
    safe_probe = action(env, intent="validate demand with safe research", evidence_refs=[])
    plain_write = action(env, action_type="create_markdown_file", tool="safe_file_writer", intent="write known summary", evidence_refs=["ev_known"])

    ranked = EpistemicActionEvaluator().rank(env, [plain_write, safe_probe], mission_entropy=0.7)
    traced = EpistemicActionEvaluator().score(env, safe_probe, mission_entropy=0.7, event_bus=bus)

    assert ranked[0].action_id == safe_probe.id
    assert traced.expected_information_gain > 0.5
    assert bus.events()[0].event_type == AgentEventType.EPISTEMIC_ACTION_SCORED


def test_unsafe_high_info_action_is_not_authorized():
    env = envelope()
    unsafe = action(
        env,
        action_type="spend_money",
        tool="payment_tool",
        intent="learn market demand by spending money",
        estimated_cost=0.5,
        risk_score=80,
        sensitivity=SensitivityLevel.FINANCIAL,
        externality=ExternalityLevel.EXTERNAL_PRIVATE,
    )

    score = EpistemicActionEvaluator().score(env, unsafe, mission_entropy=0.9, expected_information_gain=0.9)

    assert score.authority_allowed is False
    assert score.authority_impact == 1.0
    assert score.action_executed is False


def test_low_entropy_direct_route_preferred():
    env = envelope()
    direct = action(env, action_type="create_markdown_file", tool="safe_file_writer", intent="write final known summary", evidence_refs=["ev_known"])
    exploratory = action(env, intent="research compare validate another branch", evidence_refs=[])

    ranked = EpistemicActionEvaluator().rank(env, [exploratory, direct], mission_entropy=0.1)

    assert ranked[0].action_id == direct.id
    assert ranked[0].expected_progress > ranked[1].expected_progress


def test_curiosity_loop_prevented():
    env = envelope()
    curious = action(env, intent="research forever with no progress")

    score = EpistemicActionEvaluator().score(env, curious, mission_entropy=0.9, expected_progress=0.1, expected_information_gain=0.95)

    assert score.curiosity_loop_blocked is True
    assert score.expected_information_gain == 0.25


def test_authority_impact_is_penalized():
    env = envelope()
    out_of_scope = action(env, action_type="send_email", tool="email_sender", intent="send external message")

    score = EpistemicActionEvaluator().score(env, out_of_scope, mission_entropy=0.5)

    assert score.authority_allowed is False
    assert score.authority_impact == 1.0
    assert score.total_action_value < 0.0


def test_epistemic_action_evaluator_does_not_execute_actions():
    env = envelope()
    score = EpistemicActionEvaluator().score(env, action(env), mission_entropy=0.5)

    assert score.advisory_only is True
    assert score.action_executed is False


def test_epistemic_action_evaluator_does_not_expand_authority():
    env = envelope(allowed_tools=["safe_file_writer"], allowed_actions=["create_markdown_file"])
    before = env.model_dump(mode="json")
    score = EpistemicActionEvaluator().score(env, action(env, action_type="create_markdown_file", tool="safe_file_writer"), mission_entropy=0.5)

    assert env.model_dump(mode="json") == before
    assert score.authority_expansion is False
    assert not hasattr(score, "allowed_tools")
    assert not hasattr(score, "allowed_actions")
