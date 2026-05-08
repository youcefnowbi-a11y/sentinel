from __future__ import annotations

import gzip
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx

from sentinel.agent import AgentEventType, ArtifactCaptureSandbox, EventBus
from sentinel.agent.browser import (
    BrowserEvidenceAdapter,
    BrowserEvidenceAdapterStatus,
    BrowserEvidenceFetchRequest,
    PublicUrlDecision,
    PublicUrlDecisionStatus,
    ReadOnlyHttpFetcher,
)


class FakeResolver:
    def __init__(self, mapping: dict[str, list[str]]):
        self.mapping = mapping

    def __call__(self, host: str) -> list[str]:
        return self.mapping.get(host, [])


def request(**overrides) -> BrowserEvidenceFetchRequest:
    data = {
        "mission_id": "mission_browser_live",
        "url": "https://example.com/page",
        "purpose": "Collect public browser evidence.",
        "allowed_domains": ["example.com"],
        "max_bytes": 100_000,
    }
    data.update(overrides)
    return BrowserEvidenceFetchRequest(**data)


def test_read_only_http_fetcher_collects_mock_public_page(tmp_path):
    def handler(http_request: httpx.Request) -> httpx.Response:
        assert http_request.method == "GET"
        assert http_request.headers["user-agent"].startswith("SentinelBrowserReadOnly")
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text="<html><title>Live Mock</title><body>Public evidence from mock transport.</body></html>",
        )

    bus = EventBus("mission_browser_live")
    sandbox = ArtifactCaptureSandbox(mission_id="mission_browser_live", capture_root=tmp_path / "captures")
    fetcher = ReadOnlyHttpFetcher(transport=httpx.MockTransport(handler))

    result = BrowserEvidenceAdapter(fetcher=fetcher).collect(
        request(),
        event_bus=bus,
        artifact_capture=sandbox,
        resolver=FakeResolver({"example.com": ["93.184.216.34"]}),
    )

    assert result.accepted is True
    assert result.title == "Live Mock"
    assert result.receipt is not None
    assert result.receipt.content_type == "text/html; charset=utf-8"
    assert [event.event_type for event in bus.events()] == [
        AgentEventType.BROWSER_URL_CLASSIFIED,
        AgentEventType.ARTIFACT_CAPTURED,
        AgentEventType.BROWSER_EVIDENCE_COLLECTED,
    ]


def test_read_only_http_fetcher_redirect_is_revalidated_by_adapter(tmp_path):
    def handler(http_request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "https://127.0.0.1/admin"}, text="")

    bus = EventBus("mission_browser_live")
    sandbox = ArtifactCaptureSandbox(mission_id="mission_browser_live", capture_root=tmp_path / "captures")
    fetcher = ReadOnlyHttpFetcher(transport=httpx.MockTransport(handler))

    result = BrowserEvidenceAdapter(fetcher=fetcher).collect(
        request(),
        event_bus=bus,
        artifact_capture=sandbox,
        resolver=FakeResolver({"example.com": ["93.184.216.34"]}),
    )

    assert result.accepted is False
    assert result.status == BrowserEvidenceAdapterStatus.BLOCKED
    assert result.reason == "private_or_internal_ip"
    assert AgentEventType.ARTIFACT_CAPTURED not in [event.event_type for event in bus.events()]


def test_read_only_http_fetcher_enforces_size_before_artifact(tmp_path):
    def handler(http_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="x" * 128)

    bus = EventBus("mission_browser_live")
    sandbox = ArtifactCaptureSandbox(mission_id="mission_browser_live", capture_root=tmp_path / "captures")
    fetcher = ReadOnlyHttpFetcher(transport=httpx.MockTransport(handler))

    result = BrowserEvidenceAdapter(fetcher=fetcher).collect(
        request(max_bytes=16),
        event_bus=bus,
        artifact_capture=sandbox,
        resolver=FakeResolver({"example.com": ["93.184.216.34"]}),
    )

    assert result.accepted is False
    assert result.reason == "browser_fetch_failed"
    assert result.errors == ["browser_body_too_large"]
    assert AgentEventType.ARTIFACT_CAPTURED not in [event.event_type for event in bus.events()]


def test_read_only_http_fetcher_enforces_compressed_size_before_artifact(tmp_path):
    def handler(http_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html", "content-encoding": "gzip"},
            content=gzip.compress(b"x" * 128),
        )

    bus = EventBus("mission_browser_live")
    sandbox = ArtifactCaptureSandbox(mission_id="mission_browser_live", capture_root=tmp_path / "captures")
    fetcher = ReadOnlyHttpFetcher(transport=httpx.MockTransport(handler))

    result = BrowserEvidenceAdapter(fetcher=fetcher).collect(
        request(max_bytes=256, max_compressed_bytes=16),
        event_bus=bus,
        artifact_capture=sandbox,
        resolver=FakeResolver({"example.com": ["93.184.216.34"]}),
    )

    assert result.accepted is False
    assert result.reason == "browser_fetch_failed"
    assert result.errors == ["browser_compressed_body_too_large"]
    assert AgentEventType.ARTIFACT_CAPTURED not in [event.event_type for event in bus.events()]


def test_read_only_http_fetcher_pinned_http_path_returns_connection_proof():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.server.seen_host = self.headers.get("Host")  # type: ignore[attr-defined]
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><title>Pinned</title><body>pinned transport proof</body></html>")

        def log_message(self, format: str, *args) -> None:  # noqa: A002 - stdlib signature.
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_port
    final_url = f"http://example.com:{port}/proof"
    try:
        page = ReadOnlyHttpFetcher()._fetch_pinned(
            request(url=final_url, require_https=False, allowed_domains=["example.com"]),
            final_url,
            PublicUrlDecision(
                status=PublicUrlDecisionStatus.ALLOWED,
                reason="allowed_public_url",
                original_url=final_url,
                normalized_url=final_url,
                final_url=final_url,
                host="example.com",
                resolved_addresses=["127.0.0.1"],
            ),
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert page.status_code == 200
    assert "pinned transport proof" in page.body
    assert page.connection_proof is not None
    assert page.connection_proof.connected_address == "127.0.0.1"
    assert page.connection_proof.pinned is True
    assert getattr(server, "seen_host") == f"example.com:{port}"
