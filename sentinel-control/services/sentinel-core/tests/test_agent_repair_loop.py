from __future__ import annotations

from pathlib import Path

from sentinel.agent import (
    AdversarialFinding,
    AgentEventType,
    AgentPhase,
    AgentRuntime,
    CognitiveRepairLoop,
    ContextBuilder,
    EffortLevel,
    EffortRoute,
    EventBus,
    RepairDecisionType,
    ReviewFinding,
)
from sentinel.agent.models import CapabilityNeed
from sentinel.agent.state import AgentState
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
        "mission_title": "P1G repair loop test",
        "mission_objective": "Decide bounded cognitive repair.",
        "success_criteria": ["Repair decision trace exists"],
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


def effort(env: MissionAuthorityEnvelope, level: EffortLevel = EffortLevel.LOW) -> EffortRoute:
    score = {
        EffortLevel.LOW: 0.10,
        EffortLevel.MEDIUM: 0.35,
        EffortLevel.HIGH: 0.65,
        EffortLevel.EXTREME: 0.95,
    }[level]
    return EffortRoute(
        mission_id=env.id,
        level=level,
        score=score,
        uncertainty_pressure=score,
        verification_pressure=score,
        risk_pressure=0.0,
        budget_pressure=0.15,
        recommended_cycles=0,
        max_parallel_workers=1,
        reason=f"test_effort={level}",
    )


def finding(severity: str = "critical") -> ReviewFinding:
    return ReviewFinding(code=f"{severity}_finding", severity=severity, message=f"{severity} repair finding")


def adversarial(env: MissionAuthorityEnvelope, severity: str = "high") -> AdversarialFinding:
    return AdversarialFinding(
        mission_id=env.id,
        attack_type="test_attack",
        finding=f"{severity} adversarial finding",
        severity=severity,
        suggested_repair="Bound the claim and keep evidence refs.",
    )


def decide(
    env: MissionAuthorityEnvelope,
    state: AgentState,
    *,
    review_findings: list[ReviewFinding] | None = None,
    adversarial_findings: list[AdversarialFinding] | None = None,
    effort_level: EffortLevel = EffortLevel.LOW,
):
    context = ContextBuilder().build(env)
    bus = EventBus(env.id)
    decision = CognitiveRepairLoop().decide(
        context,
        state,
        review_findings=review_findings or [],
        adversarial_findings=adversarial_findings or [],
        objective_scores=[],
        effort_route=effort(env, effort_level),
        event_bus=bus,
    )
    return decision, bus


def test_no_repair_if_no_findings_even_with_low_confidence():
    env = envelope()
    state = AgentState(mission_id=env.id, confidence_score=0.0)

    decision, bus = decide(env, state, effort_level=EffortLevel.EXTREME)

    assert decision.decision == RepairDecisionType.NO_REPAIR_NEEDED
    assert decision.repair_pressure == 0.0
    assert AgentEventType.REPAIR_DECIDED in [event.event_type for event in bus.events()]


def test_critical_finding_creates_repair_pressure_and_instruction():
    env = envelope()
    state = AgentState(mission_id=env.id, confidence_score=0.8)

    decision, _ = decide(env, state, review_findings=[finding("critical")])

    assert decision.decision == RepairDecisionType.REPAIR_ALLOWED
    assert decision.repair_pressure >= 0.25
    assert decision.instructions
    assert decision.instructions[0].forbidden_actions == env.forbidden_actions


def test_adversarial_finding_and_low_confidence_create_repair_pressure():
    env = envelope()
    high_confidence = AgentState(mission_id=env.id, confidence_score=0.9)
    low_confidence = AgentState(mission_id=env.id, confidence_score=0.0)

    high_decision, _ = decide(
        env,
        high_confidence,
        review_findings=[finding("medium")],
        adversarial_findings=[adversarial(env)],
        effort_level=EffortLevel.LOW,
    )
    low_decision, _ = decide(
        env,
        low_confidence,
        review_findings=[finding("medium")],
        adversarial_findings=[adversarial(env)],
        effort_level=EffortLevel.HIGH,
    )

    assert low_decision.repair_pressure > high_decision.repair_pressure
    assert low_decision.decision == RepairDecisionType.REPAIR_ALLOWED
    assert "confidence_deficit" in low_decision.reasons


def test_repair_blocked_after_max_cycles():
    env = envelope()
    state = AgentState(mission_id=env.id, confidence_score=0.2, repair_cycles=1, max_repair_cycles=1)

    decision, _ = decide(env, state, review_findings=[finding("critical")])

    assert decision.decision == RepairDecisionType.REPAIR_BLOCKED
    assert "max_repair_cycles_exhausted" in decision.reasons


def test_high_pressure_escalates_when_cycles_remain():
    env = envelope()
    state = AgentState(
        mission_id=env.id,
        confidence_score=0.0,
        missing_capabilities=[CapabilityNeed(name="payment_execution", reason="Forbidden", required=True, available=False)],
    )

    decision, _ = decide(
        env,
        state,
        review_findings=[finding("critical")],
        adversarial_findings=[adversarial(env, "critical")],
        effort_level=EffortLevel.EXTREME,
    )

    assert decision.decision == RepairDecisionType.ESCALATE
    assert decision.repair_pressure >= 0.85


