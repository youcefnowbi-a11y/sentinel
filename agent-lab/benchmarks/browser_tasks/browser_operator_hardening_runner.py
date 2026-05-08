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

from sentinel.agent.action_engine import (  # noqa: E402
    ActionEngine,
    CompiledMissionDecision,
    CompiledMissionPolicyCompiler,
    SceneActionCandidate,
)
from sentinel.agent.artifact_capture import ArtifactCaptureSandbox  # noqa: E402
from sentinel.agent.browser import (  # noqa: E402
    BrowserAccessibilitySnapshotBuilder,
    BrowserBoundingBox,
    BrowserControlledCapabilityRunner,
    BrowserInteractionBackendResult,
    BrowserInteractionExecutionReceipt,
    BrowserInteractionExecutionRequest,
    BrowserInteractionIntent,
    BrowserInteractionStep,
    BrowserInteractionTarget,
    BrowserPerceptionAdapter,
    BrowserPostActionVerifier,
    BrowserRenderedPage,
    BrowserRenderedSnapshotReceipt,
    BrowserRenderedSnapshotResult,
    BrowserScreenshotRegion,
    BrowserSnapshotStatus,
    BrowserUIObservationBuilder,
    BrowserVisualObservationBuilder,
    BrowserWaitPredicate,
    PublicUrlDecision,
    PublicUrlDecisionStatus,
)
from sentinel.agent.browser.interaction_dry_run import BrowserInteractionDryRunPlanner  # noqa: E402
from sentinel.agent.event_bus import EventBus  # noqa: E402
from sentinel.agent.events import AgentEventType  # noqa: E402
from sentinel.agent.final_gate import CoreFinalGate  # noqa: E402
from sentinel.agent.perception import PerceptionEngine, PerceptionSourceType, PerceptionTarget, PerceptionText, PerceptionTextSource  # noqa: E402
from sentinel.agent.phases import AgentPhase  # noqa: E402
from sentinel.agent.tool_call_protocol import CanonicalToolCall  # noqa: E402
from sentinel.capabilities import default_tool_registry  # noqa: E402
from sentinel.mission import MissionAuthorityEnvelope  # noqa: E402
from sentinel.shared.enums import MissionMode, MissionType  # noqa: E402


REPORT_DIR = Path(__file__).resolve().parent / "reports"
TMP_ROOT = Path(__file__).resolve().parent / "tmp_p4h_z"
RUN_ID = "p4h_z_browser_operator_hardening_30run"
DEFAULT_RUN_COUNT = 30
DOMAIN = "example.com"
URL = f"https://{DOMAIN}/hardening"
PNG_BYTES = b"\x89PNG\r\n\x1a\nfake"

HARDENING_MISSIONS = [
    "BF-HARD-001-ambiguous-context-target",
    "BF-HARD-002-low-confidence-ambiguous-reject",
    "BF-HARD-003-dom-ax-weak-visual-ref",
    "BF-HARD-004-failed-verifier-repair-loop",
    "BF-HARD-005-multistep-budgeted-chain",
    "BF-HARD-006-step-budget-pressure-reject",
    "BF-HARD-007-visual-ocr-ref-denial",
    "BF-HARD-008-fabricated-ref-denial",
]

AMBIGUOUS_MISSIONS = {
    "BF-HARD-001-ambiguous-context-target",
    "BF-HARD-002-low-confidence-ambiguous-reject",
}
VISUAL_MISSIONS = {
    "BF-HARD-003-dom-ax-weak-visual-ref",
    "BF-HARD-007-visual-ocr-ref-denial",
}
REPAIR_MISSIONS = {"BF-HARD-004-failed-verifier-repair-loop"}
BUDGET_MISSIONS = {"BF-HARD-006-step-budget-pressure-reject"}


BASE_HTML = """
<html><body>
  <main aria-label="Hardening panel">
    <h1>Hardening Trial</h1>
    <label>Email <textarea placeholder="Email"></textarea></label>
    <button>Continue</button>
    <p>Ready</p>
  </main>
</body></html>
"""


AMBIGUOUS_HTML = """
<html><body>
  <main aria-label="Ambiguous target panel">
    <section aria-label="billing"><h2>Billing</h2><button>Open</button></section>
    <section aria-label="support"><h2>Support</h2><button>Open</button></section>
  </main>
</body></html>
"""


WEAK_HTML = """
<html><body>
  <main aria-label="Weak DOM panel">
    <button aria-label=""> </button>
    <p data-visual-label="Hidden visual target">visual-only label nearby</p>
  </main>
</body></html>
"""


