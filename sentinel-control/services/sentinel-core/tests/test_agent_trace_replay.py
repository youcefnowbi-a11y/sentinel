from __future__ import annotations

from pathlib import Path

from sentinel.agent import AgentEventType, AgentPhase, AgentRuntime, AgentTraceReplayer, EventBus, EvidenceDecisionType, replay_agent_trace
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
        "mission_title": "P1I replay test",
        "mission_objective": "Replay agent state from trace.",
        "success_criteria": ["Trace replay snapshot exists"],
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


def append_evidence_chain(bus: EventBus, decision_type: EvidenceDecisionType) -> None:
    bus.append(
        AgentEventType.EVIDENCE_CHAIN_BUILT,
        f"Evidence for {decision_type}.",
        payload={
            "chain_id": f"chain_{decision_type.value}",
            "decision_type": decision_type,
            "claim_id": f"claim_{decision_type.value}",
            "verdict": "supported",
            "confidence": 1.0,
            "evidence_ref_ids": [],
            "contradiction_ids": [],
        },
    )


def append_minimal_cognitive_prefix(bus: EventBus) -> None:
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.METHODS_SELECTED, "Methods.", payload={"methods": ["evidence_ladder"]})
    bus.append(AgentEventType.CAPABILITIES_SELECTED, "Capabilities.", payload={"needed": ["gtm_pack_generation"], "missing": []})
    bus.append(
        AgentEventType.TOOLS_SELECTED,
        "Tools.",
        payload={
            "selected_tools": ["safe_file_writer"],
            "candidate_tools": [],
            "blocked_tools": [],
            "unavailable_capabilities": [],
            "missing_capabilities": [],
        },
    )
    append_evidence_chain(bus, EvidenceDecisionType.TOOL_SELECTION)
    bus.append(AgentEventType.HYPOTHESES_REVIEWED, "Hypotheses.", payload={"verified": ["hyp_1"], "rejected": []})
    append_evidence_chain(bus, EvidenceDecisionType.HYPOTHESIS_VERDICT)
    bus.append(AgentEventType.WORLD_MODEL_SIMULATED, "World.", payload={"actions": []})
    bus.append(
        AgentEventType.OBJECTIVE_SCORED,
        "Score.",
        payload={"selected_action_id": "act_1", "selected_action_name": "proceed_to_planning", "scores": []},
    )
    bus.append(
        AgentEventType.EFFORT_ROUTED,
        "Effort.",
        payload={"level": "low", "score": 0.1, "recommended_cycles": 0, "max_parallel_workers": 1},
    )


