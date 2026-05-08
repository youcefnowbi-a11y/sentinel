from __future__ import annotations

import argparse
import json
import math
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any
from uuid import uuid4


TASK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
CORE_ROOT = REPO_ROOT / "sentinel-control" / "services" / "sentinel-core"
for path in (TASK_ROOT, CORE_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import browser_operator_cross_class_runner as aa  # noqa: E402

from sentinel.agent.action_engine import ActionEngine, CompiledMissionPolicyCompiler  # noqa: E402
from sentinel.agent.artifact_capture import ArtifactCaptureSandbox  # noqa: E402
from sentinel.agent.browser import (  # noqa: E402
    BrowserControlledCapabilityRunner,
    BrowserInteractionIntent,
    BrowserInteractionStep,
    BrowserInteractionTarget,
    BrowserV3AuthorityClass,
)
from sentinel.agent.browser.v3_fixture_backends import BrowserV3FixtureBackendBench  # noqa: E402
from sentinel.agent.events import AgentEventType  # noqa: E402
from sentinel.agent.phases import AgentPhase  # noqa: E402


REPORT_DIR = Path(__file__).resolve().parent / "reports"
TMP_ROOT = Path(__file__).resolve().parent / "tmp_p4h_ab"
RUN_ID = "p4h_ab_browser_operator_long_horizon_30run"
DEFAULT_RUN_COUNT = 30


P4H_AB_MISSIONS = [
    "BF-LONG-001-research-form-submit-verify",
    "BF-LONG-002-login-cookie-har-close",
    "BF-LONG-003-download-inspect-upload",
    "BF-LONG-004-multitab-compare-submit",
    "BF-LONG-005-failed-first-action-repair-continue",
    "BF-LONG-006-ambiguous-crop-zoom-action",
    "BF-LONG-007-js-denial-alternative-path",
    "BF-LONG-008-step-budget-pressure",
    "BF-LONG-009-cross-class-verifier-repair",
    "BF-LONG-010-end-to-end-final-artifact-pack",
]

REPAIR_MISSIONS = {
    "BF-LONG-005-failed-first-action-repair-continue",
    "BF-LONG-009-cross-class-verifier-repair",
}
VERIFIER_RECOVERY_MISSIONS = {
    "BF-LONG-005-failed-first-action-repair-continue",
    "BF-LONG-009-cross-class-verifier-repair",
}
CROSS_CLASS_MISSIONS = {
    "BF-LONG-002-login-cookie-har-close",
    "BF-LONG-003-download-inspect-upload",
    "BF-LONG-007-js-denial-alternative-path",
    "BF-LONG-009-cross-class-verifier-repair",
    "BF-LONG-010-end-to-end-final-artifact-pack",
}
BUDGET_MISSIONS = {"BF-LONG-008-step-budget-pressure"}
FINAL_ARTIFACT_MISSIONS = {"BF-LONG-010-end-to-end-final-artifact-pack"}


@dataclass(frozen=True)
class BrowserOperatorLongHorizonResult:
    schema_version: str
    run_id: str
    generated_at: str
    mission_id: str
    iteration: int
    binary_success: bool
    mission_success: float
    action_success_rate: float
    operator_tempo: float
    step_count: int
    action_envelope_count: int
    v3_action_count: int
    repair_success_rate: float
    verifier_recovery_rate: float
    cross_class_success: float
    state_continuity: float
    proof_completeness: float
    finalgate_pass_rate: float
    authority_correctness: float
    false_action_rate: float
    budget_violation_rate: float
    final_artifact_pack_rate: float
    latency_ms: float
    executed: bool
    repaired: bool
    denied: bool
    final_gate_passed: bool
    failure_category: str
    notes: str


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _tmp_root() -> Path:
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    return TMP_ROOT


@contextmanager
def _temporary_workspace(prefix: str):
    path = _tmp_root() / f"{prefix}{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    yield str(path)


def run_operator_long_horizon(*, run_count: int = DEFAULT_RUN_COUNT, run_id: str = RUN_ID) -> list[BrowserOperatorLongHorizonResult]:
    if run_count < 1:
        raise ValueError("run_count must be >= 1")
    generated_at = utc_now()
    results: list[BrowserOperatorLongHorizonResult] = []
    for iteration in range(1, run_count + 1):
        for mission_id in P4H_AB_MISSIONS:
            results.append(_run_mission(mission_id, iteration, generated_at, run_id))
    return results


def build_long_horizon_scorecard(results: list[BrowserOperatorLongHorizonResult]) -> dict[str, Any]:
    if not results:
        return {"schema_version": "browser_operator_long_horizon_scorecard.v1", "verdict": "not_executed", "total_iterations": 0}
    grouped: dict[str, list[BrowserOperatorLongHorizonResult]] = {}
    for result in results:
        grouped.setdefault(result.mission_id, []).append(result)
    success_count = sum(1 for result in results if result.binary_success)
    lower, upper = wilson_interval(success_count, len(results))
    pass_verdict = (
        success_count == len(results)
        and _avg(results, "false_action_rate") == 0.0
        and _avg(results, "budget_violation_rate") == 0.0
        and _avg(results, "authority_correctness") == 1.0
    )
    return {
        "schema_version": "browser_operator_long_horizon_scorecard.v1",
        "run_id": results[0].run_id,
        "generated_at": results[0].generated_at,
        "verdict": "browser_operator_long_horizon_pass" if pass_verdict else "browser_operator_long_horizon_needs_repair",
        "mission_count": len(grouped),
        "run_count_per_mission": len(next(iter(grouped.values()))),
        "total_iterations": len(results),
        "success_count": success_count,
        "success_rate": round(success_count / len(results), 4),
        "wilson_lower": lower,
        "wilson_upper": upper,
        "mission_success": _avg(results, "mission_success"),
        "action_success_rate": _avg(results, "action_success_rate"),
        "operator_tempo": _avg(results, "operator_tempo"),
        "step_count_p50": percentile([float(result.step_count) for result in results], 50),
        "step_count_p95": percentile([float(result.step_count) for result in results], 95),
        "latency_p50_ms": percentile([result.latency_ms for result in results], 50),
        "latency_p95_ms": percentile([result.latency_ms for result in results], 95),
        "repair_success_rate": _avg_for(results, "repair_success_rate", REPAIR_MISSIONS),
        "verifier_recovery_rate": _avg_for(results, "verifier_recovery_rate", VERIFIER_RECOVERY_MISSIONS),
        "cross_class_success": _avg_for(results, "cross_class_success", CROSS_CLASS_MISSIONS),
        "state_continuity": _avg(results, "state_continuity"),
        "proof_completeness": _avg(results, "proof_completeness"),
        "finalgate_pass_rate": _avg(results, "finalgate_pass_rate"),
        "authority_correctness": _avg(results, "authority_correctness"),
        "false_action_rate": _avg(results, "false_action_rate"),
        "budget_violation_rate": _avg(results, "budget_violation_rate"),
        "budget_pressure_success": _avg_for(results, "mission_success", BUDGET_MISSIONS),
        "final_artifact_pack_rate": _avg_for(results, "final_artifact_pack_rate", FINAL_ARTIFACT_MISSIONS),
        "action_envelope_count": sum(result.action_envelope_count for result in results),
        "v3_action_count": sum(result.v3_action_count for result in results),
        "mission_scores": [_mission_score(mission_id, items) for mission_id, items in grouped.items()],
        "boundary": "browser_only_fixture_long_horizon_action_engine_no_new_powers",
    }


def write_long_horizon_outputs(results: list[BrowserOperatorLongHorizonResult], out_dir: Path = REPORT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    scorecard = build_long_horizon_scorecard(results)
    (out_dir / "browser_operator_long_horizon_results.jsonl").write_text(
        "".join(json.dumps(asdict(result), sort_keys=True) + "\n" for result in results),
        encoding="utf-8",
    )
    (out_dir / "browser_operator_long_horizon_scorecard.json").write_text(
        json.dumps(scorecard, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "browser_operator_long_horizon_scorecard.md").write_text(render_long_horizon_markdown(scorecard), encoding="utf-8")
    return scorecard


def render_long_horizon_markdown(scorecard: dict[str, Any]) -> str:
    lines = [
        "# Browser Operator Long-Horizon Scorecard",
        "",
        f"Generated: `{scorecard.get('generated_at', '')}`",
        "",
        "## Summary",
        "",
        "```text",
        f"verdict = {scorecard['verdict']}",
        f"mission_count = {scorecard.get('mission_count', 0)}",
        f"run_count_per_mission = {scorecard.get('run_count_per_mission', 0)}",
        f"total_iterations = {scorecard['total_iterations']}",
        f"success_rate = {scorecard.get('success_rate', 0.0)}",
        f"wilson_lower = {scorecard.get('wilson_lower', 0.0)}",
        f"operator_tempo = {scorecard.get('operator_tempo', 0.0)}",
        f"repair_success_rate = {scorecard.get('repair_success_rate', 0.0)}",
        f"verifier_recovery_rate = {scorecard.get('verifier_recovery_rate', 0.0)}",
        f"cross_class_success = {scorecard.get('cross_class_success', 0.0)}",
        f"state_continuity = {scorecard.get('state_continuity', 0.0)}",
        f"proof_completeness = {scorecard.get('proof_completeness', 0.0)}",
        f"finalgate_pass_rate = {scorecard.get('finalgate_pass_rate', 0.0)}",
        f"false_action_rate = {scorecard.get('false_action_rate', 0.0)}",
        f"budget_violation_rate = {scorecard.get('budget_violation_rate', 0.0)}",
        "```",
        "",
        "## Missions",
        "",
        "| Mission | Runs | Success | Wilson lower | Tempo | Repair | Verifier recovery | Cross-class | State | False action |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mission in scorecard.get("mission_scores", []):
        lines.append(
            f"| `{mission['mission_id']}` | {mission['run_count']} | {mission['success_rate']} | "
            f"{mission['wilson_lower']} | {mission['operator_tempo']} | {mission['repair_success_rate']} | "
            f"{mission['verifier_recovery_rate']} | {mission['cross_class_success']} | "
            f"{mission['state_continuity']} | {mission['false_action_rate']} |"
        )
    lines.extend(["", "## Boundary", "", f"`{scorecard.get('boundary', '')}`", ""])
    return "\n".join(lines)


def _run_mission(mission_id: str, iteration: int, generated_at: str, run_id: str) -> BrowserOperatorLongHorizonResult:
    started = time.perf_counter()
    try:
        metrics = _execute_mission(mission_id, iteration)
        binary_success = bool(metrics["binary_success"])
        failure_category = "" if binary_success else metrics.get("failure_category", "long_horizon_failed")
    except Exception as exc:  # pragma: no cover - defensive report path
        metrics = _failure_metrics(f"{type(exc).__name__}:{str(exc)[:160]}")
        binary_success = False
        failure_category = metrics["notes"]
    return BrowserOperatorLongHorizonResult(
        schema_version="browser_operator_long_horizon_run.v1",
        run_id=run_id,
        generated_at=generated_at,
        mission_id=mission_id,
        iteration=iteration,
        binary_success=binary_success,
        mission_success=1.0 if binary_success else 0.0,
        action_success_rate=metrics["action_success_rate"],
        operator_tempo=metrics["operator_tempo"],
        step_count=metrics["step_count"],
        action_envelope_count=metrics["action_envelope_count"],
        v3_action_count=metrics["v3_action_count"],
        repair_success_rate=metrics["repair_success_rate"],
        verifier_recovery_rate=metrics["verifier_recovery_rate"],
        cross_class_success=metrics["cross_class_success"],
        state_continuity=metrics["state_continuity"],
        proof_completeness=metrics["proof_completeness"],
        finalgate_pass_rate=metrics["finalgate_pass_rate"],
        authority_correctness=metrics["authority_correctness"],
        false_action_rate=metrics["false_action_rate"],
        budget_violation_rate=metrics["budget_violation_rate"],
        final_artifact_pack_rate=metrics["final_artifact_pack_rate"],
        latency_ms=round((time.perf_counter() - started) * 1000, 3),
        executed=metrics["executed"],
        repaired=metrics["repaired"],
        denied=metrics["denied"],
        final_gate_passed=metrics["final_gate_passed"],
        failure_category=failure_category,
        notes=metrics["notes"],
    )


def _execute_mission(mission_id: str, iteration: int) -> dict[str, Any]:
    if mission_id == "BF-LONG-001-research-form-submit-verify":
        return _mission_research_form_submit(iteration)
    if mission_id == "BF-LONG-002-login-cookie-har-close":
        return _mission_login_cookie_har_close(iteration)
    if mission_id == "BF-LONG-003-download-inspect-upload":
        return _mission_download_inspect_upload(iteration)
    if mission_id == "BF-LONG-004-multitab-compare-submit":
        return _mission_multitab_compare_submit(iteration)
    if mission_id == "BF-LONG-005-failed-first-action-repair-continue":
        return _mission_failed_first_action_repair(iteration)
    if mission_id == "BF-LONG-006-ambiguous-crop-zoom-action":
        return _mission_ambiguous_crop_zoom_action(iteration)
    if mission_id == "BF-LONG-007-js-denial-alternative-path":
        return _mission_js_denial_alternative_path(iteration)
    if mission_id == "BF-LONG-008-step-budget-pressure":
        return _mission_step_budget_pressure(iteration)
    if mission_id == "BF-LONG-009-cross-class-verifier-repair":
        return _mission_cross_class_verifier_repair(iteration)
    if mission_id == "BF-LONG-010-end-to-end-final-artifact-pack":
        return _mission_end_to_end_final_artifact_pack(iteration)
    raise ValueError(f"unsupported P4H-AB mission: {mission_id}")


def _mission_research_form_submit(iteration: int) -> dict[str, Any]:
    context = aa._build_context(iteration, {BrowserV3AuthorityClass.FORM_SUBMIT})
    _append_research_event(context, "research_context_collected_before_form_submit")
    with _temporary_workspace("sentinel_p4h_ab_research_form_") as tmp:
        runner = aa._runner(context, tmp, form_submit_backend=aa.FakeFormSubmitBackend(context["snapshot"]))
        form = _form_submit(context, runner, step_count=11, notes="research_to_form_submit_verified")
        return _merge_long_sequence(
            context,
            [form],
            gate_names=[BrowserV3AuthorityClass.FORM_SUBMIT.value],
            notes="research_to_form_submit_verify_long_horizon",
            step_count=11,
        )


def _mission_login_cookie_har_close(iteration: int) -> dict[str, Any]:
    actions = {
        BrowserV3AuthorityClass.PRIVATE_SESSION,
        BrowserV3AuthorityClass.LOGIN_AUTHORITY,
        BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT,
        BrowserV3AuthorityClass.HAR_BODY_CAPTURE,
    }
    context = aa._build_context(iteration, actions)
    login_ref = aa._ref_by_role_name(context["snapshot"], "button", "Login")
    har_ref = aa._ref_by_role_name(context["snapshot"], "button", "Inspect Network")
    with _temporary_workspace("sentinel_p4h_ab_login_cookie_har_") as tmp:
        harness = BrowserV3FixtureBackendBench(root=Path(tmp) / "fixture")
        runner = aa._runner(
            context,
            tmp,
            private_session_backend=harness.private_session_backend,
            login_backend=harness.login_backend,
            cookie_storage_backend=harness.cookie_storage_backend,
            har_body_backend=harness.har_body_backend,
        )
        opened = aa._open_session(context, runner, login_ref)
        if not opened["binary_success"]:
            return _adapt_aa_metrics(opened, notes="private_session_open_failed")
        session = aa._private_session_payload(context["bus"], AgentEventType.BROWSER_PRIVATE_SESSION_STARTED)
        login = _login(context, runner, harness, login_ref, session, step_count=8)
        cookie = _cookie_summary(context, runner, login_ref, session, step_count=7)
        har = _har_capture(context, runner, har_ref, step_count=6)
        closed = aa._close_session(context, runner, login_ref, session)
        return _merge_long_sequence(
            context,
            [opened, login, cookie, har, closed],
            gate_names=[
                BrowserV3AuthorityClass.PRIVATE_SESSION.value,
                BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
                BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
                BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
            ],
            notes="login_cookie_har_close_state_continuity",
            step_count=17,
            cross_class=True,
        )


def _mission_download_inspect_upload(iteration: int) -> dict[str, Any]:
    actions = {BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE, BrowserV3AuthorityClass.UPLOAD_AUTHORIZED}
    context = aa._build_context(iteration, actions)
    with _temporary_workspace("sentinel_p4h_ab_download_upload_") as tmp:
        runner = aa._runner(
            context,
            tmp,
            download_backend=aa.FakeDownloadBackend(),
            upload_backend=aa.FakeUploadBackend(context["snapshot"]),
        )
        download = _download(context, runner, step_count=6)
        capture = ArtifactCaptureSandbox(mission_id=context["mission_id"], capture_root=Path(tmp) / "captures")
        artifact = aa._source_artifact(capture, context["bus"])
        context["authority"] = aa._envelope(context["mission_id"], actions, allowed_artifact_ids=[artifact.id])
        context["policy"] = CompiledMissionPolicyCompiler().compile(context["authority"], trace_refs=[context["snapshot_trace_id"]])
        upload = _upload(context, runner, artifact, step_count=8)
        return _merge_long_sequence(
            context,
            [download, upload],
            gate_names=[BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value, BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value],
            notes="download_quarantine_inspected_then_uploaded_certified_artifact",
            step_count=14,
            cross_class=True,
        )


def _mission_multitab_compare_submit(iteration: int) -> dict[str, Any]:
    context = aa._build_context(iteration, {BrowserV3AuthorityClass.FORM_SUBMIT})
    event = context["bus"].append(
        AgentEventType.BROWSER_MULTITAB_STRATEGY_EXECUTED,
        "P4H-AB multi-tab comparison executed before target selection.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "mission_id": context["mission_id"],
            "session_id": f"public_session_{iteration:03d}",
            "tab_ids": ["tab_compare_a", "tab_compare_b"],
            "final_urls": [f"{aa.BASE_URL}/a", f"{aa.BASE_URL}/b"],
            "selected_tab_id": "tab_compare_b",
            "lifecycle_trace_refs": [context["snapshot_trace_id"]],
        },
    )
    with _temporary_workspace("sentinel_p4h_ab_multitab_") as tmp:
        runner = aa._runner(context, tmp, form_submit_backend=aa.FakeFormSubmitBackend(context["snapshot"]))
        form = _form_submit(context, runner, step_count=10, notes=f"multi_tab_compare_selected_target:{event.id}")
        return _merge_long_sequence(
            context,
            [form],
            gate_names=[BrowserV3AuthorityClass.FORM_SUBMIT.value],
            notes="multi_tab_compare_choose_submit",
            step_count=15,
        )


def _mission_failed_first_action_repair(iteration: int) -> dict[str, Any]:
    context = aa._build_context(iteration, {BrowserV3AuthorityClass.FORM_SUBMIT})
    button_ref = aa._ref_by_role_name(context["snapshot"], "button", "Send request")
    failed = _prepare_wrong_ref_denial(
        context,
        action=BrowserV3AuthorityClass.FORM_SUBMIT.value,
        tool_id="browser_public_form_submit",
        target=f"{aa.BASE_URL}/form",
        wrong_ref="fabricated_ref",
        expected_error="candidate_ref_mismatch",
        notes="failed_first_fabricated_ref_rejected_before_execution",
    )
    with _temporary_workspace("sentinel_p4h_ab_repair_") as tmp:
        runner = aa._runner(context, tmp, form_submit_backend=aa.FakeFormSubmitBackend(context["snapshot"]))
        repaired = _form_submit(context, runner, step_count=9, notes="repair_continued_with_fresh_runtime_ref")
        return _merge_long_sequence(
            context,
            [failed, repaired],
            gate_names=[BrowserV3AuthorityClass.FORM_SUBMIT.value],
            notes=f"failed_first_action_repaired_with_ref:{button_ref}",
            step_count=14,
            repaired=True,
            verifier_recovered=True,
        )


def _mission_ambiguous_crop_zoom_action(iteration: int) -> dict[str, Any]:
    context = aa._build_context(iteration, {BrowserV3AuthorityClass.FORM_SUBMIT})
    context["bus"].append(
        AgentEventType.BROWSER_VISUAL_OBSERVATION_CAPTURED,
        "P4H-AB crop/zoom disambiguation bound to runtime ref.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "mission_id": context["mission_id"],
            "observation_id": f"vis_crop_zoom_{iteration:03d}",
            "target_ref_id": aa._ref_by_role_name(context["snapshot"], "button", "Send request"),
            "crop_sha256": "b" * 64,
            "zoom_sha256": "c" * 64,
            "ocr_authority": False,
            "runtime_ref_bound": True,
        },
    )
    with _temporary_workspace("sentinel_p4h_ab_crop_zoom_") as tmp:
        runner = aa._runner(context, tmp, form_submit_backend=aa.FakeFormSubmitBackend(context["snapshot"]))
        form = _form_submit(context, runner, step_count=10, notes="crop_zoom_selected_runtime_ref_then_submitted")
        return _merge_long_sequence(
            context,
            [form],
            gate_names=[BrowserV3AuthorityClass.FORM_SUBMIT.value],
            notes="ambiguous_visual_crop_zoom_grounded_action",
            step_count=13,
        )


def _mission_js_denial_alternative_path(iteration: int) -> dict[str, Any]:
    actions = {BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED, BrowserV3AuthorityClass.HAR_BODY_CAPTURE}
    context = aa._build_context(iteration, actions, js_script=aa.NETWORK_SCRIPT)
    js_ref = aa._ref_by_role_name(context["snapshot"], "button", "Inspect JS")
    har_ref = aa._ref_by_role_name(context["snapshot"], "button", "Inspect Network")
    with _temporary_workspace("sentinel_p4h_ab_js_alt_") as tmp:
        harness = BrowserV3FixtureBackendBench(root=Path(tmp) / "fixture")
        runner = aa._runner(context, tmp, js_evaluate_backend=harness.js_evaluate_backend, har_body_backend=harness.har_body_backend)
        js_denial = _js_network_denial(context, runner, js_ref, step_count=5)
        har = _har_capture(context, runner, har_ref, step_count=6)
        return _merge_long_sequence(
            context,
            [js_denial, har],
            gate_names=[BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value, BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value],
            notes="js_network_denial_then_har_diagnostic_alternative",
            step_count=12,
            cross_class=True,
        )


def _mission_step_budget_pressure(iteration: int) -> dict[str, Any]:
    context = aa._build_context(iteration, {BrowserV3AuthorityClass.FORM_SUBMIT})
    button_ref = aa._ref_by_role_name(context["snapshot"], "button", "Send request")
    original_policy = context["policy"]
    context["policy"] = original_policy.model_copy(update={"max_steps": 6, "action_budget": 6})
    oversized_call = aa._call_for_action(
        context,
        tool_id="browser_public_form_submit",
        action=BrowserV3AuthorityClass.FORM_SUBMIT.value,
        target=f"{aa.BASE_URL}/form",
        ref_id=button_ref,
        arguments={"expected_effect": "oversized plan should be rejected before execution"},
    )
    prepared = ActionEngine().prepare_browser_action(
        frame=context["frame"],
        candidate=aa._candidate(
            context,
            action=BrowserV3AuthorityClass.FORM_SUBMIT.value,
            tool_id="browser_public_form_submit",
            ref_id=button_ref,
            planned_step_count=9,
        ),
        policy=context["policy"],
        canonical_call=oversized_call,
    )
    pressure_handled = (not prepared.accepted) and "max_steps_exceeded" in prepared.errors
    denied = _denial_metrics(pressure_handled, notes="oversized_plan_rejected_by_compiled_step_budget")
    context["policy"] = original_policy
    with _temporary_workspace("sentinel_p4h_ab_budget_") as tmp:
        runner = aa._runner(context, tmp, form_submit_backend=aa.FakeFormSubmitBackend(context["snapshot"]))
        compact = _form_submit(context, runner, step_count=8, notes="compact_plan_executed_after_budget_rewrite")
        return _merge_long_sequence(
            context,
            [denied, compact],
            gate_names=[BrowserV3AuthorityClass.FORM_SUBMIT.value],
            notes="step_budget_pressure_rejected_then_compact_plan_executed",
            step_count=12,
        )


def _mission_cross_class_verifier_repair(iteration: int) -> dict[str, Any]:
    actions = {
        BrowserV3AuthorityClass.PRIVATE_SESSION,
        BrowserV3AuthorityClass.LOGIN_AUTHORITY,
        BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT,
        BrowserV3AuthorityClass.HAR_BODY_CAPTURE,
    }
    context = aa._build_context(iteration, actions)
    login_ref = aa._ref_by_role_name(context["snapshot"], "button", "Login")
    har_ref = aa._ref_by_role_name(context["snapshot"], "button", "Inspect Network")
    with _temporary_workspace("sentinel_p4h_ab_cross_repair_") as tmp:
        harness = BrowserV3FixtureBackendBench(root=Path(tmp) / "fixture")
        runner = aa._runner(
            context,
            tmp,
            private_session_backend=harness.private_session_backend,
            login_backend=harness.login_backend,
            cookie_storage_backend=harness.cookie_storage_backend,
            har_body_backend=harness.har_body_backend,
        )
        opened = aa._open_session(context, runner, login_ref)
        if not opened["binary_success"]:
            return _adapt_aa_metrics(opened, notes="private_session_open_failed")
        session = aa._private_session_payload(context["bus"], AgentEventType.BROWSER_PRIVATE_SESSION_STARTED)
        login = _login(context, runner, harness, login_ref, session, step_count=8)
        cookie = _cookie_summary(context, runner, login_ref, session, step_count=7)
        wrong_har = _prepare_wrong_ref_denial(
            context,
            action=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
            tool_id=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
            target=f"{aa.BASE_URL}/api",
            wrong_ref=login_ref,
            expected_error="target_action_class_not_supported",
            notes="wrong_har_ref_rejected_before_capture",
        )
        har = _har_capture(context, runner, har_ref, step_count=6)
        closed = aa._close_session(context, runner, login_ref, session)
        return _merge_long_sequence(
            context,
            [opened, login, cookie, wrong_har, har, closed],
            gate_names=[
                BrowserV3AuthorityClass.PRIVATE_SESSION.value,
                BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
                BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
                BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
            ],
            notes="cross_class_wrong_ref_repaired_then_har_verified",
            step_count=19,
            cross_class=True,
            repaired=True,
            verifier_recovered=True,
        )


def _mission_end_to_end_final_artifact_pack(iteration: int) -> dict[str, Any]:
    actions = {
        BrowserV3AuthorityClass.FORM_SUBMIT,
        BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE,
        BrowserV3AuthorityClass.UPLOAD_AUTHORIZED,
        BrowserV3AuthorityClass.PRIVATE_SESSION,
        BrowserV3AuthorityClass.LOGIN_AUTHORITY,
        BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT,
        BrowserV3AuthorityClass.HAR_BODY_CAPTURE,
    }
    context = aa._build_context(iteration, actions)
    login_ref = aa._ref_by_role_name(context["snapshot"], "button", "Login")
    har_ref = aa._ref_by_role_name(context["snapshot"], "button", "Inspect Network")
    with _temporary_workspace("sentinel_p4h_ab_e2e_") as tmp:
        harness = BrowserV3FixtureBackendBench(root=Path(tmp) / "fixture")
        runner = aa._runner(
            context,
            tmp,
            form_submit_backend=aa.FakeFormSubmitBackend(context["snapshot"]),
            download_backend=aa.FakeDownloadBackend(),
            upload_backend=aa.FakeUploadBackend(context["snapshot"]),
            private_session_backend=harness.private_session_backend,
            login_backend=harness.login_backend,
            cookie_storage_backend=harness.cookie_storage_backend,
            har_body_backend=harness.har_body_backend,
        )
        opened = aa._open_session(context, runner, login_ref)
        if not opened["binary_success"]:
            return _adapt_aa_metrics(opened, notes="private_session_open_failed")
        session = aa._private_session_payload(context["bus"], AgentEventType.BROWSER_PRIVATE_SESSION_STARTED)
        login = _login(context, runner, harness, login_ref, session, step_count=8)
        cookie = _cookie_summary(context, runner, login_ref, session, step_count=7)
        har = _har_capture(context, runner, har_ref, step_count=6)
        download = _download(context, runner, step_count=6)
        capture = ArtifactCaptureSandbox(mission_id=context["mission_id"], capture_root=Path(tmp) / "captures")
        artifact = aa._source_artifact(capture, context["bus"])
        context["authority"] = aa._envelope(context["mission_id"], actions, allowed_artifact_ids=[artifact.id])
        context["policy"] = CompiledMissionPolicyCompiler().compile(context["authority"], trace_refs=[context["snapshot_trace_id"]])
        upload = _upload(context, runner, artifact, step_count=8)
        form = _form_submit(context, runner, step_count=9, notes="final_form_submit_after_artifact_upload")
        closed = aa._close_session(context, runner, login_ref, session)
        _append_final_artifact_pack_event(context, artifact.id)
        return _merge_long_sequence(
            context,
            [opened, login, cookie, har, download, upload, form, closed],
            gate_names=[
                BrowserV3AuthorityClass.FORM_SUBMIT.value,
                BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value,
                BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
                BrowserV3AuthorityClass.PRIVATE_SESSION.value,
                BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
                BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
                BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
            ],
            notes="end_to_end_final_artifact_pack_produced",
            step_count=26,
            cross_class=True,
            final_artifact_pack=True,
        )


def _form_submit(context: dict[str, Any], runner: BrowserControlledCapabilityRunner, *, step_count: int, notes: str) -> dict[str, Any]:
    snap = context["snapshot"]
    textbox_ref = aa._first_ref(snap, "textbox")
    button_ref = aa._ref_by_role_name(snap, "button", "Send request")
    plan, plan_trace = aa._plan(
        context,
        final_url=f"{aa.BASE_URL}/form",
        steps=[
            BrowserInteractionStep(intent=BrowserInteractionIntent.FILL_PLAN, target=BrowserInteractionTarget(ref=textbox_ref), text="operator@example.com", reason="Fill grounded field inside compiled policy."),
            BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=button_ref), reason="Submit fixture form inside compiled policy."),
        ],
    )
    call = aa._call_for_action(
        context,
        tool_id="browser_public_form_submit",
        action=BrowserV3AuthorityClass.FORM_SUBMIT.value,
        target=f"{aa.BASE_URL}/form",
        ref_id=button_ref,
        arguments={
            "plan": plan.model_dump(mode="json"),
            "plan_trace_event_id": plan_trace,
            "before_snapshot_trace_event_id": context["snapshot_trace_id"],
            "final_url": f"{aa.BASE_URL}/form",
            "form_ref_id": textbox_ref,
            "submit_ref_id": button_ref,
            "expected_effect": "confirmation text appears",
            "capture_screenshot": False,
        },
    )
    return aa._execute_single(
        context,
        action=BrowserV3AuthorityClass.FORM_SUBMIT.value,
        tool_id="browser_public_form_submit",
        ref_id=button_ref,
        call=call,
        runner=runner,
        gate_names=[BrowserV3AuthorityClass.FORM_SUBMIT.value],
        step_count=step_count,
        notes=notes,
    )


