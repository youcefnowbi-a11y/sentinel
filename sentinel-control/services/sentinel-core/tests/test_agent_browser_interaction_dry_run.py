from __future__ import annotations

from types import SimpleNamespace

import pytest

from sentinel.agent import AgentEventType, EventBus
from sentinel.agent.browser import (
    BrowserAccessibilitySnapshotBuilder,
    BrowserInteractionDryRunPlanner,
    BrowserInteractionImpact,
    BrowserInteractionIntent,
    BrowserInteractionStep,
    BrowserInteractionTarget,
    BrowserWaitPredicate,
    hash_browser_interaction_plan_payload,
)
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.agent.phases import AgentPhase


MISSION_ID = "mission_browser_interaction"


def snapshot():
    html = """
    <html><body>
      <main>
        <h1>Contact</h1>
        <a href="/pricing">Pricing</a>
        <button>Continue</button>
        <input type="text" placeholder="Email" />
        <select><option>Starter</option></select>
      </main>
    </body></html>
    """
    return BrowserAccessibilitySnapshotBuilder().build(html=html, text="Contact Pricing Continue Email Starter")


def first_ref(snap, role: str | None = None) -> str:
    for ref_id, ref in snap.refs.items():
        if role is None or ref.role == role:
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


def dry_run_check(trace):
    return CoreFinalGate._browser_interaction_dry_run_contract(SimpleNamespace(trace=tuple(trace)))


def test_creates_interaction_plan_from_stable_refs():
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    snapshot_event_id = append_snapshot_event(bus, snap)
    ref_id = first_ref(snap, "link")

    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        steps=[
            {
                "intent": "click_plan",
                "target": {"ref": ref_id},
                "reason": "Plan opening pricing page.",
            }
        ],
        event_bus=bus,
        final_url="https://example.com",
        snapshot_trace_id=snapshot_event_id,
    )

    assert result.accepted is True
    assert result.plan is not None
    assert result.proof is not None
    assert result.plan.required_ref_ids == [ref_id]
    assert result.plan.steps[0].target.role == "link"
    assert result.plan.steps[0].impact == BrowserInteractionImpact.LOCAL_PAGE_STATE
    assert result.proof.plan_sha256 == result.plan.plan_sha256
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_INTERACTION_PLAN_CREATED
    assert bus.events()[-1].payload["dry_run_only"] is True

    check = dry_run_check(bus.events())
    assert check.passed is True


def test_rejects_unknown_ref_target():
    snap = snapshot()
    bus = EventBus(MISSION_ID)

    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        steps=[{"intent": "click_plan", "target": {"ref": "missing-ref"}}],
        event_bus=bus,
    )

    assert result.accepted is False
    assert "unknown_ref_0:missing-ref" in result.errors
    assert not bus.events()


def test_rejects_stale_snapshot_or_page_hash():
    snap = snapshot()
    bus = EventBus(MISSION_ID)

    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        expected_page_sha256="stale-page-hash",
        steps=[{"intent": "hover_plan", "target": {"ref": first_ref(snap)}}],
        event_bus=bus,
    )

    assert result.accepted is False
    assert result.reason == "stale_page_hash"


@pytest.mark.parametrize("intent", ["submit", "submit_plan", "upload", "download", "evaluate", "arbitrary_js"])
def test_rejects_non_delegated_interaction_actions(intent: str):
    snap = snapshot()
    bus = EventBus(MISSION_ID)

    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        steps=[{"intent": intent, "target": {"ref": first_ref(snap)}}],
        event_bus=bus,
    )

    assert result.accepted is False
    assert any("forbidden_interaction_intent_0" in error for error in result.errors)


def test_wait_and_form_steps_are_dry_run_plans_only():
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    snapshot_event_id = append_snapshot_event(bus, snap)
    input_ref = first_ref(snap, "textbox")

    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        steps=[
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.FILL_PLAN,
                target=BrowserInteractionTarget(ref=input_ref),
                text="user@example.com",
            ),
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.WAIT_FOR_TEXT_PLAN,
                text="Thanks",
                wait_predicate=BrowserWaitPredicate.TEXT,
            ),
        ],
        event_bus=bus,
        snapshot_trace_id=snapshot_event_id,
    )

    assert result.accepted is True
    assert result.plan is not None
    assert [step.intent for step in result.plan.steps] == [
        BrowserInteractionIntent.FILL_PLAN,
        BrowserInteractionIntent.WAIT_FOR_TEXT_PLAN,
    ]
    assert result.plan.steps[0].impact == BrowserInteractionImpact.LOCAL_FORM_STATE
    assert result.plan.dry_run_only is True
    assert dry_run_check(bus.events()).passed is True


def test_final_gate_rejects_forged_interaction_plan_hash():
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    snapshot_event_id = append_snapshot_event(bus, snap)
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        steps=[{"intent": "click_plan", "target": {"ref": first_ref(snap)}}],
        event_bus=bus,
        snapshot_trace_id=snapshot_event_id,
    )
    assert result.accepted is True

    events = list(bus.events())
    forged_payload = dict(events[-1].payload)
    forged_payload["plan_sha256"] = "0" * 64
    events[-1] = events[-1].model_copy(update={"payload": forged_payload})

    check = dry_run_check(events)

    assert check.passed is False
    assert any("browser_interaction_plan_hash" in error for error in check.details["errors"])


def test_final_gate_rejects_plan_with_forged_unknown_ref():
    snap = snapshot()
    bus = EventBus(MISSION_ID)
    snapshot_event_id = append_snapshot_event(bus, snap)
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        steps=[{"intent": "click_plan", "target": {"ref": first_ref(snap)}}],
        event_bus=bus,
        snapshot_trace_id=snapshot_event_id,
    )
    assert result.accepted is True

    events = list(bus.events())
    forged_payload = dict(events[-1].payload)
    forged_plan = dict(forged_payload["plan"])
    forged_plan["required_ref_ids"] = ["missing-ref"]
    plan_payload = {key: value for key, value in forged_plan.items() if key != "plan_sha256"}
    forged_plan["plan_sha256"] = hash_browser_interaction_plan_payload(plan_payload)
    forged_payload["plan"] = forged_plan
    forged_payload["plan_sha256"] = forged_plan["plan_sha256"]
    forged_payload["required_ref_ids"] = ["missing-ref"]
    events[-1] = events[-1].model_copy(update={"payload": forged_payload})

    check = dry_run_check(events)

    assert check.passed is False
    assert any("browser_interaction_plan_unknown_ref" in error for error in check.details["errors"])


def test_final_gate_rejects_real_browser_interaction_event_during_p3g():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.CONTROLLED_CAPABILITY_EXECUTED,
        "Real browser interaction event should not exist in P3G.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={"action": "browser_click"},
    )

    check = dry_run_check(bus.events())

    assert check.passed is False
    assert any("browser_real_interaction_event_in_p3g" in error for error in check.details["errors"])