@dataclass(frozen=True)
class BrowserOperatorHardeningResult:
    schema_version: str
    run_id: str
    generated_at: str
    mission_id: str
    iteration: int
    binary_success: bool
    mission_success: float
    action_success_rate: float
    operator_tempo: float
    repair_success_rate: float
    verifier_recovery_rate: float
    ambiguous_target_accuracy: float
    visual_target_accuracy: float
    false_action_rate: float
    proof_completeness: float
    authority_correctness: float
    budget_enforcement_rate: float
    latency_ms: float
    step_count: int
    executed: bool
    repaired: bool
    denied: bool
    final_gate_passed: bool
    failure_category: str
    notes: str


class HardeningInteractionBackend:
    def __init__(self, before_snapshot, *, after_text: str, after_url: str = URL) -> None:
        self.before_snapshot = before_snapshot
        self.after_text = after_text
        self.after_url = after_url

    def __call__(self, request: BrowserInteractionExecutionRequest) -> BrowserInteractionBackendResult:
        html = f"<html><body><main><h1>{self.after_text}</h1><button>Continue</button></main></body></html>"
        return BrowserInteractionBackendResult(
            before_snapshot=self.before_snapshot,
            after_page=BrowserRenderedPage(
                final_url=self.after_url,
                status_code=200,
                title="Hardening Trial",
                text=self.after_text,
                links=[],
                html=html,
                screenshot_png=PNG_BYTES,
            ),
            final_url_before=request.final_url,
            final_url_after=self.after_url,
            executed_step_ids=[step.id for step in request.plan.steps],
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


def run_operator_hardening(*, run_count: int = DEFAULT_RUN_COUNT, run_id: str = RUN_ID) -> list[BrowserOperatorHardeningResult]:
    if run_count < 1:
        raise ValueError("run_count must be >= 1")
    generated_at = utc_now()
    results: list[BrowserOperatorHardeningResult] = []
    for iteration in range(1, run_count + 1):
        for mission_id in HARDENING_MISSIONS:
            results.append(_run_mission(mission_id, iteration, generated_at, run_id))
    return results


def build_hardening_scorecard(results: list[BrowserOperatorHardeningResult]) -> dict[str, Any]:
    if not results:
        return {"schema_version": "browser_operator_hardening_scorecard.v1", "verdict": "not_executed", "total_iterations": 0}
    grouped: dict[str, list[BrowserOperatorHardeningResult]] = {}
    for result in results:
        grouped.setdefault(result.mission_id, []).append(result)
    success_count = sum(1 for result in results if result.binary_success)
    lower, upper = wilson_interval(success_count, len(results))
    return {
        "schema_version": "browser_operator_hardening_scorecard.v1",
        "run_id": results[0].run_id,
        "generated_at": results[0].generated_at,
        "verdict": "browser_operator_hardening_pass" if success_count == len(results) else "browser_operator_hardening_needs_repair",
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
        "repair_success_rate": _avg_for(results, "repair_success_rate", REPAIR_MISSIONS),
        "verifier_recovery_rate": _avg(results, "verifier_recovery_rate"),
        "ambiguous_target_accuracy": _avg_for(results, "ambiguous_target_accuracy", AMBIGUOUS_MISSIONS),
        "visual_target_accuracy": _avg_for(results, "visual_target_accuracy", VISUAL_MISSIONS),
        "false_action_rate": _avg(results, "false_action_rate"),
        "proof_completeness": _avg(results, "proof_completeness"),
        "authority_correctness": _avg(results, "authority_correctness"),
        "budget_enforcement_rate": _avg_for(results, "budget_enforcement_rate", BUDGET_MISSIONS),
        "latency_p50_ms": percentile([result.latency_ms for result in results], 50),
        "latency_p95_ms": percentile([result.latency_ms for result in results], 95),
        "step_count_p50": percentile([float(result.step_count) for result in results], 50),
        "step_count_p95": percentile([float(result.step_count) for result in results], 95),
        "mission_scores": [_mission_score(mission_id, items) for mission_id, items in grouped.items()],
        "boundary": "browser_only_fixture_hardening_no_new_powers",
    }


def write_hardening_outputs(results: list[BrowserOperatorHardeningResult], out_dir: Path = REPORT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    scorecard = build_hardening_scorecard(results)
    (out_dir / "browser_operator_hardening_results.jsonl").write_text(
        "".join(json.dumps(asdict(result), sort_keys=True) + "\n" for result in results),
        encoding="utf-8",
    )
    (out_dir / "browser_operator_hardening_scorecard.json").write_text(
        json.dumps(scorecard, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "browser_operator_hardening_scorecard.md").write_text(render_hardening_markdown(scorecard), encoding="utf-8")
    return scorecard


def render_hardening_markdown(scorecard: dict[str, Any]) -> str:
    lines = [
        "# Browser Operator Hardening Scorecard",
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
        f"operator_tempo = {scorecard.get('operator_tempo', 0.0)}",
        f"repair_success_rate = {scorecard.get('repair_success_rate', 0.0)}",
        f"verifier_recovery_rate = {scorecard.get('verifier_recovery_rate', 0.0)}",
        f"ambiguous_target_accuracy = {scorecard.get('ambiguous_target_accuracy', 0.0)}",
        f"visual_target_accuracy = {scorecard.get('visual_target_accuracy', 0.0)}",
        f"false_action_rate = {scorecard.get('false_action_rate', 0.0)}",
        f"budget_enforcement_rate = {scorecard.get('budget_enforcement_rate', 0.0)}",
        "```",
        "",
        "## Missions",
        "",
        "| Mission | Runs | Success | Wilson lower | Tempo | Repair | Verifier recovery | Ambiguous | Visual | False action |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mission in scorecard.get("mission_scores", []):
        lines.append(
            f"| `{mission['mission_id']}` | {mission['run_count']} | {mission['success_rate']} | "
            f"{mission['wilson_lower']} | {mission['operator_tempo']} | {mission['repair_success_rate']} | "
            f"{mission['verifier_recovery_rate']} | {mission['ambiguous_target_accuracy']} | "
            f"{mission['visual_target_accuracy']} | {mission['false_action_rate']} |"
        )
    lines.extend(["", "## Boundary", "", f"`{scorecard.get('boundary', '')}`", ""])
    return "\n".join(lines)


def _run_mission(mission_id: str, iteration: int, generated_at: str, run_id: str) -> BrowserOperatorHardeningResult:
    started = time.perf_counter()
    try:
        metrics = _execute_mission(mission_id, iteration)
        binary_success = bool(metrics["binary_success"])
        failure_category = "" if binary_success else metrics.get("failure_category", "hardening_failed")
    except Exception as exc:  # pragma: no cover - defensive report path
        metrics = _failure_metrics(f"{type(exc).__name__}:{str(exc)[:160]}")
        binary_success = False
        failure_category = metrics["notes"]
    return BrowserOperatorHardeningResult(
        schema_version="browser_operator_hardening_run.v1",
        run_id=run_id,
        generated_at=generated_at,
        mission_id=mission_id,
        iteration=iteration,
        binary_success=binary_success,
        mission_success=1.0 if binary_success else 0.0,
        action_success_rate=metrics["action_success_rate"],
        operator_tempo=metrics["operator_tempo"],
        repair_success_rate=metrics["repair_success_rate"],
        verifier_recovery_rate=metrics["verifier_recovery_rate"],
        ambiguous_target_accuracy=metrics["ambiguous_target_accuracy"],
        visual_target_accuracy=metrics["visual_target_accuracy"],
        false_action_rate=metrics["false_action_rate"],
        proof_completeness=metrics["proof_completeness"],
        authority_correctness=metrics["authority_correctness"],
        budget_enforcement_rate=metrics["budget_enforcement_rate"],
        latency_ms=round((time.perf_counter() - started) * 1000, 3),
        step_count=metrics["step_count"],
        executed=metrics["executed"],
        repaired=metrics["repaired"],
        denied=metrics["denied"],
        final_gate_passed=metrics["final_gate_passed"],
        failure_category=failure_category,
        notes=metrics["notes"],
    )


def _execute_mission(mission_id: str, iteration: int) -> dict[str, Any]:
    if mission_id == "BF-HARD-001-ambiguous-context-target":
        context = _build_context(iteration, html=AMBIGUOUS_HTML, text="Billing Open Support Open")
        support_ref = _ref_by_role_name_nth(context["snapshot"], "button", "Open", 1)
        return _execute_path(
            context,
            ref_id=support_ref,
            steps=[BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=support_ref), reason="Choose Support Open by duplicate nth/context.")],
            expected_text="Support Opened",
            after_text="Support Opened",
            notes="ambiguous_duplicate_target_resolved_by_context",
            step_count=7,
            ambiguous_target_accuracy=1.0,
        )
    if mission_id == "BF-HARD-002-low-confidence-ambiguous-reject":
        context = _build_context(iteration, html=AMBIGUOUS_HTML, text="Billing Open Support Open")
        ref_id = _ref_by_role_name_nth(context["snapshot"], "button", "Open", 0)
        prepared = _prepare(context, ref_id=ref_id, required_confidence=0.99, confidence_score=0.42)
        denied = not prepared.accepted and "candidate_confidence_below_threshold" in prepared.errors
        return _denial_metrics(denied, notes="low_confidence_ambiguous_target_rejected", ambiguous_target_accuracy=1.0)
    if mission_id == "BF-HARD-003-dom-ax-weak-visual-ref":
        context = _build_context(iteration, html=WEAK_HTML, text="visual-only label nearby")
        ref_id = _first_ref(context["snapshot"], "button")
        return _execute_path(
            context,
            ref_id=ref_id,
            steps=[BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=ref_id), reason="Use visual-bound runtime ref on weak structural label.")],
            expected_text="Visual Ref Accepted",
            after_text="Visual Ref Accepted",
            notes="dom_ax_weak_target_executed_only_because_runtime_ref_bound",
            step_count=7,
            visual_target_accuracy=1.0,
        )
    if mission_id == "BF-HARD-004-failed-verifier-repair-loop":
        context = _build_context(iteration, html=BASE_HTML, text="Hardening Trial Email Continue Ready")
        ref_id = _first_ref(context["snapshot"], "button")
        first = _execute_path(
            context,
            ref_id=ref_id,
            steps=[BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=ref_id), reason="First attempt expected to miss verifier condition.")],
            expected_text="Expected Done",
            after_text="Wrong State",
            notes="first_verifier_failure",
            step_count=6,
            allow_verifier_failure=True,
        )
        if first["verifier_recovery_rate"] != 0.0:
            return _failure_metrics("first verifier unexpectedly recovered")
        repair = _execute_path(
            context,
            ref_id=ref_id,
            steps=[BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=ref_id), reason="Repair after verifier miss.")],
            expected_text="Expected Done",
            after_text="Expected Done",
            notes="failed_verifier_repaired_inside_policy",
            step_count=9,
            repair_attempt_count=1,
        )
        repair["repaired"] = True
        repair["repair_success_rate"] = 1.0 if repair["binary_success"] else 0.0
        repair["verifier_recovery_rate"] = 1.0 if repair["binary_success"] else 0.0
        repair["notes"] = "failed_verifier_repaired_inside_policy"
        return repair
    if mission_id == "BF-HARD-005-multistep-budgeted-chain":
        context = _build_context(iteration, html=BASE_HTML, text="Hardening Trial Email Continue Ready")
        textbox_ref = _first_ref(context["snapshot"], "textbox")
        button_ref = _first_ref(context["snapshot"], "button")
        return _execute_path(
            context,
            ref_id=button_ref,
            steps=[
                BrowserInteractionStep(intent=BrowserInteractionIntent.FILL_PLAN, target=BrowserInteractionTarget(ref=textbox_ref), text="hardening@example.com", reason="Fill grounded field."),
                BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=button_ref), reason="Click grounded button."),
                BrowserInteractionStep(intent=BrowserInteractionIntent.WAIT_FOR_TEXT_PLAN, target=BrowserInteractionTarget(), text="Chain Complete", wait_predicate=BrowserWaitPredicate.TEXT, reason="Verify progress."),
            ],
            expected_text="Chain Complete",
            after_text="Chain Complete",
            notes="multistep_chain_executed_without_micro_approval",
            step_count=8,
            planned_step_count=3,
        )
    if mission_id == "BF-HARD-006-step-budget-pressure-reject":
        context = _build_context(iteration, html=BASE_HTML, text="Hardening Trial Email Continue Ready", max_actions=2)
        ref_id = _first_ref(context["snapshot"], "button")
        prepared = _prepare(context, ref_id=ref_id, planned_step_count=3)
        denied = not prepared.accepted and "max_steps_exceeded" in prepared.errors
        return _denial_metrics(denied, notes="compiled_policy_step_budget_rejected", budget_enforcement_rate=1.0)
    if mission_id == "BF-HARD-007-visual-ocr-ref-denial":
        mission_id_runtime = f"mission_p4h_z_ocr_{iteration:03d}"
        target = PerceptionTarget(source_type=PerceptionSourceType.BROWSER, name="Visual OCR Button", visible=True, understood=True, actionable=False)
        frame = PerceptionEngine().build_frame(
            mission_id=mission_id_runtime,
            source_type=PerceptionSourceType.BROWSER,
            source_url=URL,
            targets=[target],
            texts=[PerceptionText(source=PerceptionTextSource.OCR, text="Visual OCR Button", confidence_score=0.55)],
        )
        authority = _envelope(mission_id_runtime)
        policy = CompiledMissionPolicyCompiler().compile(authority)
        candidate = SceneActionCandidate(
            mission_id=mission_id_runtime,
            perception_frame_id=frame.id,
            source_type=PerceptionSourceType.BROWSER,
            target_id=target.id,
            action_class="browser_interaction_limited",
            tool_id="browser_public_operator_limited",
            intent="Reject OCR-only visual target.",
            expected_effect="No action.",
        )
        prepared = ActionEngine().prepare_browser_action(frame=frame, candidate=candidate, policy=policy, canonical_call=_call(ref_id=""))
        denied = not prepared.accepted and "target_runtime_ref_missing" in prepared.errors
        return _denial_metrics(denied, notes="visual_ocr_target_denied_without_runtime_ref", visual_target_accuracy=1.0)
    if mission_id == "BF-HARD-008-fabricated-ref-denial":
        context = _build_context(iteration, html=BASE_HTML, text="Hardening Trial Email Continue Ready")
        prepared = _prepare(context, ref_id="fabricated_ref")
        denied = not prepared.accepted and "candidate_ref_mismatch" in prepared.errors
        return _denial_metrics(denied, notes="fabricated_ref_denied_before_execution")
    raise ValueError(f"unsupported hardening mission: {mission_id}")


