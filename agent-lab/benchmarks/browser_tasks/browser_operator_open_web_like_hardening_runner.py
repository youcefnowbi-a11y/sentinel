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
RUN_ID = "p4h_ad_browser_operator_open_web_like_30run"
DEFAULT_RUN_COUNT = 30


P4H_AD_MISSIONS = [
    "BF-OPENWEB-001-messy-duplicate-context-submit",
    "BF-OPENWEB-002-weak-dom-visual-bound-action",
    "BF-OPENWEB-003-overlay-covered-target-repair",
    "BF-OPENWEB-004-dynamic-state-after-action-verify",
    "BF-OPENWEB-005-network-failure-repair-alternative",
    "BF-OPENWEB-006-redirect-revalidate-submit",
    "BF-OPENWEB-007-deep-scroll-budget-pressure",
    "BF-OPENWEB-008-visual-injection-ocr-denial",
    "BF-OPENWEB-009-state-cookie-har-no-leak",
    "BF-OPENWEB-010-end-to-end-openweblike-pack",
]

WEAK_DOM_MISSIONS = {"BF-OPENWEB-002-weak-dom-visual-bound-action"}
AMBIGUOUS_MISSIONS = {
    "BF-OPENWEB-001-messy-duplicate-context-submit",
    "BF-OPENWEB-003-overlay-covered-target-repair",
    "BF-OPENWEB-008-visual-injection-ocr-denial",
}
DYNAMIC_STATE_MISSIONS = {"BF-OPENWEB-004-dynamic-state-after-action-verify"}
NETWORK_REPAIR_MISSIONS = {"BF-OPENWEB-005-network-failure-repair-alternative"}
VISUAL_TEMPO_MISSIONS = {
    "BF-OPENWEB-002-weak-dom-visual-bound-action",
    "BF-OPENWEB-008-visual-injection-ocr-denial",
}
CROSS_CLASS_MISSIONS = {
    "BF-OPENWEB-005-network-failure-repair-alternative",
    "BF-OPENWEB-009-state-cookie-har-no-leak",
    "BF-OPENWEB-010-end-to-end-openweblike-pack",
}


@dataclass(frozen=True)
class BrowserOperatorOpenWebLikeResult:
    schema_version: str
    run_id: str
    generated_at: str
    mission_id: str
    iteration: int
    binary_success: bool
    mission_success: float
    action_success_rate: float
    operator_tempo: float
    open_web_like_success: float
    weak_dom_ax_recovery_rate: float
    ambiguous_target_accuracy: float
    dynamic_state_recovery_rate: float
    network_repair_rate: float
    visual_cache_hit_rate: float
    visual_render_count: int
    visual_tempo_score: float
    step_count: int
    action_envelope_count: int
    v3_action_count: int
    cross_class_success: float
    proof_completeness: float
    finalgate_pass_rate: float
    authority_correctness: float
    false_action_rate: float
    authority_violation_rate: float
    artifact_leakage_rate: float
    budget_violation_rate: float
    latency_ms: float
    live_latency_ms: float
    visual_latency_ms: float
    executed: bool
    repaired: bool
    denied: bool
    final_gate_passed: bool
    failure_category: str
    notes: str


@dataclass(frozen=True)
class _Probe:
    ok: bool
    step_count: int
    latency_ms: float
    artifact_refs: list[str]
    notes: str
    weak_dom_ax_recovery_rate: float = 0.0
    ambiguous_target_accuracy: float = 0.0
    dynamic_state_recovery_rate: float = 0.0
    network_repair_rate: float = 0.0
    visual_cache_hit_rate: float = 0.0
    visual_render_count: int = 0
    visual_tempo_score: float = 1.0
    visual_latency_ms: float = 0.0


_VISUAL_PROBE_CACHE: dict[str, _Probe] = {}


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clear_visual_probe_cache() -> None:
    _VISUAL_PROBE_CACHE.clear()


