from __future__ import annotations

from types import SimpleNamespace

from sentinel.agent import AgentEventType, EventBus
from sentinel.agent.browser import BrowserPublicLifecycleController
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.agent.phases import AgentPhase


MISSION_ID = "mission_browser_public_lifecycle"


class FakeResolver:
    def __init__(self, mapping: dict[str, list[str]] | None = None):
        self.mapping = mapping or {}

    def __call__(self, host: str) -> list[str]:
        return self.mapping.get(host, [])


def lifecycle_check(trace):
    return CoreFinalGate._browser_public_lifecycle_contract(SimpleNamespace(trace=tuple(trace)))


def resolver():
    return FakeResolver(
        {
            "example.com": ["93.184.216.34"],
            "docs.example.com": ["93.184.216.35"],
        }
    )


def test_public_session_tab_navigation_and_closure_are_trace_bound():
    bus = EventBus(MISSION_ID)
    controller = BrowserPublicLifecycleController()

    session_result = controller.start_session(
        mission_id=MISSION_ID,
        purpose="Track public evidence tabs.",
        max_tabs=2,
        event_bus=bus,
    )
    assert session_result.accepted is True
    assert session_result.session is not None

    open_result = controller.open_tab(
        session_id=session_result.session.id,
        url="https://example.com/start",
        allowed_domains=["example.com", "docs.example.com"],
        resolver=resolver(),
        event_bus=bus,
    )
    assert open_result.accepted is True
    assert open_result.tab is not None
    assert open_result.receipt is not None
    assert open_result.receipt.stateless_public is True
    assert open_result.receipt.cookies_enabled is False
    assert open_result.receipt.storage_enabled is False

    nav_result = controller.navigate_tab(
        session_id=session_result.session.id,
        tab_id=open_result.tab.id,
        url="https://docs.example.com/page",
        allowed_domains=["example.com", "docs.example.com"],
        resolver=resolver(),
        event_bus=bus,
    )
    assert nav_result.accepted is True
    assert nav_result.tab is not None
    assert nav_result.tab.navigation_count == 1

    close_tab_result = controller.close_tab(
        session_id=session_result.session.id,
        tab_id=open_result.tab.id,
        event_bus=bus,
    )
    assert close_tab_result.accepted is True

    close_session_result = controller.close_session(
        session_id=session_result.session.id,
        event_bus=bus,
    )
    assert close_session_result.accepted is True

    assert [event.event_type for event in bus.events()] == [
        AgentEventType.BROWSER_PUBLIC_SESSION_STARTED,
        AgentEventType.BROWSER_URL_CLASSIFIED,
        AgentEventType.BROWSER_PUBLIC_TAB_OPENED,
        AgentEventType.BROWSER_URL_CLASSIFIED,
        AgentEventType.BROWSER_PUBLIC_TAB_NAVIGATED,
        AgentEventType.BROWSER_PUBLIC_TAB_CLOSED,
        AgentEventType.BROWSER_PUBLIC_SESSION_CLOSED,
    ]
    assert lifecycle_check(bus.events()).passed is True
    assert bus.verify_chain() is True


def test_public_lifecycle_blocks_private_url_before_tab_open():
    bus = EventBus(MISSION_ID)
    controller = BrowserPublicLifecycleController()
    session = controller.start_session(
        mission_id=MISSION_ID,
        purpose="Track public evidence tabs.",
        event_bus=bus,
    )
    assert session.session is not None

    result = controller.open_tab(
        session_id=session.session.id,
        url="https://127.0.0.1/admin",
        allowed_domains=["127.0.0.1"],
        event_bus=bus,
    )

    assert result.accepted is False
    assert result.reason == "private_or_internal_ip"
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_PUBLIC_LIFECYCLE_REJECTED
    assert lifecycle_check(bus.events()).passed is True


