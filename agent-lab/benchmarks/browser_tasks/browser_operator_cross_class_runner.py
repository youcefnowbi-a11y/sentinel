from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from types import SimpleNamespace
from typing import Any
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[3]
CORE_ROOT = REPO_ROOT / "sentinel-control" / "services" / "sentinel-core"
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from sentinel.agent.action_engine import ActionEngine, CompiledMissionPolicyCompiler, SceneActionCandidate  # noqa: E402
from sentinel.agent.artifact_capture import ArtifactCaptureSandbox, CapturedArtifact  # noqa: E402
from sentinel.agent.browser import (  # noqa: E402
    BrowserAccessibilitySnapshotBuilder,
    BrowserControlledCapabilityRunner,
    BrowserDownloadBackendResult,
    BrowserFormSubmitBackendResult,
    BrowserInteractionIntent,
    BrowserInteractionStep,
    BrowserInteractionTarget,
    BrowserPerceptionAdapter,
    BrowserRenderedPage,
    BrowserUIObservationBuilder,
    BrowserUploadBackendResult,
    BrowserV3AuthorityClass,
    BrowserV3AuthorityGrant,
)
from sentinel.agent.browser.interaction_dry_run import BrowserInteractionDryRunPlanner  # noqa: E402
from sentinel.agent.browser.v3_fixture_backends import BrowserV3FixtureBackendBench  # noqa: E402
from sentinel.agent.event_bus import EventBus  # noqa: E402
from sentinel.agent.events import AgentEventType  # noqa: E402
from sentinel.agent.final_gate import CoreFinalGate  # noqa: E402
from sentinel.agent.perception import PerceptionSourceType  # noqa: E402
from sentinel.agent.phases import AgentPhase  # noqa: E402
from sentinel.agent.tool_call_protocol import CanonicalToolCall  # noqa: E402
from sentinel.capabilities import default_tool_registry  # noqa: E402
from sentinel.mission import MissionAuthorityEnvelope  # noqa: E402
from sentinel.shared.enums import MissionMode, MissionType  # noqa: E402


REPORT_DIR = Path(__file__).resolve().parent / "reports"
TMP_ROOT = Path(__file__).resolve().parent / "tmp_p4h_aa"
RUN_ID = "p4h_aa_browser_v3_action_engine_routing_30run"
DEFAULT_RUN_COUNT = 30
DOMAIN = "example.com"
BASE_URL = f"https://{DOMAIN}"
CONTEXT_PACK_ID = "cpk_p4haa00000001"
PDF_BYTES = b"%PDF-1.7\nsentinel p4h-aa upload/download fixture\n%%EOF"
PNG_BYTES = b"\x89PNG\r\n\x1a\nfake"
SAFE_SCRIPT = "return { title: document.title };"
NETWORK_SCRIPT = "return fetch('/leak');"


P4H_AA_MISSIONS = [
    "BF-V3ACT-001-form-submit-envelope",
    "BF-V3ACT-002-download-quarantine-envelope",
    "BF-V3ACT-003-upload-authorized-envelope",
    "BF-V3ACT-004-private-session-open-close-envelope",
    "BF-V3ACT-005-login-authority-envelope",
    "BF-V3ACT-006-cookie-storage-envelope",
    "BF-V3ACT-007-js-sandbox-no-network-denial",
    "BF-V3ACT-008-har-body-redaction-envelope",
    "BF-V3ACT-009-cross-class-authority-flow",
    "BF-V3ACT-010-out-of-policy-v3-denial",
]

DENIAL_MISSIONS = {
    "BF-V3ACT-007-js-sandbox-no-network-denial",
    "BF-V3ACT-010-out-of-policy-v3-denial",
}
CROSS_CLASS_MISSIONS = {"BF-V3ACT-009-cross-class-authority-flow"}


@dataclass(frozen=True)
class BrowserV3ActionRoutingResult:
    schema_version: str
    run_id: str
    generated_at: str
    mission_id: str
    iteration: int
    binary_success: bool
    mission_success: float
    action_success_rate: float
    operator_tempo: float
    action_envelope_count: int
    v3_action_count: int
    v3_receipt_completeness: float
    finalgate_pass_rate: float
    authority_correctness: float
    false_action_rate: float
    proof_completeness: float
    denial_correctness: float
    cross_class_success: float
    latency_ms: float
    step_count: int
    executed: bool
    denied: bool
    final_gate_passed: bool
    failure_category: str
    notes: str


class FakeFormSubmitBackend:
    def __init__(self, before_snapshot, *, after_url: str = f"{BASE_URL}/form/thanks", after_text: str = "Thanks, request received.") -> None:
        self.before_snapshot = before_snapshot
        self.after_url = after_url
        self.after_text = after_text

    def __call__(self, request) -> BrowserFormSubmitBackendResult:
        return BrowserFormSubmitBackendResult(
            before_snapshot=self.before_snapshot,
            after_page=BrowserRenderedPage(
                final_url=self.after_url,
                status_code=200,
                title="Thanks",
                text=self.after_text,
                html=f"<html><body><main><h1>{self.after_text}</h1></main></body></html>",
                screenshot_png=PNG_BYTES,
            ),
            final_url_before=request.final_url,
            final_url_after=self.after_url,
            submitted=True,
            submitted_ref_ids=[request.form_ref_id, request.submit_ref_id],
        )


class FakeDownloadBackend:
    def __call__(self, _request) -> BrowserDownloadBackendResult:
        return BrowserDownloadBackendResult(
            final_url=f"{BASE_URL}/report.pdf",
            status_code=200,
            content_type="application/pdf",
            data=PDF_BYTES,
            filename="report.pdf",
            compressed_bytes_read=len(PDF_BYTES),
            uncompressed_bytes_read=len(PDF_BYTES),
        )


class FakeUploadBackend:
    def __init__(self, before_snapshot, *, after_url: str = f"{BASE_URL}/upload/thanks", after_text: str = "Upload complete.") -> None:
        self.before_snapshot = before_snapshot
        self.after_url = after_url
        self.after_text = after_text

    def __call__(self, request) -> BrowserUploadBackendResult:
        return BrowserUploadBackendResult(
            before_snapshot=self.before_snapshot,
            after_page=BrowserRenderedPage(
                final_url=self.after_url,
                status_code=200,
                title="Upload complete",
                text=self.after_text,
                html=f"<html><body><main><h1>{self.after_text}</h1></main></body></html>",
                screenshot_png=PNG_BYTES,
            ),
            final_url_before=request.final_url,
            final_url_after=self.after_url,
            uploaded=True,
            uploaded_ref_ids=[request.upload_ref_id],
        )


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