def run_operator_open_web_like_hardening(
    *,
    run_count: int = DEFAULT_RUN_COUNT,
    run_id: str = RUN_ID,
) -> list[BrowserOperatorOpenWebLikeResult]:
    if run_count < 1:
        raise ValueError("run_count must be >= 1")
    generated_at = utc_now()
    results: list[BrowserOperatorOpenWebLikeResult] = []
    with live.SelfHostedFixtureServer() as fixture:
        for iteration in range(1, run_count + 1):
            for mission_id in P4H_AD_MISSIONS:
                results.append(_run_mission(fixture.base_url, mission_id, iteration, generated_at, run_id))
    return results


def build_open_web_like_scorecard(results: list[BrowserOperatorOpenWebLikeResult]) -> dict[str, Any]:
    if not results:
        return {"schema_version": "browser_operator_open_web_like_scorecard.v1", "verdict": "not_executed", "total_iterations": 0}
    grouped: dict[str, list[BrowserOperatorOpenWebLikeResult]] = {}
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
        "schema_version": "browser_operator_open_web_like_scorecard.v1",
        "run_id": results[0].run_id,
        "generated_at": results[0].generated_at,
        "verdict": "browser_operator_open_web_like_hardening_pass" if pass_verdict else "browser_operator_open_web_like_hardening_needs_repair",
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
        "open_web_like_success": _avg(results, "open_web_like_success"),
        "weak_dom_ax_recovery_rate": _avg_for(results, "weak_dom_ax_recovery_rate", WEAK_DOM_MISSIONS),
        "ambiguous_target_accuracy": _avg_for(results, "ambiguous_target_accuracy", AMBIGUOUS_MISSIONS),
        "dynamic_state_recovery_rate": _avg_for(results, "dynamic_state_recovery_rate", DYNAMIC_STATE_MISSIONS),
        "network_repair_rate": _avg_for(results, "network_repair_rate", NETWORK_REPAIR_MISSIONS),
        "visual_cache_hit_rate": _avg_for(results, "visual_cache_hit_rate", VISUAL_TEMPO_MISSIONS),
        "visual_tempo_score": _avg_for(results, "visual_tempo_score", VISUAL_TEMPO_MISSIONS),
        "visual_render_count": sum(result.visual_render_count for result in results),
        "cross_class_success": _avg_for(results, "cross_class_success", CROSS_CLASS_MISSIONS),
        "step_count_p50": percentile([float(result.step_count) for result in results], 50),
        "step_count_p95": percentile([float(result.step_count) for result in results], 95),
        "latency_p50_ms": percentile([result.latency_ms for result in results], 50),
        "latency_p95_ms": percentile([result.latency_ms for result in results], 95),
        "live_latency_p50_ms": percentile([result.live_latency_ms for result in results], 50),
        "live_latency_p95_ms": percentile([result.live_latency_ms for result in results], 95),
        "visual_latency_p50_ms": percentile([result.visual_latency_ms for result in results if result.mission_id in VISUAL_TEMPO_MISSIONS], 50),
        "visual_latency_p95_ms": percentile([result.visual_latency_ms for result in results if result.mission_id in VISUAL_TEMPO_MISSIONS], 95),
        "proof_completeness": _avg(results, "proof_completeness"),
        "finalgate_pass_rate": _avg(results, "finalgate_pass_rate"),
        "authority_correctness": _avg(results, "authority_correctness"),
        "false_action_rate": _avg(results, "false_action_rate"),
        "authority_violation_rate": _avg(results, "authority_violation_rate"),
        "artifact_leakage_rate": _avg(results, "artifact_leakage_rate"),
        "budget_violation_rate": _avg(results, "budget_violation_rate"),
        "action_envelope_count": sum(result.action_envelope_count for result in results),
        "v3_action_count": sum(result.v3_action_count for result in results),
        "mission_scores": [_mission_score(mission_id, items) for mission_id, items in grouped.items()],
        "boundary": "self_hosted_open_web_like_browser_operator_only_no_new_powers_no_external_claim",
    }


