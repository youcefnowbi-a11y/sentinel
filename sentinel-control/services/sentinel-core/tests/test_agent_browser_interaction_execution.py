from __future__ import annotations

from types import SimpleNamespace

import pytest

from sentinel.agent import AgentEventType, ArtifactCaptureSandbox, EventBus
from sentinel.agent.browser import (
    BrowserAccessibilitySnapshotBuilder,
    BrowserControlledCapabilityRunner,
    BrowserInteractionBackendResult,
    BrowserInteractionExecutionRequest,
    BrowserInteractionIntent,
    BrowserInteractionStep,
    BrowserInteractionTarget,
    BrowserLimitedInteractionExecutor,
    BrowserRenderedSnapshotRequest,
    BrowserRenderedPage,
    BrowserSnapshotStatus,
    BrowserWaitPredicate,
    PlaywrightReadOnlyRenderer,
    PlaywrightLimitedInteractionBackend,
    hash_browser_interaction_plan_payload,
)
from sentinel.agent.browser.interaction_dry_run import BrowserInteractionDryRunPlanner
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.agent.phases import AgentPhase
from sentinel.agent.tool_call_protocol import CanonicalToolCall
from sentinel.capabilities import default_tool_registry
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


MISSION_ID = "mission_browser_interaction_execution"
PNG_BYTES = b"\x89PNG\r\n\x1a\nfake"


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "id": MISSION_ID,
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "Browser interaction execution",
        "mission_objective": "Execute one limited public browser interaction with proof.",
        "success_criteria": ["Browser interaction receipt exists"],
        "mode": MissionMode.POWER,
        "risk_appetite_score": 80,
        "allowed_systems": ["local_workspace", "public_web"],
        "allowed_tools": ["browser_public_operator_limited"],
        "allowed_actions": ["browser_interaction_limited"],
        "forbidden_actions": ["browser_submit_form", "credential_access", "upload", "download"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 20,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def snapshot():
    html = """
    <html><body>
      <main>
        <h1>Contact</h1>
        <button>Continue</button>
        <input type="text" placeholder="Email" />
        <select><option>Starter</option></select>
      </main>
    </body></html>
    """
    return BrowserAccessibilitySnapshotBuilder().build(html=html, text="Contact Continue Email Starter")


def first_ref(snap, role: str) -> str:
    for ref_id, ref in snap.refs.items():
        if ref.role == role:
            return ref_id
    raise AssertionError(f"missing ref for role {role}")


def append_snapshot_event(bus: EventBus, snap) -> str:
    event = bus.append(
        AgentEventType.BROWSER_SNAPSHOT_CAPTURED,
        "Rendered browser snapshot captured.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_1",
            "snapshot_artifact_id": "artifact_snapshot",
            "snapshot_artifact_sha256": "a" * 64,
            "accessibility_snapshot_sha256": snap.snapshot_sha256,
            "accessibility_page_sha256": snap.page_sha256,
            "accessibility_ref_count": snap.stats.refs,
            "accessibility_interactive_count": snap.stats.interactive,
            "accessibility_ref_ids": sorted(snap.refs),
        },
    )
    return event.id


def create_plan(bus: EventBus, snap, *, final_url: str = "https://example.com/form", steps=None):
    snapshot_event_id = append_snapshot_event(bus, snap)
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        steps=steps
        or [
            {
                "intent": "fill_plan",
                "target": {"ref": first_ref(snap, "textbox")},
                "text": "user@example.com",
            }
        ],
        event_bus=bus,
        final_url=final_url,
        snapshot_trace_id=snapshot_event_id,
    )
    assert result.accepted is True
    assert result.plan is not None
    return result.plan, result.trace_event_id, snapshot_event_id


def sandbox(tmp_path) -> ArtifactCaptureSandbox:
    return ArtifactCaptureSandbox(mission_id=MISSION_ID, capture_root=tmp_path / "captures")


class FakeInteractionBackend:
    def __init__(self, before_snapshot, *, after_url="https://example.com/form", after_text="Submitted local form state."):
        self.before_snapshot = before_snapshot
        self.after_url = after_url
        self.after_text = after_text

    def __call__(self, request: BrowserInteractionExecutionRequest) -> BrowserInteractionBackendResult:
        html = f"<html><body><main><h1>{self.after_text}</h1><button>Continue</button></main></body></html>"
        return BrowserInteractionBackendResult(
            before_snapshot=self.before_snapshot,
            after_page=BrowserRenderedPage(
                final_url=self.after_url,
                status_code=200,
                title="After",
                text=self.after_text,
                links=[],
                html=html,
                screenshot_png=PNG_BYTES,
            ),
            final_url_before=request.final_url,
            final_url_after=self.after_url,
            executed_step_ids=[step.id for step in request.plan.steps],
        )


