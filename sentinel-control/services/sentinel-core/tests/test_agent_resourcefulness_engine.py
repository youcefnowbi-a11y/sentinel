from __future__ import annotations

import pytest

from sentinel.agent import (
    AgentEventType,
    DebrouilleLevel,
    EventBus,
    PartialSuccessReport,
    ResourcefulnessEngine,
)
from sentinel.mission import MissionAction, MissionAuthorityEnvelope
from sentinel.shared.enums import ConfidenceLevel, ExternalityLevel, MissionMode, MissionType, ReversibilityLevel, SensitivityLevel


SAFE_ACTIONS = ["create_markdown_file", "export_json", "write_trace", "generate_research_questions"]


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_p5i",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P5I resourcefulness fixture",
        "mission_objective": "Find authorized fallback routes.",
        "success_criteria": ["Fallback exists"],
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


def blocked_action(env: MissionAuthorityEnvelope, **overrides) -> MissionAction:
    data = {
        "mission_id": env.id,
        "action_type": "send_email",
        "tool": "email_sender",
        "intent": "blocked external send",
        "expected_output": "sent message",
        "estimated_cost": 0.0,
        "confidence": ConfidenceLevel.LOW,
        "risk_score": 80.0,
        "reversibility": ReversibilityLevel.IRREVERSIBLE,
        "externality": ExternalityLevel.EXTERNAL_PRIVATE,
        "sensitivity": SensitivityLevel.PERSONAL,
    }
    data.update(overrides)
    return MissionAction(**data)


def test_d0_obey_when_no_block_detected():
    env = envelope()

    result = ResourcefulnessEngine().route(env)

    assert result.level == DebrouilleLevel.D0_OBEY
    assert result.reason == "no_block_detected"


def test_d1_repair_creates_fallback_trace():
    env = envelope()
    bus = EventBus(env.id)

    result = ResourcefulnessEngine().route(env, failure_type="repair", evidence_refs=["ev_repair"], event_bus=bus)

    assert result.level == DebrouilleLevel.D1_REPAIR
    assert result.fallback_plan_set is not None
    assert result.fallback_plan_set.execution_started is False
    assert AgentEventType.RESOURCEFULNESS_ROUTED in [event.event_type for event in bus.events()]
    assert AgentEventType.FALLBACK_PLAN_CREATED in [event.event_type for event in bus.events()]


def test_d2_authorized_substitution():
    env = envelope()

    result = ResourcefulnessEngine().route(
        env,
        blocked_action=blocked_action(env),
        substitute_tool="safe_file_writer",
        substitute_action="create_markdown_file",
    )

    assert result.level == DebrouilleLevel.D2_SUBSTITUTE
    assert result.tool_substitution_decision is not None
    assert result.tool_substitution_decision.authorized is True


def test_unauthorized_substitution_rejected():
    env = envelope()

    result = ResourcefulnessEngine().route(
        env,
        blocked_action=blocked_action(env),
        substitute_tool="email_sender",
        substitute_action="send_email",
    )

    assert result.level == DebrouilleLevel.D2_SUBSTITUTE
    assert result.tool_substitution_decision is not None
    assert result.tool_substitution_decision.authorized is False
    assert result.execution_started is False


def test_d3_replan_inside_envelope():
    env = envelope()

    result = ResourcefulnessEngine().route(env, failure_type="replan", evidence_refs=["ev_block"])

    assert result.level == DebrouilleLevel.D3_REPLAN
    assert result.fallback_plan_set is not None
    assert "create_alternate_plan_inside_envelope" in result.fallback_plan_set.plans


def test_d4_bounded_exploration_plan():
    env = envelope()

    result = ResourcefulnessEngine().route(env, uncertain_branches=8, evidence_refs=["ev_uncertain"])

    assert result.level == DebrouilleLevel.D4_EXPLORE
    assert result.fallback_plan_set is not None
    assert len(result.fallback_plan_set.plans) == 5
    assert result.fallback_plan_set.bounded is True


def test_d5_extension_proposal_only_no_activation():
    env = envelope()
    bus = EventBus(env.id)

    result = ResourcefulnessEngine().route(
        env,
        blocked_action=blocked_action(env),
        missing_authority=["email_send"],
        partial_outputs=["draft_created"],
        evidence_refs=["ev_partial"],
        event_bus=bus,
    )

    assert result.level == DebrouilleLevel.D5_PROPOSE_EXTENSION
    assert result.authority_extension_proposal is not None
    assert result.authority_extension_proposal.proposal_only is True
    assert result.authority_extension_proposal.activated is False
    assert result.partial_success_report is not None
    event_types = [event.event_type for event in bus.events()]
    assert AgentEventType.PARTIAL_SUCCESS_DECLARED in event_types
    assert AgentEventType.AUTHORITY_EXTENSION_PROPOSED in event_types


def test_partial_success_requires_evidence_refs():
    with pytest.raises(ValueError, match="requires evidence refs"):
        PartialSuccessReport(mission_id="mission", summary="No evidence.", completed_outputs=["draft"], evidence_refs=[])


def test_resourcefulness_engine_does_not_expand_authority():
    env = envelope(allowed_tools=["safe_file_writer"], allowed_actions=["create_markdown_file"])
    before = env.model_dump(mode="json")

    result = ResourcefulnessEngine().route(env, missing_authority=["payment"], evidence_refs=["ev_boundary"])

    assert env.model_dump(mode="json") == before
    assert result.authority_expansion is False
    assert result.authority_extension_proposal is not None
    assert result.authority_extension_proposal.authority_expansion is False


def test_resourcefulness_engine_does_not_execute():
    env = envelope()

    result = ResourcefulnessEngine().route(env, failure_type="repair", evidence_refs=["ev_repair"])

    assert result.advisory_only is True
    assert result.execution_started is False
    assert result.fallback_plan_set is not None
    assert result.fallback_plan_set.execution_started is False