def test_public_lifecycle_rejects_navigation_after_session_closed():
    bus = EventBus(MISSION_ID)
    controller = BrowserPublicLifecycleController()
    session = controller.start_session(
        mission_id=MISSION_ID,
        purpose="Track public evidence tabs.",
        event_bus=bus,
    )
    assert session.session is not None
    opened = controller.open_tab(
        session_id=session.session.id,
        url="https://example.com/start",
        allowed_domains=["example.com"],
        resolver=resolver(),
        event_bus=bus,
    )
    assert opened.tab is not None
    controller.close_session(session_id=session.session.id, event_bus=bus)

    result = controller.navigate_tab(
        session_id=session.session.id,
        tab_id=opened.tab.id,
        url="https://example.com/next",
        allowed_domains=["example.com"],
        resolver=resolver(),
        event_bus=bus,
    )

    assert result.accepted is False
    assert result.reason == "browser_public_session_closed"
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_PUBLIC_LIFECYCLE_REJECTED
    assert lifecycle_check(bus.events()).passed is True


def test_public_lifecycle_enforces_max_tabs():
    bus = EventBus(MISSION_ID)
    controller = BrowserPublicLifecycleController()
    session = controller.start_session(
        mission_id=MISSION_ID,
        purpose="Track one tab.",
        max_tabs=1,
        event_bus=bus,
    )
    assert session.session is not None

    first = controller.open_tab(
        session_id=session.session.id,
        url="https://example.com/one",
        allowed_domains=["example.com"],
        resolver=resolver(),
        event_bus=bus,
    )
    second = controller.open_tab(
        session_id=session.session.id,
        url="https://example.com/two",
        allowed_domains=["example.com"],
        resolver=resolver(),
        event_bus=bus,
    )

    assert first.accepted is True
    assert second.accepted is False
    assert second.reason == "browser_public_tab_limit_reached"
    assert lifecycle_check(bus.events()).passed is True


def test_final_gate_rejects_forged_tab_open_without_url_policy_trace():
    bus = EventBus(MISSION_ID)
    started = bus.append(
        AgentEventType.BROWSER_PUBLIC_SESSION_STARTED,
        "session",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_session",
            "session_id": "session_1",
            "purpose": "forged",
            "max_tabs": 2,
            "stateless_public": True,
            "cookies_enabled": False,
            "storage_enabled": False,
            "status": "active",
        },
    )
    bus.append(
        AgentEventType.BROWSER_PUBLIC_TAB_OPENED,
        "forged open",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_tab",
            "session_id": "session_1",
            "tab_id": "tab_1",
            "final_url": "https://example.com",
            "navigation_count": 0,
            "stateless_public": True,
            "cookies_enabled": False,
            "storage_enabled": False,
            "status": "active",
        },
        trace_refs=[started.id],
    )

    check = lifecycle_check(bus.events())

    assert check.passed is False
    assert any("browser_public_tab_open_missing_url_policy" in error for error in check.details["errors"])


def test_final_gate_rejects_navigation_for_unknown_tab():
    bus = EventBus(MISSION_ID)
    url_event = bus.append(
        AgentEventType.BROWSER_URL_CLASSIFIED,
        "url",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "url_decision_id": "url_1",
            "status": "allowed",
            "reason": "allowed_public_url",
            "original_url": "https://example.com",
            "final_url": "https://example.com/",
            "host": "example.com",
            "resolved_addresses": ["93.184.216.34"],
            "redirect_chain": ["https://example.com/"],
            "errors": [],
        },
    )
    bus.append(
        AgentEventType.BROWSER_PUBLIC_TAB_NAVIGATED,
        "forged navigate",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_nav",
            "session_id": "missing_session",
            "tab_id": "missing_tab",
            "previous_url": "https://example.com/old",
            "final_url": "https://example.com/",
            "url_policy_trace_id": url_event.id,
            "navigation_count": 1,
            "stateless_public": True,
            "cookies_enabled": False,
            "storage_enabled": False,
            "status": "active",
        },
        trace_refs=[url_event.id],
    )

    check = lifecycle_check(bus.events())

    assert check.passed is False
    assert any("browser_public_tab_nav_session_missing" in error for error in check.details["errors"])