def run_v3_action_routing(*, run_count: int = DEFAULT_RUN_COUNT, run_id: str = RUN_ID) -> list[BrowserV3ActionRoutingResult]:
    if run_count < 1:
        raise ValueError("run_count must be >= 1")
    generated_at = utc_now()
    results: list[BrowserV3ActionRoutingResult] = []
    for iteration in range(1, run_count + 1):
        for mission_id in P4H_AA_MISSIONS:
            results.append(_run_mission(mission_id, iteration, generated_at, run_id))
    return results


def build_v3_action_routing_scorecard(results: list[BrowserV3ActionRoutingResult]) -> dict[str, Any]:
    if not results:
        return {"schema_version": "browser_v3_action_routing_scorecard.v1", "verdict": "not_executed", "total_iterations": 0}
    grouped: dict[str, list[BrowserV3ActionRoutingResult]] = {}
    for result in results:
        grouped.setdefault(result.mission_id, []).append(result)
    success_count = sum(1 for result in results if result.binary_success)
    lower, upper = wilson_interval(success_count, len(results))
    return {
        "schema_version": "browser_v3_action_routing_scorecard.v1",
        "run_id": results[0].run_id,
        "generated_at": results[0].generated_at,
        "verdict": "browser_v3_action_engine_routing_pass" if success_count == len(results) else "browser_v3_action_engine_routing_needs_repair",
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
        "action_envelope_count": sum(result.action_envelope_count for result in results),
        "v3_receipt_completeness": _avg(results, "v3_receipt_completeness"),
        "finalgate_pass_rate": _avg(results, "finalgate_pass_rate"),
        "authority_correctness": _avg(results, "authority_correctness"),
        "false_action_rate": _avg(results, "false_action_rate"),
        "proof_completeness": _avg(results, "proof_completeness"),
        "denial_correctness": _avg_for(results, "denial_correctness", DENIAL_MISSIONS),
        "cross_class_success": _avg_for(results, "cross_class_success", CROSS_CLASS_MISSIONS),
        "latency_p50_ms": percentile([result.latency_ms for result in results], 50),
        "latency_p95_ms": percentile([result.latency_ms for result in results], 95),
        "step_count_p50": percentile([float(result.step_count) for result in results], 50),
        "step_count_p95": percentile([float(result.step_count) for result in results], 95),
        "mission_scores": [_mission_score(mission_id, items) for mission_id, items in grouped.items()],
        "boundary": "browser_only_fixture_v3_action_engine_routing_no_new_powers",
    }


