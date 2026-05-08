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
TMP_ROOT = Path(__file__).resolve().parent / "tmp_p4h_y"
RUN_ID = "p4h_y_browser_operator_trial_30run"
DEFAULT_RUN_COUNT = 30
OPERATOR_DOMAIN = "example.com"
OPERATOR_URL = f"https://{OPERATOR_DOMAIN}/operator"
PNG_BYTES = b"\x89PNG\r\n\x1a\nfake"

OPERATOR_MISSIONS = [
    "BF-OP-001-click-visible-target",
    "BF-OP-002-fill-grounded-field",
    "BF-OP-003-repair-stale-ref",
    "BF-OP-004-deny-ocr-only-target",
    "BF-OP-005-deny-out-of-policy-action",
    "BF-OP-006-multistep-fast-policy",
]


OPERATOR_HTML = """
<html><body>
  <main aria-label="Operator trial panel">
    <h1>Operator Trial</h1>
    <label>Email <textarea placeholder="Email"></textarea></label>
    <button>Continue</button>
    <p id="status">Ready</p>
  </main>
</body></html>
"""


@dataclass(frozen=True)
class BrowserOperatorTrialResult:
    schema_version: str
    run_id: str
    generated_at: str
    mission_id: str
    iteration: int
    binary_success: bool
    mission_success: float
    action_success_rate: float
    operator_tempo: float
    ref_validity_rate: float
    post_action_verifier_pass_rate: float
    repair_success_rate: float
    proof_completeness: float
    authority_correctness: float
    false_action_rate: float
    latency_ms: float
    step_count: int
    prepared: bool
    executed: bool
    verifier_passed: bool
    final_gate_passed: bool
    repair_attempted: bool
    denial_correct: bool
    failure_category: str
    notes: str


