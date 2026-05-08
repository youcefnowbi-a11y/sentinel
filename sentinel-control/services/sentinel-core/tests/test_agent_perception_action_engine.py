from __future__ import annotations

import hashlib
import json
from types import SimpleNamespace

import pytest

from sentinel.agent import (
    ActionEngine,
    ActionEngineStatus,
    BrowserControlledCapabilityResult,
    BrowserControlledCapabilityStatus,
    CanonicalToolCall,
    CompiledMissionDecision,
    CompiledMissionPolicyCompiler,
    EventBus,
    PerceptionEngine,
    PerceptionSourceType,
    PerceptionTarget,
    PerceptionText,
    PerceptionTextSource,
    SceneActionCandidate,
)
from sentinel.agent.browser import (
    BrowserAccessibilitySnapshotBuilder,
    BrowserBoundingBox,
    BrowserInteractionExecutionReceipt,
    BrowserPerceptionAdapter,
    BrowserRenderedSnapshotReceipt,
    BrowserRenderedSnapshotResult,
    BrowserScreenshotRegion,
    BrowserSnapshotStatus,
    BrowserUIObservationBuilder,
    BrowserVisualObservationBuilder,
    PublicUrlDecision,
    PublicUrlDecisionStatus,
)
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.capabilities.risk import ToolSideEffect
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


MISSION_ID = "mission_p4h_x_perception_action"


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "id": MISSION_ID,
        "user_id": "user_p4h_x",
        "mission_type": MissionType.GTM,
        "mission_title": "P4H-X perception action slice",
        "mission_objective": "Act through browser perception/action only inside compiled mission policy.",
        "success_criteria": ["Prepared action envelope uses runtime ref and existing browser runner."],
        "mode": MissionMode.POWER,
        "allowed_systems": ["public_web"],
        "allowed_tools": ["browser_public_operator_limited"],
        "allowed_actions": ["browser_interaction_limited"],
        "allowed_domains": ["example.com"],
        "forbidden_actions": ["browser_form_submit", "browser_private_session"],
        "risk_appetite_score": 75,
        "max_actions": 5,
        "max_duration_minutes": 10,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def canonical_call(*, ref_id: str, action: str = "browser_interaction_limited", target: str = "https://example.com") -> CanonicalToolCall:
    payload = {
        "tool_id": "browser_public_operator_limited",
        "action": action,
        "arguments": {"ref_id": ref_id, "allowed_domains": ["example.com"]},
        "capability": "public_web_interaction",
        "target": target,
        "requested_side_effects": [ToolSideEffect.BROWSER_READ.value, ToolSideEffect.NETWORK_READ.value],
    }
    canonical_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return CanonicalToolCall(
        tool_id=payload["tool_id"],
        action=payload["action"],
        arguments=payload["arguments"],
        capability=payload["capability"],
        target=payload["target"],
        requested_side_effects=[ToolSideEffect.BROWSER_READ, ToolSideEffect.NETWORK_READ],
        canonical_hash=canonical_hash,
    )


def browser_frame():
    bus = EventBus(MISSION_ID)
    snapshot = BrowserAccessibilitySnapshotBuilder().build(
        html="<html><body><button>Continue</button><p>Ready</p></body></html>",
        text="Continue Ready",
    )
    ui_set = BrowserUIObservationBuilder().from_accessibility_snapshot(
        mission_id=MISSION_ID,
        url="https://example.com",
        snapshot=snapshot,
        event_bus=bus,
    )
    button_ref = next(ref_id for ref_id, ref in snapshot.refs.items() if ref.role == "button")
    visual = BrowserVisualObservationBuilder().create(
        mission_id=MISSION_ID,
        url="https://example.com",
        region=BrowserScreenshotRegion(
            bbox=BrowserBoundingBox(x=20, y=30, width=120, height=40),
            source_screenshot_sha256="f" * 64,
            source_width=800,
            source_height=600,
            ref_id=button_ref,
            reason="Ground visible Continue button.",
        ),
        crop_bytes=b"button-crop",
        page_sha256=snapshot.page_sha256,
        snapshot_sha256=snapshot.snapshot_sha256,
        viewport={"width": 800, "height": 600},
        ui_observation_ref_ids=[button_ref],
        event_bus=bus,
    )
    frame = BrowserPerceptionAdapter().build_frame(ui_observation_set=ui_set, visual_observations=[visual])
    return frame, button_ref, bus