def write_v3_action_routing_outputs(results: list[BrowserV3ActionRoutingResult], out_dir: Path = REPORT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    scorecard = build_v3_action_routing_scorecard(results)
    (out_dir / "browser_v3_action_routing_results.jsonl").write_text(
        "".join(json.dumps(asdict(result), sort_keys=True) + "\n" for result in results),
        encoding="utf-8",
    )
    (out_dir / "browser_v3_action_routing_scorecard.json").write_text(
        json.dumps(scorecard, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "browser_v3_action_routing_scorecard.md").write_text(render_v3_action_routing_markdown(scorecard), encoding="utf-8")
    return scorecard


def render_v3_action_routing_markdown(scorecard: dict[str, Any]) -> str:
    lines = [
        "# Browser V3 ActionEngine Routing Scorecard",
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
        f"v3_receipt_completeness = {scorecard.get('v3_receipt_completeness', 0.0)}",
        f"finalgate_pass_rate = {scorecard.get('finalgate_pass_rate', 0.0)}",
        f"authority_correctness = {scorecard.get('authority_correctness', 0.0)}",
        f"false_action_rate = {scorecard.get('false_action_rate', 0.0)}",
        f"cross_class_success = {scorecard.get('cross_class_success', 0.0)}",
        "```",
        "",
        "## Missions",
        "",
        "| Mission | Runs | Success | Wilson lower | Tempo | V3 receipts | FinalGate | Denial | False action |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mission in scorecard.get("mission_scores", []):
        lines.append(
            f"| `{mission['mission_id']}` | {mission['run_count']} | {mission['success_rate']} | "
            f"{mission['wilson_lower']} | {mission['operator_tempo']} | {mission['v3_receipt_completeness']} | "
            f"{mission['finalgate_pass_rate']} | {mission['denial_correctness']} | {mission['false_action_rate']} |"
        )
    lines.extend(["", "## Boundary", "", f"`{scorecard.get('boundary', '')}`", ""])
    return "\n".join(lines)


def _run_mission(mission_id: str, iteration: int, generated_at: str, run_id: str) -> BrowserV3ActionRoutingResult:
    started = time.perf_counter()
    try:
        metrics = _execute_mission(mission_id, iteration)
        binary_success = bool(metrics["binary_success"])
        failure_category = "" if binary_success else metrics.get("failure_category", "v3_action_routing_failed")
    except Exception as exc:  # pragma: no cover - defensive report path
        metrics = _failure_metrics(f"{type(exc).__name__}:{str(exc)[:160]}")
        binary_success = False
        failure_category = metrics["notes"]
    return BrowserV3ActionRoutingResult(
        schema_version="browser_v3_action_routing_run.v1",
        run_id=run_id,
        generated_at=generated_at,
        mission_id=mission_id,
        iteration=iteration,
        binary_success=binary_success,
        mission_success=1.0 if binary_success else 0.0,
        action_success_rate=metrics["action_success_rate"],
        operator_tempo=metrics["operator_tempo"],
        action_envelope_count=metrics["action_envelope_count"],
        v3_action_count=metrics["v3_action_count"],
        v3_receipt_completeness=metrics["v3_receipt_completeness"],
        finalgate_pass_rate=metrics["finalgate_pass_rate"],
        authority_correctness=metrics["authority_correctness"],
        false_action_rate=metrics["false_action_rate"],
        proof_completeness=metrics["proof_completeness"],
        denial_correctness=metrics["denial_correctness"],
        cross_class_success=metrics["cross_class_success"],
        latency_ms=round((time.perf_counter() - started) * 1000, 3),
        step_count=metrics["step_count"],
        executed=metrics["executed"],
        denied=metrics["denied"],
        final_gate_passed=metrics["final_gate_passed"],
        failure_category=failure_category,
        notes=metrics["notes"],
    )


def _execute_mission(mission_id: str, iteration: int) -> dict[str, Any]:
    if mission_id == "BF-V3ACT-001-form-submit-envelope":
        return _mission_form_submit(iteration)
    if mission_id == "BF-V3ACT-002-download-quarantine-envelope":
        return _mission_download(iteration)
    if mission_id == "BF-V3ACT-003-upload-authorized-envelope":
        return _mission_upload(iteration)
    if mission_id == "BF-V3ACT-004-private-session-open-close-envelope":
        return _mission_private_session(iteration)
    if mission_id == "BF-V3ACT-005-login-authority-envelope":
        return _mission_login(iteration)
    if mission_id == "BF-V3ACT-006-cookie-storage-envelope":
        return _mission_cookie_storage(iteration)
    if mission_id == "BF-V3ACT-007-js-sandbox-no-network-denial":
        return _mission_js_no_network_denial(iteration)
    if mission_id == "BF-V3ACT-008-har-body-redaction-envelope":
        return _mission_har_body(iteration)
    if mission_id == "BF-V3ACT-009-cross-class-authority-flow":
        return _mission_cross_class(iteration)
    if mission_id == "BF-V3ACT-010-out-of-policy-v3-denial":
        return _mission_out_of_policy_denial(iteration)
    raise ValueError(f"unsupported P4H-AA mission: {mission_id}")


def _mission_form_submit(iteration: int) -> dict[str, Any]:
    context = _build_context(iteration, {BrowserV3AuthorityClass.FORM_SUBMIT})
    snap = context["snapshot"]
    textbox_ref = _first_ref(snap, "textbox")
    button_ref = _ref_by_role_name(snap, "button", "Send request")
    plan, plan_trace = _plan(
        context,
        final_url=f"{BASE_URL}/form",
        steps=[
            BrowserInteractionStep(intent=BrowserInteractionIntent.FILL_PLAN, target=BrowserInteractionTarget(ref=textbox_ref), text="lead@example.com", reason="Fill public form."),
            BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=button_ref), reason="Submit public form through V3 authority."),
        ],
    )
    call = _call_for_action(
        context,
        tool_id="browser_public_form_submit",
        action=BrowserV3AuthorityClass.FORM_SUBMIT.value,
        target=f"{BASE_URL}/form",
        ref_id=button_ref,
        arguments={
            "plan": plan.model_dump(mode="json"),
            "plan_trace_event_id": plan_trace,
            "before_snapshot_trace_event_id": context["snapshot_trace_id"],
            "final_url": f"{BASE_URL}/form",
            "form_ref_id": textbox_ref,
            "submit_ref_id": button_ref,
            "expected_effect": "confirmation text appears",
            "capture_screenshot": False,
        },
    )
    with _temporary_workspace("sentinel_p4h_aa_form_") as tmp:
        runner = _runner(context, tmp, form_submit_backend=FakeFormSubmitBackend(snap))
        return _execute_single(
            context,
            action=BrowserV3AuthorityClass.FORM_SUBMIT.value,
            tool_id="browser_public_form_submit",
            ref_id=button_ref,
            call=call,
            runner=runner,
            gate_names=[BrowserV3AuthorityClass.FORM_SUBMIT.value],
            step_count=8,
            notes="form_submit_routed_through_action_engine",
        )


def _mission_download(iteration: int) -> dict[str, Any]:
    context = _build_context(iteration, {BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE})
    link_ref = _first_ref(context["snapshot"], "link")
    call = _call_for_action(
        context,
        tool_id=BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value,
        action=BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value,
        target=f"{BASE_URL}/report.pdf",
        ref_id=link_ref,
        arguments={
            "source_url": f"{BASE_URL}/report.pdf",
            "source_ref_id": link_ref,
            "allowed_mime_types": ["application/pdf"],
            "max_bytes": 4096,
            "expected_effect": "PDF captured into quarantine",
        },
    )
    with _temporary_workspace("sentinel_p4h_aa_download_") as tmp:
        runner = _runner(context, tmp, download_backend=FakeDownloadBackend())
        return _execute_single(
            context,
            action=BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value,
            tool_id=BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value,
            ref_id=link_ref,
            call=call,
            runner=runner,
            gate_names=[BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value],
            step_count=6,
            notes="download_quarantine_routed_through_action_engine",
        )


def _mission_upload(iteration: int) -> dict[str, Any]:
    context = _build_context(iteration, {BrowserV3AuthorityClass.UPLOAD_AUTHORIZED})
    upload_ref = _ref_by_role_name(context["snapshot"], "button", "Upload")
    plan, plan_trace = _plan(
        context,
        final_url=f"{BASE_URL}/upload",
        steps=[BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=upload_ref), reason="Upload certified artifact.")],
    )
    with _temporary_workspace("sentinel_p4h_aa_upload_") as tmp:
        capture = ArtifactCaptureSandbox(mission_id=context["mission_id"], capture_root=Path(tmp) / "captures")
        artifact = _source_artifact(capture, context["bus"])
        context["authority"] = _envelope(
            context["mission_id"],
            {BrowserV3AuthorityClass.UPLOAD_AUTHORIZED},
            allowed_artifact_ids=[artifact.id],
        )
        context["policy"] = CompiledMissionPolicyCompiler().compile(context["authority"], trace_refs=[context["snapshot_trace_id"]])
        call = _call_for_action(
            context,
            tool_id=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
            action=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
            target=f"{BASE_URL}/upload",
            ref_id=upload_ref,
            arguments={
                "plan": plan.model_dump(mode="json"),
                "plan_trace_event_id": plan_trace,
                "before_snapshot_trace_event_id": context["snapshot_trace_id"],
                "final_url": f"{BASE_URL}/upload",
                "upload_ref_id": upload_ref,
                "source_artifact": artifact.model_dump(mode="json"),
                "expected_effect": "upload confirmation appears",
                "capture_screenshot": False,
            },
        )
        runner = _runner(context, tmp, upload_backend=FakeUploadBackend(context["snapshot"]))
        return _execute_single(
            context,
            action=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
            tool_id=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
            ref_id=upload_ref,
            call=call,
            runner=runner,
            gate_names=[BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value],
            step_count=8,
            notes="upload_authorized_routed_through_action_engine",
        )


def _mission_private_session(iteration: int) -> dict[str, Any]:
    context = _build_context(iteration, {BrowserV3AuthorityClass.PRIVATE_SESSION})
    ref_id = _ref_by_role_name(context["snapshot"], "button", "Login")
    with _temporary_workspace("sentinel_p4h_aa_private_") as tmp:
        harness = BrowserV3FixtureBackendBench(root=Path(tmp) / "fixture")
        runner = _runner(context, tmp, private_session_backend=harness.private_session_backend)
        opened = _execute_single(
            context,
            action=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
            tool_id=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
            ref_id=ref_id,
            call=_call_for_action(
                context,
                tool_id=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
                action=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
                target=f"{BASE_URL}/session",
                ref_id=ref_id,
                arguments={"operation": "open", "allowed_domains": [DOMAIN], "storage_enabled": True, "expected_effect": "private session opened"},
            ),
            runner=runner,
            gate_names=[],
            step_count=4,
            notes="private_session_open_routed",
        )
        if not opened["binary_success"]:
            return opened
        session = _private_session_payload(context["bus"], AgentEventType.BROWSER_PRIVATE_SESSION_STARTED)
        closed = _execute_single(
            context,
            action=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
            tool_id=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
            ref_id=ref_id,
            call=_call_for_action(
                context,
                tool_id=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
                action=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
                target=f"{BASE_URL}/session",
                ref_id=ref_id,
                arguments={
                    "operation": "close",
                    "session_id": session["session_id"],
                    "profile_id": session["profile_id"],
                    "allowed_domains": [DOMAIN],
                    "storage_enabled": True,
                    "expected_effect": "private session closed and destroyed",
                },
            ),
            runner=runner,
            gate_names=[BrowserV3AuthorityClass.PRIVATE_SESSION.value],
            step_count=6,
            notes="private_session_open_close_routed_through_action_engine",
        )
        return _merge_sequence(context, [opened, closed], notes="private_session_open_close_routed_through_action_engine", step_count=6)


