from __future__ import annotations

from sentinel.agent import (
    AdaptiveDebateRouter,
    AgentCountController,
    AgentEventType,
    AgentRolePurpose,
    AgentSocietyManager,
    BayesianBeliefState,
    Belief,
    BrainBench,
    BrainBenchCase,
    BrainMode,
    CanonicalStep,
    ContradictionSupport,
    EpistemicActionEvaluator,
    EventBus,
    EvidenceSupport,
    MissionEntropyEstimator,
    MissionGlobalWorkspace,
    ProcedurePrecondition,
    RequiredAuthority,
    ResourcefulnessEngine,
    SkillProcedure,
    SkillProcedureGraph,
    SuccessProof,
    WorkspaceDelta,
    WorkspaceFact,
)
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
        "user_id": "user_p5l",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P5L integrated review fixture",
        "mission_objective": "Certify the Brain L4 stack without external powers.",
        "success_criteria": ["Integrated review passes"],
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


def action(env: MissionAuthorityEnvelope, **overrides) -> MissionAction:
    data = {
        "mission_id": env.id,
        "action_type": "generate_research_questions",
        "tool": "research_planner",
        "intent": "validate uncertainty before writing",
        "expected_output": "bounded question list",
        "estimated_cost": 0.0,
        "confidence": ConfidenceLevel.HIGH,
        "risk_score": 5.0,
        "reversibility": ReversibilityLevel.DRAFT,
        "externality": ExternalityLevel.INTERNAL_LOCAL,
        "sensitivity": SensitivityLevel.INTERNAL,
        "evidence_refs": ["ev_plan"],
    }
    data.update(overrides)
    return MissionAction(**data)


def skill_graph() -> SkillProcedureGraph:
    return SkillProcedureGraph(
        procedures=[
            SkillProcedure(
                name="Bounded Research Procedure",
                objective_keywords=["research", "review", "certify"],
                capability_names=["research_planning", "local_write"],
                preconditions=[ProcedurePrecondition(name="Mission context exists", satisfied=True, evidence_refs=["ev_context"])],
                required_authority=RequiredAuthority(
                    allowed_tools=["safe_file_writer", "research_planner"],
                    allowed_actions=["create_markdown_file", "generate_research_questions"],
                    allowed_paths=["data/generated_projects"],
                ),
                canonical_steps=[
                    CanonicalStep(order=1, action="generate_research_questions", tool="research_planner", description="Plan verification questions.", evidence_refs=["ev_plan"]),
                    CanonicalStep(order=2, action="create_markdown_file", tool="safe_file_writer", description="Write review artifact.", evidence_refs=["ev_write"]),
                ],
                success_proofs=[SuccessProof(name="Review artifact cites evidence", evidence_refs=["ev_proof"])],
            )
        ]
    )


def test_low_entropy_pipeline_stays_fast_bounded_and_trace_verified():
    env = envelope(mission_objective="Create a bounded local summary from provided evidence.", success_criteria=["Summary exists"])
    bus = EventBus(env.id)

    entropy = MissionEntropyEstimator().estimate(env, evidence_refs=["ev_summary"], selected_tools=["safe_file_writer", "research_planner"], event_bus=bus)
    route = AgentCountController().route(env, entropy, event_bus=bus)
    society = AgentSocietyManager().plan(env, route, entropy, event_bus=bus)
    workspace = MissionGlobalWorkspace.create(env, evidence_refs=["ev_context"], event_bus=bus)
    broadcast = workspace.prepare_broadcast("planner_agent", purpose=[AgentRolePurpose.EXPLORATION.value], max_items=2, event_bus=bus)
    belief = Belief(mission_id=env.id, hypothesis_id="h_summary", statement="A local summary can satisfy the mission.")
    belief_state = BayesianBeliefState.create(env.id, [belief])
    belief_state, belief_update = belief_state.update_belief(belief.id, evidence_support=[EvidenceSupport(evidence_ref="ev_summary", weight=0.8, reliability=0.8)], event_bus=bus)
    debate = AdaptiveDebateRouter().route(env.id, estimate=entropy, belief_state=belief_state, event_bus=bus)
    score = EpistemicActionEvaluator().score(env, action(env), mission_entropy=entropy.mission_entropy, event_bus=bus)
    procedure = skill_graph().match(env, objective="research review certify", capability_names=["research_planning", "local_write"], event_bus=bus)
    brainbench = BrainBench().run(
        [
            BrainBenchCase(name="simple allocation", category="allocation", expected={"allowed_counts": [1]}, observed={"recommended_agent_count": route.recommended_agent_count}),
            BrainBenchCase(name="simple debate off", category="debate_trigger", expected={"debate_needed": False}, observed={"debate_needed": debate.debate_needed}),
            BrainBenchCase(name="valid l4 trace", category="trace_integrity", expected={"trace_integrity_ok": True}, observed={"trace_integrity_ok": bus.verify_chain()}),
        ],
        event_bus=bus,
    )

    assert entropy.entropy_band == "low"
    assert route.brain_mode == BrainMode.FAST_BRAIN
    assert route.recommended_agent_count == 1
    assert society.agent_count == 1
    assert debate.debate_needed is False
    assert score.authority_allowed is True
    assert procedure.blocked_execution_recommendation is False
    assert belief_update.posterior_probability > belief_update.prior_probability
    assert broadcast.minimized_context is True
    assert brainbench.accepted is True
    assert bus.verify_chain() is True
    assert all(event.payload.get("authority_expansion") is not True for event in bus.events())