def append_clean_execution_suffix(bus: EventBus) -> None:
    bus.append(
        AgentEventType.PLAN_CREATED,
        "Plan.",
        phase_before=AgentPhase.EFFORT_ROUTING,
        phase_after=AgentPhase.PLANNING,
        payload={
            "steps": ["step_1"],
            "selected_tools": ["safe_file_writer"],
            "verified_hypotheses": ["hyp_1"],
            "selected_action_id": "act_1",
            "selected_action_name": "proceed_to_planning",
            "effort_level": "low",
            "effort_score": 0.1,
        },
    )
    bus.append(AgentEventType.PLAN_REVIEWED, "Plan reviewed.", phase_before=AgentPhase.PLANNING, phase_after=AgentPhase.PLAN_REVIEWING)
    append_evidence_chain(bus, EvidenceDecisionType.PLAN_CREATION)
    bus.append(AgentEventType.WORKER_STARTED, "Worker.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.EXECUTING)
    bus.append(
        AgentEventType.WORKER_COMPLETED,
        "Worker done.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.ARTIFACT_REVIEWING,
        payload={"project_path": "data/generated_projects/test"},
    )
    bus.append(AgentEventType.ARTIFACTS_REVIEWED, "Artifacts.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.ARTIFACT_REVIEWING)
    bus.append(
        AgentEventType.REPAIR_DECIDED,
        "Repair.",
        phase_before=AgentPhase.ARTIFACT_REVIEWING,
        phase_after=AgentPhase.ARTIFACT_REVIEWING,
        payload={
            "decision": "no_repair_needed",
            "repair_pressure": 0.0,
            "current_repair_cycles": 0,
            "max_repair_cycles": 1,
        },
    )
    append_evidence_chain(bus, EvidenceDecisionType.REPAIR_DECISION)
    bus.append(AgentEventType.SUCCESS_EVALUATED, "Success.", phase_before=AgentPhase.ARTIFACT_REVIEWING, phase_after=AgentPhase.SUCCESS_EVALUATING, payload={"success": True})
    append_evidence_chain(bus, EvidenceDecisionType.SUCCESS_EVALUATION)
    bus.append(AgentEventType.LEARNING_PROPOSED, "Learning.", phase_before=AgentPhase.SUCCESS_EVALUATING, phase_after=AgentPhase.LEARNING_PROPOSING, payload={"proposal_count": 0})
    append_evidence_chain(bus, EvidenceDecisionType.LEARNING_PROPOSAL)
    bus.append(AgentEventType.AGENT_COMPLETED, "Completed.", phase_before=AgentPhase.LEARNING_PROPOSING, phase_after=AgentPhase.COMPLETED)


def test_replay_reconstructs_snapshot_from_clean_runtime_trace(tmp_path: Path):
    env = envelope()

    result = AgentRuntime(project_root=tmp_path).run(env, {"idea": "Replay clean run"}, evidence_refs=["ev_wtp"])
    replay = replay_agent_trace(result.trace)

    assert replay.accepted is True
    assert result.state_snapshot is not None
    assert result.state_snapshot.trace_hash == result.trace[-1].event_hash
    assert replay.snapshot.final_phase == AgentPhase.COMPLETED
    assert replay.snapshot.selected_tools == result.selected_tools
    assert replay.snapshot.effort_level == result.effort_route.level
    assert replay.snapshot.repair_decision == result.repair_decision.decision
    assert replay.snapshot.success is True


def test_replay_accepts_canonical_handbuilt_trace():
    bus = EventBus("mission_001")
    append_minimal_cognitive_prefix(bus)
    append_clean_execution_suffix(bus)

    replay = AgentTraceReplayer().replay(bus.events())

    assert replay.accepted is True
    assert replay.snapshot.selected_methods == ["evidence_ladder"]
    assert replay.snapshot.selected_tools == ["safe_file_writer"]
    assert replay.snapshot.verified_hypotheses == ["hyp_1"]
    assert replay.snapshot.project_path == "data/generated_projects/test"


def test_replay_rejects_plan_payload_mismatch_even_when_hash_chain_is_valid():
    bus = EventBus("mission_001")
    append_minimal_cognitive_prefix(bus)
    bus.append(
        AgentEventType.PLAN_CREATED,
        "Plan mismatch.",
        phase_before=AgentPhase.EFFORT_ROUTING,
        phase_after=AgentPhase.PLANNING,
        payload={
            "steps": ["step_1"],
            "selected_tools": ["unselected_tool"],
            "verified_hypotheses": ["hyp_1"],
            "selected_action_id": "act_1",
            "selected_action_name": "proceed_to_planning",
            "effort_level": "low",
            "effort_score": 0.1,
        },
    )
    bus.append(AgentEventType.AGENT_BLOCKED, "Blocked.", phase_before=AgentPhase.PLANNING, phase_after=AgentPhase.BLOCKED)

    replay = AgentTraceReplayer().replay(bus.events())

    assert replay.certification.certified is True
    assert replay.accepted is False
    assert "plan_selected_tools_mismatch" in replay.errors


def test_replay_rejects_plan_that_invents_tool_when_none_was_selected():
    bus = EventBus("mission_001")
    append_minimal_cognitive_prefix(bus)
    events = list(bus.events())
    empty_tool_event = events[3].model_copy(
        update={
            "payload": {
                "selected_tools": [],
                "candidate_tools": [],
                "blocked_tools": [],
                "unavailable_capabilities": [],
                "missing_capabilities": [],
            }
        }
    )
    events[3] = empty_tool_event

    replay_prefix = EventBus("mission_001")
    for event in events:
        replay_prefix.append(
            event.event_type,
            event.summary,
            phase_before=event.phase_before,
            phase_after=event.phase_after,
            payload=event.payload,
        )
    replay_prefix.append(
        AgentEventType.PLAN_CREATED,
        "Plan invented tool.",
        phase_before=AgentPhase.EFFORT_ROUTING,
        phase_after=AgentPhase.PLANNING,
        payload={
            "steps": ["step_1"],
            "selected_tools": ["rogue_tool"],
            "verified_hypotheses": ["hyp_1"],
            "selected_action_id": "act_1",
            "selected_action_name": "proceed_to_planning",
            "effort_level": "low",
            "effort_score": 0.1,
        },
    )
    replay_prefix.append(AgentEventType.AGENT_BLOCKED, "Blocked.", phase_before=AgentPhase.PLANNING, phase_after=AgentPhase.BLOCKED)

    replay = AgentTraceReplayer().replay(replay_prefix.events())

    assert replay.certification.certified is True
    assert replay.accepted is False
    assert "plan_selected_tools_mismatch" in replay.errors


def test_replay_rejects_plan_that_invents_action_and_effort_metadata():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.METHODS_SELECTED, "Methods.", payload={"methods": ["evidence_ladder"]})
    bus.append(AgentEventType.CAPABILITIES_SELECTED, "Capabilities.", payload={"needed": ["gtm_pack_generation"], "missing": []})
    bus.append(AgentEventType.TOOLS_SELECTED, "Tools.", payload={"selected_tools": [], "candidate_tools": [], "blocked_tools": [], "unavailable_capabilities": []})
    append_evidence_chain(bus, EvidenceDecisionType.TOOL_SELECTION)
    bus.append(AgentEventType.HYPOTHESES_REVIEWED, "Hypotheses.", payload={"verified": ["hyp_1"], "rejected": []})
    append_evidence_chain(bus, EvidenceDecisionType.HYPOTHESIS_VERDICT)
    bus.append(AgentEventType.WORLD_MODEL_SIMULATED, "World.", payload={"actions": []})
    bus.append(AgentEventType.OBJECTIVE_SCORED, "Score.", payload={"scores": []})
    bus.append(AgentEventType.EFFORT_ROUTED, "Effort.", payload={})
    bus.append(
        AgentEventType.PLAN_CREATED,
        "Plan invented action metadata.",
        phase_before=AgentPhase.EFFORT_ROUTING,
        phase_after=AgentPhase.PLANNING,
        payload={
            "steps": ["step_1"],
            "selected_tools": [],
            "verified_hypotheses": ["hyp_1"],
            "selected_action_id": "act_rogue",
            "selected_action_name": "rogue_action",
            "effort_level": "extreme",
            "effort_score": 0.9,
        },
    )
    bus.append(AgentEventType.AGENT_BLOCKED, "Blocked.", phase_before=AgentPhase.PLANNING, phase_after=AgentPhase.BLOCKED)

    replay = AgentTraceReplayer().replay(bus.events())

    assert replay.certification.certified is True
    assert replay.accepted is False
    assert "plan_selected_action_id_mismatch" in replay.errors
    assert "plan_selected_action_name_mismatch" in replay.errors
    assert "plan_effort_level_mismatch" in replay.errors
    assert "plan_effort_score_mismatch" in replay.errors


def test_replay_rejects_final_status_conflict():
    bus = EventBus("mission_001")
    append_minimal_cognitive_prefix(bus)
    append_clean_execution_suffix(bus)
    events = list(bus.events())
    failed_terminal = events[-1].model_copy(
        update={
            "event_type": AgentEventType.AGENT_FAILED,
            "phase_after": AgentPhase.FAILED,
        }
    )
    events[-1] = failed_terminal

    replay = AgentTraceReplayer().replay(events)

    assert replay.accepted is False
    assert "hash_chain_invalid" in replay.errors
    assert "failed_event_conflicts_with_success_evaluation" in replay.errors


def test_replay_rejects_malformed_repair_payload_without_crashing():
    bus = EventBus("mission_001")
    append_minimal_cognitive_prefix(bus)
    bus.append(
        AgentEventType.PLAN_CREATED,
        "Plan.",
        phase_before=AgentPhase.EFFORT_ROUTING,
        phase_after=AgentPhase.PLANNING,
        payload={
            "steps": ["step_1"],
            "selected_tools": ["safe_file_writer"],
            "verified_hypotheses": ["hyp_1"],
            "selected_action_id": "act_1",
            "selected_action_name": "proceed_to_planning",
            "effort_level": "low",
            "effort_score": 0.1,
        },
    )
    bus.append(AgentEventType.PLAN_REVIEWED, "Plan reviewed.", phase_before=AgentPhase.PLANNING, phase_after=AgentPhase.PLAN_REVIEWING)
    append_evidence_chain(bus, EvidenceDecisionType.PLAN_CREATION)
    bus.append(AgentEventType.WORKER_STARTED, "Worker.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.EXECUTING)
    bus.append(
        AgentEventType.WORKER_COMPLETED,
        "Worker done.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.ARTIFACT_REVIEWING,
        payload={"project_path": "data/generated_projects/test"},
    )
    bus.append(AgentEventType.ARTIFACTS_REVIEWED, "Artifacts.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.ARTIFACT_REVIEWING)
    bus.append(
        AgentEventType.REPAIR_DECIDED,
        "Malformed repair decision.",
        phase_before=AgentPhase.ARTIFACT_REVIEWING,
        phase_after=AgentPhase.ARTIFACT_REVIEWING,
        payload={
            "decision": "no_repair_needed",
            "repair_pressure": 0.0,
            "current_repair_cycles": "not-an-int",
            "max_repair_cycles": "not-an-int",
        },
    )
    append_evidence_chain(bus, EvidenceDecisionType.REPAIR_DECISION)
    bus.append(AgentEventType.SUCCESS_EVALUATED, "Success.", phase_before=AgentPhase.ARTIFACT_REVIEWING, phase_after=AgentPhase.SUCCESS_EVALUATING, payload={"success": True})
    append_evidence_chain(bus, EvidenceDecisionType.SUCCESS_EVALUATION)
    bus.append(AgentEventType.LEARNING_PROPOSED, "Learning.", phase_before=AgentPhase.SUCCESS_EVALUATING, phase_after=AgentPhase.LEARNING_PROPOSING, payload={"proposal_count": 0})
    append_evidence_chain(bus, EvidenceDecisionType.LEARNING_PROPOSAL)
    bus.append(AgentEventType.AGENT_COMPLETED, "Completed.", phase_before=AgentPhase.LEARNING_PROPOSING, phase_after=AgentPhase.COMPLETED)

    replay = AgentTraceReplayer().replay(bus.events())

    assert replay.certification.certified is True
    assert replay.accepted is False
    assert "invalid_repair_decided_current_repair_cycles" in replay.errors
    assert "invalid_repair_decided_max_repair_cycles" in replay.errors