def _mission_login(iteration: int) -> dict[str, Any]:
    context = _build_context(iteration, {BrowserV3AuthorityClass.PRIVATE_SESSION, BrowserV3AuthorityClass.LOGIN_AUTHORITY})
    ref_id = _ref_by_role_name(context["snapshot"], "button", "Login")
    with _temporary_workspace("sentinel_p4h_aa_login_") as tmp:
        harness = BrowserV3FixtureBackendBench(root=Path(tmp) / "fixture")
        runner = _runner(context, tmp, private_session_backend=harness.private_session_backend, login_backend=harness.login_backend)
        opened = _open_session(context, runner, ref_id)
        if not opened["binary_success"]:
            return opened
        login_snap = harness.capture_login_snapshot(f"{BASE_URL}/login")
        plan, plan_trace, snapshot_trace, login_ref = _login_plan(context, login_snap)
        session = _private_session_payload(context["bus"], AgentEventType.BROWSER_PRIVATE_SESSION_STARTED)
        login = _execute_single(
            context,
            action=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
            tool_id=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
            ref_id=ref_id,
            call=_call_for_action(
                context,
                tool_id=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
                action=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
                target=f"{BASE_URL}/login",
                ref_id=ref_id,
                arguments={
                    "session_id": session["session_id"],
                    "profile_id": session["profile_id"],
                    "private_session_trace_event_id": session["trace_event_id"],
                    "account_id": "acct_1",
                    "login_url": f"{BASE_URL}/login",
                    "plan": plan.model_dump(mode="json"),
                    "plan_trace_event_id": plan_trace,
                    "before_snapshot_trace_event_id": snapshot_trace,
                    "login_ref_id": login_ref,
                    "expected_effect": "account session authenticated",
                },
            ),
            runner=runner,
            gate_names=[BrowserV3AuthorityClass.LOGIN_AUTHORITY.value],
            step_count=8,
            notes="login_authority_routed_through_action_engine",
        )
        _close_session(context, runner, ref_id, session)
        return _merge_sequence(context, [opened, login], notes="login_authority_routed_through_action_engine", step_count=9)


def _mission_cookie_storage(iteration: int) -> dict[str, Any]:
    context = _build_context(iteration, {BrowserV3AuthorityClass.PRIVATE_SESSION, BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT})
    ref_id = _ref_by_role_name(context["snapshot"], "button", "Login")
    with _temporary_workspace("sentinel_p4h_aa_cookie_") as tmp:
        harness = BrowserV3FixtureBackendBench(root=Path(tmp) / "fixture")
        runner = _runner(context, tmp, private_session_backend=harness.private_session_backend, cookie_storage_backend=harness.cookie_storage_backend)
        opened = _open_session(context, runner, ref_id)
        if not opened["binary_success"]:
            return opened
        session = _private_session_payload(context["bus"], AgentEventType.BROWSER_PRIVATE_SESSION_STARTED)
        cookie = _execute_single(
            context,
            action=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
            tool_id=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
            ref_id=ref_id,
            call=_call_for_action(
                context,
                tool_id=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
                action=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
                target=f"{BASE_URL}/account",
                ref_id=ref_id,
                arguments={
                    "session_id": session["session_id"],
                    "profile_id": session["profile_id"],
                    "private_session_trace_event_id": session["trace_event_id"],
                    "operation": "redacted_summary",
                    "target_domain": DOMAIN,
                    "expected_effect": "redacted cookie/storage summary produced",
                },
            ),
            runner=runner,
            gate_names=[BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value],
            step_count=7,
            notes="cookie_storage_contract_routed_through_action_engine",
        )
        _close_session(context, runner, ref_id, session)
        return _merge_sequence(context, [opened, cookie], notes="cookie_storage_contract_routed_through_action_engine", step_count=8)


def _mission_js_no_network_denial(iteration: int) -> dict[str, Any]:
    context = _build_context(iteration, {BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED}, js_script=NETWORK_SCRIPT)
    ref_id = _ref_by_role_name(context["snapshot"], "button", "Inspect JS")
    with _temporary_workspace("sentinel_p4h_aa_js_") as tmp:
        harness = BrowserV3FixtureBackendBench(root=Path(tmp) / "fixture")
        runner = _runner(context, tmp, js_evaluate_backend=harness.js_evaluate_backend)
        result = _execute_single(
            context,
            action=BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value,
            tool_id=BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value,
            ref_id=ref_id,
            call=_call_for_action(
                context,
                tool_id=BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value,
                action=BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value,
                target=f"{BASE_URL}/js",
                ref_id=ref_id,
                arguments={
                    "page_url": f"{BASE_URL}/js",
                    "script_source": NETWORK_SCRIPT,
                    "expected_effect": "network attempt rejected",
                    "max_result_bytes": 2048,
                },
            ),
            runner=runner,
            gate_names=[BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value],
            step_count=5,
            notes="js_sandbox_network_attempt_denied_through_action_engine",
            expect_rejection_reason="browser_js_evaluate_network_call_detected",
        )
        result["denial_correctness"] = 1.0 if result["binary_success"] else 0.0
        result["denied"] = True
        return result


def _mission_har_body(iteration: int) -> dict[str, Any]:
    context = _build_context(iteration, {BrowserV3AuthorityClass.HAR_BODY_CAPTURE})
    ref_id = _ref_by_role_name(context["snapshot"], "button", "Inspect Network")
    with _temporary_workspace("sentinel_p4h_aa_har_") as tmp:
        harness = BrowserV3FixtureBackendBench(root=Path(tmp) / "fixture")
        runner = _runner(context, tmp, har_body_backend=harness.har_body_backend)
        return _execute_single(
            context,
            action=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
            tool_id=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
            ref_id=ref_id,
            call=_call_for_action(
                context,
                tool_id=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
                action=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
                target=f"{BASE_URL}/api",
                ref_id=ref_id,
                arguments={
                    "source_url": f"{BASE_URL}/api",
                    "allowed_mime_types": ["application/json"],
                    "max_bytes": 4096,
                    "max_records": 20,
                    "expected_effect": "redacted bounded HAR/body capture",
                },
            ),
            runner=runner,
            gate_names=[BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value],
            step_count=6,
            notes="har_body_capture_routed_through_action_engine",
        )