def execution_check(trace):
    return CoreFinalGate._browser_interaction_execution_contract(SimpleNamespace(trace=tuple(trace)))


def test_executes_limited_interaction_from_certified_plan(tmp_path):
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    plan, plan_trace_id, snapshot_trace_id = create_plan(bus, snap)

    result = BrowserLimitedInteractionExecutor(backend=FakeInteractionBackend(snap)).execute(
        BrowserInteractionExecutionRequest(
            mission_id=MISSION_ID,
            plan=plan,
            plan_trace_event_id=plan_trace_id,
            before_snapshot_trace_event_id=snapshot_trace_id,
            final_url="https://example.com/form",
        ),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
        policy_trace_id="policy_1",
    )

    assert result.accepted is True
    assert result.receipt is not None
    assert result.receipt.plan_sha256 == plan.plan_sha256
    assert result.receipt.same_origin is True
    assert result.artifact_ids
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_INTERACTION_EXECUTED
    assert execution_check(bus.events()).passed is True


def test_rejects_forged_plan_hash_before_backend(tmp_path):
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    plan, plan_trace_id, snapshot_trace_id = create_plan(bus, snap)
    forged = plan.model_copy(update={"plan_sha256": "0" * 64})

    result = BrowserLimitedInteractionExecutor(backend=FakeInteractionBackend(snap)).execute(
        BrowserInteractionExecutionRequest(
            mission_id=MISSION_ID,
            plan=forged,
            plan_trace_event_id=plan_trace_id,
            before_snapshot_trace_event_id=snapshot_trace_id,
            final_url="https://example.com/form",
        ),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )

    assert result.accepted is False
    assert "plan_hash_invalid" in result.errors
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_INTERACTION_REJECTED


def test_rejects_stale_backend_snapshot(tmp_path):
    snap = snapshot()
    stale = BrowserAccessibilitySnapshotBuilder().build(html="<html><body><button>Other</button></body></html>", text="Other")
    bus = EventBus(MISSION_ID)
    plan, plan_trace_id, snapshot_trace_id = create_plan(bus, snap)

    result = BrowserLimitedInteractionExecutor(backend=FakeInteractionBackend(stale)).execute(
        BrowserInteractionExecutionRequest(
            mission_id=MISSION_ID,
            plan=plan,
            plan_trace_event_id=plan_trace_id,
            before_snapshot_trace_event_id=snapshot_trace_id,
            final_url="https://example.com/form",
        ),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )

    assert result.accepted is False
    assert result.reason == "browser_interaction_stale_snapshot"


def test_rejects_cross_origin_after_action(tmp_path):
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    plan, plan_trace_id, snapshot_trace_id = create_plan(bus, snap)

    result = BrowserLimitedInteractionExecutor(backend=FakeInteractionBackend(snap, after_url="https://other.example/form")).execute(
        BrowserInteractionExecutionRequest(
            mission_id=MISSION_ID,
            plan=plan,
            plan_trace_event_id=plan_trace_id,
            before_snapshot_trace_event_id=snapshot_trace_id,
            final_url="https://example.com/form",
        ),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )

    assert result.accepted is False
    assert result.reason == "browser_interaction_cross_origin_result"


def test_press_plan_is_not_delegated_for_limited_execution(tmp_path):
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    plan, plan_trace_id, snapshot_trace_id = create_plan(
        bus,
        snap,
        steps=[
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.PRESS_PLAN,
                key="Enter",
                reason="Should not execute in P3H.",
            )
        ],
    )

    result = BrowserLimitedInteractionExecutor(backend=FakeInteractionBackend(snap)).execute(
        BrowserInteractionExecutionRequest(
            mission_id=MISSION_ID,
            plan=plan,
            plan_trace_event_id=plan_trace_id,
            before_snapshot_trace_event_id=snapshot_trace_id,
            final_url="https://example.com/form",
        ),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )

    assert result.accepted is False
    assert any("intent_not_delegated_for_limited_execution" in error for error in result.errors)


