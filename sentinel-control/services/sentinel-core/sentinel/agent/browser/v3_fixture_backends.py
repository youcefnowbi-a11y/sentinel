from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field

from sentinel.agent.browser.accessibility_snapshot import BrowserAccessibilitySnapshotBuilder
from sentinel.agent.browser.models import BrowserAccessibilitySnapshot, BrowserRenderedPage, BrowserRoleSnapshotStats
from sentinel.agent.browser.v3_advanced_authorities import (
    BrowserCookieStorageBackendResult,
    BrowserCookieStorageContractRequest,
    BrowserHarBodyCaptureBackendResult,
    BrowserHarBodyCaptureRequest,
    BrowserJsEvaluateBackendResult,
    BrowserJsEvaluateSandboxedRequest,
    BrowserLoginAuthorityRequest,
    BrowserLoginBackendResult,
    BrowserPrivateSessionBackendResult,
    BrowserPrivateSessionRequest,
)
from sentinel.shared.models import SentinelModel


class BrowserV3FixtureSession(SentinelModel):
    session_id: str
    profile_id: str
    profile_path: str
    storage_enabled: bool = False
    allowed_domains: list[str] = Field(default_factory=list)
    storage_state_sha256: str
    open: bool = True


class BrowserV3FixtureBackendBench:
    """Fixture-backed Browser V3 backend set for backend-reality tests.

    This bench does not add runtime powers. It supplies deterministic backend
    callables that create and destroy a real local profile directory, emit
    redacted browser-state summaries, detect script network markers, and produce
    bounded HAR/body fixtures for executor and EvalBench validation.
    """

    def __init__(
        self,
        *,
        root: str | Path,
        leak_cookie_summary: bool = False,
        leak_har_entry: bool = False,
        cookie_leak_payload: dict | None = None,
        har_leak_entry_payload: dict | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.profile_root = self.root / "profiles"
        self.profile_root.mkdir(parents=True, exist_ok=True)
        self.leak_cookie_summary = leak_cookie_summary
        self.leak_har_entry = leak_har_entry
        self.cookie_leak_payload = cookie_leak_payload
        self.har_leak_entry_payload = har_leak_entry_payload
        self.sessions: dict[str, BrowserV3FixtureSession] = {}

    def profile_path(self, profile_id: str) -> Path:
        return self.profile_root / _safe_name(profile_id)

    def capture_login_snapshot(self, login_url: str, *, timeout_ms: int = 30_000):
        html = """
        <html><head><title>Login</title></head><body>
          <main>
            <form action="/account" method="post">
              <input name="username" aria-label="Username" />
              <input name="password" aria-label="Password" type="password" />
              <button type="submit">Login</button>
            </form>
          </main>
        </body></html>
        """
        return BrowserAccessibilitySnapshotBuilder().build(html=html, text="Login")

    def private_session_backend(self, request: BrowserPrivateSessionRequest) -> BrowserPrivateSessionBackendResult:
        session_id = request.session_id or f"sess_{_safe_name(request.id)}"
        profile_id = request.profile_id or f"prof_{_safe_name(request.id)}"
        profile_path = self.profile_path(profile_id)
        if request.operation == "open":
            profile_path.mkdir(parents=True, exist_ok=True)
            state = {
                "session_id": session_id,
                "profile_id": profile_id,
                "storage_enabled": request.storage_enabled,
                "allowed_domains": sorted(request.allowed_domains),
            }
            storage_state_sha256 = _sha256_payload(state)
            (profile_path / "storage_state.json").write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
            self.sessions[session_id] = BrowserV3FixtureSession(
                session_id=session_id,
                profile_id=profile_id,
                profile_path=str(profile_path),
                storage_enabled=request.storage_enabled,
                allowed_domains=list(request.allowed_domains),
                storage_state_sha256=storage_state_sha256,
                open=True,
            )
            return BrowserPrivateSessionBackendResult(
                session_id=session_id,
                profile_id=profile_id,
                operation=request.operation,
                created=profile_path.exists(),
                destroyed=False,
                profile_destroyed=False,
                storage_enabled=request.storage_enabled,
                storage_state_sha256=storage_state_sha256,
                allowed_domains=list(request.allowed_domains),
                health={"fixture_profile_path": str(profile_path)},
            )

        session = self.sessions.get(session_id)
        if profile_path.exists():
            shutil.rmtree(profile_path)
        profile_destroyed = not profile_path.exists()
        if session is not None:
            session.open = False
        return BrowserPrivateSessionBackendResult(
            session_id=session_id,
            profile_id=profile_id,
            operation=request.operation,
            created=False,
            destroyed=profile_destroyed,
            profile_destroyed=profile_destroyed,
            storage_enabled=session.storage_enabled if session else request.storage_enabled,
            storage_state_sha256=session.storage_state_sha256 if session else _sha256_payload({"destroyed": profile_destroyed, "session_id": session_id}),
            allowed_domains=session.allowed_domains if session else list(request.allowed_domains),
            health={"fixture_profile_path": str(profile_path), "profile_exists_after_close": profile_path.exists()},
        )

    def login_backend(self, request: BrowserLoginAuthorityRequest) -> BrowserLoginBackendResult:
        before_snapshot = BrowserAccessibilitySnapshot(
            snapshot="fixture login before",
            refs={},
            stats=BrowserRoleSnapshotStats(lines=1, chars=20, refs=0, interactive=0),
            snapshot_sha256=request.plan.snapshot_sha256,
            page_sha256=request.plan.page_sha256,
        )
        final_url = _same_origin_url(request.login_url, "/account")
        html = f"<html><body><main>Logged in as {request.account_id}</main></body></html>"
        return BrowserLoginBackendResult(
            before_snapshot=before_snapshot,
            after_page=BrowserRenderedPage(
                final_url=final_url,
                status_code=200,
                title="Fixture Account",
                text=f"Logged in as {request.account_id}",
                html=html,
            ),
            final_url_before=request.login_url,
            final_url_after=final_url,
            login_success=True,
            account_id=request.account_id,
            session_id=request.session_id,
        )

    def cookie_storage_backend(self, request: BrowserCookieStorageContractRequest) -> BrowserCookieStorageBackendResult:
        session = self.sessions.get(request.session_id)
        summary = {"cookie_name_hashes": [_sha256_text(f"{request.target_domain}:sid")], "storage_key_hashes": [_sha256_text("fixture:key")]}
        if self.leak_cookie_summary:
            summary = self.cookie_leak_payload or {"cookies": ["Set-Cookie: sid=raw-fixture"]}
        return BrowserCookieStorageBackendResult(
            cookie_count=1,
            storage_key_count=1,
            storage_state_sha256=session.storage_state_sha256 if session else _sha256_payload({"session_id": request.session_id}),
            redacted_summary=summary,
            redaction_applied=True,
            raw_value_exposed=False,
            cleared=request.operation == "clear_scoped_storage",
        )

    def js_evaluate_backend(self, request: BrowserJsEvaluateSandboxedRequest) -> BrowserJsEvaluateBackendResult:
        markers = (
            "fetch(",
            "xmlhttprequest",
            "sendbeacon",
            "websocket(",
            "import(",
            "new image",
            "createelement('img",
            'createelement("img',
            "createelement('script",
            'createelement("script',
        )
        lowered = request.script_source.lower()
        network_calls = [request.page_url] if any(marker in lowered for marker in markers) else []
        return BrowserJsEvaluateBackendResult(
            result={"fixture": True, "page_url_hash": _sha256_text(request.page_url)},
            timed_out=False,
            network_calls=network_calls,
            console=[],
        )

    def har_body_backend(self, request: BrowserHarBodyCaptureRequest) -> BrowserHarBodyCaptureBackendResult:
        entry = {
            "url_hash": _sha256_text(request.source_url),
            "method": "GET",
            "status": 200,
            "body_redacted": True,
        }
        if self.leak_har_entry:
            entry.update(self.har_leak_entry_payload or {"request_headers": {"authorization": "Bearer raw-fixture"}})
        payload = {"entries": [entry], "source_url_hash": _sha256_text(request.source_url)}
        return BrowserHarBodyCaptureBackendResult(
            entries=[entry],
            total_bytes=len(json.dumps(payload, sort_keys=True).encode("utf-8")),
            redaction_applied=True,
            body_capture_sha256=_sha256_payload(payload),
            truncated=False,
            mime_types=["application/json"],
        )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_payload(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")).hexdigest()


def _safe_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in {"_", "-"} else "_" for character in value)[:96]


def _same_origin_url(url: str, path: str) -> str:
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return f"{origin}{path}"