class RecordingBrowserRunner:
    def __init__(self) -> None:
        self.call: CanonicalToolCall | None = None

    def run(self, call: CanonicalToolCall, authority: MissionAuthorityEnvelope, *, event_bus: EventBus) -> BrowserControlledCapabilityResult:
        self.call = call
        return BrowserControlledCapabilityResult(
            accepted=True,
            status=BrowserControlledCapabilityStatus.EXECUTED,
            tool_id=call.tool_id,
            action=call.action,
            reason="recording_browser_runner_executed",
            trace_event_id="trace_runner",
            receipt_id="receipt_runner",
        )


def test_perception_frame_compiled_policy_and_action_envelope_use_browser_ref_only():
    frame, button_ref, bus = browser_frame()
    target = frame.target_by_ref(button_ref)
    assert target is not None
    assert target.visible is True
    assert target.actionable is True
    assert target.authorized is False
    assert frame.source_type == PerceptionSourceType.BROWSER
    assert frame.visual_artifact_sha256 is not None

    policy = CompiledMissionPolicyCompiler().compile(envelope())
    candidate = SceneActionCandidate(
        mission_id=MISSION_ID,
        perception_frame_id=frame.id,
        source_type=PerceptionSourceType.BROWSER,
        target_id=target.id,
        runtime_ref_id=button_ref,
        action_class="browser_interaction_limited",
        tool_id="browser_public_operator_limited",
        intent="Click the runtime-grounded Continue button.",
        expected_effect="Continue action changes page state.",
        confidence_score=target.confidence.overall,
    )
    call = canonical_call(ref_id=button_ref)

    prepared = ActionEngine().prepare_browser_action(
        frame=frame,
        candidate=candidate,
        policy=policy,
        canonical_call=call,
    )

    assert prepared.accepted is True
    assert prepared.status == ActionEngineStatus.PREPARED
    assert prepared.decision == CompiledMissionDecision.GRANTED
    assert prepared.envelope is not None
    assert prepared.envelope.runtime_ref_id == button_ref
    assert prepared.envelope.visual_actuation_plan.steps == [
        "bind_runtime_ref",
        "dispatch_existing_browser_runner",
        "verify_post_action_evidence",
    ]

    runner = RecordingBrowserRunner()
    executed = ActionEngine().execute_browser_action(
        action_envelope=prepared.envelope,
        mission_envelope=envelope(),
        runner=runner,
        event_bus=bus,
    )
    assert executed.accepted is True
    assert runner.call == call


def test_ocr_visibility_alone_cannot_create_action_authority():
    with pytest.raises(ValueError, match="ocr_text_cannot_authorize_action"):
        PerceptionText(source=PerceptionTextSource.OCR, text="Continue", authoritative_for_action=True)

    target = PerceptionTarget(
        source_type=PerceptionSourceType.BROWSER,
        name="Continue",
        visible=True,
        understood=True,
        actionable=False,
        action_classes=[],
    )
    frame = PerceptionEngine().build_frame(
        mission_id=MISSION_ID,
        source_type=PerceptionSourceType.BROWSER,
        source_url="https://example.com",
        targets=[target],
        texts=[PerceptionText(source=PerceptionTextSource.OCR, text="Continue", confidence_score=0.5)],
    )
    policy = CompiledMissionPolicyCompiler().compile(envelope())
    candidate = SceneActionCandidate(
        mission_id=MISSION_ID,
        perception_frame_id=frame.id,
        source_type=PerceptionSourceType.BROWSER,
        target_id=target.id,
        action_class="browser_interaction_limited",
        tool_id="browser_public_operator_limited",
        intent="Click OCR-visible text.",
        expected_effect="Rejected because no runtime ref exists.",
    )

    prepared = ActionEngine().prepare_browser_action(
        frame=frame,
        candidate=candidate,
        policy=policy,
        canonical_call=canonical_call(ref_id=""),
    )

    assert prepared.accepted is False
    assert prepared.decision == CompiledMissionDecision.INVALID
    assert "target_not_actionable" in prepared.errors
    assert "target_runtime_ref_missing" in prepared.errors


def test_future_perception_backends_are_not_active_in_v0():
    with pytest.raises(ValueError, match="perception_source_not_active:desktop"):
        PerceptionEngine().build_frame(
            mission_id=MISSION_ID,
            source_type=PerceptionSourceType.DESKTOP,
        )


def test_compiled_policy_rejects_out_of_scope_action_class():
    frame, button_ref, _bus = browser_frame()
    target = frame.target_by_ref(button_ref)
    assert target is not None
    policy = CompiledMissionPolicyCompiler().compile(envelope())
    candidate = SceneActionCandidate(
        mission_id=MISSION_ID,
        perception_frame_id=frame.id,
        source_type=PerceptionSourceType.BROWSER,
        target_id=target.id,
        runtime_ref_id=button_ref,
        action_class="browser_form_submit",
        tool_id="browser_public_operator_limited",
        intent="Try ungranted form submit.",
        expected_effect="Rejected by compiled policy.",
    )
    prepared = ActionEngine().prepare_browser_action(
        frame=frame,
        candidate=candidate,
        policy=policy,
        canonical_call=canonical_call(ref_id=button_ref, action="browser_form_submit"),
    )
    assert prepared.accepted is False
    assert prepared.decision == CompiledMissionDecision.OUT_OF_SCOPE
    assert "action_class_out_of_scope" in prepared.errors


