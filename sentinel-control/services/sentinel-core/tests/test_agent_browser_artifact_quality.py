from __future__ import annotations

import json
import struct
from types import SimpleNamespace

from sentinel.agent import ArtifactCaptureSandbox, EventBus
from sentinel.agent.browser import (
    BrowserAccessibilitySnapshotBuilder,
    BrowserRenderedElementScreenshot,
    BrowserRenderedPage,
    BrowserRenderedSnapshotAdapter,
    BrowserRenderedSnapshotRequest,
    BrowserSnapshotStatus,
)
from sentinel.agent.final_gate import CoreFinalGate


MISSION_ID = "mission_browser_artifact_quality"


def png_bytes(width: int, height: int, *, padding: int = 0) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
        + b"\x00\x00\x00\x00"
        + (b"x" * padding)
    )


def pdf_bytes() -> bytes:
    return b"%PDF-1.4\n1 0 obj\n<< /Type /Page >>\nendobj\n%%EOF\n"


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
        "mission_id": MISSION_ID,
        "url": "https://example.com/rendered",
        "purpose": "Capture rich browser artifacts.",
        "allowed_domains": ["example.com"],
    }
    data.update(overrides)
    return BrowserRenderedSnapshotRequest(**data)


def sandbox(tmp_path) -> ArtifactCaptureSandbox:
    return ArtifactCaptureSandbox(mission_id=MISSION_ID, capture_root=tmp_path / "captures")


def browser_receipt_check(trace):
    return CoreFinalGate._browser_capability_receipts(SimpleNamespace(trace=tuple(trace), controlled_capability_results=[]))


def test_rendered_snapshot_normalizes_oversized_screenshot_with_proof(tmp_path):
    bus = EventBus(MISSION_ID)
    page = BrowserRenderedPage(
        final_url="https://example.com/rendered",
        status_code=200,
        title="Big screenshot",
        text="Screenshot normalization proof.",
        html="<html><body><main>Screenshot normalization proof.</main></body></html>",
        screenshot_png=png_bytes(1200, 900, padding=500),
    )

    def normalizer(data, metadata):
        assert metadata.width == 1200
        assert "dimensions_exceed_max_side" in metadata.warnings
        return png_bytes(800, 600)

    result = BrowserRenderedSnapshotAdapter(
        renderer=FakeRenderer(page),
        screenshot_normalizer=normalizer,
    ).capture(
        request(max_screenshot_side=800),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
        resolver=FakeResolver(),
    )

    assert result.accepted is True
    assert result.screenshot_metadata is not None
    assert result.screenshot_metadata.normalized is True
    assert result.screenshot_metadata.original_width == 1200
    assert result.screenshot_metadata.width == 800
    assert result.receipt is not None
    assert result.receipt.screenshot_metadata["normalized"] is True
    assert browser_receipt_check(bus.events()).passed is True


def test_rendered_snapshot_captures_pdf_artifact_and_metadata(tmp_path):
    bus = EventBus(MISSION_ID)
    page = BrowserRenderedPage(
        final_url="https://example.com/rendered",
        status_code=200,
        title="PDF",
        text="PDF artifact proof.",
        html="<html><body><main>PDF artifact proof.</main></body></html>",
        screenshot_png=png_bytes(640, 480),
        pdf_bytes=pdf_bytes(),
    )

    result = BrowserRenderedSnapshotAdapter(renderer=FakeRenderer(page)).capture(
        request(capture_pdf=True),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
        resolver=FakeResolver(),
    )

    assert result.accepted is True
    assert result.pdf_metadata is not None
    assert result.pdf_metadata.content_type == "application/pdf"
    assert result.receipt is not None
    assert result.receipt.pdf_artifact_id is not None
    assert result.receipt.pdf_artifact_sha256 is not None
    assert bus.events()[-1].payload["pdf_metadata"]["bytes"] == len(pdf_bytes())
    assert browser_receipt_check(bus.events()).passed is True