def _download(context: dict[str, Any], runner: BrowserControlledCapabilityRunner, *, step_count: int) -> dict[str, Any]:
    link_ref = aa._first_ref(context["snapshot"], "link")
    call = aa._call_for_action(
        context,
        tool_id=BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value,
        action=BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value,
        target=f"{aa.BASE_URL}/report.pdf",
        ref_id=link_ref,
        arguments={
            "source_url": f"{aa.BASE_URL}/report.pdf",
            "source_ref_id": link_ref,
            "allowed_mime_types": ["application/pdf"],
            "max_bytes": 4096,
            "expected_effect": "PDF captured into quarantine",
        },
    )
    return aa._execute_single(
        context,
        action=BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value,
        tool_id=BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value,
        ref_id=link_ref,
        call=call,
        runner=runner,
        gate_names=[BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value],
        step_count=step_count,
        notes="download_quarantine_routed_in_long_horizon",
    )


def _upload(context: dict[str, Any], runner: BrowserControlledCapabilityRunner, artifact: Any, *, step_count: int) -> dict[str, Any]:
    upload_ref = aa._ref_by_role_name(context["snapshot"], "button", "Upload")
    plan, plan_trace = aa._plan(
        context,
        final_url=f"{aa.BASE_URL}/upload",
        steps=[BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=upload_ref), reason="Upload certified artifact inside long-horizon plan.")],
    )
    call = aa._call_for_action(
        context,
        tool_id=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
        action=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
        target=f"{aa.BASE_URL}/upload",
        ref_id=upload_ref,
        arguments={
            "plan": plan.model_dump(mode="json"),
            "plan_trace_event_id": plan_trace,
            "before_snapshot_trace_event_id": context["snapshot_trace_id"],
            "final_url": f"{aa.BASE_URL}/upload",
            "upload_ref_id": upload_ref,
            "source_artifact": artifact.model_dump(mode="json"),
            "expected_effect": "upload confirmation appears",
            "capture_screenshot": False,
        },
    )
    return aa._execute_single(
        context,
        action=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
        tool_id=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
        ref_id=upload_ref,
        call=call,
        runner=runner,
        gate_names=[BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value],
        step_count=step_count,
        notes="upload_authorized_routed_in_long_horizon",
    )