def _mission_cross_class(iteration: int) -> dict[str, Any]:
    actions = {
        BrowserV3AuthorityClass.PRIVATE_SESSION,
        BrowserV3AuthorityClass.LOGIN_AUTHORITY,
        BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT,
        BrowserV3AuthorityClass.HAR_BODY_CAPTURE,
    }
    context = _build_context(iteration, actions)
    ref_id = _ref_by_role_name(context["snapshot"], "button", "Login")
    har_ref = _ref_by_role_name(context["snapshot"], "button", "Inspect Network")
    with _temporary_workspace("sentinel_p4h_aa_cross_") as tmp:
        harness = BrowserV3FixtureBackendBench(root=Path(tmp) / "fixture")
        runner = _runner(
            context,
            tmp,
            private_session_backend=harness.private_session_backend,
            login_backend=harness.login_backend,
            cookie_storage_backend=harness.cookie_storage_backend,
            har_body_backend=harness.har_body_backend,
        )
        opened = _open_session(context, runner, ref_id)
        if not opened["binary_success"]:
            return opened
        login_snap = harness.capture_login_snapshot(f"{BASE_URL}/login")
        plan, plan_trace, snapshot_trace, login_ref = _login_plan(context, login_snap)
        session = _private_session_payload(context["bus"], AgentEventType.BROWSER_PRIVATE_SESSION_STARTED)
        login = _execute_single(
            context,
            action=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
            tool_id=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
            ref_id=ref_id,
            call=_call_for_action(
                context,
                tool_id=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
                action=BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
                target=f"{BASE_URL}/login",
                ref_id=ref_id,
                arguments={
                    "session_id": session["session_id"],
                    "profile_id": session["profile_id"],
                    "private_session_trace_event_id": session["trace_event_id"],
                    "account_id": "acct_1",
                    "login_url": f"{BASE_URL}/login",
                    "plan": plan.model_dump(mode="json"),
                    "plan_trace_event_id": plan_trace,
                    "before_snapshot_trace_event_id": snapshot_trace,
                    "login_ref_id": login_ref,
                },
            ),
            runner=runner,
            gate_names=[],
            step_count=8,
            notes="cross_login_routed",
        )
        cookie = _execute_single(
            context,
            action=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
            tool_id=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
            ref_id=ref_id,
            call=_call_for_action(
                context,
                tool_id=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
                action=BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
                target=f"{BASE_URL}/account",
                ref_id=ref_id,
                arguments={
                    "session_id": session["session_id"],
                    "profile_id": session["profile_id"],
                    "private_session_trace_event_id": session["trace_event_id"],
                    "target_domain": DOMAIN,
                },
            ),
            runner=runner,
            gate_names=[],
            step_count=7,
            notes="cross_cookie_routed",
        )
        har = _execute_single(
            context,
            action=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
            tool_id=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
            ref_id=har_ref,
            call=_call_for_action(
                context,
                tool_id=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
                action=BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
                target=f"{BASE_URL}/api",
                ref_id=har_ref,
                arguments={"source_url": f"{BASE_URL}/api", "allowed_mime_types": ["application/json"]},
            ),
            runner=runner,
            gate_names=[],
            step_count=6,
            notes="cross_har_routed",
        )
        closed = _close_session(context, runner, ref_id, session)
        return _merge_sequence(
            context,
            [opened, login, cookie, har, closed],
            notes="private_login_cookie_har_close_routed_through_action_engine",
            step_count=14,
            cross_class=True,
        )


def _mission_out_of_policy_denial(iteration: int) -> dict[str, Any]:
    context = _build_context(iteration, {BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE})
    ref_id = _ref_by_role_name(context["snapshot"], "button", "Upload")
    call = _call_for_action(
        context,
        tool_id=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
        action=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value,
        target=f"{BASE_URL}/upload",
        ref_id=ref_id,
        arguments={"expected_effect": "should not execute"},
        compile_trace=False,
    )
    prepared = ActionEngine().prepare_browser_action(
        frame=context["frame"],
        candidate=_candidate(context, action=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value, tool_id=BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value, ref_id=ref_id),
        policy=context["policy"],
        canonical_call=call,
    )
    denied = not prepared.accepted and "action_class_out_of_scope" in prepared.errors
    return _denial_metrics(denied, notes="out_of_policy_v3_action_rejected_by_action_engine")


def _execute_single(
    context: dict[str, Any],
    *,
    action: str,
    tool_id: str,
    ref_id: str,
    call: CanonicalToolCall,
    runner: BrowserControlledCapabilityRunner,
    gate_names: list[str],
    step_count: int,
    notes: str,
    expect_rejection_reason: str | None = None,
) -> dict[str, Any]:
    prepared = ActionEngine().prepare_browser_action(
        frame=context["frame"],
        candidate=_candidate(context, action=action, tool_id=tool_id, ref_id=ref_id, planned_step_count=max(1, step_count)),
        policy=context["policy"],
        canonical_call=call,
    )
    if not prepared.accepted or prepared.envelope is None:
        return _failure_metrics(f"prepare_failed:{prepared.reason}:{','.join(prepared.errors)}")
    executed = ActionEngine().execute_browser_action(
        action_envelope=prepared.envelope,
        mission_envelope=context["authority"],
        runner=runner,
        event_bus=context["bus"],
    )
    expected_denial = expect_rejection_reason is not None
    if expected_denial:
        denial_ok = (not executed.accepted) and executed.controlled_result is not None and executed.controlled_result.reason == expect_rejection_reason
        gate_ok = _all_gates_pass(context, gate_names)
        return {
            "binary_success": bool(denial_ok and gate_ok and context["bus"].verify_chain()),
            "action_success_rate": 1.0 if denial_ok else 0.0,
            "operator_tempo": _tempo(step_count),
            "action_envelope_count": 1,
            "v3_action_count": 1,
            "v3_receipt_completeness": 1.0,
            "finalgate_pass_rate": 1.0 if gate_ok else 0.0,
            "authority_correctness": 1.0 if denial_ok else 0.0,
            "false_action_rate": 0.0 if denial_ok else 1.0,
            "proof_completeness": 1.0 if gate_ok else 0.0,
            "denial_correctness": 1.0 if denial_ok else 0.0,
            "cross_class_success": 0.0,
            "step_count": step_count,
            "executed": False,
            "denied": denial_ok,
            "final_gate_passed": gate_ok,
            "notes": notes,
        }
    if not executed.accepted:
        return _failure_metrics(f"execute_failed:{executed.reason}:{','.join(executed.errors)}")
    gate_ok = _all_gates_pass(context, gate_names)
    receipt_ok = bool(executed.controlled_result and executed.controlled_result.receipt_id)
    success = bool(gate_ok and receipt_ok and context["bus"].verify_chain())
    return {
        "binary_success": success,
        "action_success_rate": 1.0 if executed.accepted else 0.0,
        "operator_tempo": _tempo(step_count),
        "action_envelope_count": 1,
        "v3_action_count": 1,
        "v3_receipt_completeness": 1.0 if receipt_ok else 0.0,
        "finalgate_pass_rate": 1.0 if gate_ok else 0.0,
        "authority_correctness": 1.0,
        "false_action_rate": 0.0,
        "proof_completeness": 1.0 if gate_ok else 0.0,
        "denial_correctness": 0.0,
        "cross_class_success": 0.0,
        "step_count": step_count,
        "executed": True,
        "denied": False,
        "final_gate_passed": gate_ok,
        "notes": notes,
    }