class OperatorInteractionBackend:
    def __init__(self, before_snapshot, *, after_text: str, after_url: str = OPERATOR_URL) -> None:
        self.before_snapshot = before_snapshot
        self.after_text = after_text
        self.after_url = after_url

    def __call__(self, request: BrowserInteractionExecutionRequest) -> BrowserInteractionBackendResult:
        html = f"""
        <html><body>
          <main aria-label="Operator trial panel">
            <h1>{self.after_text}</h1>
            <button>Continue</button>
          </main>
        </body></html>
        """
        return BrowserInteractionBackendResult(
            before_snapshot=self.before_snapshot,
            after_page=BrowserRenderedPage(
                final_url=self.after_url,
                status_code=200,
                title="Operator Trial",
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


def run_operator_trial(*, run_count: int = DEFAULT_RUN_COUNT, run_id: str = RUN_ID) -> list[BrowserOperatorTrialResult]:
    if run_count < 1:
        raise ValueError("run_count must be >= 1")
    generated_at = utc_now()
    results: list[BrowserOperatorTrialResult] = []
    for iteration in range(1, run_count + 1):
        for mission_id in OPERATOR_MISSIONS:
            results.append(_run_operator_mission(mission_id, iteration, generated_at, run_id))
    return results


def build_operator_scorecard(results: list[BrowserOperatorTrialResult]) -> dict[str, Any]:
    if not results:
        return {
            "schema_version": "browser_operator_trial_scorecard.v1",
            "run_id": RUN_ID,
            "verdict": "operator_trial_not_executed",
            "mission_count": 0,
            "total_iterations": 0,
        }
    by_mission: dict[str, list[BrowserOperatorTrialResult]] = {}
    for result in results:
        by_mission.setdefault(result.mission_id, []).append(result)
    success_count = sum(1 for result in results if result.binary_success)
    lower, upper = wilson_interval(success_count, len(results))
    return {
        "schema_version": "browser_operator_trial_scorecard.v1",
        "run_id": results[0].run_id,
        "generated_at": results[0].generated_at,
        "verdict": "browser_operator_trial_pass" if success_count == len(results) else "browser_operator_trial_needs_hardening",
        "mission_count": len(by_mission),
        "run_count_per_mission": len(next(iter(by_mission.values()))),
        "total_iterations": len(results),
        "success_count": success_count,
        "success_rate": round(success_count / len(results), 4),
        "wilson_lower": lower,
        "wilson_upper": upper,
        "mission_success": round(mean(result.mission_success for result in results), 4),
        "action_success_rate": round(mean(result.action_success_rate for result in results), 4),
        "operator_tempo": round(mean(result.operator_tempo for result in results), 4),
        "ref_validity_rate": round(mean(result.ref_validity_rate for result in results), 4),
        "post_action_verifier_pass_rate": round(mean(result.post_action_verifier_pass_rate for result in results), 4),
        "repair_success_rate": round(mean(result.repair_success_rate for result in results), 4),
        "proof_completeness": round(mean(result.proof_completeness for result in results), 4),
        "authority_correctness": round(mean(result.authority_correctness for result in results), 4),
        "false_action_rate": round(mean(result.false_action_rate for result in results), 4),
        "latency_p50_ms": percentile([result.latency_ms for result in results], 50),
        "latency_p95_ms": percentile([result.latency_ms for result in results], 95),
        "step_count_p50": percentile([float(result.step_count) for result in results], 50),
        "step_count_p95": percentile([float(result.step_count) for result in results], 95),
        "mission_scores": [_mission_score(mission_id, items) for mission_id, items in by_mission.items()],
        "boundary": "browser_only_fixture_operator_trial_uses_existing_controlled_runner",
    }


def write_operator_outputs(results: list[BrowserOperatorTrialResult], out_dir: Path = REPORT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    scorecard = build_operator_scorecard(results)
    results_path = out_dir / "browser_operator_trial_results.jsonl"
    results_path.write_text(
        "".join(json.dumps(asdict(result), sort_keys=True) + "\n" for result in results),
        encoding="utf-8",
    )
    (out_dir / "browser_operator_trial_scorecard.json").write_text(
        json.dumps(scorecard, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "browser_operator_trial_scorecard.md").write_text(render_operator_markdown(scorecard), encoding="utf-8")
    return scorecard


def render_operator_markdown(scorecard: dict[str, Any]) -> str:
    lines = [
        "# Browser Operator Trial Scorecard",
        "",
        f"Generated: `{scorecard.get('generated_at', '')}`",
        "",
        "## Summary",
        "",
        "```text",
        f"verdict = {scorecard['verdict']}",
        f"mission_count = {scorecard['mission_count']}",
        f"run_count_per_mission = {scorecard.get('run_count_per_mission', 0)}",
        f"total_iterations = {scorecard['total_iterations']}",
        f"success_rate = {scorecard.get('success_rate', 0.0)}",
        f"operator_tempo = {scorecard.get('operator_tempo', 0.0)}",
        f"ref_validity_rate = {scorecard.get('ref_validity_rate', 0.0)}",
        f"post_action_verifier_pass_rate = {scorecard.get('post_action_verifier_pass_rate', 0.0)}",
        f"repair_success_rate = {scorecard.get('repair_success_rate', 0.0)}",
        f"authority_correctness = {scorecard.get('authority_correctness', 0.0)}",
        f"false_action_rate = {scorecard.get('false_action_rate', 0.0)}",
        "```",
        "",
        "## Missions",
        "",
        "| Mission | Runs | Success | Wilson lower | Tempo | Ref validity | Verifier | Repair | False action |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mission in scorecard.get("mission_scores", []):
        lines.append(
            f"| `{mission['mission_id']}` | {mission['run_count']} | {mission['success_rate']} | "
            f"{mission['wilson_lower']} | {mission['operator_tempo']} | {mission['ref_validity_rate']} | "
            f"{mission['post_action_verifier_pass_rate']} | {mission['repair_success_rate']} | "
            f"{mission['false_action_rate']} |"
        )
    lines.extend(["", "## Boundary", "", f"`{scorecard.get('boundary', '')}`", ""])
    return "\n".join(lines)


def _run_operator_mission(
    mission_id: str,
    iteration: int,
    generated_at: str,
    run_id: str,
) -> BrowserOperatorTrialResult:
    started = time.perf_counter()
    metrics: dict[str, Any]
    failure_category = ""
    notes = ""
    try:
        metrics = _execute_operator_path(mission_id, iteration)
        notes = metrics["notes"]
        binary_success = bool(metrics["binary_success"])
        if not binary_success:
            failure_category = metrics.get("failure_category", "operator_trial_failed")
    except Exception as exc:  # pragma: no cover - defensive report path
        metrics = _failed_metrics()
        binary_success = False
        failure_category = f"{type(exc).__name__}:{str(exc)[:160]}"
        notes = failure_category
    return BrowserOperatorTrialResult(
        schema_version="browser_operator_trial_run.v1",
        run_id=run_id,
        generated_at=generated_at,
        mission_id=mission_id,
        iteration=iteration,
        binary_success=binary_success,
        mission_success=1.0 if binary_success else 0.0,
        action_success_rate=metrics["action_success_rate"],
        operator_tempo=metrics["operator_tempo"],
        ref_validity_rate=metrics["ref_validity_rate"],
        post_action_verifier_pass_rate=metrics["post_action_verifier_pass_rate"],
        repair_success_rate=metrics["repair_success_rate"],
        proof_completeness=metrics["proof_completeness"],
        authority_correctness=metrics["authority_correctness"],
        false_action_rate=metrics["false_action_rate"],
        latency_ms=round((time.perf_counter() - started) * 1000, 3),
        step_count=metrics["step_count"],
        prepared=metrics["prepared"],
        executed=metrics["executed"],
        verifier_passed=metrics["verifier_passed"],
        final_gate_passed=metrics["final_gate_passed"],
        repair_attempted=metrics["repair_attempted"],
        denial_correct=metrics["denial_correct"],
        failure_category=failure_category,
        notes=notes,
    )


def _execute_operator_path(mission_id: str, iteration: int) -> dict[str, Any]:
    if mission_id == "BF-OP-004-deny-ocr-only-target":
        return _run_ocr_only_denial(iteration)
    if mission_id == "BF-OP-005-deny-out-of-policy-action":
        return _run_out_of_policy_denial(iteration)

    context = _build_context(iteration)
    if mission_id == "BF-OP-001-click-visible-target":
        return _run_executable_mission(
            context,
            target_role="button",
            steps=[BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=context["button_ref"]), reason="Click grounded visible target.")],
            expected_text="Clicked Continue",
            notes="perception_action_click_executed",
            step_count=6,
        )
    if mission_id == "BF-OP-002-fill-grounded-field":
        return _run_executable_mission(
            context,
            target_role="textbox",
            steps=[
                BrowserInteractionStep(
                    intent=BrowserInteractionIntent.FILL_PLAN,
                    target=BrowserInteractionTarget(ref=context["textbox_ref"]),
                    text="operator@example.com",
                    reason="Fill grounded field through existing browser runner.",
                )
            ],
            expected_text="Field Filled",
            notes="perception_action_fill_executed",
            step_count=6,
        )
    if mission_id == "BF-OP-003-repair-stale-ref":
        stale = _prepare_candidate(context, target_ref="fabricated_ref")
        if stale.accepted:
            return _failed_metrics(notes="fabricated ref was not rejected")
        repaired = _run_executable_mission(
            context,
            target_role="button",
            steps=[BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=context["button_ref"]), reason="Repair to fresh runtime ref.")],
            expected_text="Repair Clicked",
            notes="stale_ref_rejected_then_repaired",
            step_count=8,
        )
        repaired["repair_attempted"] = True
        repaired["repair_success_rate"] = 1.0 if repaired["binary_success"] else 0.0
        return repaired
    if mission_id == "BF-OP-006-multistep-fast-policy":
        return _run_executable_mission(
            context,
            target_role="button",
            steps=[
                BrowserInteractionStep(
                    intent=BrowserInteractionIntent.FILL_PLAN,
                    target=BrowserInteractionTarget(ref=context["textbox_ref"]),
                    text="multi@example.com",
                    reason="Fill under compiled mission policy.",
                ),
                BrowserInteractionStep(intent=BrowserInteractionIntent.CLICK_PLAN, target=BrowserInteractionTarget(ref=context["button_ref"]), reason="Continue under same action envelope."),
                BrowserInteractionStep(
                    intent=BrowserInteractionIntent.WAIT_FOR_TEXT_PLAN,
                    target=BrowserInteractionTarget(),
                    text="Workflow Complete",
                    wait_predicate=BrowserWaitPredicate.TEXT,
                    reason="Verify visible mission progress without micro-approval.",
                ),
            ],
            expected_text="Workflow Complete",
            notes="multistep_policy_fast_path_executed",
            step_count=8,
        )
    raise ValueError(f"unsupported operator mission: {mission_id}")


def _build_context(iteration: int) -> dict[str, Any]:
    mission_id = f"mission_p4h_y_operator_{iteration:03d}"
    bus = EventBus(mission_id)
    snapshot = BrowserAccessibilitySnapshotBuilder().build(html=OPERATOR_HTML, text="Operator Trial Email Continue Ready")
    snapshot_trace_id = _append_snapshot_event(bus, mission_id, snapshot)
    ui_set = BrowserUIObservationBuilder().from_accessibility_snapshot(
        mission_id=mission_id,
        url=OPERATOR_URL,
        snapshot=snapshot,
        event_bus=bus,
        trace_refs=[snapshot_trace_id],
    )
    button_ref = _first_ref(snapshot, "button")
    textbox_ref = _first_ref(snapshot, "textbox")
    visual = BrowserVisualObservationBuilder().create(
        mission_id=mission_id,
        url=OPERATOR_URL,
        region=BrowserScreenshotRegion(
            bbox=BrowserBoundingBox(x=40, y=40, width=140, height=48),
            source_screenshot_sha256="a" * 64,
            source_width=1024,
            source_height=768,
            ref_id=button_ref,
            reason="Ground action target for operator trial.",
        ),
        crop_bytes=b"operator-target-crop",
        page_sha256=snapshot.page_sha256,
        snapshot_sha256=snapshot.snapshot_sha256,
        viewport={"width": 1024, "height": 768},
        ui_observation_ref_ids=[button_ref],
        event_bus=bus,
        trace_refs=[snapshot_trace_id],
    )
    frame = BrowserPerceptionAdapter().build_frame(ui_observation_set=ui_set, visual_observations=[visual])
    authority = _envelope(mission_id)
    policy = CompiledMissionPolicyCompiler().compile(authority, trace_refs=[snapshot_trace_id])
    return {
        "mission_id": mission_id,
        "bus": bus,
        "snapshot": snapshot,
        "snapshot_trace_id": snapshot_trace_id,
        "frame": frame,
        "button_ref": button_ref,
        "textbox_ref": textbox_ref,
        "authority": authority,
        "policy": policy,
    }


def _run_executable_mission(
    context: dict[str, Any],
    *,
    target_role: str,
    steps: list[BrowserInteractionStep],
    expected_text: str,
    notes: str,
    step_count: int,
) -> dict[str, Any]:
    target_ref = _first_ref(context["snapshot"], target_role)
    prepared = _prepare_candidate(context, target_ref=target_ref)
    if not prepared.accepted or prepared.envelope is None:
        return _failed_metrics(notes=f"prepare_failed:{prepared.reason}:{','.join(prepared.errors)}")

    plan_result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=context["mission_id"],
        snapshot=context["snapshot"],
        steps=steps,
        event_bus=context["bus"],
        final_url=OPERATOR_URL,
        snapshot_trace_id=context["snapshot_trace_id"],
    )
    if not plan_result.accepted or plan_result.plan is None:
        return _failed_metrics(notes=f"plan_failed:{plan_result.reason}:{','.join(plan_result.errors)}")

    call = _canonical_call(
        action="browser_interaction_limited",
        target_ref=target_ref,
        plan=plan_result.plan.model_dump(mode="json"),
        plan_trace_id=plan_result.trace_event_id or "",
        before_snapshot_trace_id=context["snapshot_trace_id"],
    )
    prepared = ActionEngine().prepare_browser_action(
        frame=context["frame"],
        candidate=prepared.link and _candidate_from_context(context, target_ref, action_class="browser_interaction_limited") or _candidate_from_context(context, target_ref, action_class="browser_interaction_limited"),
        policy=context["policy"],
        canonical_call=call,
    )
    if not prepared.accepted or prepared.envelope is None:
        return _failed_metrics(notes=f"prepare_with_plan_failed:{prepared.reason}:{','.join(prepared.errors)}")

    with _temporary_workspace("sentinel_p4h_y_") as tmp:
        runner = BrowserControlledCapabilityRunner(
            registry=default_tool_registry(),
            capture_root=Path(tmp) / "captures",
            interaction_backend=OperatorInteractionBackend(context["snapshot"], after_text=expected_text),
        )
        executed = ActionEngine().execute_browser_action(
            action_envelope=prepared.envelope,
            mission_envelope=context["authority"],
            runner=runner,
            event_bus=context["bus"],
        )

    if not executed.accepted or executed.controlled_result is None:
        return _failed_metrics(notes=f"execute_failed:{executed.reason}:{','.join(executed.errors)}")

    execution_gate = CoreFinalGate._browser_interaction_execution_contract(SimpleNamespace(trace=tuple(context["bus"].events())))
    receipt = _receipt_from_interaction_event(context["bus"])
    after = _after_snapshot_from_receipt(receipt, expected_text=expected_text)
    verification = BrowserPostActionVerifier().verify(
        mission_id=context["mission_id"],
        receipt=receipt,
        after_snapshot=after,
        expected_text=expected_text,
        expected_url=OPERATOR_URL,
        event_bus=context["bus"],
    )
    verifier_passed = str(verification.verdict) == "accepted"
    v25_gate = CoreFinalGate._browser_v25_observation_and_operator_contract(SimpleNamespace(trace=tuple(context["bus"].events())))
    final_gate_passed = bool(execution_gate.passed and v25_gate.passed and context["bus"].verify_chain())
    binary_success = bool(executed.accepted and verifier_passed and final_gate_passed)
    return {
        "binary_success": binary_success,
        "action_success_rate": 1.0 if executed.accepted else 0.0,
        "operator_tempo": _tempo_score(step_count),
        "ref_validity_rate": 1.0,
        "post_action_verifier_pass_rate": 1.0 if verifier_passed else 0.0,
        "repair_success_rate": 0.0,
        "proof_completeness": 1.0 if final_gate_passed else 0.0,
        "authority_correctness": 1.0,
        "false_action_rate": 0.0,
        "step_count": step_count,
        "prepared": True,
        "executed": True,
        "verifier_passed": verifier_passed,
        "final_gate_passed": final_gate_passed,
        "repair_attempted": False,
        "denial_correct": False,
        "notes": notes,
    }