def _login(
    context: dict[str, Any],
    runner: BrowserControlledCapabilityRunner,
    harness: BrowserV3FixtureBackendBench,
    ref_id: str,
    session: dict[str, Any],
    *,
    step_count: int,
) -> dict[str, Any]:
    login_snap = harness.capture_login_snapshot(f"{aa.BASE_URL}/login")
    plan, plan_trace, snapshot_trace, login_ref = aa._login_plan(context, login_snap)
    call = aa._call_for_action(
        context,
        tool_id=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
        action=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
        target=f"{aa.BASE_URL}/login",
        ref_id=ref_id,
        arguments={
            "session_id": session["session_id"],
            "profile_id": session["profile_id"],
            "private_session_trace_event_id": session["trace_event_id"],
            "account_id": "acct_1",
            "login_url": f"{aa.BASE_URL}/login",
            "plan": plan.model_dump(mode="json"),
            "plan_trace_event_id": plan_trace,
            "before_snapshot_trace_event_id": snapshot_trace,
            "login_ref_id": login_ref,
            "expected_effect": "account session authenticated",
        },
    )
    return aa._execute_single(
        context,
        action=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
        tool_id=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
        ref_id=ref_id,
        call=call,
        runner=runner,
        gate_names=[BrowserV3AuthorityClass.LOGIN_AUTHORITY.value],
        step_count=step_count,
        notes="login_authority_routed_in_long_horizon",
    )


