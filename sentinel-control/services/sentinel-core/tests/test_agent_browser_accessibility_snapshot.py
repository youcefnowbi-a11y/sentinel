from __future__ import annotations

import json
import struct

from sentinel.agent import AgentEventType, ArtifactCaptureSandbox, EventBus
from sentinel.agent.browser import (
    BrowserAccessibilitySnapshotBuilder,
    BrowserRenderedPage,
    BrowserRenderedSnapshotAdapter,
    BrowserRenderedSnapshotRequest,
    BrowserSnapshotStatus,
)


def png_bytes(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height) + b"\x08\x02\x00\x00\x00" + b"\x00\x00\x00\x00"


class FakeResolver:
    def __call__(self, host: str) -> list[str]:
        return ["93.184.216.34"]


class FakeRenderer:
    def __init__(self, page: BrowserRenderedPage) -> None:
        self.page = page

    def __call__(self, request: BrowserRenderedSnapshotRequest, final_url: str) -> BrowserRenderedPage:
        return self.page.model_copy(update={"final_url": final_url})


def request(**overrides) -> BrowserRenderedSnapshotRequest:
    data = {
        "mission_id": "mission_browser_snapshot",
        "url": "https://example.com/rendered",
        "purpose": "Capture rendered public evidence.",
        "allowed_domains": ["example.com"],
    }
    data.update(overrides)
    return BrowserRenderedSnapshotRequest(**data)


def sandbox(tmp_path) -> ArtifactCaptureSandbox:
    return ArtifactCaptureSandbox(mission_id="mission_browser_snapshot", capture_root=tmp_path / "captures")


def test_accessibility_snapshot_builder_creates_stable_refs_and_duplicate_nth():
    html = """
    <html><body>
      <main><h1>Checkout</h1>
        <a href="/pricing">Pricing</a>
        <button>OK</button>
        <button>OK</button>
        <input type="search" placeholder="Search docs" />
      </main>
    </body></html>
    """

    snapshot = BrowserAccessibilitySnapshotBuilder().build(html=html, text="Checkout Pricing OK OK Search docs")

    assert '- link "Pricing" [ref=' in snapshot.snapshot
    assert '- button "OK" [ref=' in snapshot.snapshot
    assert "[nth=1]" in snapshot.snapshot
    assert snapshot.stats.refs >= 4
    assert snapshot.stats.interactive >= 4
    assert snapshot.snapshot_sha256
    assert snapshot.page_sha256


def test_rendered_snapshot_records_accessibility_snapshot_and_screenshot_metadata(tmp_path):
    html = """
    <html><head><title>Rendered</title></head><body>
      <main><h1>Rendered proof</h1><a href="/pricing">Pricing</a><button>Save</button></main>
    </body></html>
    """
    page = BrowserRenderedPage(
        final_url="https://example.com/rendered",
        status_code=200,
        title="Rendered",
        text="Rendered proof Pricing Save",
        links=["https://example.com/pricing"],
        html=html,
        screenshot_png=png_bytes(640, 480),
    )
    bus = EventBus("mission_browser_snapshot")

    result = BrowserRenderedSnapshotAdapter(renderer=FakeRenderer(page)).capture(
        request(),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
        resolver=FakeResolver(),
    )

    assert result.accepted is True
    assert result.accessibility_snapshot is not None
    assert result.accessibility_snapshot.stats.refs >= 2
    assert result.screenshot_metadata is not None
    assert result.screenshot_metadata.width == 640
    assert result.screenshot_metadata.height == 480
    assert result.receipt is not None
    assert result.receipt.accessibility_snapshot_sha256 == result.accessibility_snapshot.snapshot_sha256
    assert result.receipt.screenshot_metadata["width"] == 640

    event = bus.events()[-1]
    assert event.event_type == AgentEventType.BROWSER_SNAPSHOT_CAPTURED
    assert event.payload["accessibility_snapshot_sha256"] == result.accessibility_snapshot.snapshot_sha256
    assert event.payload["screenshot_metadata"]["height"] == 480

    snapshot_event = bus.events()[1]
    snapshot_path = tmp_path / "captures" / snapshot_event.payload["relative_path"]
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert payload["accessibility_snapshot"]["snapshot_sha256"] == result.accessibility_snapshot.snapshot_sha256
    assert payload["screenshot_metadata"]["content_type"] == "image/png"


def test_rendered_snapshot_rejects_screenshot_that_exceeds_max_side(tmp_path):
    page = BrowserRenderedPage(
        final_url="https://example.com/rendered",
        status_code=200,
        title="Too Large",
        text="Rendered proof",
        html="<html><body><main>Rendered proof</main></body></html>",
        screenshot_png=png_bytes(1200, 600),
    )
    bus = EventBus("mission_browser_snapshot")

    result = BrowserRenderedSnapshotAdapter(renderer=FakeRenderer(page)).capture(
        request(max_screenshot_side=800),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
        resolver=FakeResolver(),
    )

    assert result.accepted is False
    assert result.status == BrowserSnapshotStatus.REJECTED
    assert result.reason == "browser_screenshot_dimensions_too_large"
    assert AgentEventType.ARTIFACT_CAPTURED not in [event.event_type for event in bus.events()]