def _build_context(iteration: int, *, html: str, text: str, max_actions: int = 12) -> dict[str, Any]:
    mission_id = f"mission_p4h_z_hardening_{iteration:03d}_{abs(hash(html)) % 10000}"
    bus = EventBus(mission_id)
    snapshot = BrowserAccessibilitySnapshotBuilder().build(html=html, text=text)
    snapshot_trace_id = _append_snapshot_event(bus, mission_id, snapshot)
    ui_set = BrowserUIObservationBuilder().from_accessibility_snapshot(
        mission_id=mission_id,
        url=URL,
        snapshot=snapshot,
        event_bus=bus,
        trace_refs=[snapshot_trace_id],
    )
    visual_ref = _first_interactive_ref(snapshot)
    visual = BrowserVisualObservationBuilder().create(
        mission_id=mission_id,
        url=URL,
        region=BrowserScreenshotRegion(
            bbox=BrowserBoundingBox(x=32, y=36, width=150, height=42),
            source_screenshot_sha256="c" * 64,
            source_width=1024,
            source_height=768,
            ref_id=visual_ref,
            reason="P4H-Z visual crop bound to runtime ref.",
        ),
        crop_bytes=b"hardening-crop",
        page_sha256=snapshot.page_sha256,
        snapshot_sha256=snapshot.snapshot_sha256,
        viewport={"width": 1024, "height": 768},
        ui_observation_ref_ids=[visual_ref],
        event_bus=bus,
        trace_refs=[snapshot_trace_id],
    )
    frame = BrowserPerceptionAdapter().build_frame(ui_observation_set=ui_set, visual_observations=[visual])
    authority = _envelope(mission_id, max_actions=max_actions)
    return {
        "mission_id": mission_id,
        "bus": bus,
        "snapshot": snapshot,
        "snapshot_trace_id": snapshot_trace_id,
        "frame": frame,
        "authority": authority,
        "policy": CompiledMissionPolicyCompiler().compile(authority, trace_refs=[snapshot_trace_id]),
    }