def test_high_entropy_pipeline_preserves_disputes_and_bounded_resourcefulness():
    env = envelope(
        mission_title="Deep research audit across browser code security market and data",
        mission_objective="Research, verify, compare, and audit many sources before producing a multi-domain plan.",
        success_criteria=["Verify claims", "Compare sources", "Audit risks", "Produce plan"],
        allowed_systems=["local_workspace", "public_web"],
        allowed_tools=["safe_file_writer", "research_planner", "browser_public_read"],
        allowed_actions=[*SAFE_ACTIONS, "browser_read_public_page"],
        allowed_domains=["example.com"],
        max_actions=20,
        risk_appetite_score=75,
    )
    bus = EventBus(env.id)

    entropy = MissionEntropyEstimator().estimate(
        env,
        evidence_refs=["ev_seed"],
        open_questions=["Which claim is false?", "Which source is reliable?"],
        selected_tools=["safe_file_writer"],
        blocked_tools=["email_sender"],
        event_bus=bus,
    )
    route = AgentCountController().route(env, entropy, event_bus=bus)
    society = AgentSocietyManager().plan(env, route, entropy, uncertain_path_detected=True, event_bus=bus)
    workspace = MissionGlobalWorkspace.create(env, evidence_refs=["ev_context"], event_bus=bus)
    workspace = workspace.apply_delta(
        WorkspaceDelta(
            mission_id=env.id,
            base_version=0,
            accepted_facts=[WorkspaceFact(text="Seed evidence exists for the audit.", evidence_refs=["ev_seed"], tags=["research"])],
        ),
        event_bus=bus,
    )
    belief = Belief(mission_id=env.id, hypothesis_id="h_market_claim", statement="The market claim is reliable.")
    belief_state = BayesianBeliefState.create(env.id, [belief])
    belief_state, update = belief_state.update_belief(
        belief.id,
        evidence_support=[EvidenceSupport(evidence_ref="ev_seed", weight=0.45, reliability=0.6)],
        contradiction_support=[ContradictionSupport(evidence_ref="ev_counter", severity=0.8, reliability=0.8)],
        event_bus=bus,
    )
    debate = AdaptiveDebateRouter().route(env.id, estimate=entropy, belief_state=belief_state, unresolved_disputes=["source reliability disputed"], event_bus=bus)
    resourcefulness = ResourcefulnessEngine().route(env, missing_authority=["email_send"], partial_outputs=["audit_plan"], evidence_refs=["ev_boundary"], event_bus=bus)
    brainbench = BrainBench().run(
        [
            BrainBenchCase(name="complex allocation", category="allocation", expected={"allowed_counts": list(range(8, 21))}, observed={"recommended_agent_count": route.recommended_agent_count}),
            BrainBenchCase(name="contradiction debate", category="debate_trigger", expected={"debate_needed": True}, observed={"debate_needed": debate.debate_needed}),
            BrainBenchCase(name="resourcefulness d5", category="resourcefulness", expected={"level": "D5_propose_extension"}, observed={"level": resourcefulness.level.value}),
        ],
        event_bus=bus,
    )

    assert entropy.entropy_band == "high"
    assert 8 <= route.recommended_agent_count <= 20
    assert {"aggregator_agent", "verifier_agent", "skeptic_agent"}.issubset({role.role for role in society.roles})
    assert any(role.role == "resourcefulness_agent" for role in society.roles)
    assert update.posterior_update_reason == "mixed_support_and_contradiction"
    assert update.posterior_variance > update.prior_variance
    assert debate.debate_needed is True
    assert "source reliability disputed" in debate.unresolved_disputes
    assert resourcefulness.authority_extension_proposal is not None
    assert resourcefulness.authority_extension_proposal.activated is False
    assert brainbench.accepted is True
    assert bus.verify_chain() is True


def test_integrated_trace_forgery_is_core_final_gate_incompatible():
    env = envelope()
    bus = EventBus(env.id)
    MissionEntropyEstimator().estimate(env, evidence_refs=["ev_summary"], selected_tools=["safe_file_writer"], event_bus=bus)
    events = list(bus.events())
    forged_event = events[0].model_copy(update={"payload": {**events[0].payload, "authority_expansion": True}})

    assert bus.verify_chain() is True
    assert EventBus.verify_events([forged_event]) is False
    report = BrainBench().run(
        [BrainBenchCase(name="forged p5 trace", category="trace_integrity", expected={"trace_integrity_ok": True}, observed={"trace_integrity_ok": False}, forged_trace=True)]
    )
    assert report.accepted is False
    assert "forged_l4_trace_rejected" in report.errors