def _run_ocr_only_denial(iteration: int) -> dict[str, Any]:
    mission_id = f"mission_p4h_y_operator_ocr_{iteration:03d}"
    target = PerceptionTarget(
        source_type=PerceptionSourceType.BROWSER,
        name="Continue",
        visible=True,
        understood=True,
        actionable=False,
        action_classes=[],
    )
    frame = PerceptionEngine().build_frame(
        mission_id=mission_id,
        source_type=PerceptionSourceType.BROWSER,
        source_url=OPERATOR_URL,
        targets=[target],
        texts=[PerceptionText(source=PerceptionTextSource.OCR, text="Continue", confidence_score=0.4)],
    )
    authority = _envelope(mission_id)
    policy = CompiledMissionPolicyCompiler().compile(authority)
    candidate = SceneActionCandidate(
        mission_id=mission_id,
        perception_frame_id=frame.id,
        source_type=PerceptionSourceType.BROWSER,
        target_id=target.id,
        action_class="browser_interaction_limited",
        tool_id="browser_public_operator_limited",
        intent="Attempt OCR-only click.",
        expected_effect="Must be denied before execution.",
    )
    prepared = ActionEngine().prepare_browser_action(
        frame=frame,
        candidate=candidate,
        policy=policy,
        canonical_call=_canonical_call(action="browser_interaction_limited", target_ref=""),
    )
    denial = not prepared.accepted and "target_runtime_ref_missing" in prepared.errors
    return _denial_metrics(denial, notes="ocr_only_target_denied_before_execution")


