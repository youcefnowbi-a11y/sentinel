from __future__ import annotations

from pathlib import Path
from typing import Any

from sentinel.agent import (
    AgentEventType,
    AgentPhase,
    AgentRunResult,
    AgentStateSnapshot,
    EvalCase,
    EvalCheckKind,
    EvidenceDecisionType,
    EventBus,
    RuntimeCertificationResult,
    SentinelEvalBench,
)
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


GTM_REQUIRED_FILES = [
    "00_VERDICT.md",
    "01_EVIDENCE.md",
    "02_ICP.md",
    "03_COMPETITOR_GAPS.md",
    "04_LANDING_PAGE_COPY.md",
    "05_OUTREACH_MESSAGES.md",
    "07_7_DAY_ROADMAP.md",
    "08_WATCHLIST.md",
    "mission_artifacts.json",
    "mission_timeline.json",
    "artifact_manifest.json",
    "outreach_drafts.json",
]


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "P1K eval bench mission",
        "mission_objective": "Evaluate Sentinel mission harness contracts.",
        "success_criteria": ["GTM files exist", "Trace exists", "Evidence chains exist"],
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


def successful_gtm_case(**overrides) -> EvalCase:
    data = {
        "id": "gtm_success",
        "name": "Successful GTM mission contract",
        "envelope": envelope(),
        "user_input": {"idea": "Sentinel EvalBench"},
        "evidence_refs": ["ev_wtp", "ev_competitor"],
        "expected_success": True,
        "expected_final_phase": AgentPhase.COMPLETED,
        "required_artifact_files": GTM_REQUIRED_FILES,
        "required_event_types": [
            AgentEventType.TOOLS_SELECTED,
            AgentEventType.PLAN_CREATED,
            AgentEventType.WORKER_COMPLETED,
            AgentEventType.AGENT_COMPLETED,
            AgentEventType.EVIDENCE_CHAIN_BUILT,
        ],
        "forbidden_event_types": [AgentEventType.AGENT_ESCALATED, AgentEventType.AGENT_REVOKED],
        "required_selected_tools": ["safe_file_writer"],
        "required_missing_capabilities": ["browser_research"],
        "required_evidence_chain_types": [
            EvidenceDecisionType.TOOL_SELECTION,
            EvidenceDecisionType.HYPOTHESIS_VERDICT,
            EvidenceDecisionType.PLAN_CREATION,
            EvidenceDecisionType.REPAIR_DECISION,
            EvidenceDecisionType.SUCCESS_EVALUATION,
            EvidenceDecisionType.LEARNING_PROPOSAL,
        ],
    }
    data.update(overrides)
    return EvalCase(**data)


def test_eval_bench_accepts_successful_gtm_case_with_noop_and_stability(tmp_path):
    bench = SentinelEvalBench(project_root=tmp_path)

    suite = bench.run_suite([successful_gtm_case()], iterations=2, include_no_op=True)

    assert suite.accepted is True
    case_result = suite.case_results[0]
    assert case_result.accepted is True
    assert case_result.no_op_checks[0].kind == EvalCheckKind.NO_OP
    assert case_result.no_op_checks[0].passed is True
    assert case_result.stability_checks[0].kind == EvalCheckKind.STABILITY
    assert case_result.stability_checks[0].passed is True
    assert case_result.metrics is not None
    assert case_result.metrics.run_count == 2
    assert case_result.metrics.accepted_rate == 1.0
    assert case_result.metrics.success_rate == 1.0
    assert case_result.metrics.unstable_iterations == []
    assert all(run.accepted for run in case_result.runs)
    assert {check.kind for check in suite.checks} >= {EvalCheckKind.F2P, EvalCheckKind.P2P, EvalCheckKind.NO_OP, EvalCheckKind.STABILITY}


def test_eval_bench_f2p_fails_when_required_artifact_is_missing(tmp_path):
    bench = SentinelEvalBench(project_root=tmp_path)
    case = successful_gtm_case(id="missing_artifact", required_artifact_files=[*GTM_REQUIRED_FILES, "99_NON_EXISTENT.md"])

    result = bench.run_case(case, iterations=1, include_no_op=True)

    assert result.accepted is False
    artifact_check = next(check for check in result.runs[0].checks if check.name == "required_artifact_files")
    assert artifact_check.kind == EvalCheckKind.F2P
    assert artifact_check.passed is False
    assert "99_NON_EXISTENT.md" in artifact_check.details["missing_files"]