def test_browser_perception_adapter_can_expose_v3_action_candidate_without_authorizing_it():
    bus = EventBus(MISSION_ID)
    snapshot = BrowserAccessibilitySnapshotBuilder().build(
        html="<html><body><button>Send request</button></body></html>",
        text="Send request",
    )
    ui_set = BrowserUIObservationBuilder().from_accessibility_snapshot(
        mission_id=MISSION_ID,
        url="https://example.com/form",
        snapshot=snapshot,
        event_bus=bus,
    )
    button_ref = next(ref_id for ref_id, ref in snapshot.refs.items() if ref.role == "button")

    frame = BrowserPerceptionAdapter().build_frame(
        ui_observation_set=ui_set,
        action_classes_by_ref={button_ref: ["browser_form_submit"]},
    )
    target = frame.target_by_ref(button_ref)

    assert target is not None
    assert target.actionable is True
    assert target.authorized is False
    assert "browser_interaction_limited" in target.action_classes
    assert "browser_form_submit" in target.action_classes


def test_compiled_policy_enforces_step_action_and_repair_budgets():
    frame, button_ref, _bus = browser_frame()
    target = frame.target_by_ref(button_ref)
    assert target is not None
    policy = CompiledMissionPolicyCompiler().compile(envelope(max_actions=1))
    candidate = SceneActionCandidate(
        mission_id=MISSION_ID,
        perception_frame_id=frame.id,
        source_type=PerceptionSourceType.BROWSER,
        target_id=target.id,
        runtime_ref_id=button_ref,
        action_class="browser_interaction_limited",
        tool_id="browser_public_operator_limited",
        intent="Try to exceed compiled policy budgets.",
        expected_effect="Rejected before execution.",
        planned_step_count=2,
        actions_already_used=1,
        repair_attempt_count=2,
    )
    prepared = ActionEngine().prepare_browser_action(
        frame=frame,
        candidate=candidate,
        policy=policy,
        canonical_call=canonical_call(ref_id=button_ref),
    )

    assert prepared.accepted is False
    assert prepared.decision == CompiledMissionDecision.OUT_OF_SCOPE
    assert "action_budget_exceeded" in prepared.errors
    assert "max_steps_exceeded" in prepared.errors
    assert "repair_budget_exceeded" in prepared.errors


def test_post_action_verifier_still_uses_existing_browser_finalgate_contract():
    bus = EventBus(MISSION_ID)
    receipt = BrowserInteractionExecutionReceipt(
        mission_id=MISSION_ID,
        request_id="req_1",
        plan_id="plan_1",
        plan_sha256="p" * 64,
        plan_trace_event_id="plan_trace",
        before_snapshot_trace_event_id="before_trace",
        before_snapshot_sha256="b" * 64,
        before_page_sha256="c" * 64,
        after_snapshot_sha256="a" * 64,
        after_page_sha256="d" * 64,
        final_url_before="https://example.com",
        final_url_after="https://example.com",
        same_origin=True,
        trace_refs=["plan_trace", "before_trace"],
    )
    after = BrowserRenderedSnapshotResult(
        accepted=True,
        status=BrowserSnapshotStatus.CAPTURED,
        reason="browser_snapshot_captured",
        request_id="snap_1",
        url_decision=PublicUrlDecision(
            status=PublicUrlDecisionStatus.ALLOWED,
            reason="allowed_public_url",
            original_url="https://example.com",
            final_url="https://example.com",
        ),
        extracted_text="Continue action completed.",
        receipt=BrowserRenderedSnapshotReceipt(
            mission_id=MISSION_ID,
            request_id="snap_1",
            original_url="https://example.com",
            final_url="https://example.com",
            accessibility_snapshot_sha256="a" * 64,
            trace_refs=["snap_trace"],
        ),
        trace_event_id="snap_trace",
    )

    verification = ActionEngine().verify_browser_post_action(
        mission_id=MISSION_ID,
        receipt=receipt,
        after_snapshot=after,
        expected_text="completed",
        expected_url="https://example.com",
        event_bus=bus,
    )

    assert verification.verdict == "accepted"
    check = CoreFinalGate._browser_v25_observation_and_operator_contract(SimpleNamespace(trace=tuple(bus.events())))
    assert check.passed is True
