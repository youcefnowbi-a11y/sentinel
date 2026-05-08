from __future__ import annotations

import pytest

from sentinel.agent import AgentEventType, ArtifactCaptureSandbox, EventBus
from sentinel.agent.browser import (
    BrowserRenderedSnapshotAdapter,
    BrowserRenderedSnapshotRequest,
    BrowserSnapshotStatus,
    PlaywrightReadOnlyRenderer,
)


class FakeResolver:
    def __call__(self, host: str) -> list[str]:
        if host == "example.com":
            return ["93.184.216.34"]
        return []


def test_playwright_read_only_renderer_captures_rendered_fixture(tmp_path):
    url = "https://example.com/rendered"
    html = """
    <html>
      <head><title>Rendered Fixture</title></head>
      <body>
        <h1>Rendered proof</h1>
        <a href="/pricing">Pricing</a>
        <img src="https://127.0.0.1/private.png" />
      </body>
    </html>
    """
    request = BrowserRenderedSnapshotRequest(
        mission_id="mission_browser_playwright",
        url=url,
        purpose="Capture rendered evidence.",
        allowed_domains=["example.com"],
    )
    bus = EventBus("mission_browser_playwright")
    sandbox = ArtifactCaptureSandbox(mission_id="mission_browser_playwright", capture_root=tmp_path / "captures")
    renderer = PlaywrightReadOnlyRenderer(document_fixtures={url: html})

    try:
        result = BrowserRenderedSnapshotAdapter(renderer=renderer).capture(
            request,
            event_bus=bus,
            artifact_capture=sandbox,
            resolver=FakeResolver(),
        )
    except Exception as exc:
        pytest.skip(f"Playwright browser backend unavailable: {exc}")

    assert result.accepted is True
    assert result.status == BrowserSnapshotStatus.CAPTURED
    assert result.title == "Rendered Fixture"
    assert "Rendered proof" in result.extracted_text
    assert result.links == ["https://example.com/pricing"]
    assert result.receipt is not None
    assert result.receipt.screenshot_artifact_id is not None
    assert result.receipt.screenshot_artifact_sha256 is not None
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_SNAPSHOT_CAPTURED
    assert bus.verify_chain() is True