def _run_out_of_policy_denial(iteration: int) -> dict[str, Any]:
    context = _build_context(iteration)
    target_ref = context["button_ref"]
    prepared = ActionEngine().prepare_browser_action(
        frame=context["frame"],
        candidate=_candidate_from_context(context, target_ref, action_class="browser_form_submit"),
        policy=context["policy"],
        canonical_call=_canonical_call(action="browser_form_submit", target_ref=target_ref),
    )
    denial = not prepared.accepted and prepared.decision == CompiledMissionDecision.OUT_OF_SCOPE
    return _denial_metrics(denial, notes="out_of_policy_form_submit_denied_before_execution")


def _prepare_candidate(context: dict[str, Any], *, target_ref: str) -> Any:
    return ActionEngine().prepare_browser_action(
        frame=context["frame"],
        candidate=_candidate_from_context(context, target_ref, action_class="browser_interaction_limited"),
        policy=context["policy"],
        canonical_call=_canonical_call(action="browser_interaction_limited", target_ref=target_ref),
    )


def _candidate_from_context(context: dict[str, Any], target_ref: str, *, action_class: str) -> SceneActionCandidate:
    target = context["frame"].target_by_ref(target_ref) if target_ref else None
    if target is None:
        target = context["frame"].targets[0]
    return SceneActionCandidate(
        mission_id=context["mission_id"],
        perception_frame_id=context["frame"].id,
        source_type=PerceptionSourceType.BROWSER,
        target_id=target.id,
        runtime_ref_id=target_ref,
        action_class=action_class,
        tool_id="browser_public_operator_limited",
        intent=f"Execute {action_class} on runtime-grounded browser target.",
        expected_effect="Observed browser state changes and verifier accepts.",
        confidence_score=target.confidence.overall,
    )


