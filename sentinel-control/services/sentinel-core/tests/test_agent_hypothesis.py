from __future__ import annotations

import pytest

from sentinel.agent import (
    AgentEventType,
    AgentPhase,
    AgentRuntime,
    ContextBuilder,
    EventBus,
    HypothesisStatus,
    HypothesisVerifier,
    MissionHypothesis,
    PlannerBridge,
    ReviewLoop,
)
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
        "mission_title": "P1D hypothesis test",
        "mission_objective": "Verify hypothesis engine before planning.",
        "success_criteria": ["Hypothesis trace exists"],
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


def test_hypothesis_verifier_promotes_only_locally_verified_hypotheses():
    env = envelope()
    context = ContextBuilder().build(env, evidence_refs=["ev_wtp"])
    bus = EventBus(env.id)

    result = HypothesisVerifier().run(context, event_bus=bus)

    assert result.hypotheses
    assert result.verified_hypotheses
    assert all(hypothesis.status == HypothesisStatus.VERIFIED for hypothesis in result.verified_hypotheses)
    assert all(hypothesis.trace_refs for hypothesis in result.hypotheses)
    assert {event.event_type for event in bus.events()} >= {
        AgentEventType.HYPOTHESES_GENERATED,
        AgentEventType.HYPOTHESES_VERIFIED,
        AgentEventType.HYPOTHESES_REVIEWED,
    }


def test_hypotheses_without_evidence_remain_unpromoted():
    env = envelope()
    context = ContextBuilder().build(env)
    bus = EventBus(env.id)

    result = HypothesisVerifier().run(context, event_bus=bus)

    assert result.verified_hypotheses == []
    assert {hypothesis.status for hypothesis in result.hypotheses} == {HypothesisStatus.NEEDS_EVIDENCE}


def test_adversarial_review_rejects_absolute_claims():
    env = envelope()
    context = ContextBuilder().build(
        env,
        user_input={"hypotheses": ["Everyone is guaranteed to pay and there is zero risk."]},
        evidence_refs=["ev_001"],
    )
    bus = EventBus(env.id)

    result = HypothesisVerifier().run(context, event_bus=bus)
    rejected = [hypothesis for hypothesis in result.hypotheses if "guaranteed" in hypothesis.statement.lower()]

    assert rejected
    assert rejected[0].status == HypothesisStatus.REJECTED
    assert result.adversarial_findings
    assert result.adversarial_findings[0].severity == "high"


def test_planner_bridge_rejects_unverified_hypothesis():
    env = envelope()
    context = ContextBuilder().build(env, evidence_refs=["ev_001"])
    hypothesis = MissionHypothesis(
        mission_id=env.id,
        statement="This should not enter the planner.",
        source="test",
        status=HypothesisStatus.NEEDS_EVIDENCE,
    )

    with pytest.raises(ValueError, match="verified"):
        PlannerBridge().create_plan(context, [], [], verified_hypotheses=[hypothesis])


def test_agent_runtime_records_hypothesis_phase_before_planning(tmp_path):
    env = envelope()

    result = AgentRuntime(project_root=tmp_path).run(env, {"idea": "Sentinel Launch"}, evidence_refs=["ev_wtp"])
    event_types = [event.event_type for event in result.trace]

    assert result.success is True
    assert result.final_phase == AgentPhase.COMPLETED
    assert result.hypotheses
    assert result.verified_hypotheses
    assert all(hypothesis.status == HypothesisStatus.VERIFIED for hypothesis in result.verified_hypotheses)
    assert event_types.index(AgentEventType.HYPOTHESES_REVIEWED) < event_types.index(AgentEventType.PLAN_CREATED)
    plan_event = next(event for event in result.trace if event.event_type == AgentEventType.PLAN_CREATED)
    assert set(plan_event.payload["verified_hypotheses"]) == {hypothesis.id for hypothesis in result.verified_hypotheses}
    assert result.active_plan is not None
    hypothesis_refs = {f"hypothesis:{hypothesis.id}" for hypothesis in result.verified_hypotheses}
    hypothesis_ids = {hypothesis.id for hypothesis in result.verified_hypotheses}
    for step in result.active_plan.steps:
        assert hypothesis_refs <= set(step.action.evidence_refs)
        assert hypothesis_refs <= set(step.required_evidence_refs)
        payload = step.action.input["verified_hypotheses"]
        assert hypothesis_ids <= {item["id"] for item in payload}


def test_review_loop_rejects_plan_that_drops_verified_hypotheses():
    env = envelope()
    context = ContextBuilder().build(env, evidence_refs=["ev_wtp"])
    hypothesis = MissionHypothesis(
        mission_id=env.id,
        statement="Validated evidence must bind the plan.",
        source="test",
        status=HypothesisStatus.VERIFIED,
        confidence=0.9,
        evidence_refs=["ev_wtp"],
    )
    plan = PlannerBridge().create_plan(context, [], [], verified_hypotheses=[hypothesis])
    unsafe_steps = []
    for step in plan.steps:
        action_input = {key: value for key, value in step.action.input.items() if key != "verified_hypotheses"}
        action = step.action.model_copy(
            update={
                "input": action_input,
                "evidence_refs": [ref for ref in step.action.evidence_refs if ref != f"hypothesis:{hypothesis.id}"],
            }
        )
        unsafe_steps.append(
            step.model_copy(
                update={
                    "action": action,
                    "required_evidence_refs": [
                        ref for ref in step.required_evidence_refs if ref != f"hypothesis:{hypothesis.id}"
                    ],
                }
            )
        )
    unsafe_plan = plan.model_copy(update={"steps": unsafe_steps})

    findings = ReviewLoop().review_plan(context, unsafe_plan, [], verified_hypotheses=[hypothesis])
    codes = {finding.code for finding in findings}

    assert "plan_missing_verified_hypothesis_refs" in codes
    assert "plan_missing_verified_hypothesis_payload" in codes


def test_runtime_does_not_promote_unverified_hypotheses_when_evidence_is_absent(tmp_path):
    env = envelope()

    result = AgentRuntime(project_root=tmp_path).run(env, {"idea": "No evidence launch"})

    assert result.success is True
    assert result.hypotheses
    assert result.verified_hypotheses == []
    assert all(hypothesis.status == HypothesisStatus.NEEDS_EVIDENCE for hypothesis in result.hypotheses)
    plan_event = next(event for event in result.trace if event.event_type == AgentEventType.PLAN_CREATED)
    assert plan_event.payload["verified_hypotheses"] == []
