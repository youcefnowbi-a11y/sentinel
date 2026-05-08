from __future__ import annotations

from types import SimpleNamespace

from sentinel.agent import AgentEventType, EventBus
from sentinel.agent.browser import (
    BrowserAccessibilitySnapshotBuilder,
    BrowserBoundingBox,
    BrowserCdpAccessibilityAdapter,
    BrowserDomSnapshotAdapter,
    BrowserScreenshotRegion,
    BrowserUIObservationBuilder,
    BrowserVisualObservationBuilder,
    BrowserVisualObservationKind,
)
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.agent.phases import AgentPhase


MISSION_ID = "mission_browser_v25_observation"


def v25_check(trace):
    return CoreFinalGate._browser_v25_observation_and_operator_contract(SimpleNamespace(trace=tuple(trace)))


def test_cdp_ax_tree_dom_snapshot_and_ui_observation_are_hash_bound():
    bus = EventBus(MISSION_ID)
    ax_result = BrowserCdpAccessibilityAdapter().capture(
        mission_id=MISSION_ID,
        url="https://example.com",
        raw_tree={
            "nodes": [
                {"nodeId": "1", "backendDOMNodeId": 10, "role": {"value": "RootWebArea"}, "name": {"value": "Example"}},
                {"nodeId": "2", "backendDOMNodeId": 11, "role": {"value": "button"}, "name": {"value": "Continue"}},
            ]
        },
        event_bus=bus,
    )
    assert ax_result.accepted is True
    assert ax_result.tree is not None
    assert ax_result.tree.node_count == 2

    dom_result = BrowserDomSnapshotAdapter().capture(
        mission_id=MISSION_ID,
        url="https://example.com",
        raw_snapshot={
            "nodes": [
                {"tag": "main", "text": "Example"},
                {
                    "tag": "button",
                    "text": "Continue",
                    "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                },
            ]
        },
        event_bus=bus,
    )
    assert dom_result.accepted is True
    assert dom_result.snapshot is not None
    assert dom_result.snapshot.layout_count == 1

    snap = BrowserAccessibilitySnapshotBuilder().build(
        html="<html><body><button>Continue</button></body></html>",
        text="Continue",
    )
    observation_set = BrowserUIObservationBuilder().from_accessibility_snapshot(
        mission_id=MISSION_ID,
        url="https://example.com",
        snapshot=snap,
        event_bus=bus,
    )

    assert observation_set.observations
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_UI_OBSERVATION_CAPTURED
    assert v25_check(bus.events()).passed is True
    assert bus.verify_chain() is True


def test_visual_crop_and_zoom_observation_use_stub_ocr_and_bounded_bytes():
    bus = EventBus(MISSION_ID)
    region = BrowserScreenshotRegion(
        bbox=BrowserBoundingBox(x=1, y=2, width=120, height=40),
        source_screenshot_sha256="a" * 64,
        ref_id="e1",
        reason="Ground button label.",
    )

    observation = BrowserVisualObservationBuilder().create(
        mission_id=MISSION_ID,
        url="https://example.com",
        region=region,
        kind=BrowserVisualObservationKind.ZOOM_REGION,
        crop_bytes=b"small-crop",
        zoom_factor=2,
        event_bus=bus,
    )

    assert observation.bytes_observed == len(b"small-crop")
    assert observation.artifact_sha256
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_VISUAL_OBSERVATION_CAPTURED
    assert v25_check(bus.events()).passed is True


def test_final_gate_rejects_forged_ui_observation_hash():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.BROWSER_UI_OBSERVATION_CAPTURED,
        "forged ui observation",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "observation_set_id": "buiset_1",
            "observation_sha256": "0" * 64,
            "observation_set": {
                "id": "buiset_1",
                "mission_id": MISSION_ID,
                "url": "https://example.com",
                "observations": [],
                "source_count": 1,
                "observation_sha256": "0" * 64,
                "trace_refs": [],
            },
            "source": "accessibility_snapshot",
            "source_count": 1,
            "observation_count": 0,
            "url": "https://example.com",
            "stateless_public": True,
            "cookies_enabled": False,
            "storage_enabled": False,
            "js_enabled": False,
            "downloads_enabled": False,
        },
    )

    check = v25_check(bus.events())

    assert check.passed is False
    assert any("browser_v25_ui_observation_hash_mismatch" in error for error in check.details["errors"])
