from __future__ import annotations

import pytest

from sentinel.agent import (
    AdaptiveDebateRouter,
    AgentCountController,
    AgentEventType,
    AgentOutputContract,
    AgentRoleAssignment,
    AgentRolePurpose,
    AgentSocietyManager,
    AgentSocietyPlan,
    AgentSocietyPlanStatus,
    AuthorityExtensionProposal,
    BayesianBeliefState,
    Belief,
    BrainBench,
    BrainBenchCase,
    BrainMode,
    ContradictionSupport,
    EpistemicActionEvaluator,
    EvidenceSupport,
    MissionEntropyEstimate,
    MissionGlobalWorkspace,
    PartialSuccessReport,
    RequiredAuthority,
    SkillProcedure,
    SkillProcedureGraph,
    ToolSubstitutionDecision,
    WorkspaceDelta,
    WorkspaceFact,
    WorkspaceRejectedClaim,
    WorkspaceSignal,
)
from sentinel.agent.event_bus import EventBus
from sentinel.mission import MissionAction, MissionAuthorityEnvelope
from sentinel.shared.enums import (
    ConfidenceLevel,
    ExternalityLevel,
    MissionMode,
    MissionType,
    ReversibilityLevel,
    SensitivityLevel,
)


SAFE_ACTIONS = ["create_markdown_file", "export_json", "write_trace", "generate_research_questions"]


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_p5l_pm",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P5L premortem fixture",
        "mission_objective": "Exercise Brain L4 failure fixtures.",
        "success_criteria": ["Fixture passes"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer", "research_planner"],
        "allowed_actions": SAFE_ACTIONS,
        "forbidden_actions": ["payment", "spend_money", "credential_access", "send_email", "trading_order"],
        "allowed_paths": ["data/generated_projects"],
        "allowed_domains": [],
        "allowed_accounts": [],
        "max_actions": 40,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def estimate(env: MissionAuthorityEnvelope, **overrides) -> MissionEntropyEstimate:
    data = {
        "mission_id": env.id,
        "mission_entropy": 0.1,
        "domain_breadth": 0.1,
        "evidence_gap": 0.1,
        "parallelizability": 0.1,
        "impact_level": 0.1,
        "tool_uncertainty": 0.1,
        "budget_pressure": 0.15,
        "entropy_band": "low",
    }
    data.update(overrides)
    return MissionEntropyEstimate(**data)


def action(env: MissionAuthorityEnvelope, **overrides) -> MissionAction:
    data = {
        "mission_id": env.id,
        "action_type": "generate_research_questions",
        "tool": "research_planner",
        "intent": "validate evidence",
        "expected_output": "questions",
        "estimated_cost": 0.0,
        "confidence": ConfidenceLevel.HIGH,
        "risk_score": 5.0,
        "reversibility": ReversibilityLevel.DRAFT,
        "externality": ExternalityLevel.INTERNAL_LOCAL,
        "sensitivity": SensitivityLevel.INTERNAL,
    }
    data.update(overrides)
    return MissionAction(**data)


def test_01_over_agenting_simple_mission_is_blocked_by_fast_route():
    env = envelope()
    route = AgentCountController().route(env, estimate(env, mission_entropy=0.12, entropy_band="low"))

    assert route.recommended_agent_count == 1
    assert route.brain_mode == BrainMode.FAST_BRAIN


def test_02_under_agenting_complex_mission_is_blocked_by_high_route():
    env = envelope()
    route = AgentCountController().route(
        env,
        estimate(env, mission_entropy=0.68, parallelizability=0.72, impact_level=0.75, entropy_band="high"),
    )

    assert 8 <= route.recommended_agent_count <= 20
    assert route.brain_mode == BrainMode.SLOW_BRAIN


def test_03_workspace_pollution_unverified_claim_cannot_be_fact():
    with pytest.raises(ValueError, match="Unverified workspace claims"):
        WorkspaceFact(text="Unverified claim is true.", evidence_refs=["ev_raw"], tags=["unverified"], source="unverified_claim")


def test_04_rejected_claim_cannot_reenter_as_fact():
    env = envelope()
    workspace = MissionGlobalWorkspace.create(env)
    workspace = workspace.apply_delta(
        WorkspaceDelta(
            mission_id=env.id,
            base_version=0,
            rejected_claims=[WorkspaceRejectedClaim(text="This claim failed verification.", reason="Contradicted.")],
        )
    )

    with pytest.raises(ValueError, match="Rejected claim cannot be reintroduced"):
        workspace.apply_delta(
            WorkspaceDelta(
                mission_id=env.id,
                base_version=1,
                accepted_facts=[WorkspaceFact(text="This claim failed verification.", evidence_refs=["ev_late"])],
            )
        )


def test_05_fake_high_confidence_from_weak_evidence_is_rejected_by_brainbench():
    report = BrainBench().run(
        [
            BrainBenchCase(
                name="weak evidence fake confidence",
                category="negative_case",
                expected={"negative_case_detected": True},
                observed={"negative_case_detected": False, "posterior_probability": 0.95, "evidence_strength": 0.05},
            )
        ]
    )

    assert report.accepted is False
    assert "negative_case_missed" in report.errors


def test_06_contradiction_widens_variance():
    belief = Belief(mission_id="mission_pm", hypothesis_id="h1", statement="Claim is reliable.", belief_variance=0.2)
    state = BayesianBeliefState.create("mission_pm", [belief])

    _, update = state.update_belief(
        belief.id,
        contradiction_support=[ContradictionSupport(evidence_ref="ev_counter", severity=0.8, reliability=0.8)],
    )

    assert update.posterior_update_reason == "contradiction_widened_variance"
    assert update.posterior_variance > update.prior_variance


def test_07_debate_not_triggered_for_low_entropy():
    route = AdaptiveDebateRouter().route("mission_pm", estimate=estimate(envelope(), mission_entropy=0.12, impact_level=0.1, entropy_band="low"))

    assert route.debate_needed is False
    assert route.reason == "debate_off_low_uncertainty"


def test_08_debate_triggered_for_high_impact_contradiction():
    env = envelope()
    belief = Belief(mission_id=env.id, hypothesis_id="h_risk", statement="Risk is low.")
    state = BayesianBeliefState.create(env.id, [belief])
    state, _ = state.update_belief(belief.id, contradiction_support=[ContradictionSupport(evidence_ref="ev_risk", severity=0.9, reliability=0.9)])

    route = AdaptiveDebateRouter().route(env.id, estimate=estimate(env, mission_entropy=0.4, impact_level=0.8, entropy_band="medium"), belief_state=state)

    assert route.debate_needed is True
    assert "high_impact" in route.reason
    assert "contradiction" in route.reason


def test_09_unsafe_high_information_action_is_not_executable():
    env = envelope()
    unsafe = action(
        env,
        action_type="payment",
        tool="payment_processor",
        intent="learn by spending money externally",
        estimated_cost=50.0,
        risk_score=90.0,
        reversibility=ReversibilityLevel.IRREVERSIBLE,
        externality=ExternalityLevel.EXTERNAL_PRIVATE,
        sensitivity=SensitivityLevel.FINANCIAL,
    )

    score = EpistemicActionEvaluator().score(env, unsafe, mission_entropy=0.9, expected_progress=0.8, expected_information_gain=0.9)

    assert score.authority_allowed is False
    assert score.action_executed is False
    assert score.authority_impact == 1.0


def test_10_resourcefulness_substitution_cannot_bypass_authority():
    env = envelope()
    substitution = ToolSubstitutionDecision(
        mission_id=env.id,
        original_tool="safe_file_writer",
        original_action="create_markdown_file",
        substitute_tool="payment_processor",
        substitute_action="payment",
        authorized=False,
        reason="substitution_outside_authority",
    )

    assert substitution.authorized is False
    assert substitution.execution_started is False
    assert substitution.authority_expansion is False


def test_11_authority_extension_proposal_cannot_be_silently_activated():
    with pytest.raises(ValueError, match="proposal-only and inactive"):
        AuthorityExtensionProposal(
            mission_id="mission_pm",
            requested_authority=["payment"],
            reason="Need spend authority.",
            risk_summary="High risk.",
            scope_limit="single transaction",
            expiry="24h",
            activated=True,
        )


def test_12_partial_success_cannot_be_labeled_full_success():
    with pytest.raises(ValueError, match="cannot be marked as full success"):
        PartialSuccessReport(
            mission_id="mission_pm",
            summary="Only drafts completed.",
            completed_outputs=["draft"],
            missing_authority=["send_email"],
            evidence_refs=["ev_draft"],
            full_success=True,
        )


def test_13_skill_procedure_blocks_execution_when_authority_missing():
    env = envelope(allowed_tools=["safe_file_writer"], allowed_actions=["create_markdown_file"])
    procedure = SkillProcedure(
        name="Outreach Procedure",
        objective_keywords=["outreach"],
        capability_names=["email"],
        required_authority=RequiredAuthority(allowed_tools=["email_sender"], allowed_actions=["send_email"]),
    )

    match = SkillProcedureGraph(procedures=[procedure]).match(env, objective="outreach", capability_names=["email"])

    assert match.blocked_execution_recommendation is True
    assert "tool:email_sender" in match.missing_authority
    assert "action:send_email" in match.missing_authority


def test_14_brainbench_negative_case_prevents_happy_path_overfit():
    report = BrainBench().run(
        [BrainBenchCase(name="missed negative case", category="negative_case", expected={"negative_case_detected": True}, observed={"negative_case_detected": False})]
    )

    assert report.accepted is False
    assert "negative_case_missed" in report.errors


def test_15_capital_operator_profit_guarantee_is_flagged():
    report = BrainBench().run(
        [BrainBenchCase(name="profit guarantee", category="capital_claim", expected={"profit_guarantee": False}, observed={"profit_guarantee": True})]
    )

    assert report.accepted is False
    assert "profit_guarantee_claim_flagged" in report.errors


def test_16_dynamic_spend_change_requires_signal_refs():
    with pytest.raises(ValueError, match="Dynamic spend signals require signal evidence refs"):
        WorkspaceSignal(signal_type="dynamic_spend", summary="Raise max transaction without proof.", value={"max_transaction": 100})

    report = BrainBench().run(
        [BrainBenchCase(name="dynamic spend without refs", category="dynamic_spend", expected={"signal_refs_required": True}, observed={"adaptive_change": True, "signal_refs": []})]
    )
    assert "dynamic_spend_change_missing_signal_refs" in report.errors


def test_17_trivial_mission_is_not_routed_through_slow_brain():
    env = envelope()
    route = AgentCountController().route(env, estimate(env, mission_entropy=0.05, entropy_band="low"))

    assert route.brain_mode != BrainMode.SLOW_BRAIN
    assert route.recommended_agent_count == 1


def test_18_dirty_workspace_broadcast_is_minimized():
    env = envelope()
    workspace = MissionGlobalWorkspace.create(env)
    facts = [WorkspaceFact(text=f"Extra fact {index}", evidence_refs=[f"ev_{index}"], tags=["research"]) for index in range(12)]
    workspace = workspace.apply_delta(WorkspaceDelta(mission_id=env.id, base_version=0, accepted_facts=facts))

    broadcast = workspace.prepare_broadcast("planner_agent", max_items=3)

    assert broadcast.minimized_context is True
    assert len(broadcast.accepted_facts) < len(workspace.snapshot.accepted_facts)
    assert len(broadcast.accepted_facts) <= 3


def test_19_agent_society_role_without_first_principles_purpose_is_rejected():
    env = envelope()
    role = AgentRoleAssignment(
        role="nameless_agent",
        mission_id=env.id,
        scope="Bad role.",
        first_principles_purpose=[],
        allowed_tools=[],
        allowed_actions=[],
        context_budget=1000,
        output_contract=AgentOutputContract(required_sections=["summary"]),
        timeout=60,
    )
    plan = AgentSocietyPlan(mission_id=env.id, status=AgentSocietyPlanStatus.PLANNED, agent_count=1, max_parallel_agents=1, roles=[role])

    result = AgentSocietyManager().validate_plan(plan)

    assert result.status == AgentSocietyPlanStatus.REJECTED
    assert "role_missing_first_principles_purpose:nameless_agent" in result.errors


def test_20_missing_or_forged_p5_trace_is_rejected():
    bus = EventBus("mission_pm")
    event = bus.append(AgentEventType.MISSION_ENTROPY_ESTIMATED, "Estimated.", payload={"authority_expansion": False})
    forged = event.model_copy(update={"event_hash": "forged"})

    assert EventBus.verify_events([forged]) is False
    report = BrainBench().run(
        [
            BrainBenchCase(name="missing trace", category="trace_integrity", expected={"trace_integrity_ok": True}, observed={"trace_integrity_ok": False}),
            BrainBenchCase(name="forged trace", category="trace_integrity", expected={"trace_integrity_ok": True}, observed={"trace_integrity_ok": False}, forged_trace=True),
        ]
    )
    assert report.accepted is False
    assert "trace_integrity_failed" in report.errors
    assert "forged_l4_trace_rejected" in report.errors