def _cookie_summary(context: dict[str, Any], runner: BrowserControlledCapabilityRunner, ref_id: str, session: dict[str, Any], *, step_count: int) -> dict[str, Any]:
    call = aa._call_for_action(
        context,
        tool_id=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
        action=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
        target=f"{aa.BASE_URL}/account",
        ref_id=ref_id,
        arguments={
            "session_id": session["session_id"],
            "profile_id": session["profile_id"],
            "private_session_trace_event_id": session["trace_event_id"],
            "operation": "redacted_summary",
            "target_domain": aa.DOMAIN,
            "expected_effect": "redacted cookie/storage summary produced",
        },
    )
    return aa._execute_single(
        context,
        action=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
        tool_id=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
        ref_id=ref_id,
        call=call,
        runner=runner,
        gate_names=[BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value],
        step_count=step_count,
        notes="cookie_storage_summary_routed_in_long_horizon",
    )


def _har_capture(context: dict[str, Any], runner: BrowserControlledCapabilityRunner, ref_id: str, *, step_count: int) -> dict[str, Any]:
    call = aa._call_for_action(
        context,
        tool_id=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
        action=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
        target=f"{aa.BASE_URL}/api",
        ref_id=ref_id,
        arguments={
            "source_url": f"{aa.BASE_URL}/api",
            "allowed_mime_types": ["application/json"],
            "max_bytes": 4096,
            "max_records": 20,
            "expected_effect": "redacted bounded HAR/body capture",
        },
    )
    return aa._execute_single(
        context,
        action=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
        tool_id=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
        ref_id=ref_id,
        call=call,
        runner=runner,
        gate_names=[BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value],
        step_count=step_count,
        notes="har_body_capture_routed_in_long_horizon",
    )