def test_repair_cannot_revive_terminal_phase():
    env = envelope()
    state = AgentState(mission_id=env.id, phase=AgentPhase.COMPLETED, confidence_score=0.0)

    decision, _ = decide(env, state, review_findings=[finding("critical")])

    assert decision.decision == RepairDecisionType.REPAIR_BLOCKED
    assert "terminal_phase_cannot_be_repaired" in decision.reasons


def test_runtime_records_no_repair_decision_on_clean_run(tmp_path: Path):
    env = envelope()

    result = AgentRuntime(project_root=tmp_path).run(env, {"idea": "Clean repair path"}, evidence_refs=["ev_wtp"])
    event_types = [event.event_type for event in result.trace]

    assert result.success is True
    assert result.repair_decision is not None
    assert result.repair_decision.decision == RepairDecisionType.NO_REPAIR_NEEDED
    assert event_types.index(AgentEventType.ARTIFACTS_REVIEWED) < event_types.index(AgentEventType.REPAIR_DECIDED)
    assert event_types.index(AgentEventType.REPAIR_DECIDED) < event_types.index(AgentEventType.SUCCESS_EVALUATED)


def test_runtime_enters_repair_once_for_repairable_artifact_finding(tmp_path: Path):
    env = envelope()
    runtime = AgentRuntime(project_root=tmp_path)

    runtime.review_loop.review_worker_result = lambda result: [finding("critical")]
    result = runtime.run(env, {"idea": "Repairable issue"}, evidence_refs=["ev_wtp"])

    repair_event = next(event for event in result.trace if event.event_type == AgentEventType.REPAIR_DECIDED)
    assert result.repair_decision is not None
    assert result.repair_decision.decision == RepairDecisionType.REPAIR_ALLOWED
    assert result.repair_decision.current_repair_cycles == 0
    assert repair_event.phase_after == AgentPhase.REPAIRING
    success_event = next(event for event in result.trace if event.event_type == AgentEventType.SUCCESS_EVALUATED)
    repair_execution_event = next(event for event in result.trace if event.event_type == AgentEventType.REPAIR_EXECUTED)
    assert repair_execution_event.phase_before == AgentPhase.REPAIRING
    assert repair_execution_event.phase_after == AgentPhase.EXECUTING
    assert success_event.phase_before == AgentPhase.ARTIFACT_REVIEWING
    assert result.final_phase == AgentPhase.FAILED
    assert result.selected_tools == ["safe_file_writer"]


def test_runtime_bounded_repair_pass_can_recover_from_first_artifact_finding(tmp_path: Path):
    env = envelope()
    runtime = AgentRuntime(project_root=tmp_path)
    original_review = runtime.review_loop.review_worker_result
    review_calls = 0

    def review_once_then_clear(result):
        nonlocal review_calls
        review_calls += 1
        if review_calls == 1:
            return [finding("critical")]
        return original_review(result)

    runtime.review_loop.review_worker_result = review_once_then_clear

    result = runtime.run(env, {"idea": "Repair once then finish"}, evidence_refs=["ev_wtp"])
    event_types = [event.event_type for event in result.trace]

    assert result.success is True
    assert result.final_phase == AgentPhase.COMPLETED
    assert review_calls == 2
    assert event_types.count(AgentEventType.WORKER_STARTED) == 2
    assert event_types.count(AgentEventType.WORKER_COMPLETED) == 2
    assert AgentEventType.REPAIR_EXECUTED in event_types
    assert len(result.mission_results) == 2
    assert all(mission_result.trace_events for mission_result in result.mission_results)
    assert result.mission_result is not None
    assert result.mission_results[-1].project_path == result.mission_result.project_path
    assert result.mission_results[-1].success == result.mission_result.success
    assert result.repair_decision is not None
    assert result.repair_decision.decision == RepairDecisionType.REPAIR_ALLOWED
    assert result.state_snapshot is not None
    assert result.state_snapshot.repair_cycles == 1
    assert result.runtime_certification is not None
    assert result.runtime_certification.certified is True


def test_runtime_blocks_repair_when_global_action_budget_would_overflow(tmp_path: Path):
    env = envelope(max_actions=6)
    runtime = AgentRuntime(project_root=tmp_path)
    runtime.review_loop.review_worker_result = lambda result: [finding("critical")]

    result = runtime.run(env, {"idea": "Repair would exceed global budget"}, evidence_refs=["ev_wtp"])
    event_types = [event.event_type for event in result.trace]

    assert result.success is False
    assert result.final_phase == AgentPhase.FAILED
    assert result.repair_decision is not None
    assert result.repair_decision.decision == RepairDecisionType.REPAIR_BLOCKED
    assert "repair_blocked_by_global_action_budget" in result.repair_decision.reasons
    assert event_types.count(AgentEventType.WORKER_STARTED) == 1
    assert AgentEventType.REPAIR_EXECUTED not in event_types
