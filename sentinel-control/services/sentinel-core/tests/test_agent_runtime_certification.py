from __future__ import annotations

from pathlib import Path

from sentinel.agent import AgentEventType, AgentPhase, AgentRuntime, EventBus, RuntimeCertificationGate, certify_runtime_trace
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
        "mission_title": "P1H certification test",
        "mission_objective": "Certify runtime event order.",
        "success_criteria": ["Runtime certification passes"],
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


def rehash_agent_trace(events):
    previous_hash = None
    rehashed = []
    for index, event in enumerate(events):
        event_data = event.model_dump()
        event_data.update(
            {
                "sequence": index,
                "logical_time": index,
                "previous_hash": previous_hash,
                "event_hash": "",
            }
        )
        event_hash = EventBus._hash_payload(event_data)
        rehashed_event = event.model_copy(
            update={
                "sequence": index,
                "logical_time": index,
                "previous_hash": previous_hash,
                "event_hash": event_hash,
            }
        )
        rehashed.append(rehashed_event)
        previous_hash = event_hash
    return rehashed


def test_runtime_certification_accepts_clean_agent_run(tmp_path: Path):
    env = envelope()

    result = AgentRuntime(project_root=tmp_path).run(env, {"idea": "Certified run"}, evidence_refs=["ev_wtp"])

    assert result.runtime_certification is not None
    assert result.runtime_certification.certified is True
    assert result.runtime_certification.execution_seen is True
    assert result.runtime_certification.planning_seen is True


def test_runtime_certification_accepts_early_blocked_trace_without_execution():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.AGENT_BLOCKED, "Blocked.", phase_before=AgentPhase.INITIALIZED, phase_after=AgentPhase.BLOCKED)

    certification = certify_runtime_trace(bus.events())

    assert certification.certified is True
    assert certification.execution_seen is False
    assert certification.planning_seen is False