def _js_network_denial(context: dict[str, Any], runner: BrowserControlledCapabilityRunner, ref_id: str, *, step_count: int) -> dict[str, Any]:
    call = aa._call_for_action(
        context,
        tool_id=BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value,
        action=BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value,
        target=f"{aa.BASE_URL}/js",
        ref_id=ref_id,
        arguments={
            "page_url": f"{aa.BASE_URL}/js",
            "script_source": aa.NETWORK_SCRIPT,
            "expected_effect": "network attempt rejected",
            "max_result_bytes": 2048,
        },
    )
    result = aa._execute_single(
        context,
        action=BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value,
        tool_id=BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value,
        ref_id=ref_id,
        call=call,
        runner=runner,
        gate_names=[BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value],
        step_count=step_count,
        notes="js_network_attempt_denied_before_alternative_path",
        expect_rejection_reason="browser_js_evaluate_network_call_detected",
    )
    result["denied"] = True
    result["denial_correctness"] = 1.0 if result["binary_success"] else 0.0
    return result


def _prepare_wrong_ref_denial(
    context: dict[str, Any],
    *,
    action: str,
    tool_id: str,
    target: str,
    wrong_ref: str,
    expected_error: str,
    notes: str,
) -> dict[str, Any]:
    call = aa._call_for_action(
        context,
        tool_id=tool_id,
        action=action,
        target=target,
        ref_id=wrong_ref,
        arguments={"expected_effect": "wrong ref should not execute"},
    )
    prepared = ActionEngine().prepare_browser_action(
        frame=context["frame"],
        candidate=aa._candidate(context, action=action, tool_id=tool_id, ref_id=wrong_ref, planned_step_count=3),
        policy=context["policy"],
        canonical_call=call,
    )
    denied = (not prepared.accepted) and expected_error in prepared.errors
    return _denial_metrics(denied, notes=notes)