def _open_session(context: dict[str, Any], runner: BrowserControlledCapabilityRunner, ref_id: str) -> dict[str, Any]:
    return _execute_single(
        context,
        action=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
        tool_id=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
        ref_id=ref_id,
        call=_call_for_action(
            context,
            tool_id=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
            action=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
            target=f"{BASE_URL}/session",
            ref_id=ref_id,
            arguments={"operation": "open", "allowed_domains": [DOMAIN], "storage_enabled": True},
        ),
        runner=runner,
        gate_names=[],
        step_count=4,
        notes="private_session_open_routed",
    )


def _close_session(
    context: dict[str, Any],
    runner: BrowserControlledCapabilityRunner,
    ref_id: str,
    session: dict[str, Any],
) -> dict[str, Any]:
    return _execute_single(
        context,
        action=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
        tool_id=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
        ref_id=ref_id,
        call=_call_for_action(
            context,
            tool_id=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
            action=BrowserV3AuthorityClass.PRIVATE_SESSION.value,
            target=f"{BASE_URL}/session",
            ref_id=ref_id,
            arguments={
                "operation": "close",
                "session_id": session["session_id"],
                "profile_id": session["profile_id"],
                "allowed_domains": [DOMAIN],
                "storage_enabled": True,
            },
        ),
        runner=runner,
        gate_names=[BrowserV3AuthorityClass.PRIVATE_SESSION.value],
        step_count=5,
        notes="private_session_close_routed",
    )


def _build_context(iteration: int, actions: set[BrowserV3AuthorityClass], *, js_script: str = SAFE_SCRIPT) -> dict[str, Any]:
    mission_id = f"mission_p4h_aa_{iteration:03d}_{abs(hash(tuple(sorted(action.value for action in actions)))) % 10000}"
    bus = EventBus(mission_id)
    snapshot = BrowserAccessibilitySnapshotBuilder().build(html=_html(), text="V3 Actions Email Send request Download report Upload Login Inspect JS Inspect Network")
    snapshot_trace_id = _append_snapshot_event(bus, mission_id, snapshot)
    action_classes_by_ref: dict[str, list[str]] = {}
    for ref_id, ref in snapshot.refs.items():
        role = ref.role
        name = ref.name or ""
        if BrowserV3AuthorityClass.FORM_SUBMIT in actions and role == "button" and name == "Send request":
            action_classes_by_ref.setdefault(ref_id, []).append(BrowserV3AuthorityClass.FORM_SUBMIT.value)
        if BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE in actions and role == "link":
            action_classes_by_ref.setdefault(ref_id, []).append(BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value)
        if BrowserV3AuthorityClass.UPLOAD_AUTHORIZED in actions and role == "button" and name == "Upload":
            action_classes_by_ref.setdefault(ref_id, []).append(BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value)
        if BrowserV3AuthorityClass.LOGIN_AUTHORITY in actions and role == "button" and name == "Login":
            action_classes_by_ref.setdefault(ref_id, []).append(BrowserV3AuthorityClass.LOGIN_AUTHORITY.value)
        if BrowserV3AuthorityClass.PRIVATE_SESSION in actions and role == "button" and name == "Login":
            action_classes_by_ref.setdefault(ref_id, []).append(BrowserV3AuthorityClass.PRIVATE_SESSION.value)
        if BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT in actions and role == "button" and name == "Login":
            action_classes_by_ref.setdefault(ref_id, []).append(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value)
        if BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED in actions and role == "button" and name == "Inspect JS":
            action_classes_by_ref.setdefault(ref_id, []).append(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value)
        if BrowserV3AuthorityClass.HAR_BODY_CAPTURE in actions and role == "button" and name == "Inspect Network":
            action_classes_by_ref.setdefault(ref_id, []).append(BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value)
    ui_set = BrowserUIObservationBuilder().from_accessibility_snapshot(
        mission_id=mission_id,
        url=BASE_URL,
        snapshot=snapshot,
        event_bus=bus,
        trace_refs=[snapshot_trace_id],
    )
    frame = BrowserPerceptionAdapter().build_frame(
        ui_observation_set=ui_set,
        action_classes_by_ref=action_classes_by_ref,
    )
    authority = _envelope(mission_id, actions, js_script=js_script)
    return {
        "mission_id": mission_id,
        "bus": bus,
        "snapshot": snapshot,
        "snapshot_trace_id": snapshot_trace_id,
        "frame": frame,
        "authority": authority,
        "policy": CompiledMissionPolicyCompiler().compile(authority, trace_refs=[snapshot_trace_id]),
    }


def _html() -> str:
    return """
    <html><body>
      <main>
        <h1>V3 Actions</h1>
        <input type="text" placeholder="Email" />
        <button>Send request</button>
        <a href="/report.pdf">Download report</a>
        <input type="file" aria-label="Upload file" />
        <button>Upload</button>
        <button>Login</button>
        <button>Inspect JS</button>
        <button>Inspect Network</button>
      </main>
    </body></html>
    """


def _envelope(
    mission_id: str,
    actions: set[BrowserV3AuthorityClass],
    *,
    allowed_artifact_ids: list[str] | None = None,
    js_script: str = SAFE_SCRIPT,
) -> MissionAuthorityEnvelope:
    grants = [
        _grant(action, allowed_artifact_ids=allowed_artifact_ids or [], allowed_script_hashes=[_script_hash(SAFE_SCRIPT), _script_hash(NETWORK_SCRIPT), _script_hash(js_script)])
        for action in actions
    ]
    tools = sorted(_tool_id_for_action(action.value) for action in actions)
    return MissionAuthorityEnvelope(
        id=mission_id,
        user_id="user_p4h_aa",
        mission_type=MissionType.RESEARCH_SUMMARY,
        mission_title="P4H-AA Browser V3 ActionEngine routing",
        mission_objective="Route existing Browser V3 authority classes through ActionEngine.",
        success_criteria=["V3 authority action is prepared, executed or denied, and FinalGate-certified."],
        mode=MissionMode.POWER,
        allowed_systems=["public_web", "local_workspace"],
        allowed_tools=tools,
        allowed_actions=sorted(action.value for action in actions),
        forbidden_actions=["payment"],
        allowed_domains=[DOMAIN],
        allowed_accounts=["acct_1"],
        allowed_paths=["data/generated_projects"],
        risk_appetite_score=90,
        max_actions=80,
        max_duration_minutes=10,
        max_cost_usd=1.0,
        browser_v3_authority_grants=[grant.model_dump(mode="json") for grant in grants],
    )