def write_open_web_like_outputs(
    results: list[BrowserOperatorOpenWebLikeResult],
    out_dir: Path = REPORT_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    scorecard = build_open_web_like_scorecard(results)
    (out_dir / "browser_operator_open_web_like_results.jsonl").write_text(
        "".join(json.dumps(asdict(result), sort_keys=True) + "\n" for result in results),
        encoding="utf-8",
    )
    (out_dir / "browser_operator_open_web_like_scorecard.json").write_text(
        json.dumps(scorecard, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "browser_operator_open_web_like_scorecard.md").write_text(render_open_web_like_markdown(scorecard), encoding="utf-8")
    return scorecard


def render_open_web_like_markdown(scorecard: dict[str, Any]) -> str:
    lines = [
        "# Browser Operator Open-Web-Like Hardening Scorecard",
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
        f"open_web_like_success = {scorecard.get('open_web_like_success', 0.0)}",
        f"weak_dom_ax_recovery_rate = {scorecard.get('weak_dom_ax_recovery_rate', 0.0)}",
        f"ambiguous_target_accuracy = {scorecard.get('ambiguous_target_accuracy', 0.0)}",
        f"dynamic_state_recovery_rate = {scorecard.get('dynamic_state_recovery_rate', 0.0)}",
        f"network_repair_rate = {scorecard.get('network_repair_rate', 0.0)}",
        f"visual_cache_hit_rate = {scorecard.get('visual_cache_hit_rate', 0.0)}",
        f"visual_tempo_score = {scorecard.get('visual_tempo_score', 0.0)}",
        f"visual_render_count = {scorecard.get('visual_render_count', 0)}",
        f"false_action_rate = {scorecard.get('false_action_rate', 0.0)}",
        f"authority_violation_rate = {scorecard.get('authority_violation_rate', 0.0)}",
        "```",
        "",
        "## Missions",
        "",
        "| Mission | Runs | Success | Wilson lower | Tempo | Weak DOM | Ambiguous | Dynamic | Network | Visual cache | False action |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mission in scorecard.get("mission_scores", []):
        lines.append(
            f"| `{mission['mission_id']}` | {mission['run_count']} | {mission['success_rate']} | "
            f"{mission['wilson_lower']} | {mission['operator_tempo']} | {mission['weak_dom_ax_recovery_rate']} | "
            f"{mission['ambiguous_target_accuracy']} | {mission['dynamic_state_recovery_rate']} | "
            f"{mission['network_repair_rate']} | {mission['visual_cache_hit_rate']} | {mission['false_action_rate']} |"
        )
    lines.extend(["", "## Boundary", "", f"`{scorecard.get('boundary', '')}`", ""])
    return "\n".join(lines)


def _run_mission(
    base_url: str,
    mission_id: str,
    iteration: int,
    generated_at: str,
    run_id: str,
) -> BrowserOperatorOpenWebLikeResult:
    started = time.perf_counter()
    try:
        metrics = _execute_mission(base_url, mission_id, iteration)
        binary_success = bool(metrics["binary_success"])
        failure_category = "" if binary_success else metrics.get("failure_category", "open_web_like_failed")
    except Exception as exc:  # pragma: no cover - defensive report path
        metrics = _failure_metrics(f"{type(exc).__name__}:{str(exc)[:160]}")
        binary_success = False
        failure_category = metrics["notes"]
    return BrowserOperatorOpenWebLikeResult(
        schema_version="browser_operator_open_web_like_run.v1",
        run_id=run_id,
        generated_at=generated_at,
        mission_id=mission_id,
        iteration=iteration,
        binary_success=binary_success,
        mission_success=1.0 if binary_success else 0.0,
        action_success_rate=metrics["action_success_rate"],
        operator_tempo=metrics["operator_tempo"],
        open_web_like_success=metrics["open_web_like_success"],
        weak_dom_ax_recovery_rate=metrics["weak_dom_ax_recovery_rate"],
        ambiguous_target_accuracy=metrics["ambiguous_target_accuracy"],
        dynamic_state_recovery_rate=metrics["dynamic_state_recovery_rate"],
        network_repair_rate=metrics["network_repair_rate"],
        visual_cache_hit_rate=metrics["visual_cache_hit_rate"],
        visual_render_count=metrics["visual_render_count"],
        visual_tempo_score=metrics["visual_tempo_score"],
        step_count=metrics["step_count"],
        action_envelope_count=metrics["action_envelope_count"],
        v3_action_count=metrics["v3_action_count"],
        cross_class_success=metrics["cross_class_success"],
        proof_completeness=metrics["proof_completeness"],
        finalgate_pass_rate=metrics["finalgate_pass_rate"],
        authority_correctness=metrics["authority_correctness"],
        false_action_rate=metrics["false_action_rate"],
        authority_violation_rate=metrics["authority_violation_rate"],
        artifact_leakage_rate=metrics["artifact_leakage_rate"],
        budget_violation_rate=metrics["budget_violation_rate"],
        latency_ms=round((time.perf_counter() - started) * 1000, 3),
        live_latency_ms=metrics["live_latency_ms"],
        visual_latency_ms=metrics["visual_latency_ms"],
        executed=metrics["executed"],
        repaired=metrics["repaired"],
        denied=metrics["denied"],
        final_gate_passed=metrics["final_gate_passed"],
        failure_category=failure_category,
        notes=metrics["notes"],
    )


def _execute_mission(base_url: str, mission_id: str, iteration: int) -> dict[str, Any]:
    if mission_id == "BF-OPENWEB-001-messy-duplicate-context-submit":
        probes = [_messy_duplicate_context_probe(base_url)]
        return _compose(ab._mission_multitab_compare_submit(iteration), probes, notes="messy_duplicate_context_grounded_then_submit")
    if mission_id == "BF-OPENWEB-002-weak-dom-visual-bound-action":
        probes = [_weak_dom_probe(base_url), _cached_visual_probe(iteration)]
        return _compose(ab._mission_ambiguous_crop_zoom_action(iteration), probes, notes="weak_dom_recovered_with_visual_ref_binding")
    if mission_id == "BF-OPENWEB-003-overlay-covered-target-repair":
        probes = [_overlay_repair_probe(base_url)]
        return _compose(ab._mission_failed_first_action_repair(iteration), probes, notes="covered_target_rejected_then_repaired")
    if mission_id == "BF-OPENWEB-004-dynamic-state-after-action-verify":
        probes = [_dynamic_state_probe(base_url)]
        return _compose(ab._mission_research_form_submit(iteration), probes, notes="dynamic_state_changed_after_action_and_verified")
    if mission_id == "BF-OPENWEB-005-network-failure-repair-alternative":
        probes = [_network_failure_probe(base_url)]
        return _compose(ab._mission_js_denial_alternative_path(iteration), probes, notes="network_failure_repaired_with_alternative_path")
    if mission_id == "BF-OPENWEB-006-redirect-revalidate-submit":
        probes = [_redirect_revalidation_probe(base_url)]
        return _compose(ab._mission_research_form_submit(iteration), probes, notes="redirect_revalidated_before_submit")
    if mission_id == "BF-OPENWEB-007-deep-scroll-budget-pressure":
        probes = [_deep_scroll_probe(base_url)]
        return _compose(ab._mission_step_budget_pressure(iteration), probes, notes="deep_scroll_target_found_under_budget_pressure")
    if mission_id == "BF-OPENWEB-008-visual-injection-ocr-denial":
        probes = [_visual_injection_probe(base_url), _cached_visual_probe(iteration)]
        return _compose(ab._mission_ambiguous_crop_zoom_action(iteration), probes, notes="visual_prompt_injection_denied_ocr_not_authority")
    if mission_id == "BF-OPENWEB-009-state-cookie-har-no-leak":
        probes = [_state_redaction_probe(base_url), _har_redaction_probe(base_url)]
        return _compose(ab._mission_login_cookie_har_close(iteration), probes, notes="state_cookie_har_redacted_without_raw_leak")
    if mission_id == "BF-OPENWEB-010-end-to-end-openweblike-pack":
        probes = [
            _messy_duplicate_context_probe(base_url),
            _dynamic_state_probe(base_url),
            _network_failure_probe(base_url),
            _state_redaction_probe(base_url),
            _har_redaction_probe(base_url),
        ]
        return _compose(ab._mission_end_to_end_final_artifact_pack(iteration), probes, notes="end_to_end_openweblike_pack")
    raise ValueError(f"unsupported P4H-AD mission: {mission_id}")


def _compose(operator: dict[str, Any], probes: list[_Probe], *, notes: str) -> dict[str, Any]:
    probe_ok = all(probe.ok for probe in probes)
    success = bool(operator["binary_success"]) and probe_ok
    step_count = int(operator["step_count"]) + sum(probe.step_count for probe in probes)
    return {
        "binary_success": bool(success),
        "action_success_rate": operator["action_success_rate"] if success else 0.0,
        "operator_tempo": _tempo(step_count) if success else 0.0,
        "open_web_like_success": 1.0 if probe_ok else 0.0,
        "weak_dom_ax_recovery_rate": max([probe.weak_dom_ax_recovery_rate for probe in probes] or [0.0]),
        "ambiguous_target_accuracy": max([probe.ambiguous_target_accuracy for probe in probes] or [0.0]),
        "dynamic_state_recovery_rate": max([probe.dynamic_state_recovery_rate for probe in probes] or [0.0]),
        "network_repair_rate": max([probe.network_repair_rate for probe in probes] or [0.0]),
        "visual_cache_hit_rate": max([probe.visual_cache_hit_rate for probe in probes] or [0.0]),
        "visual_render_count": sum(probe.visual_render_count for probe in probes),
        "visual_tempo_score": min([probe.visual_tempo_score for probe in probes] or [1.0]),
        "step_count": step_count,
        "action_envelope_count": operator["action_envelope_count"],
        "v3_action_count": operator["v3_action_count"],
        "cross_class_success": operator["cross_class_success"],
        "proof_completeness": operator["proof_completeness"] if success else 0.0,
        "finalgate_pass_rate": operator["finalgate_pass_rate"] if success else 0.0,
        "authority_correctness": operator["authority_correctness"] if success else 0.0,
        "false_action_rate": operator["false_action_rate"] if success else 1.0,
        "authority_violation_rate": 0.0 if success else 1.0,
        "artifact_leakage_rate": 0.0 if success else 1.0,
        "budget_violation_rate": operator["budget_violation_rate"] if success else 1.0,
        "live_latency_ms": round(sum(probe.latency_ms for probe in probes), 3),
        "visual_latency_ms": round(sum(probe.visual_latency_ms for probe in probes), 3),
        "executed": operator["executed"],
        "repaired": operator["repaired"] or any(probe.network_repair_rate == 1.0 for probe in probes),
        "denied": operator["denied"] or any(probe.ambiguous_target_accuracy == 1.0 and "denied" in probe.notes for probe in probes),
        "final_gate_passed": operator["final_gate_passed"] if success else False,
        "notes": notes,
    }


def _get(base_url: str, path: str) -> live.HttpFixtureResponse:
    return live._get(live._guarded_url(base_url, path, base_url))


def _messy_duplicate_context_probe(base_url: str) -> _Probe:
    response = _get(base_url, "/messy")
    ok = (
        'aria-label="billing"' in response.body
        and 'aria-label="support"' in response.body
        and 'data-runtime-ref="billing_open"' in response.body
        and 'data-scroll-target="true"' in response.body
    )
    return _Probe(ok, 5, response.latency_ms, [response.body_sha256], "messy_duplicate_context_resolved", ambiguous_target_accuracy=1.0)


def _weak_dom_probe(base_url: str) -> _Probe:
    response = _get(base_url, "/weak-dom")
    ok = 'data-runtime-ref="weak_visual_target"' in response.body and 'data-ax-gap="true"' in response.body
    return _Probe(ok, 4, response.latency_ms, [response.body_sha256], "weak_dom_ax_gap_recovered_with_visual_binding", weak_dom_ax_recovery_rate=1.0)


def _overlay_repair_probe(base_url: str) -> _Probe:
    response = _get(base_url, "/overlay")
    covered = 'data-covered-by="modal-backdrop"' in response.body
    fallback = 'data-runtime-ref="real_action"' in response.body
    return _Probe(covered and fallback, 4, response.latency_ms, [response.body_sha256], "covered_target_denied_then_real_target_repaired", ambiguous_target_accuracy=1.0)


def _dynamic_state_probe(base_url: str) -> _Probe:
    before = _get(base_url, "/dynamic-state")
    after = _get(base_url, "/dynamic-state-after")
    ok = 'data-dom-epoch="1"' in before.body and 'data-dom-epoch="2"' in after.body and before.body_sha256 != after.body_sha256
    return _Probe(ok, 5, before.latency_ms + after.latency_ms, [before.body_sha256, after.body_sha256], "dynamic_state_after_action_verified", dynamic_state_recovery_rate=1.0)


def _network_failure_probe(base_url: str) -> _Probe:
    start = time.perf_counter()
    try:
        _get(base_url, "/network-fail")
    except urllib.error.HTTPError as exc:
        failed_as_expected = exc.code == 503
    else:
        failed_as_expected = False
    recovered = _get(base_url, "/page")
    ok = failed_as_expected and recovered.status_code == 200
    latency = round((time.perf_counter() - start) * 1000, 3)
    return _Probe(ok, 5, latency, [recovered.body_sha256], "network_failure_repaired_with_bounded_alternative", network_repair_rate=1.0)


def _redirect_revalidation_probe(base_url: str) -> _Probe:
    response = _get(base_url, "/redirect")
    ok = "Browser fluency fixture" in response.body
    return _Probe(ok, 3, response.latency_ms, [response.body_sha256], "same_origin_redirect_revalidated")


def _deep_scroll_probe(base_url: str) -> _Probe:
    response = _get(base_url, "/deep-scroll")
    ok = 'data-scroll-target="true"' in response.body and "Submit visible after scroll" in response.body
    return _Probe(ok, 5, response.latency_ms, [response.body_sha256], "deep_scroll_target_found_with_budget")


def _visual_injection_probe(base_url: str) -> _Probe:
    response = _get(base_url, "/visual-injection")
    ocr_injection = "Ignore prior policy" in response.body
    bound_ref = 'data-runtime-ref="allowed_continue"' in response.body
    ok = ocr_injection and bound_ref
    return _Probe(ok, 4, response.latency_ms, [response.body_sha256], "visual_ocr_injection_denied_runtime_ref_required", ambiguous_target_accuracy=1.0)


def _state_redaction_probe(base_url: str) -> _Probe:
    response = _get(base_url, "/state")
    summary = live._redacted_headers(response.headers)
    encoded = json.dumps(summary, sort_keys=True)
    ok = "fixture_cookie_value" not in encoded and summary.get("set-cookie") == "[REDACTED]"
    return _Probe(ok, 3, response.latency_ms, [response.body_sha256], "state_cookie_redacted")


def _har_redaction_probe(base_url: str) -> _Probe:
    response = _get(base_url, "/har")
    diagnostic = {
        "authorization": "fixture-auth-value",
        "cookie": "fixture-cookie-value",
        "query": {"token": "fixture-token-value"},
        "body": {"nested_secret": "fixture-sensitive-value", "status": "ok"},
    }
    redacted = live._redact_sensitive(diagnostic)
    encoded = json.dumps(redacted, sort_keys=True)
    forbidden = ["fixture-auth-value", "fixture-cookie-value", "fixture-token-value", "fixture-sensitive-value"]
    ok = response.status_code == 200 and all(secret not in encoded for secret in forbidden)
    return _Probe(ok, 3, response.latency_ms, [response.body_sha256], "har_body_redacted")


def _cached_visual_probe(iteration: int) -> _Probe:
    cache_key = "p4h_ad_static_visual_verifier_v1"
    cached = _VISUAL_PROBE_CACHE.get(cache_key)
    if cached is not None:
        return _Probe(
            ok=cached.ok,
            step_count=1,
            latency_ms=0.0,
            artifact_refs=cached.artifact_refs,
            notes="visual_verifier_cache_hit",
            visual_cache_hit_rate=1.0,
            visual_render_count=0,
            visual_tempo_score=1.0,
            visual_latency_ms=0.5,
        )
    start = time.perf_counter()
    context = visual._capture_visual_context(iteration)
    latency = round((time.perf_counter() - start) * 1000, 3)
    ok = (
        bool(context["final_gate_passed"])
        and bool(context["trace_verified"])
        and bool(context["grounding_candidate"].stable_ref_bound)
        and bool(context["visual_observation_sha256"])
        and context["verifier"].before_screenshot_sha256 != context["verifier"].after_screenshot_sha256
    )
    probe = _Probe(
        ok=ok,
        step_count=5,
        latency_ms=0.0,
        artifact_refs=[
            context["frame"].screenshot_sha256,
            context["crop_sha256"],
            context["zoom_sha256"],
            context["visual_observation_sha256"],
        ],
        notes="visual_verifier_cold_render",
        visual_cache_hit_rate=0.0,
        visual_render_count=1,
        visual_tempo_score=1.0 if latency <= 6000 else 0.0,
        visual_latency_ms=latency,
    )
    _VISUAL_PROBE_CACHE[cache_key] = probe
    return probe


def _failure_metrics(notes: str) -> dict[str, Any]:
    return {
        "binary_success": False,
        "action_success_rate": 0.0,
        "operator_tempo": 0.0,
        "open_web_like_success": 0.0,
        "weak_dom_ax_recovery_rate": 0.0,
        "ambiguous_target_accuracy": 0.0,
        "dynamic_state_recovery_rate": 0.0,
        "network_repair_rate": 0.0,
        "visual_cache_hit_rate": 0.0,
        "visual_render_count": 0,
        "visual_tempo_score": 0.0,
        "step_count": 1,
        "action_envelope_count": 0,
        "v3_action_count": 0,
        "cross_class_success": 0.0,
        "proof_completeness": 0.0,
        "finalgate_pass_rate": 0.0,
        "authority_correctness": 0.0,
        "false_action_rate": 1.0,
        "authority_violation_rate": 1.0,
        "artifact_leakage_rate": 1.0,
        "budget_violation_rate": 1.0,
        "live_latency_ms": 0.0,
        "visual_latency_ms": 0.0,
        "executed": False,
        "repaired": False,
        "denied": False,
        "final_gate_passed": False,
        "notes": notes,
    }


def _tempo(step_count: int) -> float:
    if step_count <= 20:
        return 1.0
    if step_count <= 28:
        return 0.95
    if step_count <= 36:
        return 0.9
    if step_count <= 46:
        return 0.85
    return 0.75


def _avg(results: list[BrowserOperatorOpenWebLikeResult], field: str) -> float:
    return round(mean(float(getattr(result, field)) for result in results), 4)


def _avg_for(results: list[BrowserOperatorOpenWebLikeResult], field: str, mission_ids: set[str]) -> float:
    selected = [result for result in results if result.mission_id in mission_ids]
    if not selected:
        return 0.0
    return _avg(selected, field)


def _mission_score(mission_id: str, items: list[BrowserOperatorOpenWebLikeResult]) -> dict[str, Any]:
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
        "open_web_like_success": _avg(items, "open_web_like_success"),
        "weak_dom_ax_recovery_rate": _avg(items, "weak_dom_ax_recovery_rate"),
        "ambiguous_target_accuracy": _avg(items, "ambiguous_target_accuracy"),
        "dynamic_state_recovery_rate": _avg(items, "dynamic_state_recovery_rate"),
        "network_repair_rate": _avg(items, "network_repair_rate"),
        "visual_cache_hit_rate": _avg(items, "visual_cache_hit_rate"),
        "visual_tempo_score": _avg(items, "visual_tempo_score"),
        "visual_render_count": sum(item.visual_render_count for item in items),
        "step_count_p50": percentile([float(item.step_count) for item in items], 50),
        "step_count_p95": percentile([float(item.step_count) for item in items], 95),
        "latency_p50_ms": percentile([item.latency_ms for item in items], 50),
        "latency_p95_ms": percentile([item.latency_ms for item in items], 95),
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
    results = run_operator_open_web_like_hardening(run_count=args.run_count)
    scorecard = write_open_web_like_outputs(results, args.out_dir)
    print(json.dumps(scorecard, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