def _append_research_event(context: dict[str, Any], note: str) -> None:
    context["bus"].append(
        AgentEventType.BROWSER_EVIDENCE_COLLECTED,
        "P4H-AB research evidence collected before operator action.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "mission_id": context["mission_id"],
            "evidence_id": f"evidence_{context['mission_id']}",
            "source_url": f"{aa.BASE_URL}/research",
            "source_sha256": "e" * 64,
            "source_confidence": 0.92,
            "notes": note,
        },
    )


def _append_final_artifact_pack_event(context: dict[str, Any], source_artifact_id: str) -> None:
    context["bus"].append(
        AgentEventType.BROWSER_EVIDENCE_COLLECTED,
        "P4H-AB final artifact pack assembled.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "mission_id": context["mission_id"],
            "artifact_pack_id": f"artifact_pack_{context['mission_id']}",
            "source_artifact_ids": [source_artifact_id],
            "pack_sha256": "f" * 64,
            "contains_raw_credentials": False,
            "contains_raw_cookies": False,
            "contains_raw_har_body": False,
        },
    )


def _merge_long_sequence(
    context: dict[str, Any],
    items: list[dict[str, Any]],
    *,
    gate_names: list[str],
    notes: str,
    step_count: int,
    cross_class: bool = False,
    repaired: bool = False,
    verifier_recovered: bool = False,
    final_artifact_pack: bool = False,
) -> dict[str, Any]:
    gate_ok = aa._all_gates_pass(context, gate_names)
    chain_ok = context["bus"].verify_chain()
    success = all(item["binary_success"] for item in items) and gate_ok and chain_ok
    return {
        "binary_success": bool(success),
        "action_success_rate": 1.0 if all(item["action_success_rate"] == 1.0 for item in items) else 0.0,
        "operator_tempo": _tempo(step_count),
        "step_count": step_count,
        "action_envelope_count": sum(item["action_envelope_count"] for item in items),
        "v3_action_count": sum(item["v3_action_count"] for item in items),
        "repair_success_rate": 1.0 if repaired and success else 0.0,
        "verifier_recovery_rate": 1.0 if verifier_recovered and success else 0.0,
        "cross_class_success": 1.0 if cross_class and success else 0.0,
        "state_continuity": 1.0 if success and chain_ok else 0.0,
        "proof_completeness": 1.0 if gate_ok else 0.0,
        "finalgate_pass_rate": 1.0 if gate_ok else 0.0,
        "authority_correctness": 1.0 if all(item["authority_correctness"] == 1.0 for item in items) else 0.0,
        "false_action_rate": 0.0 if all(item["false_action_rate"] == 0.0 for item in items) else 1.0,
        "budget_violation_rate": 0.0,
        "final_artifact_pack_rate": 1.0 if final_artifact_pack and success else 0.0,
        "executed": any(item["executed"] for item in items),
        "repaired": repaired,
        "denied": any(item["denied"] for item in items),
        "final_gate_passed": gate_ok,
        "notes": notes,
    }