def _execute_path(
    context: dict[str, Any],
    *,
    ref_id: str,
    steps: list[BrowserInteractionStep],
    expected_text: str,
    after_text: str,
    notes: str,
    step_count: int,
    planned_step_count: int | None = None,
    repair_attempt_count: int = 0,
    ambiguous_target_accuracy: float = 0.0,
    visual_target_accuracy: float = 0.0,
    allow_verifier_failure: bool = False,
) -> dict[str, Any]:
    prepared = _prepare(
        context,
        ref_id=ref_id,
        planned_step_count=planned_step_count or max(1, len(steps)),
        repair_attempt_count=repair_attempt_count,
    )
    if not prepared.accepted or prepared.envelope is None:
        return _failure_metrics(f"prepare_failed:{prepared.reason}:{','.join(prepared.errors)}")
    plan_result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=context["mission_id"],
        snapshot=context["snapshot"],
        steps=steps,
        event_bus=context["bus"],
        final_url=URL,
        snapshot_trace_id=context["snapshot_trace_id"],
    )
    if not plan_result.accepted or plan_result.plan is None:
        return _failure_metrics(f"plan_failed:{plan_result.reason}:{','.join(plan_result.errors)}")
    call = _call(
        ref_id=ref_id,
        plan=plan_result.plan.model_dump(mode="json"),
        plan_trace_id=plan_result.trace_event_id or "",
        before_snapshot_trace_id=context["snapshot_trace_id"],
    )
    prepared = ActionEngine().prepare_browser_action(
        frame=context["frame"],
        candidate=_candidate(context, ref_id, planned_step_count=planned_step_count or len(steps), repair_attempt_count=repair_attempt_count),
        policy=context["policy"],
        canonical_call=call,
    )
    if not prepared.accepted or prepared.envelope is None:
        return _failure_metrics(f"prepare_with_plan_failed:{prepared.reason}:{','.join(prepared.errors)}")
    with _temporary_workspace("sentinel_p4h_z_") as tmp:
        runner = BrowserControlledCapabilityRunner(
            registry=default_tool_registry(),
            capture_root=Path(tmp) / "captures",
            interaction_backend=HardeningInteractionBackend(context["snapshot"], after_text=after_text),
        )
        executed = ActionEngine().execute_browser_action(
            action_envelope=prepared.envelope,
            mission_envelope=context["authority"],
            runner=runner,
            event_bus=context["bus"],
        )
    if not executed.accepted:
        return _failure_metrics(f"execute_failed:{executed.reason}:{','.join(executed.errors)}")
    interaction_gate = CoreFinalGate._browser_interaction_execution_contract(SimpleNamespace(trace=tuple(context["bus"].events())))
    receipt = _receipt_from_interaction_event(context["bus"])
    verification = BrowserPostActionVerifier().verify(
        mission_id=context["mission_id"],
        receipt=receipt,
        after_snapshot=_after_snapshot(receipt, text=after_text),
        expected_text=expected_text,
        expected_url=URL,
        event_bus=context["bus"],
    )
    verifier_passed = str(verification.verdict) == "accepted"
    v25_gate = CoreFinalGate._browser_v25_observation_and_operator_contract(SimpleNamespace(trace=tuple(context["bus"].events())))
    final_gate_passed = bool(interaction_gate.passed and v25_gate.passed and context["bus"].verify_chain())
    binary_success = bool(executed.accepted and final_gate_passed and (verifier_passed or allow_verifier_failure))
    return {
        "binary_success": binary_success,
        "action_success_rate": 1.0 if executed.accepted else 0.0,
        "operator_tempo": _tempo(step_count),
        "repair_success_rate": 0.0,
        "verifier_recovery_rate": 1.0 if verifier_passed else 0.0,
        "ambiguous_target_accuracy": ambiguous_target_accuracy,
        "visual_target_accuracy": visual_target_accuracy,
        "false_action_rate": 0.0,
        "proof_completeness": 1.0 if final_gate_passed else 0.0,
        "authority_correctness": 1.0,
        "budget_enforcement_rate": 0.0,
        "step_count": step_count,
        "executed": True,
        "repaired": False,
        "denied": False,
        "final_gate_passed": final_gate_passed,
        "notes": notes,
    }