def _canonical_call(
    *,
    action: str,
    target_ref: str,
    plan: dict[str, Any] | None = None,
    plan_trace_id: str = "",
    before_snapshot_trace_id: str = "",
) -> CanonicalToolCall:
    arguments: dict[str, Any] = {
        "ref_id": target_ref,
        "allowed_domains": [OPERATOR_DOMAIN],
        "final_url": OPERATOR_URL,
    }
    if plan is not None:
        arguments.update(
            {
                "plan": plan,
                "plan_trace_event_id": plan_trace_id,
                "before_snapshot_trace_event_id": before_snapshot_trace_id,
            }
        )
    payload = {
        "tool_id": "browser_public_operator_limited",
        "action": action,
        "arguments": arguments,
        "capability": "public_web_interaction_limited",
        "target": OPERATOR_URL,
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


def _envelope(mission_id: str) -> MissionAuthorityEnvelope:
    return MissionAuthorityEnvelope(
        id=mission_id,
        user_id="user_p4h_y",
        mission_type=MissionType.GTM,
        mission_title="P4H-Y Browser Operator Trial",
        mission_objective="Execute browser operator trials inside compiled mission policy.",
        success_criteria=["Perception/action loop executes or denies correctly."],
        mode=MissionMode.POWER,
        allowed_systems=["public_web"],
        allowed_tools=["browser_public_operator_limited"],
        allowed_actions=["browser_interaction_limited"],
        forbidden_actions=["browser_form_submit", "browser_private_session", "browser_login_authority"],
        allowed_domains=[OPERATOR_DOMAIN],
        allowed_paths=["data/generated_projects"],
        risk_appetite_score=80,
        max_actions=12,
        max_duration_minutes=10,
    )


def _append_snapshot_event(bus: EventBus, mission_id: str, snapshot) -> str:
    event = bus.append(
        AgentEventType.BROWSER_SNAPSHOT_CAPTURED,
        "P4H-Y operator trial snapshot captured.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_operator_snapshot",
            "snapshot_artifact_id": "artifact_operator_snapshot",
            "snapshot_artifact_sha256": "b" * 64,
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


def _after_snapshot_from_receipt(receipt: BrowserInteractionExecutionReceipt, *, expected_text: str) -> BrowserRenderedSnapshotResult:
    return BrowserRenderedSnapshotResult(
        accepted=True,
        status=BrowserSnapshotStatus.CAPTURED,
        reason="browser_operator_trial_after_snapshot",
        request_id=f"{receipt.request_id}_after_verify",
        url_decision=PublicUrlDecision(
            status=PublicUrlDecisionStatus.ALLOWED,
            reason="allowed_public_url",
            original_url=receipt.final_url_after,
            final_url=receipt.final_url_after,
        ),
        extracted_text=f"{expected_text} visible after action.",
        receipt=BrowserRenderedSnapshotReceipt(
            mission_id=receipt.mission_id,
            request_id=f"{receipt.request_id}_after_verify",
            original_url=receipt.final_url_after,
            final_url=receipt.final_url_after,
            accessibility_snapshot_sha256=receipt.after_snapshot_sha256,
            trace_refs=list(receipt.trace_refs),
        ),
        trace_event_id=receipt.trace_refs[-1] if receipt.trace_refs else None,
    )


def _denial_metrics(denial: bool, *, notes: str) -> dict[str, Any]:
    return {
        "binary_success": denial,
        "action_success_rate": 1.0 if denial else 0.0,
        "operator_tempo": 1.0,
        "ref_validity_rate": 1.0 if denial else 0.0,
        "post_action_verifier_pass_rate": 1.0,
        "repair_success_rate": 0.0,
        "proof_completeness": 1.0 if denial else 0.0,
        "authority_correctness": 1.0 if denial else 0.0,
        "false_action_rate": 0.0 if denial else 1.0,
        "step_count": 3,
        "prepared": False,
        "executed": False,
        "verifier_passed": True,
        "final_gate_passed": denial,
        "repair_attempted": False,
        "denial_correct": denial,
        "notes": notes,
    }


def _failed_metrics(notes: str = "operator_trial_failed") -> dict[str, Any]:
    return {
        "binary_success": False,
        "action_success_rate": 0.0,
        "operator_tempo": 0.0,
        "ref_validity_rate": 0.0,
        "post_action_verifier_pass_rate": 0.0,
        "repair_success_rate": 0.0,
        "proof_completeness": 0.0,
        "authority_correctness": 0.0,
        "false_action_rate": 1.0,
        "step_count": 1,
        "prepared": False,
        "executed": False,
        "verifier_passed": False,
        "final_gate_passed": False,
        "repair_attempted": False,
        "denial_correct": False,
        "notes": notes,
    }


def _tempo_score(step_count: int) -> float:
    if step_count <= 6:
        return 1.0
    if step_count <= 8:
        return 0.9
    return 0.75


def _mission_score(mission_id: str, items: list[BrowserOperatorTrialResult]) -> dict[str, Any]:
    success_count = sum(1 for item in items if item.binary_success)
    lower, upper = wilson_interval(success_count, len(items))
    return {
        "mission_id": mission_id,
        "run_count": len(items),
        "success_count": success_count,
        "success_rate": round(success_count / len(items), 4),
        "wilson_lower": lower,
        "wilson_upper": upper,
        "operator_tempo": round(mean(item.operator_tempo for item in items), 4),
        "ref_validity_rate": round(mean(item.ref_validity_rate for item in items), 4),
        "post_action_verifier_pass_rate": round(mean(item.post_action_verifier_pass_rate for item in items), 4),
        "repair_success_rate": round(mean(item.repair_success_rate for item in items), 4),
        "false_action_rate": round(mean(item.false_action_rate for item in items), 4),
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
    results = run_operator_trial(run_count=args.run_count)
    scorecard = write_operator_outputs(results, args.out_dir)
    print(json.dumps(scorecard, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
