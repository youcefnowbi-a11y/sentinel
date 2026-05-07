from __future__ import annotations

from sentinel.agent import (
    AgentEventType,
    CanonicalStep,
    EventBus,
    KnownFailureMode,
    ProcedurePrecondition,
    RequiredAuthority,
    SkillProcedure,
    SkillProcedureGraph,
    SuccessProof,
)
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_p5j",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P5J skill procedure fixture",
        "mission_objective": "Match reusable procedures without granting authority.",
        "success_criteria": ["Procedure match exists"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer", "research_planner"],
        "allowed_actions": ["create_markdown_file", "generate_research_questions", "write_trace"],
        "forbidden_actions": ["payment", "spend_money", "credential_access", "send_email"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 30,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def procedure(**overrides) -> SkillProcedure:
    data = {
        "name": "Research Summary Procedure",
        "objective_keywords": ["research", "summary", "market"],
        "capability_names": ["research_planning", "local_write"],
        "preconditions": [ProcedurePrecondition(name="Mission context exists", satisfied=True, evidence_refs=["ev_context"])],
        "required_authority": RequiredAuthority(
            allowed_tools=["safe_file_writer", "research_planner"],
            allowed_actions=["create_markdown_file", "generate_research_questions"],
            allowed_paths=["data/generated_projects"],
        ),
        "canonical_steps": [
            CanonicalStep(order=2, action="create_markdown_file", tool="safe_file_writer", description="Write summary.", evidence_refs=["ev_write"]),
            CanonicalStep(order=1, action="generate_research_questions", tool="research_planner", description="Plan questions.", evidence_refs=["ev_plan"]),
        ],
        "success_proofs": [SuccessProof(name="Summary file has evidence refs", evidence_refs=["ev_proof"])],
        "known_failure_modes": [KnownFailureMode(code="missing_evidence", mitigation="Ask verifier for proof.")],
    }
    data.update(overrides)
    return SkillProcedure(**data)


def graph(*procedures: SkillProcedure) -> SkillProcedureGraph:
    return SkillProcedureGraph(procedures=list(procedures) or [procedure()])


def test_procedure_match_by_objective_and_capability_with_trace():
    env = envelope()
    bus = EventBus(env.id)

    match = graph().match(env, objective="Create a market research summary", capability_names=["research_planning"], event_bus=bus)

    assert match.procedure_name == "Research Summary Procedure"
    assert "market" in match.matched_objective_terms
    assert "research_planning" in match.matched_capabilities
    assert match.trace_refs
    assert bus.events()[0].event_type == AgentEventType.SKILL_PROCEDURE_MATCHED


def test_missing_authority_blocks_execution_recommendation():
    env = envelope(allowed_tools=["safe_file_writer"], allowed_actions=["create_markdown_file"])

    match = graph().match(env, objective="research summary", capability_names=["research_planning"])

    assert "tool:research_planner" in match.missing_authority
    assert "action:generate_research_questions" in match.missing_authority
    assert match.blocked_execution_recommendation is True


def test_stale_procedure_warning():
    env = envelope()

    match = graph(procedure(stale=True)).match(env, objective="research summary", capability_names=["local_write"])

    assert match.stale_warning is True


def test_canonical_steps_preserve_evidence_refs_and_order():
    env = envelope()

    match = graph().match(env, objective="research summary", capability_names=["research_planning"])

    assert [step.order for step in match.canonical_steps] == [1, 2]
    assert match.canonical_steps[0].evidence_refs == ["ev_plan"]
    assert match.canonical_steps[1].evidence_refs == ["ev_write"]


def test_skill_recommends_only_never_authorizes():
    env = envelope()

    match = graph().match(env, objective="research summary", capability_names=["research_planning"])

    assert match.recommended_only is True
    assert match.authority_expansion is False
    assert not hasattr(match, "allowed_tools")
    assert not hasattr(match, "allowed_actions")


def test_skill_procedure_graph_does_not_expand_authority():
    env = envelope(allowed_tools=["safe_file_writer"], allowed_actions=["create_markdown_file"])
    before = env.model_dump(mode="json")

    result = graph().match(env, objective="research summary", capability_names=["research_planning"])

    assert env.model_dump(mode="json") == before
    assert result.authority_expansion is False
    assert graph().authority_expansion is False
