from __future__ import annotations

from types import SimpleNamespace

from sentinel.agent import AgentEventType, EventBus
from sentinel.agent.browser import (
    BrowserAdvancedPoolLeaseStatus,
    BrowserInteractionExecutionReceipt,
    BrowserMultitabStrategyResult,
    BrowserPostActionVerifier,
    BrowserPublicMultitabOperator,
    BrowserPublicPoolManager,
    BrowserPublicTabPlan,
    BrowserRenderedSnapshotReceipt,
    BrowserRenderedSnapshotResult,
    BrowserSnapshotStatus,
    BrowserLoopDetector,
    PublicUrlDecision,
    PublicUrlDecisionStatus,
)
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.agent.phases import AgentPhase


MISSION_ID = "mission_browser_v25_operator"


class FakeResolver:
    def __call__(self, host: str) -> list[str]:
        return {
            "example.com": ["93.184.216.34"],
            "docs.example.com": ["93.184.216.35"],
        }.get(host, [])


def v25_check(trace):
    return CoreFinalGate._browser_v25_observation_and_operator_contract(SimpleNamespace(trace=tuple(trace)))


def test_public_pool_lease_release_and_multitab_strategy_are_trace_bound():
    bus = EventBus(MISSION_ID)
    pool = BrowserPublicPoolManager(capacity=1)
    pool.start(mission_id=MISSION_ID, event_bus=bus)
    lease = pool.lease(mission_id=MISSION_ID, purpose="Warm public renderer.", event_bus=bus)
    assert lease.accepted is True
    assert lease.lease is not None
    assert lease.lease.status == BrowserAdvancedPoolLeaseStatus.LEASED
    released = pool.release(lease_id=lease.lease.id, event_bus=bus)
    assert released.accepted is True

    multitab = BrowserPublicMultitabOperator().execute_strategy(
        mission_id=MISSION_ID,
        purpose="Compare public pages.",
        tab_plans=[
            BrowserPublicTabPlan(url="https://example.com/a", purpose="primary"),
            BrowserPublicTabPlan(url="https://docs.example.com/b", purpose="docs"),
        ],
        allowed_domains=["example.com", "docs.example.com"],
        resolver=FakeResolver(),
        max_tabs=2,
        event_bus=bus,
    )

    assert multitab.accepted is True
    assert len(multitab.tabs) == 2
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_MULTITAB_STRATEGY_EXECUTED
    assert v25_check(bus.events()).passed is True
    assert bus.verify_chain() is True


def test_public_pool_rejects_over_capacity_without_private_state():
    bus = EventBus(MISSION_ID)
    pool = BrowserPublicPoolManager(capacity=1)
    first = pool.lease(mission_id=MISSION_ID, purpose="first", event_bus=bus)
    second = pool.lease(mission_id=MISSION_ID, purpose="second", event_bus=bus)

    assert first.accepted is True
    assert second.accepted is False
    assert second.reason == "browser_public_pool_capacity_exhausted"


def test_loop_detector_emits_bounded_loop_event():
    bus = EventBus(MISSION_ID)
    result = BrowserLoopDetector().detect(
        mission_id=MISSION_ID,
        recent_state_keys=["click:e1:hash", "click:e1:hash", "click:e1:hash"],
        threshold=3,
        event_bus=bus,
    )

    assert result.detected is True
    assert result.repeated_count == 3
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_LOOP_DETECTED
    assert v25_check(bus.events()).passed is True


def test_post_action_verifier_accepts_receipt_bound_after_snapshot():
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
        network_ledger_sha256="n" * 64,
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
        extracted_text="The account settings panel opened.",
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

    result = BrowserPostActionVerifier().verify(
        mission_id=MISSION_ID,
        receipt=receipt,
        after_snapshot=after,
        expected_text="settings panel",
        expected_url="https://example.com",
        event_bus=bus,
    )

    assert result.verdict == "accepted"
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_VERIFICATION_COMPLETED
    assert v25_check(bus.events()).passed is True


def test_final_gate_rejects_forged_stateful_v25_pool_event():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.BROWSER_ADVANCED_POOL_LEASED,
        "forged stateful pool",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "lease_id": "lease_1",
            "instance_id": "instance_1",
            "purpose": "forged",
            "backend_kind": "playwright_public",
            "status": "leased",
            "stateless_public": False,
            "cookies_enabled": True,
            "storage_enabled": True,
            "js_enabled": True,
            "downloads_enabled": True,
        },
    )

    check = v25_check(bus.events())

    assert check.passed is False
    assert any("browser_v25_not_stateless" in error for error in check.details["errors"])