def _grant(authority_class: BrowserV3AuthorityClass, **overrides: Any) -> BrowserV3AuthorityGrant:
    data: dict[str, Any] = {
        "id": f"grant_{authority_class.value}",
        "authority_class": authority_class,
        "allowed_domains": [DOMAIN],
        "allowed_accounts": ["acct_1"],
        "allowed_mime_types": ["application/pdf", "application/json", "text/html"],
        "allowed_script_hashes": [_script_hash(SAFE_SCRIPT)],
        "allowed_artifact_ids": [],
        "max_bytes": 4096,
        "max_records": 20,
        "max_result_bytes": 2048,
        "quarantine_path": "browser/download_quarantine",
        "session_scope": "per_mission",
        "storage_allowed": True,
        "redaction_required": True,
        "blocked_flow_types": ["payment"],
    }
    data.update(overrides)
    return BrowserV3AuthorityGrant(**data)


def _runner(context: dict[str, Any], tmp: str | Path, **backends: Any) -> BrowserControlledCapabilityRunner:
    return BrowserControlledCapabilityRunner(
        registry=default_tool_registry(),
        capture_root=Path(tmp) / "captures",
        **backends,
    )


def _call_for_action(
    context: dict[str, Any],
    *,
    tool_id: str,
    action: str,
    target: str,
    ref_id: str,
    arguments: dict[str, Any],
    compile_trace: bool = True,
) -> CanonicalToolCall:
    args = {
        "context_pack_id": CONTEXT_PACK_ID,
        "authority_grant_id": f"grant_{action}",
        "allowed_domains": [DOMAIN],
        "ref_id": ref_id,
        **arguments,
    }
    if compile_trace:
        compiled_id = _compiled_event(context["bus"], CONTEXT_PACK_ID, "c" * 64).id
        args["compiled_intent_trace_id"] = compiled_id
    payload = {
        "tool_id": tool_id,
        "action": action,
        "arguments": args,
        "capability": action,
        "target": target,
        "requested_side_effects": [],
    }
    return CanonicalToolCall(
        tool_id=tool_id,
        action=action,
        arguments=args,
        capability=action,
        target=target,
        requested_side_effects=[],
        canonical_hash=_hash_payload(payload),
    )


def _candidate(
    context: dict[str, Any],
    *,
    action: str,
    tool_id: str,
    ref_id: str,
    planned_step_count: int = 1,
) -> SceneActionCandidate:
    target = context["frame"].target_by_ref(ref_id)
    if target is None:
        target = context["frame"].targets[0]
    return SceneActionCandidate(
        mission_id=context["mission_id"],
        perception_frame_id=context["frame"].id,
        source_type=PerceptionSourceType.BROWSER,
        target_id=target.id,
        runtime_ref_id=ref_id,
        action_class=action,
        tool_id=tool_id,
        intent=f"Route {action} through ActionEngine.",
        expected_effect="V3 authority class executes or denies inside compiled mission policy.",
        confidence_score=max(target.confidence.overall, 0.8),
        required_confidence=0.5,
        planned_step_count=planned_step_count,
    )


def _plan(context: dict[str, Any], *, steps: list[BrowserInteractionStep], final_url: str):
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=context["mission_id"],
        snapshot=context["snapshot"],
        steps=steps,
        event_bus=context["bus"],
        final_url=final_url,
        snapshot_trace_id=context["snapshot_trace_id"],
    )
    if not result.accepted or result.plan is None or result.trace_event_id is None:
        raise RuntimeError(f"plan_rejected:{result.reason}:{','.join(result.errors)}")
    return result.plan, result.trace_event_id


def _login_plan(context: dict[str, Any], snap):
    snapshot_event_id = _append_snapshot_event(context["bus"], context["mission_id"], snap)
    login_ref = _first_ref(snap, "button")
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=context["mission_id"],
        snapshot=snap,
        steps=[BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=login_ref), reason="Submit login by account_id.")],
        event_bus=context["bus"],
        final_url=f"{BASE_URL}/login",
        snapshot_trace_id=snapshot_event_id,
    )
    if not result.accepted or result.plan is None or result.trace_event_id is None:
        raise RuntimeError(f"login_plan_rejected:{result.reason}:{','.join(result.errors)}")
    return result.plan, result.trace_event_id, snapshot_event_id, login_ref


def _source_artifact(capture: ArtifactCaptureSandbox, bus: EventBus) -> CapturedArtifact:
    result = capture.capture_binary(
        relative_path="browser/download_quarantine/source.pdf",
        data=PDF_BYTES,
        artifact_type="browser_download_quarantine",
        content_type="application/pdf",
        event_bus=bus,
        phase=AgentPhase.EXECUTING,
    )
    if not result.accepted or result.artifact is None:
        raise RuntimeError("source_artifact_capture_failed")
    return result.artifact


def _append_snapshot_event(bus: EventBus, mission_id: str, snapshot) -> str:
    event = bus.append(
        AgentEventType.BROWSER_SNAPSHOT_CAPTURED,
        "P4H-AA V3 action routing snapshot captured.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": f"receipt_{mission_id}",
            "snapshot_artifact_id": f"artifact_{mission_id}",
            "snapshot_artifact_sha256": "a" * 64,
            "accessibility_snapshot_sha256": snapshot.snapshot_sha256,
            "accessibility_page_sha256": snapshot.page_sha256,
            "accessibility_ref_count": snapshot.stats.refs,
            "accessibility_interactive_count": snapshot.stats.interactive,
            "accessibility_ref_ids": sorted(snapshot.refs),
            "mission_id": mission_id,
        },
    )
    return event.id


def _compiled_event(bus: EventBus, context_pack_id: str, canonical_hash: str):
    return bus.append(
        AgentEventType.TOOL_INTENT_COMPILED,
        "P4H-AA brain-authored V3 intent compiled.",
        phase_before=AgentPhase.TOOL_SELECTING,
        phase_after=AgentPhase.TOOL_SELECTING,
        payload={
            "accepted": True,
            "context_pack_id": context_pack_id,
            "canonical_hash": canonical_hash,
            "compilation_hash": "d" * 64,
        },
    )


