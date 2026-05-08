from __future__ import annotations

from pathlib import Path

from sentinel.agent import AgentEventType, AgentPhase, AgentRuntime, EventBus, EvidenceDecisionType, RuntimeCertificationGate
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
        "mission_title": "P1J evidence test",
        "mission_objective": "Build replayable evidence chains for runtime decisions.",
        "success_criteria": ["Evidence chains exist"],
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


def test_runtime_builds_evidence_chains_for_mission_shaping_decisions(tmp_path: Path):
    result = AgentRuntime(project_root=tmp_path).run(envelope(), {"idea": "Evidence chain run"}, evidence_refs=["ev_wtp"])
    decision_types = {chain.decision_type for chain in result.evidence_chains}
    event_types = [event.event_type for event in result.trace]

    assert result.success is True
    assert result.runtime_certification is not None
    assert result.runtime_certification.evidence_ok is True
    assert result.state_snapshot is not None
    assert set(result.state_snapshot.evidence_chain_types) == decision_types
    assert AgentEventType.EVIDENCE_CHAIN_BUILT in event_types
    assert {
        EvidenceDecisionType.TOOL_SELECTION,
        EvidenceDecisionType.HYPOTHESIS_VERDICT,
        EvidenceDecisionType.PLAN_CREATION,
        EvidenceDecisionType.REPAIR_DECISION,
        EvidenceDecisionType.SUCCESS_EVALUATION,
        EvidenceDecisionType.LEARNING_PROPOSAL,
    }.issubset(decision_types)
    assert all(chain.evidence for chain in result.evidence_chains)


def test_runtime_evidence_chain_payloads_are_replayable(tmp_path: Path):
    result = AgentRuntime(project_root=tmp_path).run(envelope(), {"idea": "Replay evidence"}, evidence_refs=["ev_wtp"])
    evidence_events = [event for event in result.trace if event.event_type == AgentEventType.EVIDENCE_CHAIN_BUILT]

    assert len(evidence_events) == len(result.evidence_chains)
    assert {event.payload["chain_id"] for event in evidence_events} == {chain.id for chain in result.evidence_chains}
    assert {event.payload["decision_type"] for event in evidence_events} == {chain.decision_type for chain in result.evidence_chains}
    assert all(event.payload["claim_id"] for event in evidence_events)


def test_certification_rejects_plan_without_required_evidence_chains():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.TOOLS_SELECTED, "Tools.", phase_before=AgentPhase.TOOL_SELECTING, phase_after=AgentPhase.TOOL_SELECTING)
    bus.append(AgentEventType.HYPOTHESES_REVIEWED, "Hypotheses.", phase_before=AgentPhase.HYPOTHESIS_VERIFYING, phase_after=AgentPhase.HYPOTHESIS_VERIFYING)
    bus.append(AgentEventType.WORLD_MODEL_SIMULATED, "World.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.OBJECTIVE_SCORED, "Score.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.EFFORT_ROUTED, "Effort.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.EFFORT_ROUTING)
    bus.append(AgentEventType.PLAN_CREATED, "Plan without evidence.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.PLANNING)
    bus.append(AgentEventType.AGENT_BLOCKED, "Blocked.", phase_before=AgentPhase.PLANNING, phase_after=AgentPhase.BLOCKED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert certification.evidence_ok is False
    assert "missing_evidence_chain_tool_selection_before_plan_created" in certification.errors
    assert "missing_evidence_chain_hypothesis_verdict_before_plan_created" in certification.errors


def test_certification_rejects_malformed_evidence_chain_payload():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(
        AgentEventType.EVIDENCE_CHAIN_BUILT,
        "Malformed tool evidence.",
        payload={
            "chain_id": "chain_tool",
            "decision_type": EvidenceDecisionType.TOOL_SELECTION,
            "claim_id": "claim_tool",
            "verdict": "supported",
            "confidence": "high",
            "evidence_ref_ids": [],
            "contradiction_ids": [],
        },
    )
    bus.append(AgentEventType.TOOLS_SELECTED, "Tools.", phase_before=AgentPhase.TOOL_SELECTING, phase_after=AgentPhase.TOOL_SELECTING)
    bus.append(AgentEventType.HYPOTHESES_REVIEWED, "Hypotheses.", phase_before=AgentPhase.HYPOTHESIS_VERIFYING, phase_after=AgentPhase.HYPOTHESIS_VERIFYING)
    bus.append(AgentEventType.WORLD_MODEL_SIMULATED, "World.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.OBJECTIVE_SCORED, "Score.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.EFFORT_ROUTED, "Effort.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.EFFORT_ROUTING)
    bus.append(AgentEventType.PLAN_CREATED, "Plan.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.PLANNING)
    bus.append(AgentEventType.AGENT_BLOCKED, "Blocked.", phase_before=AgentPhase.PLANNING, phase_after=AgentPhase.BLOCKED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert any(error.startswith("malformed_evidence_chain_event_") for error in certification.errors)


def test_certification_rejects_learning_without_success_evidence_chain():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(
        AgentEventType.EVIDENCE_CHAIN_BUILT,
        "Repair evidence.",
        payload={
            "chain_id": "chain_repair",
            "decision_type": EvidenceDecisionType.REPAIR_DECISION,
            "claim_id": "claim_repair",
            "verdict": "supported",
            "confidence": 1.0,
            "evidence_ref_ids": [],
            "contradiction_ids": [],
        },
    )
    bus.append(AgentEventType.REPAIR_DECIDED, "Repair.", phase_before=AgentPhase.ARTIFACT_REVIEWING, phase_after=AgentPhase.ARTIFACT_REVIEWING)
    bus.append(AgentEventType.SUCCESS_EVALUATED, "Success.", phase_before=AgentPhase.ARTIFACT_REVIEWING, phase_after=AgentPhase.SUCCESS_EVALUATING)
    bus.append(AgentEventType.LEARNING_PROPOSED, "Learning without success evidence.", phase_before=AgentPhase.SUCCESS_EVALUATING, phase_after=AgentPhase.LEARNING_PROPOSING)
    bus.append(AgentEventType.AGENT_FAILED, "Failed.", phase_before=AgentPhase.LEARNING_PROPOSING, phase_after=AgentPhase.FAILED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert "missing_evidence_chain_success_evaluation_before_learning_proposed" in certification.errors
    assert "missing_evidence_chain_learning_proposal_before_agent_failed" in certification.errors