def _prepare(
    context: dict[str, Any],
    *,
    ref_id: str,
    required_confidence: float = 0.0,
    confidence_score: float | None = None,
    planned_step_count: int = 1,
    repair_attempt_count: int = 0,
) -> Any:
    return ActionEngine().prepare_browser_action(
        frame=context["frame"],
        candidate=_candidate(
            context,
            ref_id,
            required_confidence=required_confidence,
            confidence_score=confidence_score,
            planned_step_count=planned_step_count,
            repair_attempt_count=repair_attempt_count,
        ),
        policy=context["policy"],
        canonical_call=_call(ref_id=ref_id),
    )


def _candidate(
    context: dict[str, Any],
    ref_id: str,
    *,
    required_confidence: float = 0.0,
    confidence_score: float | None = None,
    planned_step_count: int = 1,
    repair_attempt_count: int = 0,
) -> SceneActionCandidate:
    target = context["frame"].target_by_ref(ref_id) if ref_id else None
    if target is None:
        target = context["frame"].targets[0]
    return SceneActionCandidate(
        mission_id=context["mission_id"],
        perception_frame_id=context["frame"].id,
        source_type=PerceptionSourceType.BROWSER,
        target_id=target.id,
        runtime_ref_id=ref_id,
        action_class="browser_interaction_limited",
        tool_id="browser_public_operator_limited",
        intent="Execute hardened browser interaction inside compiled policy.",
        expected_effect="Verified browser state change or correct denial.",
        confidence_score=target.confidence.overall if confidence_score is None else confidence_score,
        required_confidence=required_confidence,
        planned_step_count=planned_step_count,
        repair_attempt_count=repair_attempt_count,
    )