def test_runtime_certification_rejects_execution_before_plan_review():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.TOOLS_SELECTED, "Tools.", phase_before=AgentPhase.TOOL_SELECTING, phase_after=AgentPhase.TOOL_SELECTING)
    bus.append(AgentEventType.HYPOTHESES_REVIEWED, "Hypotheses.", phase_before=AgentPhase.HYPOTHESIS_VERIFYING, phase_after=AgentPhase.HYPOTHESIS_VERIFYING)
    bus.append(AgentEventType.WORLD_MODEL_SIMULATED, "World.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.OBJECTIVE_SCORED, "Score.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.EFFORT_ROUTED, "Effort.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.EFFORT_ROUTING)
    bus.append(AgentEventType.PLAN_CREATED, "Plan.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.PLANNING)
    bus.append(AgentEventType.WORKER_STARTED, "Worker too early.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.EXECUTING)
    bus.append(AgentEventType.AGENT_FAILED, "Failed.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.FAILED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert "missing_plan_reviewed_before_worker_started" in certification.errors


def test_runtime_certification_rejects_controlled_execution_before_plan_review():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.TOOLS_SELECTED, "Tools.", phase_before=AgentPhase.TOOL_SELECTING, phase_after=AgentPhase.TOOL_SELECTING)
    bus.append(AgentEventType.HYPOTHESES_REVIEWED, "Hypotheses.", phase_before=AgentPhase.HYPOTHESIS_VERIFYING, phase_after=AgentPhase.HYPOTHESIS_VERIFYING)
    bus.append(AgentEventType.WORLD_MODEL_SIMULATED, "World.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.OBJECTIVE_SCORED, "Score.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.EFFORT_ROUTED, "Effort.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.EFFORT_ROUTING)
    bus.append(AgentEventType.PLAN_CREATED, "Plan.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.PLANNING)
    bus.append(
        AgentEventType.CONTROLLED_CAPABILITY_EXECUTED,
        "Controlled execution too early.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
    )
    bus.append(AgentEventType.AGENT_FAILED, "Failed.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.FAILED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert "missing_plan_reviewed_before_controlled_capability_executed" in certification.errors


def test_runtime_certification_rejects_malformed_controlled_execution_event():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.TOOLS_SELECTED, "Tools.", phase_before=AgentPhase.TOOL_SELECTING, phase_after=AgentPhase.TOOL_SELECTING)
    bus.append(AgentEventType.HYPOTHESES_REVIEWED, "Hypotheses.", phase_before=AgentPhase.HYPOTHESIS_VERIFYING, phase_after=AgentPhase.HYPOTHESIS_VERIFYING)
    bus.append(AgentEventType.WORLD_MODEL_SIMULATED, "World.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.OBJECTIVE_SCORED, "Score.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.EFFORT_ROUTED, "Effort.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.EFFORT_ROUTING)
    bus.append(AgentEventType.PLAN_CREATED, "Plan.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.PLANNING)
    bus.append(AgentEventType.PLAN_REVIEWED, "Plan reviewed.", phase_before=AgentPhase.PLANNING, phase_after=AgentPhase.PLAN_REVIEWING)
    bus.append(
        AgentEventType.CONTROLLED_CAPABILITY_EXECUTED,
        "Malformed controlled execution.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={"tool_id": "safe_file_writer", "action": "create_markdown_file"},
    )
    bus.append(AgentEventType.AGENT_FAILED, "Failed.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.FAILED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert any(error.startswith("malformed_controlled_capability_executed_") for error in certification.errors)


def test_runtime_certification_rejects_plan_without_effort_route():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.TOOLS_SELECTED, "Tools.", phase_before=AgentPhase.TOOL_SELECTING, phase_after=AgentPhase.TOOL_SELECTING)
    bus.append(AgentEventType.HYPOTHESES_REVIEWED, "Hypotheses.", phase_before=AgentPhase.HYPOTHESIS_VERIFYING, phase_after=AgentPhase.HYPOTHESIS_VERIFYING)
    bus.append(AgentEventType.WORLD_MODEL_SIMULATED, "World.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.OBJECTIVE_SCORED, "Score.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.PLAN_CREATED, "Plan without effort.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.PLANNING)
    bus.append(AgentEventType.AGENT_BLOCKED, "Blocked.", phase_before=AgentPhase.PLANNING, phase_after=AgentPhase.BLOCKED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert "missing_effort_routed_before_plan_created" in certification.errors


def test_runtime_certification_rejects_invalid_declared_phase_transition():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.SUCCESS_EVALUATED, "Impossible jump.", phase_before=AgentPhase.ORIENTING, phase_after=AgentPhase.SUCCESS_EVALUATING)
    bus.append(AgentEventType.AGENT_FAILED, "Failed.", phase_before=AgentPhase.SUCCESS_EVALUATING, phase_after=AgentPhase.FAILED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert any(error.startswith("invalid_phase_transition_orienting_to_success_evaluating") for error in certification.errors)


def test_runtime_certification_rejects_success_before_repair_decision():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.TOOLS_SELECTED, "Tools.", phase_before=AgentPhase.TOOL_SELECTING, phase_after=AgentPhase.TOOL_SELECTING)
    bus.append(AgentEventType.HYPOTHESES_REVIEWED, "Hypotheses.", phase_before=AgentPhase.HYPOTHESIS_VERIFYING, phase_after=AgentPhase.HYPOTHESIS_VERIFYING)
    bus.append(AgentEventType.WORLD_MODEL_SIMULATED, "World.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.OBJECTIVE_SCORED, "Score.", phase_before=AgentPhase.ACTION_SCORING, phase_after=AgentPhase.ACTION_SCORING)
    bus.append(AgentEventType.EFFORT_ROUTED, "Effort.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.EFFORT_ROUTING)
    bus.append(AgentEventType.PLAN_CREATED, "Plan.", phase_before=AgentPhase.EFFORT_ROUTING, phase_after=AgentPhase.PLANNING)
    bus.append(AgentEventType.PLAN_REVIEWED, "Plan reviewed.", phase_before=AgentPhase.PLANNING, phase_after=AgentPhase.PLAN_REVIEWING)
    bus.append(AgentEventType.WORKER_STARTED, "Worker.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.EXECUTING)
    bus.append(AgentEventType.WORKER_COMPLETED, "Worker done.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.ARTIFACT_REVIEWING)
    bus.append(AgentEventType.ARTIFACTS_REVIEWED, "Artifacts.", phase_before=AgentPhase.EXECUTING, phase_after=AgentPhase.ARTIFACT_REVIEWING)
    bus.append(AgentEventType.SUCCESS_EVALUATED, "Success too early.", phase_before=AgentPhase.ARTIFACT_REVIEWING, phase_after=AgentPhase.SUCCESS_EVALUATING)
    bus.append(AgentEventType.AGENT_COMPLETED, "Completed.", phase_before=AgentPhase.LEARNING_PROPOSING, phase_after=AgentPhase.COMPLETED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert "missing_repair_decided_before_success_evaluated" in certification.errors


def test_runtime_certification_rejects_later_worker_start_before_plan_review(tmp_path: Path):
    result = AgentRuntime(project_root=tmp_path).run(envelope(), {"idea": "Forged worker order"}, evidence_refs=["ev_wtp"])
    worker_event = next(event for event in result.trace if event.event_type == AgentEventType.WORKER_STARTED)
    plan_created_index = next(index for index, event in enumerate(result.trace) if event.event_type == AgentEventType.PLAN_CREATED)
    forged_worker = worker_event.model_copy(update={"id": "aev_forged_worker_started_before_review"})
    unsafe_trace = [
        *result.trace[: plan_created_index + 1],
        forged_worker,
        *result.trace[plan_created_index + 1 :],
    ]

    certification = RuntimeCertificationGate().certify(rehash_agent_trace(unsafe_trace))

    assert certification.certified is False
    assert any(error.startswith("plan_reviewed_after_worker_started_at_") for error in certification.errors)
    assert "worker_started_without_worker_completed" in certification.errors


def test_runtime_certification_rejects_completed_without_success_evaluation_true():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.AGENT_COMPLETED, "Completed without success.", phase_before=AgentPhase.LEARNING_PROPOSING, phase_after=AgentPhase.COMPLETED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert "agent_completed_without_success_evaluation_true" in certification.errors


def test_runtime_certification_rejects_completed_without_learning_proposed():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.SUCCESS_EVALUATED, "Success.", phase_before=AgentPhase.SUCCESS_EVALUATING, phase_after=AgentPhase.SUCCESS_EVALUATING, payload={"success": True})
    bus.append(AgentEventType.AGENT_COMPLETED, "Completed without learning.", phase_before=AgentPhase.LEARNING_PROPOSING, phase_after=AgentPhase.COMPLETED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert "agent_completed_without_learning_proposed" in certification.errors


def test_runtime_certification_rejects_terminal_event_before_trace_end():
    bus = EventBus("mission_001")
    bus.append(AgentEventType.AGENT_INITIALIZED, "Initialized.", phase_before=AgentPhase.CREATED, phase_after=AgentPhase.INITIALIZED)
    bus.append(AgentEventType.AGENT_BLOCKED, "Blocked early.", phase_before=AgentPhase.INITIALIZED, phase_after=AgentPhase.BLOCKED)
    bus.append(AgentEventType.AGENT_FAILED, "Forged final.", phase_before=AgentPhase.INITIALIZED, phase_after=AgentPhase.FAILED)

    certification = RuntimeCertificationGate().certify(bus.events())

    assert certification.certified is False
    assert "terminal_event_before_end_agent_blocked_at_1" in certification.errors


def test_runtime_certification_rejects_duplicate_event_ids(tmp_path: Path):
    result = AgentRuntime(project_root=tmp_path).run(envelope(), {"idea": "Duplicate event id"}, evidence_refs=["ev_wtp"])
    unsafe_trace = list(result.trace)
    unsafe_trace[1] = unsafe_trace[1].model_copy(update={"id": unsafe_trace[0].id})

    certification = RuntimeCertificationGate().certify(rehash_agent_trace(unsafe_trace))

    assert certification.certified is False
    assert "duplicate_event_ids" in certification.errors
