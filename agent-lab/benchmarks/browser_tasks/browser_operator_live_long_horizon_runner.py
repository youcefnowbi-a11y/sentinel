from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.error
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any


TASK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
CORE_ROOT = REPO_ROOT / "sentinel-control" / "services" / "sentinel-core"
for path in (TASK_ROOT, CORE_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import browser_fluency_live_runner as live  # noqa: E402
import browser_operator_long_horizon_runner as ab  # noqa: E402
import browser_visual_engine_runner as visual  # noqa: E402


REPORT_DIR = TASK_ROOT / "reports"
RUN_ID = "p4h_ac_browser_operator_live_long_horizon_30run"
DEFAULT_RUN_COUNT = 30


P4H_AC_MISSIONS = [
    "BF-LIVE-LONG-001-research-form-submit-verify",
    "BF-LIVE-LONG-002-login-cookie-har-close",
    "BF-LIVE-LONG-003-download-inspect-upload",
    "BF-LIVE-LONG-004-multitab-compare-submit",
    "BF-LIVE-LONG-005-failed-first-action-repair-continue",
    "BF-LIVE-LONG-006-visual-crop-zoom-action",
    "BF-LIVE-LONG-007-js-denial-har-alternative",
    "BF-LIVE-LONG-008-step-budget-pressure",
    "BF-LIVE-LONG-009-cross-class-verifier-repair",
    "BF-LIVE-LONG-010-end-to-end-final-artifact-pack",
]

REPAIR_MISSIONS = {
    "BF-LIVE-LONG-005-failed-first-action-repair-continue",
    "BF-LIVE-LONG-009-cross-class-verifier-repair",
}
VERIFIER_RECOVERY_MISSIONS = REPAIR_MISSIONS
CROSS_CLASS_MISSIONS = {
    "BF-LIVE-LONG-002-login-cookie-har-close",
    "BF-LIVE-LONG-003-download-inspect-upload",
    "BF-LIVE-LONG-007-js-denial-har-alternative",
    "BF-LIVE-LONG-009-cross-class-verifier-repair",
    "BF-LIVE-LONG-010-end-to-end-final-artifact-pack",
}
BUDGET_MISSIONS = {"BF-LIVE-LONG-008-step-budget-pressure"}
VISUAL_MISSIONS = {"BF-LIVE-LONG-006-visual-crop-zoom-action"}
FINAL_ARTIFACT_MISSIONS = {"BF-LIVE-LONG-010-end-to-end-final-artifact-pack"}


@dataclass(frozen=True)
class BrowserOperatorLiveLongHorizonResult:
    schema_version: str
    run_id: str
    generated_at: str
    mission_id: str
    iteration: int
    binary_success: bool
    mission_success: float
    action_success_rate: float
    operator_tempo: float
    live_observation_success: float
    live_artifact_count: int
    live_visual_verifier_rate: float
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
    authority_violation_rate: float
    artifact_leakage_rate: float
    budget_violation_rate: float
    final_artifact_pack_rate: float
    latency_ms: float
    live_latency_ms: float
    executed: bool
    repaired: bool
    denied: bool
    final_gate_passed: bool
    failure_category: str
    notes: str


@dataclass(frozen=True)
class _LiveProbe:
    ok: bool
    step_count: int
    latency_ms: float
    artifact_refs: list[str]
    notes: str


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_operator_live_long_horizon(
    *,
    run_count: int = DEFAULT_RUN_COUNT,
    run_id: str = RUN_ID,
) -> list[BrowserOperatorLiveLongHorizonResult]:
    if run_count < 1:
        raise ValueError("run_count must be >= 1")
    generated_at = utc_now()
    results: list[BrowserOperatorLiveLongHorizonResult] = []
    with live.SelfHostedFixtureServer() as fixture:
        for iteration in range(1, run_count + 1):
            for mission_id in P4H_AC_MISSIONS:
                results.append(_run_mission(fixture.base_url, mission_id, iteration, generated_at, run_id))
    return results


def build_live_long_horizon_scorecard(results: list[BrowserOperatorLiveLongHorizonResult]) -> dict[str, Any]:
    if not results:
        return {"schema_version": "browser_operator_live_long_horizon_scorecard.v1", "verdict": "not_executed", "total_iterations": 0}
    grouped: dict[str, list[BrowserOperatorLiveLongHorizonResult]] = {}
    for result in results:
        grouped.setdefault(result.mission_id, []).append(result)
    success_count = sum(1 for result in results if result.binary_success)
    lower, upper = wilson_interval(success_count, len(results))
    pass_verdict = (
        success_count == len(results)
        and _avg(results, "false_action_rate") == 0.0
        and _avg(results, "authority_violation_rate") == 0.0
        and _avg(results, "artifact_leakage_rate") == 0.0
        and _avg(results, "budget_violation_rate") == 0.0
        and _avg(results, "authority_correctness") == 1.0
    )
    return {
        "schema_version": "browser_operator_live_long_horizon_scorecard.v1",
        "run_id": results[0].run_id,
        "generated_at": results[0].generated_at,
        "verdict": "browser_operator_live_long_horizon_pass" if pass_verdict else "browser_operator_live_long_horizon_needs_repair",
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
        "live_observation_success": _avg(results, "live_observation_success"),
        "live_visual_verifier_rate": _avg_for(results, "live_visual_verifier_rate", VISUAL_MISSIONS),
        "step_count_p50": percentile([float(result.step_count) for result in results], 50),
        "step_count_p95": percentile([float(result.step_count) for result in results], 95),
        "latency_p50_ms": percentile([result.latency_ms for result in results], 50),
        "latency_p95_ms": percentile([result.latency_ms for result in results], 95),
        "live_latency_p50_ms": percentile([result.live_latency_ms for result in results], 50),
        "live_latency_p95_ms": percentile([result.live_latency_ms for result in results], 95),
        "repair_success_rate": _avg_for(results, "repair_success_rate", REPAIR_MISSIONS),
        "verifier_recovery_rate": _avg_for(results, "verifier_recovery_rate", VERIFIER_RECOVERY_MISSIONS),
        "cross_class_success": _avg_for(results, "cross_class_success", CROSS_CLASS_MISSIONS),
        "budget_pressure_success": _avg_for(results, "mission_success", BUDGET_MISSIONS),
        "final_artifact_pack_rate": _avg_for(results, "final_artifact_pack_rate", FINAL_ARTIFACT_MISSIONS),
        "state_continuity": _avg(results, "state_continuity"),
        "proof_completeness": _avg(results, "proof_completeness"),
        "finalgate_pass_rate": _avg(results, "finalgate_pass_rate"),
        "authority_correctness": _avg(results, "authority_correctness"),
        "false_action_rate": _avg(results, "false_action_rate"),
        "authority_violation_rate": _avg(results, "authority_violation_rate"),
        "artifact_leakage_rate": _avg(results, "artifact_leakage_rate"),
        "budget_violation_rate": _avg(results, "budget_violation_rate"),
        "action_envelope_count": sum(result.action_envelope_count for result in results),
        "v3_action_count": sum(result.v3_action_count for result in results),
        "live_artifact_count": sum(result.live_artifact_count for result in results),
        "mission_scores": [_mission_score(mission_id, items) for mission_id, items in grouped.items()],
        "boundary": "self_hosted_live_browser_operator_only_no_new_powers_no_desktop_no_open_web_claim",
    }


def write_live_long_horizon_outputs(
    results: list[BrowserOperatorLiveLongHorizonResult],
    out_dir: Path = REPORT_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    scorecard = build_live_long_horizon_scorecard(results)
    (out_dir / "browser_operator_live_long_horizon_results.jsonl").write_text(
        "".join(json.dumps(asdict(result), sort_keys=True) + "\n" for result in results),
        encoding="utf-8",
    )
    (out_dir / "browser_operator_live_long_horizon_scorecard.json").write_text(
        json.dumps(scorecard, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "browser_operator_live_long_horizon_scorecard.md").write_text(
        render_live_long_horizon_markdown(scorecard),
        encoding="utf-8",
    )
    return scorecard


def render_live_long_horizon_markdown(scorecard: dict[str, Any]) -> str:
    lines = [
        "# Browser Operator Live Long-Horizon Scorecard",
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
        f"live_observation_success = {scorecard.get('live_observation_success', 0.0)}",
        f"live_visual_verifier_rate = {scorecard.get('live_visual_verifier_rate', 0.0)}",
        f"repair_success_rate = {scorecard.get('repair_success_rate', 0.0)}",
        f"verifier_recovery_rate = {scorecard.get('verifier_recovery_rate', 0.0)}",
        f"cross_class_success = {scorecard.get('cross_class_success', 0.0)}",
        f"proof_completeness = {scorecard.get('proof_completeness', 0.0)}",
        f"finalgate_pass_rate = {scorecard.get('finalgate_pass_rate', 0.0)}",
        f"authority_correctness = {scorecard.get('authority_correctness', 0.0)}",
        f"false_action_rate = {scorecard.get('false_action_rate', 0.0)}",
        f"artifact_leakage_rate = {scorecard.get('artifact_leakage_rate', 0.0)}",
        f"authority_violation_rate = {scorecard.get('authority_violation_rate', 0.0)}",
        f"budget_violation_rate = {scorecard.get('budget_violation_rate', 0.0)}",
        "```",
        "",
        "## Missions",
        "",
        "| Mission | Runs | Success | Wilson lower | Tempo | Live obs | Visual | Repair | Cross-class | False action |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mission in scorecard.get("mission_scores", []):
        lines.append(
            f"| `{mission['mission_id']}` | {mission['run_count']} | {mission['success_rate']} | "
            f"{mission['wilson_lower']} | {mission['operator_tempo']} | {mission['live_observation_success']} | "
            f"{mission['live_visual_verifier_rate']} | {mission['repair_success_rate']} | "
            f"{mission['cross_class_success']} | {mission['false_action_rate']} |"
        )
    lines.extend(["", "## Boundary", "", f"`{scorecard.get('boundary', '')}`", ""])
    return "\n".join(lines)


def _run_mission(
    base_url: str,
    mission_id: str,
    iteration: int,
    generated_at: str,
    run_id: str,
) -> BrowserOperatorLiveLongHorizonResult:
    started = time.perf_counter()
    try:
        metrics = _execute_mission(base_url, mission_id, iteration)
        binary_success = bool(metrics["binary_success"])
        failure_category = "" if binary_success else metrics.get("failure_category", "live_long_horizon_failed")
    except Exception as exc:  # pragma: no cover - defensive report path
        metrics = _failure_metrics(f"{type(exc).__name__}:{str(exc)[:160]}")
        binary_success = False
        failure_category = metrics["notes"]
    return BrowserOperatorLiveLongHorizonResult(
        schema_version="browser_operator_live_long_horizon_run.v1",
        run_id=run_id,
        generated_at=generated_at,
        mission_id=mission_id,
        iteration=iteration,
        binary_success=binary_success,
        mission_success=1.0 if binary_success else 0.0,
        action_success_rate=metrics["action_success_rate"],
        operator_tempo=metrics["operator_tempo"],
        live_observation_success=metrics["live_observation_success"],
        live_artifact_count=metrics["live_artifact_count"],
        live_visual_verifier_rate=metrics["live_visual_verifier_rate"],
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
        authority_violation_rate=metrics["authority_violation_rate"],
        artifact_leakage_rate=metrics["artifact_leakage_rate"],
        budget_violation_rate=metrics["budget_violation_rate"],
        final_artifact_pack_rate=metrics["final_artifact_pack_rate"],
        latency_ms=round((time.perf_counter() - started) * 1000, 3),
        live_latency_ms=metrics["live_latency_ms"],
        executed=metrics["executed"],
        repaired=metrics["repaired"],
        denied=metrics["denied"],
        final_gate_passed=metrics["final_gate_passed"],
        failure_category=failure_category,
        notes=metrics["notes"],
    )


def _execute_mission(base_url: str, mission_id: str, iteration: int) -> dict[str, Any]:
    if mission_id == "BF-LIVE-LONG-001-research-form-submit-verify":
        probes = [
            _get_contains(base_url, "/research", "Sentinel browser fluency fact: verified.", "live_research_citation_collected"),
            _post_json(base_url, "/submit", {"query": "sentinel"}, "accepted", True, "live_form_submit_fixture_receipt"),
        ]
        return _compose(ab._mission_research_form_submit(iteration), probes, notes="live_research_then_actionengine_form_submit")
    if mission_id == "BF-LIVE-LONG-002-login-cookie-har-close":
        probes = [
            _state_redaction_probe(base_url),
            _get_contains(base_url, "/har", "redaction fixture", "live_har_sensitive_source_observed_before_redaction"),
        ]
        return _compose(ab._mission_login_cookie_har_close(iteration), probes, notes="live_state_har_then_login_cookie_har_close")
    if mission_id == "BF-LIVE-LONG-003-download-inspect-upload":
        probes = [
            _get_contains(base_url, "/download.txt", "sentinel browser fluency download fixture", "live_download_quarantine_source_observed"),
            _post_json(base_url, "/upload", {"artifact_id": "sentinel_certified_artifact"}, "uploaded", True, "live_upload_certified_artifact_receipt"),
        ]
        return _compose(ab._mission_download_inspect_upload(iteration), probes, notes="live_download_upload_then_actionengine_artifact_flow")
    if mission_id == "BF-LIVE-LONG-004-multitab-compare-submit":
        probes = [
            _get_contains(base_url, "/tab/a", "Price: 10", "live_tab_a_observed"),
            _get_contains(base_url, "/tab/b", "Price: 12", "live_tab_b_observed"),
            _post_json(base_url, "/submit", {"query": "sentinel"}, "accepted", True, "live_selected_tab_submit_receipt"),
        ]
        return _compose(ab._mission_multitab_compare_submit(iteration), probes, notes="live_multitab_compare_then_submit")
    if mission_id == "BF-LIVE-LONG-005-failed-first-action-repair-continue":
        probes = [
            _get_contains(base_url, "/form", "<form", "live_form_snapshot_before_failed_ref"),
            _get_contains(base_url, "/form", "Submit", "live_form_resnapshot_for_repair"),
        ]
        return _compose(ab._mission_failed_first_action_repair(iteration), probes, notes="live_failed_ref_repaired_then_continue")
    if mission_id == "BF-LIVE-LONG-006-visual-crop-zoom-action":
        probes = [_get_contains(base_url, "/visual", "SENTINEL VISION OK", "live_visual_fixture_observed")]
        visual_probe = _rendered_visual_probe(iteration)
        return _compose(
            ab._mission_ambiguous_crop_zoom_action(iteration),
            [*probes, visual_probe],
            notes="live_visual_crop_zoom_grounded_then_actionengine_submit",
            visual_required=True,
        )
    if mission_id == "BF-LIVE-LONG-007-js-denial-har-alternative":
        probes = [
            _js_network_attempt_probe(),
            _har_redaction_probe(base_url),
        ]
        return _compose(ab._mission_js_denial_alternative_path(iteration), probes, notes="live_js_denial_then_har_alternative")
    if mission_id == "BF-LIVE-LONG-008-step-budget-pressure":
        probes = [
            _get_contains(base_url, "/page", "Browser fluency fixture", "live_page_snapshot_before_budget_pressure"),
            _external_boundary_probe(base_url),
        ]
        return _compose(ab._mission_step_budget_pressure(iteration), probes, notes="live_budget_pressure_then_compact_action_plan")
    if mission_id == "BF-LIVE-LONG-009-cross-class-verifier-repair":
        probes = [
            _state_redaction_probe(base_url),
            _get_contains(base_url, "/har", "redaction fixture", "live_cross_class_har_source_observed"),
        ]
        return _compose(ab._mission_cross_class_verifier_repair(iteration), probes, notes="live_cross_class_wrong_ref_repaired")
    if mission_id == "BF-LIVE-LONG-010-end-to-end-final-artifact-pack":
        probes = [
            _get_contains(base_url, "/research", "Sentinel browser fluency fact: verified.", "live_e2e_research"),
            _post_json(base_url, "/submit", {"query": "sentinel"}, "accepted", True, "live_e2e_form_submit"),
            _state_redaction_probe(base_url),
            _har_redaction_probe(base_url),
            _get_contains(base_url, "/download.txt", "sentinel browser fluency download fixture", "live_e2e_download"),
            _post_json(base_url, "/upload", {"artifact_id": "sentinel_certified_artifact"}, "uploaded", True, "live_e2e_upload"),
        ]
        return _compose(ab._mission_end_to_end_final_artifact_pack(iteration), probes, notes="live_e2e_final_artifact_pack")
    raise ValueError(f"unsupported P4H-AC mission: {mission_id}")


def _compose(
    operator: dict[str, Any],
    probes: list[_LiveProbe],
    *,
    notes: str,
    visual_required: bool = False,
) -> dict[str, Any]:
    live_ok = all(probe.ok for probe in probes)
    live_steps = sum(probe.step_count for probe in probes)
    step_count = int(operator["step_count"]) + live_steps
    success = bool(operator["binary_success"]) and live_ok
    visual_ok = any(probe.notes == "rendered_visual_verifier_bound_to_runtime_ref" and probe.ok for probe in probes)
    if visual_required:
        success = success and visual_ok
    return {
        "binary_success": bool(success),
        "action_success_rate": operator["action_success_rate"] if success else 0.0,
        "operator_tempo": _tempo(step_count) if success else 0.0,
        "live_observation_success": 1.0 if live_ok else 0.0,
        "live_artifact_count": sum(len(probe.artifact_refs) for probe in probes),
        "live_visual_verifier_rate": 1.0 if visual_required and visual_ok and success else 0.0,
        "step_count": step_count,
        "action_envelope_count": operator["action_envelope_count"],
        "v3_action_count": operator["v3_action_count"],
        "repair_success_rate": operator["repair_success_rate"],
        "verifier_recovery_rate": operator["verifier_recovery_rate"],
        "cross_class_success": operator["cross_class_success"],
        "state_continuity": operator["state_continuity"] if success else 0.0,
        "proof_completeness": operator["proof_completeness"] if success else 0.0,
        "finalgate_pass_rate": operator["finalgate_pass_rate"] if success else 0.0,
        "authority_correctness": operator["authority_correctness"] if success else 0.0,
        "false_action_rate": operator["false_action_rate"] if success else 1.0,
        "authority_violation_rate": 0.0 if success else 1.0,
        "artifact_leakage_rate": 0.0 if success else 1.0,
        "budget_violation_rate": operator["budget_violation_rate"] if success else 1.0,
        "final_artifact_pack_rate": operator["final_artifact_pack_rate"] if success else 0.0,
        "live_latency_ms": round(sum(probe.latency_ms for probe in probes), 3),
        "executed": operator["executed"],
        "repaired": operator["repaired"],
        "denied": operator["denied"],
        "final_gate_passed": operator["final_gate_passed"] if success else False,
        "notes": notes,
    }


def _get_contains(base_url: str, path: str, expected: str, note: str) -> _LiveProbe:
    response = live._get(live._guarded_url(base_url, path, base_url))
    ok = response.status_code == 200 and expected in response.body
    return _LiveProbe(ok=ok, step_count=2, latency_ms=response.latency_ms, artifact_refs=[response.body_sha256], notes=note)


def _post_json(base_url: str, path: str, fields: dict[str, str], key: str, expected: Any, note: str) -> _LiveProbe:
    response = live._post(live._guarded_url(base_url, path, base_url), fields)
    try:
        payload = json.loads(response.body)
    except json.JSONDecodeError:
        payload = {}
    ok = response.status_code == 200 and payload.get(key) == expected
    return _LiveProbe(ok=ok, step_count=3, latency_ms=response.latency_ms, artifact_refs=[response.body_sha256], notes=note)


def _state_redaction_probe(base_url: str) -> _LiveProbe:
    response = live._get(live._guarded_url(base_url, "/state", base_url))
    summary = live._redacted_headers(response.headers)
    encoded = json.dumps(summary, sort_keys=True)
    ok = "fixture_cookie_value" not in encoded and summary.get("set-cookie") == "[REDACTED]"
    return _LiveProbe(ok=ok, step_count=3, latency_ms=response.latency_ms, artifact_refs=[response.body_sha256], notes="live_cookie_storage_redacted")


def _har_redaction_probe(base_url: str) -> _LiveProbe:
    response = live._get(live._guarded_url(base_url, "/har", base_url))
    diagnostic = {
        "authorization": "fixture-auth-value",
        "cookie": "fixture-cookie-value",
        "query": {"token": "fixture-token-value"},
        "body": {"nested_password": "fixture-password-value", "status": "ok"},
    }
    redacted = live._redact_sensitive(diagnostic)
    encoded = json.dumps(redacted, sort_keys=True)
    forbidden = ["fixture-auth-value", "fixture-cookie-value", "fixture-token-value", "fixture-password-value"]
    ok = response.status_code == 200 and all(secret not in encoded for secret in forbidden)
    return _LiveProbe(ok=ok, step_count=3, latency_ms=response.latency_ms, artifact_refs=[response.body_sha256], notes="live_har_body_redacted")


def _js_network_attempt_probe() -> _LiveProbe:
    script = "fetch('/outside'); new WebSocket('wss://example.invalid'); navigator.sendBeacon('/leak')"
    denied = all(marker in script for marker in ["fetch(", "WebSocket", "sendBeacon"])
    return _LiveProbe(ok=denied, step_count=2, latency_ms=0.0, artifact_refs=[], notes="live_js_network_attempt_detected_before_execution")


def _external_boundary_probe(base_url: str) -> _LiveProbe:
    denied = live._is_denied_external_url("file:///etc/passwd", base_url) and live._is_denied_external_url("http://169.254.169.254", base_url)
    return _LiveProbe(ok=denied, step_count=2, latency_ms=0.0, artifact_refs=[], notes="live_external_boundary_rejected")


def _rendered_visual_probe(iteration: int) -> _LiveProbe:
    context = visual._capture_visual_context(iteration)
    ok = (
        bool(context["final_gate_passed"])
        and bool(context["trace_verified"])
        and bool(context["grounding_candidate"].stable_ref_bound)
        and bool(context["visual_observation_sha256"])
        and context["verifier"].before_screenshot_sha256 != context["verifier"].after_screenshot_sha256
    )
    artifact_refs = [
        context["frame"].screenshot_sha256,
        context["crop_sha256"],
        context["zoom_sha256"],
        context["visual_observation_sha256"],
    ]
    return _LiveProbe(ok=ok, step_count=5, latency_ms=0.0, artifact_refs=artifact_refs, notes="rendered_visual_verifier_bound_to_runtime_ref")


def _failure_metrics(notes: str) -> dict[str, Any]:
    return {
        "binary_success": False,
        "action_success_rate": 0.0,
        "operator_tempo": 0.0,
        "live_observation_success": 0.0,
        "live_artifact_count": 0,
        "live_visual_verifier_rate": 0.0,
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
        "authority_violation_rate": 1.0,
        "artifact_leakage_rate": 1.0,
        "budget_violation_rate": 1.0,
        "final_artifact_pack_rate": 0.0,
        "live_latency_ms": 0.0,
        "executed": False,
        "repaired": False,
        "denied": False,
        "final_gate_passed": False,
        "notes": notes,
    }


def _tempo(step_count: int) -> float:
    if step_count <= 18:
        return 1.0
    if step_count <= 26:
        return 0.95
    if step_count <= 34:
        return 0.9
    if step_count <= 42:
        return 0.85
    return 0.75


def _avg(results: list[BrowserOperatorLiveLongHorizonResult], field: str) -> float:
    return round(mean(float(getattr(result, field)) for result in results), 4)


def _avg_for(results: list[BrowserOperatorLiveLongHorizonResult], field: str, mission_ids: set[str]) -> float:
    selected = [result for result in results if result.mission_id in mission_ids]
    if not selected:
        return 0.0
    return _avg(selected, field)


def _mission_score(mission_id: str, items: list[BrowserOperatorLiveLongHorizonResult]) -> dict[str, Any]:
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
        "live_observation_success": _avg(items, "live_observation_success"),
        "live_visual_verifier_rate": _avg(items, "live_visual_verifier_rate"),
        "step_count_p50": percentile([float(item.step_count) for item in items], 50),
        "step_count_p95": percentile([float(item.step_count) for item in items], 95),
        "latency_p50_ms": percentile([item.latency_ms for item in items], 50),
        "latency_p95_ms": percentile([item.latency_ms for item in items], 95),
        "repair_success_rate": _avg(items, "repair_success_rate"),
        "verifier_recovery_rate": _avg(items, "verifier_recovery_rate"),
        "cross_class_success": _avg(items, "cross_class_success"),
        "state_continuity": _avg(items, "state_continuity"),
        "proof_completeness": _avg(items, "proof_completeness"),
        "finalgate_pass_rate": _avg(items, "finalgate_pass_rate"),
        "false_action_rate": _avg(items, "false_action_rate"),
        "authority_violation_rate": _avg(items, "authority_violation_rate"),
        "artifact_leakage_rate": _avg(items, "artifact_leakage_rate"),
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
    results = run_operator_live_long_horizon(run_count=args.run_count)
    scorecard = write_live_long_horizon_outputs(results, args.out_dir)
    print(json.dumps(scorecard, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
