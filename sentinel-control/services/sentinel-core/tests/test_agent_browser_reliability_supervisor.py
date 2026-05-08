from __future__ import annotations

from types import SimpleNamespace

from sentinel.agent import AgentEventType, EventBus
from sentinel.agent.browser import (
    BrowserHealthStatus,
    BrowserOperationError,
    BrowserReliabilitySupervisor,
    BrowserRetryPolicy,
)
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.agent.phases import AgentPhase


MISSION_ID = "mission_browser_reliability_supervisor"


def reliability_check(trace):
    return CoreFinalGate._browser_reliability_supervisor_contract(SimpleNamespace(trace=tuple(trace)))


def test_browser_pool_lease_and_release_are_stateless_and_trace_bound():
    bus = EventBus(MISSION_ID)
    supervisor = BrowserReliabilitySupervisor()

    lease = supervisor.lease(
        mission_id=MISSION_ID,
        purpose="Render public evidence repeatedly.",
        event_bus=bus,
        max_operations=2,
    )
    assert lease.accepted is True
    assert lease.lease is not None
    assert lease.receipt is not None
    assert lease.receipt.stateless_public is True
    assert lease.receipt.cookies_enabled is False
    assert lease.receipt.storage_enabled is False
    assert lease.receipt.js_enabled is False
    assert lease.receipt.downloads_enabled is False

    released = supervisor.release(lease_id=lease.lease.id, event_bus=bus)

    assert released.accepted is True
    assert [event.event_type for event in bus.events()] == [
        AgentEventType.BROWSER_POOL_LEASED,
        AgentEventType.BROWSER_POOL_RELEASED,
    ]
    assert reliability_check(bus.events()).passed is True
    assert bus.verify_chain() is True


def test_browser_health_check_is_trace_bound_to_lease():
    bus = EventBus(MISSION_ID)
    supervisor = BrowserReliabilitySupervisor()
    lease = supervisor.lease(mission_id=MISSION_ID, purpose="Probe renderer.", event_bus=bus)
    assert lease.lease is not None

    health = supervisor.health_check(
        mission_id=MISSION_ID,
        lease_id=lease.lease.id,
        event_bus=bus,
        probe=lambda: {"status": BrowserHealthStatus.HEALTHY.value, "notes": ["probe_ok"]},
    )

    assert health.status == BrowserHealthStatus.HEALTHY
    assert health.lease_id == lease.lease.id
    assert health.trace_refs[-1] == bus.events()[-1].id
    assert reliability_check(bus.events()).passed is True


def test_retry_wrapper_retries_transient_failure_then_succeeds():
    bus = EventBus(MISSION_ID)
    supervisor = BrowserReliabilitySupervisor()
    lease = supervisor.lease(mission_id=MISSION_ID, purpose="Retry render.", event_bus=bus)
    assert lease.lease is not None
    calls = {"count": 0}

    def flaky_operation():
        calls["count"] += 1
        if calls["count"] == 1:
            raise BrowserOperationError("browser_transient_error", "temporary renderer miss")
        return {"value": "ok"}

    result = supervisor.run_with_retries(
        flaky_operation,
        mission_id=MISSION_ID,
        operation_name="render_snapshot",
        lease_id=lease.lease.id,
        event_bus=bus,
        retry_policy=BrowserRetryPolicy(max_attempts=2),
    )

    assert result.accepted is True
    assert result.result == {"value": "ok"}
    assert calls["count"] == 2
    assert [event.event_type for event in bus.events()] == [
        AgentEventType.BROWSER_POOL_LEASED,
        AgentEventType.BROWSER_OPERATION_RETRIED,
    ]
    assert reliability_check(bus.events()).passed is True


def test_retry_wrapper_stops_at_max_attempts_and_rejects():
    bus = EventBus(MISSION_ID)
    supervisor = BrowserReliabilitySupervisor()

    def failing_operation():
        raise BrowserOperationError("browser_transient_error", "still unavailable")

    result = supervisor.run_with_retries(
        failing_operation,
        mission_id=MISSION_ID,
        operation_name="render_snapshot",
        event_bus=bus,
        retry_policy=BrowserRetryPolicy(max_attempts=2),
    )

    assert result.accepted is False
    assert result.reason == "browser_transient_error"
    assert [event.event_type for event in bus.events()] == [
        AgentEventType.BROWSER_OPERATION_RETRIED,
        AgentEventType.BROWSER_SUPERVISOR_REJECTED,
    ]
    assert reliability_check(bus.events()).passed is True


def test_supervisor_rejects_operation_on_released_lease():
    bus = EventBus(MISSION_ID)
    supervisor = BrowserReliabilitySupervisor()
    lease = supervisor.lease(mission_id=MISSION_ID, purpose="One operation.", event_bus=bus)
    assert lease.lease is not None
    supervisor.release(lease_id=lease.lease.id, event_bus=bus)

    result = supervisor.run_with_retries(
        lambda: {"should_not_run": True},
        mission_id=MISSION_ID,
        operation_name="render_snapshot",
        lease_id=lease.lease.id,
        event_bus=bus,
    )

    assert result.accepted is False
    assert result.errors == ["browser_pool_lease_not_active"]
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_SUPERVISOR_REJECTED
    assert reliability_check(bus.events()).passed is True


def test_final_gate_rejects_forged_stateful_browser_lease():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.BROWSER_POOL_LEASED,
        "forged stateful lease",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_1",
            "lease_id": "lease_1",
            "purpose": "forged",
            "backend_kind": "playwright_public",
            "max_operations": 2,
            "operation_count": 0,
            "stateless_public": False,
            "cookies_enabled": True,
            "storage_enabled": True,
            "js_enabled": True,
            "downloads_enabled": True,
            "status": "leased",
        },
    )

    check = reliability_check(bus.events())

    assert check.passed is False
    assert any("browser_supervisor_not_stateless" in error for error in check.details["errors"])
    assert any("browser_supervisor_cookies_enabled" in error for error in check.details["errors"])


def test_final_gate_rejects_unbounded_retry_event():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.BROWSER_OPERATION_RETRIED,
        "forged retry",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "operation_name": "render_snapshot",
            "attempt_number": 2,
            "max_attempts": 2,
            "reason": "browser_transient_error",
            "retryable": True,
            "status": "retrying",
            "stateless_public": True,
            "cookies_enabled": False,
            "storage_enabled": False,
            "js_enabled": False,
            "downloads_enabled": False,
        },
    )

    check = reliability_check(bus.events())

    assert check.passed is False
    assert any("browser_retry_attempt_not_bounded" in error for error in check.details["errors"])


def test_final_gate_rejects_release_without_lease():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.BROWSER_POOL_RELEASED,
        "forged release",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_release",
            "lease_id": "missing",
            "backend_kind": "playwright_public",
            "max_operations": 2,
            "operation_count": 0,
            "stateless_public": True,
            "cookies_enabled": False,
            "storage_enabled": False,
            "js_enabled": False,
            "downloads_enabled": False,
            "status": "released",
        },
    )

    check = reliability_check(bus.events())

    assert check.passed is False
    assert any("browser_pool_release_unknown_lease" in error for error in check.details["errors"])