def test_final_gate_rejects_forged_execution_plan_hash(tmp_path):
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    plan, plan_trace_id, snapshot_trace_id = create_plan(bus, snap)
    result = BrowserLimitedInteractionExecutor(backend=FakeInteractionBackend(snap)).execute(
        BrowserInteractionExecutionRequest(
            mission_id=MISSION_ID,
            plan=plan,
            plan_trace_event_id=plan_trace_id,
            before_snapshot_trace_event_id=snapshot_trace_id,
            final_url="https://example.com/form",
        ),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )
    assert result.accepted is True

    events = list(bus.events())
    payload = dict(events[-1].payload)
    payload["plan_sha256"] = "0" * 64
    events[-1] = events[-1].model_copy(update={"payload": payload})

    check = execution_check(events)

    assert check.passed is False
    assert any("browser_interaction_execution_plan" in error for error in check.details["errors"])


def test_controlled_runner_requires_mission_authority(tmp_path):
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    plan, plan_trace_id, snapshot_trace_id = create_plan(bus, snap)
    call = CanonicalToolCall(
        tool_id="browser_public_operator_limited",
        action="browser_interaction_limited",
        target="https://example.com/form",
        capability="public_web_interaction_limited",
        arguments={
            "plan": plan.model_dump(mode="json"),
            "plan_trace_event_id": plan_trace_id,
            "before_snapshot_trace_event_id": snapshot_trace_id,
            "final_url": "https://example.com/form",
        },
        requested_side_effects=[],
        canonical_hash="hash",
    )

    result = BrowserControlledCapabilityRunner(
        registry=default_tool_registry(),
        capture_root=tmp_path / "captures",
        interaction_backend=FakeInteractionBackend(snap),
    ).run(call, envelope(allowed_tools=[]), event_bus=bus)

    assert result.accepted is False
    assert result.reason == "tool_not_granted_by_mission_authority"


def test_controlled_runner_executes_limited_interaction_with_policy_receipt(tmp_path):
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    plan, plan_trace_id, snapshot_trace_id = create_plan(bus, snap)
    call = CanonicalToolCall(
        tool_id="browser_public_operator_limited",
        action="browser_interaction_limited",
        target="https://example.com/form",
        capability="public_web_interaction_limited",
        arguments={
            "plan": plan.model_dump(mode="json"),
            "plan_trace_event_id": plan_trace_id,
            "before_snapshot_trace_event_id": snapshot_trace_id,
            "final_url": "https://example.com/form",
        },
        requested_side_effects=[],
        canonical_hash="hash",
    )

    result = BrowserControlledCapabilityRunner(
        registry=default_tool_registry(),
        capture_root=tmp_path / "captures",
        interaction_backend=FakeInteractionBackend(snap),
    ).run(call, envelope(), event_bus=bus)

    assert result.accepted is True
    assert result.receipt_id
    assert result.browser_trace_event_id
    assert execution_check(bus.events()).passed is True


def test_playwright_backend_performs_one_limited_fill_interaction(tmp_path):
    pytest.importorskip("playwright.sync_api")
    url = "https://example.com/form"
    fixture_html = """
        <html><body>
          <main>
            <textarea placeholder="Email"></textarea>
            <button>Continue</button>
          </main>
        </body></html>
    """
    rendered = PlaywrightReadOnlyRenderer(document_fixtures={url: fixture_html})(
        BrowserRenderedSnapshotRequest(
            mission_id=MISSION_ID,
            url=url,
            purpose="Initial rendered snapshot for limited interaction.",
            allowed_domains=["example.com"],
        ),
        url,
    )
    snap = BrowserAccessibilitySnapshotBuilder().build(html=rendered.html, text=rendered.text)
    bus = EventBus(MISSION_ID)
    plan, plan_trace_id, snapshot_trace_id = create_plan(
        bus,
        snap,
        final_url=url,
        steps=[
            {
                "intent": "fill_plan",
                "target": {"ref": first_ref(snap, "textbox")},
                "text": "operator@example.com",
                "reason": "Fill public form field without submitting.",
            }
        ],
    )
    backend = PlaywrightLimitedInteractionBackend(
        document_fixtures={url: fixture_html}
    )

    result = BrowserLimitedInteractionExecutor(backend=backend).execute(
        BrowserInteractionExecutionRequest(
            mission_id=MISSION_ID,
            plan=plan,
            plan_trace_event_id=plan_trace_id,
            before_snapshot_trace_event_id=snapshot_trace_id,
            final_url=url,
        ),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )

    assert result.accepted is True
    assert result.receipt is not None
    assert result.receipt.executed_intents == ["fill_plan"]