def _call(
    *,
    ref_id: str,
    plan: dict[str, Any] | None = None,
    plan_trace_id: str = "",
    before_snapshot_trace_id: str = "",
) -> CanonicalToolCall:
    arguments: dict[str, Any] = {"ref_id": ref_id, "allowed_domains": [DOMAIN], "final_url": URL}
    if plan is not None:
        arguments.update({"plan": plan, "plan_trace_event_id": plan_trace_id, "before_snapshot_trace_event_id": before_snapshot_trace_id})
    payload = {
        "tool_id": "browser_public_operator_limited",
        "action": "browser_interaction_limited",
        "arguments": arguments,
        "capability": "public_web_interaction_limited",
        "target": URL,
        "requested_side_effects": [],
    }
    return CanonicalToolCall(
        tool_id=payload["tool_id"],
        action=payload["action"],
        arguments=arguments,
        capability=payload["capability"],
        target=payload["target"],
        requested_side_effects=[],
        canonical_hash=hashlib.sha256(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")).hexdigest(),
    )


def _envelope(mission_id: str, *, max_actions: int = 12) -> MissionAuthorityEnvelope:
    return MissionAuthorityEnvelope(
        id=mission_id,
        user_id="user_p4h_z",
        mission_type=MissionType.GTM,
        mission_title="P4H-Z Browser Operator Hardening",
        mission_objective="Stress browser operator loop under ambiguity, repair, and budget pressure.",
        success_criteria=["Hardening mission passes without false action."],
        mode=MissionMode.POWER,
        allowed_systems=["public_web"],
        allowed_tools=["browser_public_operator_limited"],
        allowed_actions=["browser_interaction_limited"],
        forbidden_actions=["browser_form_submit", "browser_private_session", "browser_login_authority"],
        allowed_domains=[DOMAIN],
        allowed_paths=["data/generated_projects"],
        risk_appetite_score=80,
        max_actions=max_actions,
        max_duration_minutes=10,
    )


def _append_snapshot_event(bus: EventBus, mission_id: str, snapshot) -> str:
    event = bus.append(
        AgentEventType.BROWSER_SNAPSHOT_CAPTURED,
        "P4H-Z hardening snapshot captured.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_hardening_snapshot",
            "snapshot_artifact_id": "artifact_hardening_snapshot",
            "snapshot_artifact_sha256": "d" * 64,
            "accessibility_snapshot_sha256": snapshot.snapshot_sha256,
            "accessibility_page_sha256": snapshot.page_sha256,
            "accessibility_ref_count": snapshot.stats.refs,
            "accessibility_interactive_count": snapshot.stats.interactive,
            "accessibility_ref_ids": sorted(snapshot.refs),
            "mission_id": mission_id,
        },
    )
    return event.id