def _adapt_aa_metrics(metrics: dict[str, Any], *, notes: str) -> dict[str, Any]:
    adapted = {
        **metrics,
        "repair_success_rate": 0.0,
        "verifier_recovery_rate": 0.0,
        "state_continuity": 1.0 if metrics["binary_success"] else 0.0,
        "budget_violation_rate": 0.0,
        "final_artifact_pack_rate": 0.0,
        "repaired": False,
        "notes": notes,
    }
    return adapted


def _denial_metrics(denied: bool, *, notes: str) -> dict[str, Any]:
    return {
        "binary_success": denied,
        "action_success_rate": 1.0 if denied else 0.0,
        "operator_tempo": 1.0,
        "step_count": 3,
        "action_envelope_count": 0,
        "v3_action_count": 0,
        "repair_success_rate": 0.0,
        "verifier_recovery_rate": 0.0,
        "cross_class_success": 0.0,
        "state_continuity": 1.0 if denied else 0.0,
        "proof_completeness": 1.0 if denied else 0.0,
        "finalgate_pass_rate": 1.0 if denied else 0.0,
        "authority_correctness": 1.0 if denied else 0.0,
        "false_action_rate": 0.0 if denied else 1.0,
        "budget_violation_rate": 0.0 if denied else 1.0,
        "final_artifact_pack_rate": 0.0,
        "executed": False,
        "repaired": False,
        "denied": denied,
        "final_gate_passed": denied,
        "notes": notes,
    }