def test_rendered_snapshot_rejects_invalid_pdf(tmp_path):
    bus = EventBus(MISSION_ID)
    page = BrowserRenderedPage(
        final_url="https://example.com/rendered",
        status_code=200,
        title="Bad PDF",
        text="Bad PDF artifact proof.",
        html="<html><body><main>Bad PDF artifact proof.</main></body></html>",
        screenshot_png=png_bytes(640, 480),
        pdf_bytes=b"not a pdf",
    )

    result = BrowserRenderedSnapshotAdapter(renderer=FakeRenderer(page)).capture(
        request(capture_pdf=True),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
        resolver=FakeResolver(),
    )

    assert result.accepted is False
    assert result.status == BrowserSnapshotStatus.REJECTED
    assert result.reason == "browser_pdf_invalid"
    assert "invalid_pdf_header" in result.errors


def test_rendered_snapshot_captures_element_screenshot_for_stable_ref(tmp_path):
    html = """
    <html><body><main><h1>Plan</h1><button>Inspect</button></main></body></html>
    """
    snapshot = BrowserAccessibilitySnapshotBuilder().build(html=html, text="Plan Inspect")
    button_ref = next(ref_id for ref_id, ref in snapshot.refs.items() if ref.role == "button")
    bus = EventBus(MISSION_ID)
    page = BrowserRenderedPage(
        final_url="https://example.com/rendered",
        status_code=200,
        title="Element",
        text="Plan Inspect",
        html=html,
        screenshot_png=png_bytes(640, 480),
        accessibility_snapshot=snapshot,
        element_screenshots=[
            BrowserRenderedElementScreenshot(ref_id=button_ref, role="button", name="Inspect", png=png_bytes(120, 40))
        ],
    )

    result = BrowserRenderedSnapshotAdapter(renderer=FakeRenderer(page)).capture(
        request(capture_element_screenshots=True, element_screenshot_ref_ids=[button_ref]),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
        resolver=FakeResolver(),
    )

    assert result.accepted is True
    assert result.element_screenshot_artifacts
    item = result.element_screenshot_artifacts[0]
    assert item.ref_id == button_ref
    assert item.artifact_id is not None
    assert item.screenshot_metadata.width == 120
    assert result.receipt is not None
    assert result.receipt.element_screenshot_artifacts[0]["ref_id"] == button_ref
    assert browser_receipt_check(bus.events()).passed is True


def test_final_gate_rejects_forged_pdf_artifact_hash(tmp_path):
    bus = EventBus(MISSION_ID)
    page = BrowserRenderedPage(
        final_url="https://example.com/rendered",
        status_code=200,
        title="PDF",
        text="PDF artifact proof.",
        html="<html><body><main>PDF artifact proof.</main></body></html>",
        screenshot_png=png_bytes(640, 480),
        pdf_bytes=pdf_bytes(),
    )
    result = BrowserRenderedSnapshotAdapter(renderer=FakeRenderer(page)).capture(
        request(capture_pdf=True),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
        resolver=FakeResolver(),
    )
    assert result.accepted is True

    events = list(bus.events())
    forged_payload = dict(events[-1].payload)
    forged_payload["pdf_artifact_sha256"] = "0" * 64
    events[-1] = events[-1].model_copy(update={"payload": forged_payload})

    check = browser_receipt_check(events)

    assert check.passed is False
    assert any("browser_event_artifact_hash_mismatch" in error for error in check.details["errors"])


def test_snapshot_artifact_remains_json_when_rich_artifacts_are_captured(tmp_path):
    bus = EventBus(MISSION_ID)
    page = BrowserRenderedPage(
        final_url="https://example.com/rendered",
        status_code=200,
        title="Snapshot JSON",
        text="Snapshot JSON proof.",
        html="<html><body><main>Snapshot JSON proof.</main></body></html>",
        screenshot_png=png_bytes(640, 480),
        pdf_bytes=pdf_bytes(),
    )

    result = BrowserRenderedSnapshotAdapter(renderer=FakeRenderer(page)).capture(
        request(capture_pdf=True),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
        resolver=FakeResolver(),
    )

    assert result.accepted is True
    snapshot_event = next(event for event in bus.events() if event.payload.get("artifact_type") == "browser_rendered_snapshot")
    snapshot_path = tmp_path / "captures" / snapshot_event.payload["relative_path"]
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert payload["title"] == "Snapshot JSON"
    assert payload["screenshot_metadata"]["width"] == 640