def _all_gates_pass(context: dict[str, Any], gate_names: list[str]) -> bool:
    trace = SimpleNamespace(trace=tuple(context["bus"].events()))
    for name in gate_names:
        if name == BrowserV3AuthorityClass.FORM_SUBMIT.value and not CoreFinalGate._browser_v3_form_submit_contract(trace).passed:
            return False
        if name == BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE.value and not CoreFinalGate._browser_v3_download_quarantine_contract(trace).passed:
            return False
        if name == BrowserV3AuthorityClass.UPLOAD_AUTHORIZED.value and not CoreFinalGate._browser_v3_upload_authorized_contract(trace).passed:
            return False
        if name == BrowserV3AuthorityClass.PRIVATE_SESSION.value and not CoreFinalGate._browser_v3_private_session_contract(trace).passed:
            return False
        if name == BrowserV3AuthorityClass.LOGIN_AUTHORITY.value and not CoreFinalGate._browser_v3_login_authority_contract(trace).passed:
            return False
        if name == BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value and not CoreFinalGate._browser_v3_cookie_storage_contract(trace).passed:
            return False
        if name == BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value and not CoreFinalGate._browser_v3_js_evaluate_sandboxed_contract(trace).passed:
            return False
        if name == BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value and not CoreFinalGate._browser_v3_har_body_capture_contract(trace).passed:
            return False
    return True


def _merge_sequence(context: dict[str, Any], items: list[dict[str, Any]], *, notes: str, step_count: int, cross_class: bool = False) -> dict[str, Any]:
    gates = [
        BrowserV3AuthorityClass.PRIVATE_SESSION.value,
        BrowserV3AuthorityClass.LOGIN_AUTHORITY.value,
        BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value,
        BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value,
    ]
    gate_ok = _all_gates_pass(context, gates)
    success = all(item["binary_success"] for item in items) and gate_ok and context["bus"].verify_chain()
    return {
        "binary_success": bool(success),
        "action_success_rate": 1.0 if all(item["action_success_rate"] == 1.0 for item in items) else 0.0,
        "operator_tempo": _tempo(step_count),
        "action_envelope_count": sum(item["action_envelope_count"] for item in items),
        "v3_action_count": sum(item["v3_action_count"] for item in items),
        "v3_receipt_completeness": 1.0 if all(item["v3_receipt_completeness"] == 1.0 for item in items) else 0.0,
        "finalgate_pass_rate": 1.0 if gate_ok else 0.0,
        "authority_correctness": 1.0,
        "false_action_rate": 0.0,
        "proof_completeness": 1.0 if gate_ok else 0.0,
        "denial_correctness": 0.0,
        "cross_class_success": 1.0 if cross_class and success else 0.0,
        "step_count": step_count,
        "executed": True,
        "denied": False,
        "final_gate_passed": gate_ok,
        "notes": notes,
    }


def _private_session_payload(bus: EventBus, event_type: AgentEventType) -> dict[str, Any]:
    event = next(event for event in reversed(bus.events()) if event.event_type == event_type)
    payload = dict(event.payload)
    payload["trace_event_id"] = event.id
    return payload


def _tool_id_for_action(action: str) -> str:
    if action == BrowserV3AuthorityClass.FORM_SUBMIT.value:
        return "browser_public_form_submit"
    return action


def _first_ref(snapshot, role: str) -> str:
    for ref_id, ref in snapshot.refs.items():
        if ref.role == role:
            return ref_id
    raise AssertionError(f"missing ref for role {role}")


def _ref_by_role_name(snapshot, role: str, name: str) -> str:
    for ref_id, ref in snapshot.refs.items():
        if ref.role == role and ref.name == name:
            return ref_id
    raise AssertionError(f"missing ref for {role}:{name}")


def _script_hash(script: str) -> str:
    return hashlib.sha256(script.encode("utf-8")).hexdigest()


def _hash_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")).hexdigest()


def _denial_metrics(denied: bool, *, notes: str) -> dict[str, Any]:
    return {
        "binary_success": denied,
        "action_success_rate": 1.0 if denied else 0.0,
        "operator_tempo": 1.0,
        "action_envelope_count": 0,
        "v3_action_count": 0,
        "v3_receipt_completeness": 1.0 if denied else 0.0,
        "finalgate_pass_rate": 1.0 if denied else 0.0,
        "authority_correctness": 1.0 if denied else 0.0,
        "false_action_rate": 0.0 if denied else 1.0,
        "proof_completeness": 1.0 if denied else 0.0,
        "denial_correctness": 1.0 if denied else 0.0,
        "cross_class_success": 0.0,
        "step_count": 2,
        "executed": False,
        "denied": denied,
        "final_gate_passed": denied,
        "notes": notes,
    }


def _failure_metrics(notes: str) -> dict[str, Any]:
    return {
        "binary_success": False,
        "action_success_rate": 0.0,
        "operator_tempo": 0.0,
        "action_envelope_count": 0,
        "v3_action_count": 0,
        "v3_receipt_completeness": 0.0,
        "finalgate_pass_rate": 0.0,
        "authority_correctness": 0.0,
        "false_action_rate": 1.0,
        "proof_completeness": 0.0,
        "denial_correctness": 0.0,
        "cross_class_success": 0.0,
        "step_count": 1,
        "executed": False,
        "denied": False,
        "final_gate_passed": False,
        "notes": notes,
    }


def _tempo(step_count: int) -> float:
    if step_count <= 6:
        return 1.0
    if step_count <= 9:
        return 0.9
    if step_count <= 14:
        return 0.8
    return 0.65


def _avg(results: list[BrowserV3ActionRoutingResult], field: str) -> float:
    return round(mean(float(getattr(result, field)) for result in results), 4)


def _avg_for(results: list[BrowserV3ActionRoutingResult], field: str, mission_ids: set[str]) -> float:
    selected = [result for result in results if result.mission_id in mission_ids]
    if not selected:
        return 0.0
    return _avg(selected, field)


def _mission_score(mission_id: str, items: list[BrowserV3ActionRoutingResult]) -> dict[str, Any]:
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
        "v3_receipt_completeness": _avg(items, "v3_receipt_completeness"),
        "finalgate_pass_rate": _avg(items, "finalgate_pass_rate"),
        "denial_correctness": _avg(items, "denial_correctness"),
        "false_action_rate": _avg(items, "false_action_rate"),
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
    parser = argparse.ArgumentParser(description="Run P4H-AA Browser V3 ActionEngine routing benchmark.")
    parser.add_argument("--run-count", type=int, default=DEFAULT_RUN_COUNT)
    parser.add_argument("--out-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    results = run_v3_action_routing(run_count=args.run_count)
    scorecard = write_v3_action_routing_outputs(results, args.out_dir)
    print(json.dumps(scorecard, indent=2, sort_keys=True))
    return 0 if scorecard["verdict"] == "browser_v3_action_engine_routing_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