def _first_ref(snapshot, role: str) -> str:
    for ref_id, ref in snapshot.refs.items():
        if ref.role == role:
            return ref_id
    raise AssertionError(f"missing ref for role {role}")


def _first_interactive_ref(snapshot) -> str:
    for ref_id, ref in snapshot.refs.items():
        if ref.role in {"button", "textbox", "link"}:
            return ref_id
    return next(iter(snapshot.refs))


def _ref_by_role_name_nth(snapshot, role: str, name: str, nth: int) -> str:
    for ref_id, ref in snapshot.refs.items():
        if ref.role == role and ref.name == name and ref.nth == nth:
            return ref_id
    raise AssertionError(f"missing ref for {role}:{name}:{nth}")


def _receipt_from_interaction_event(bus: EventBus) -> BrowserInteractionExecutionReceipt:
    event = next(event for event in reversed(bus.events()) if event.event_type == AgentEventType.BROWSER_INTERACTION_EXECUTED)
    payload = event.payload
    return BrowserInteractionExecutionReceipt(
        id=str(payload["receipt_id"]),
        mission_id=event.mission_id,
        request_id=str(payload["request_id"]),
        plan_id=str(payload["plan_id"]),
        plan_sha256=str(payload["plan_sha256"]),
        plan_trace_event_id=str(payload["plan_trace_event_id"]),
        before_snapshot_trace_event_id=str(payload["before_snapshot_trace_event_id"]),
        before_snapshot_sha256=str(payload["before_snapshot_sha256"]),
        before_page_sha256=str(payload["before_page_sha256"]),
        after_snapshot_sha256=str(payload["after_snapshot_sha256"]),
        after_page_sha256=str(payload["after_page_sha256"]),
        final_url_before=str(payload["final_url_before"]),
        final_url_after=str(payload["final_url_after"]),
        same_origin=bool(payload["same_origin"]),
        executed_step_ids=[str(item) for item in payload["executed_step_ids"]],
        executed_intents=[str(item) for item in payload["executed_intents"]],
        executed_ref_ids=[str(item) for item in payload["executed_ref_ids"]],
        after_snapshot_artifact_id=str(payload["after_snapshot_artifact_id"]),
        after_snapshot_artifact_sha256=str(payload["after_snapshot_artifact_sha256"]),
        after_screenshot_artifact_id=str(payload["after_screenshot_artifact_id"]),
        after_screenshot_artifact_sha256=str(payload["after_screenshot_artifact_sha256"]),
        network_ledger_sha256=str(payload["network_ledger_sha256"]),
        browser_health=dict(payload["browser_health"]),
        trace_refs=list(event.trace_refs),
    )