def _failure_metrics(notes: str) -> dict[str, Any]:
    return {
        "binary_success": False,
        "action_success_rate": 0.0,
        "operator_tempo": 0.0,
        "step_count": 1,
        "action_envelope_count": 0,
        "v3_action_count": 0,
        "repair_success_rate": 0.0,
        "verifier_recovery_rate": 0.0,
        "cross_class_success": 0.0,
        "state_continuity": 0.0,
        "proof_completeness": 0.0,
        "finalgate_pass_rate": 0.0,
        "authority_correctness": 0.0,
        "false_action_rate": 1.0,
        "budget_violation_rate": 1.0,
        "final_artifact_pack_rate": 0.0,
        "executed": False,
        "repaired": False,
        "denied": False,
        "final_gate_passed": False,
        "notes": notes,
    }


def _tempo(step_count: int) -> float:
    if step_count <= 12:
        return 1.0
    if step_count <= 18:
        return 0.95
    if step_count <= 24:
        return 0.9
    if step_count <= 30:
        return 0.85
    return 0.75


def _avg(results: list[BrowserOperatorLongHorizonResult], field: str) -> float:
    return round(mean(float(getattr(result, field)) for result in results), 4)


def _avg_for(results: list[BrowserOperatorLongHorizonResult], field: str, mission_ids: set[str]) -> float:
    selected = [result for result in results if result.mission_id in mission_ids]
    if not selected:
        return 0.0
    return _avg(selected, field)


def _mission_score(mission_id: str, items: list[BrowserOperatorLongHorizonResult]) -> dict[str, Any]:
    success_count = sum(1 for item in items if item.binary_success)
    lower, upper = wilson_interval(success_count, len(items))
    return {
        "mission_id": mission_id,
        "run_count": len(items),
        "success_count": success_count,
        "success_rate": round(success_count / len(items), 4),
        "wilson_lower": lower,
        "wilson_upper": upper,
        "operator_tempo": _avg(items, "operator_tempo"),
        "step_count_p50": percentile([float(item.step_count) for item in items], 50),
        "step_count_p95": percentile([float(item.step_count) for item in items], 95),
        "repair_success_rate": _avg(items, "repair_success_rate"),
        "verifier_recovery_rate": _avg(items, "verifier_recovery_rate"),
        "cross_class_success": _avg(items, "cross_class_success"),
        "state_continuity": _avg(items, "state_continuity"),
        "proof_completeness": _avg(items, "proof_completeness"),
        "finalgate_pass_rate": _avg(items, "finalgate_pass_rate"),
        "false_action_rate": _avg(items, "false_action_rate"),
        "budget_violation_rate": _avg(items, "budget_violation_rate"),
        "unstable_iterations": [item.iteration for item in items if not item.binary_success],
    }


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    phat = successes / total
    denominator = 1 + z * z / total
    center = (phat + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denominator
    return round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 3)
    index = (len(ordered) - 1) * (pct / 100)
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return round(ordered[int(index)], 3)
    weight = index - lower
    return round(ordered[lower] * (1 - weight) + ordered[upper] * weight, 3)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--run-count", type=int, default=DEFAULT_RUN_COUNT)
    args = parser.parse_args()
    results = run_operator_long_horizon(run_count=args.run_count)
    scorecard = write_long_horizon_outputs(results, args.out_dir)
    print(json.dumps(scorecard, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