def test_eval_bench_p2p_fails_when_forbidden_event_is_present(tmp_path):
    bench = SentinelEvalBench(project_root=tmp_path)
    case = successful_gtm_case(id="forbidden_worker", forbidden_event_types=[AgentEventType.WORKER_STARTED])

    result = bench.run_case(case, iterations=1, include_no_op=False)

    assert result.accepted is False
    forbidden_check = next(check for check in result.runs[0].checks if check.name == "forbidden_event_types")
    assert forbidden_check.kind == EvalCheckKind.P2P
    assert forbidden_check.passed is False
    assert AgentEventType.WORKER_STARTED.value in forbidden_check.details["forbidden_events"]


def test_eval_bench_rejects_dirty_run_root_before_runtime(tmp_path):
    bench = SentinelEvalBench(project_root=tmp_path)
    case = successful_gtm_case(id="dirty_run_root")
    dirty_root = tmp_path / "sentinel_eval_runs" / case.id / "run_0"
    dirty_root.mkdir(parents=True)
    (dirty_root / "stale_artifact.txt").write_text("stale", encoding="utf-8")

    result = bench.run_case(case, iterations=1, include_no_op=False)

    assert result.accepted is False
    clean_check = next(check for check in result.runs[0].checks if check.name == "clean_run_root")
    assert clean_check.kind == EvalCheckKind.NO_OP
    assert clean_check.passed is False
    assert clean_check.details["preexisting_entries"] == ["stale_artifact.txt"]


def test_eval_bench_marks_blocked_mission_as_valid_negative_case(tmp_path):
    bench = SentinelEvalBench(project_root=tmp_path)
    blocked_case = EvalCase(
        id="blocked_missing_tool",
        name="Blocked mission has no unsafe execution",
        envelope=envelope(allowed_actions=["create_project_folder"], allowed_tools=["safe_file_writer"]),
        user_input={"idea": "Blocked mission"},
        evidence_refs=["ev_scope"],
        expected_success=False,
        expected_final_phase=AgentPhase.BLOCKED,
        required_event_types=[AgentEventType.TOOLS_SELECTED, AgentEventType.AGENT_BLOCKED, AgentEventType.EVIDENCE_CHAIN_BUILT],
        forbidden_event_types=[AgentEventType.WORKER_STARTED, AgentEventType.WORKER_COMPLETED],
        required_missing_capabilities=["gtm_pack_generation", "browser_research"],
        required_evidence_chain_types=[EvidenceDecisionType.TOOL_SELECTION, EvidenceDecisionType.LEARNING_PROPOSAL],
    )

    result = bench.run_case(blocked_case, iterations=1, include_no_op=False)

    assert result.accepted is True
    assert result.runs[0].success is False
    assert result.runs[0].final_phase == AgentPhase.BLOCKED


def test_eval_bench_stability_detects_artifact_content_drift(tmp_path):
    counter = {"value": 0}

    class VaryingArtifactRuntime:
        def __init__(self, project_root: Path) -> None:
            self.project_root = project_root

        def run(
            self,
            envelope: MissionAuthorityEnvelope,
            user_input: dict[str, Any] | None = None,
            *,
            evidence_refs: list[str] | None = None,
            memory_items: list[dict[str, Any]] | None = None,
        ) -> AgentRunResult:
            counter["value"] += 1
            project_path = self.project_root / "data" / "generated_projects" / "artifact-stability"
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "artifact.txt").write_text(f"version={counter['value']}", encoding="utf-8")
            bus = EventBus(envelope.id)
            bus.append(AgentEventType.AGENT_COMPLETED, "Completed.", phase_after=AgentPhase.COMPLETED)
            return AgentRunResult(
                mission_id=envelope.id,
                final_phase=AgentPhase.COMPLETED,
                success=True,
                project_path=str(project_path),
                trace=list(bus.events()),
                runtime_certification=RuntimeCertificationResult(mission_id=envelope.id, certified=True),
                state_snapshot=AgentStateSnapshot(mission_id=envelope.id),
            )

    bench = SentinelEvalBench(project_root=tmp_path, runtime_factory=VaryingArtifactRuntime)
    case = EvalCase(
        id="artifact_drift",
        name="Artifact drift detection",
        envelope=envelope(mission_title="Artifact drift"),
        expected_success=True,
        expected_final_phase=AgentPhase.COMPLETED,
        required_artifact_files=["artifact.txt"],
        stable_artifact_files=["artifact.txt"],
    )

    result = bench.run_case(case, iterations=2, include_no_op=False)

    assert result.accepted is False
    assert all(run.accepted for run in result.runs)
    assert result.runs[0].artifact_signature != result.runs[1].artifact_signature
    stability_check = result.stability_checks[0]
    assert stability_check.kind == EvalCheckKind.STABILITY
    assert stability_check.passed is False
    assert stability_check.details["unstable_iterations"] == [1]
    assert result.metrics is not None
    assert result.metrics.run_count == 2
    assert result.metrics.unstable_iterations == [1]
    assert result.metrics.accepted_rate == 1.0