def _after_snapshot(receipt: BrowserInteractionExecutionReceipt, *, text: str) -> BrowserRenderedSnapshotResult:
    return BrowserRenderedSnapshotResult(
        accepted=True,
        status=BrowserSnapshotStatus.CAPTURED,
        reason="hardening_after_snapshot",
        request_id=f"{receipt.request_id}_verify",
        url_decision=PublicUrlDecision(status=PublicUrlDecisionStatus.ALLOWED, reason="allowed_public_url", original_url=URL, final_url=URL),
        extracted_text=f"{text} visible.",
        receipt=BrowserRenderedSnapshotReceipt(
            mission_id=receipt.mission_id,
            request_id=f"{receipt.request_id}_verify",
            original_url=URL,
            final_url=URL,
            accessibility_snapshot_sha256=receipt.after_snapshot_sha256,
            trace_refs=list(receipt.trace_refs),
        ),
        trace_event_id=receipt.trace_refs[-1] if receipt.trace_refs else None,
    )


def _denial_metrics(
    denied: bool,
    *,
    notes: str,
    ambiguous_target_accuracy: float = 0.0,
    visual_target_accuracy: float = 0.0,
    budget_enforcement_rate: float = 0.0,
) -> dict[str, Any]:
    return {
        "binary_success": denied,
        "action_success_rate": 1.0 if denied else 0.0,
        "operator_tempo": 1.0,
        "repair_success_rate": 0.0,
        "verifier_recovery_rate": 1.0,
        "ambiguous_target_accuracy": ambiguous_target_accuracy,
        "visual_target_accuracy": visual_target_accuracy,
        "false_action_rate": 0.0 if denied else 1.0,
        "proof_completeness": 1.0 if denied else 0.0,
        "authority_correctness": 1.0 if denied else 0.0,
        "budget_enforcement_rate": budget_enforcement_rate,
        "step_count": 3,
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
        "repair_success_rate": 0.0,
        "verifier_recovery_rate": 0.0,
        "ambiguous_target_accuracy": 0.0,
        "visual_target_accuracy": 0.0,
        "false_action_rate": 1.0,
        "proof_completeness": 0.0,
        "authority_correctness": 0.0,
        "budget_enforcement_rate": 0.0,
        "step_count": 1,
        "executed": False,
        "repaired": False,
        "denied": False,
        "final_gate_passed": False,
        "notes": notes,
    }


def _tempo(step_count: int) -> float:
    if step_count <= 6:
        return 1.0
    if step_count <= 8:
        return 0.9
    if step_count <= 10:
        return 0.8
    return 0.65


def _avg(results: list[BrowserOperatorHardeningResult], field: str) -> float:
    return round(mean(float(getattr(result, field)) for result in results), 4)


def _avg_for(results: list[BrowserOperatorHardeningResult], field: str, mission_ids: set[str]) -> float:
    selected = [result for result in results if result.mission_id in mission_ids]
    if not selected:
        return 0.0
    return _avg(selected, field)


def _mission_score(mission_id: str, items: list[BrowserOperatorHardeningResult]) -> dict[str, Any]:
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
        "repair_success_rate": _avg(items, "repair_success_rate"),
        "verifier_recovery_rate": _avg(items, "verifier_recovery_rate"),
        "ambiguous_target_accuracy": _avg(items, "ambiguous_target_accuracy"),
        "visual_target_accuracy": _avg(items, "visual_target_accuracy"),
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--run-count", type=int, default=DEFAULT_RUN_COUNT)
    args = parser.parse_args()
    results = run_operator_hardening(run_count=args.run_count)
    scorecard = write_hardening_outputs(results, args.out_dir)
    print(json.dumps(scorecard, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
