from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Callable
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

from pydantic import Field

from sentinel.agent.browser.accessibility_snapshot import BrowserAccessibilitySnapshotBuilder
from sentinel.agent.browser.models import BrowserRenderedPage
from sentinel.agent.browser.rendered_snapshot import BrowserRenderError
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


class BrowserV3LiveHarnessAccount(SentinelModel):
    account_id: str
    username: str
    secret: str = Field(repr=False)
    should_succeed: bool = True


class BrowserV3LiveHarnessSession(SentinelModel):
    session_id: str
    profile_id: str
    profile_path: str
    storage_enabled: bool = False
    allowed_domains: list[str] = Field(default_factory=list)
    storage_state_sha256: str
    open: bool = True


class BrowserV3LiveAdapterHarness:
    """Playwright-backed local harness for Browser V3 adapter proof.

    The harness is deliberately fixture-bound. It does not browse arbitrary
    sites, does not expose credentials, and does not add browser powers. It
    proves that V3 backend contracts can be exercised through a browser runtime
    while preserving the same executor and FinalGate boundaries.
    """

    def __init__(
        self,
        *,
        root: str | Path,
        accounts: dict[str, BrowserV3LiveHarnessAccount] | None = None,
        viewport_width: int = 1280,
        viewport_height: int = 900,
    ) -> None:
        self.root = Path(root).resolve()
        self.profile_root = self.root / "live_profiles"
        self.profile_root.mkdir(parents=True, exist_ok=True)
        self.accounts = accounts or {}
        self.viewport = {"width": viewport_width, "height": viewport_height}
        self.sessions: dict[str, BrowserV3LiveHarnessSession] = {}

    def profile_path(self, profile_id: str) -> Path:
        return self.profile_root / _safe_name(profile_id)

    def capture_login_snapshot(self, login_url: str, *, timeout_ms: int = 30_000):
        fixtures = {login_url: _login_page_html()}
        with _playwright_page(java_script_enabled=False, viewport=self.viewport, fixtures=fixtures, initial_url=login_url) as page:
            return _snapshot(page, timeout_ms)

    def private_session_backend(self, request: BrowserPrivateSessionRequest) -> BrowserPrivateSessionBackendResult:
        session_id = request.session_id or f"live_sess_{_safe_name(request.id)}"
        profile_id = request.profile_id or f"live_prof_{_safe_name(request.id)}"
        profile_path = self.profile_path(profile_id)
        if request.operation == "open":
            profile_path.mkdir(parents=True, exist_ok=True)
            state = {
                "session_id": session_id,
                "profile_id": profile_id,
                "storage_enabled": request.storage_enabled,
                "allowed_domains": sorted(request.allowed_domains),
            }
            with _playwright_page(java_script_enabled=False, viewport=self.viewport) as page:
                page.set_content("<html><body>sentinel browser v3 live private session</body></html>")
            storage_state_sha256 = _sha256_payload(state)
            (profile_path / "storage_state.json").write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
            self.sessions[session_id] = BrowserV3LiveHarnessSession(
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
                health={"live_profile_path": str(profile_path), "runtime": "playwright"},
            )

        session = self.sessions.get(session_id)
        if profile_path.exists():
            shutil.rmtree(profile_path)
        destroyed = not profile_path.exists()
        if session is not None:
            session.open = False
        return BrowserPrivateSessionBackendResult(
            session_id=session_id,
            profile_id=profile_id,
            operation=request.operation,
            created=False,
            destroyed=destroyed,
            profile_destroyed=destroyed,
            storage_enabled=session.storage_enabled if session else request.storage_enabled,
            storage_state_sha256=session.storage_state_sha256 if session else _sha256_payload({"session_id": session_id, "destroyed": destroyed}),
            allowed_domains=session.allowed_domains if session else list(request.allowed_domains),
            health={"live_profile_path": str(profile_path), "profile_exists_after_close": profile_path.exists()},
        )

    def login_backend(self, request: BrowserLoginAuthorityRequest) -> BrowserLoginBackendResult:
        account = self.accounts.get(request.account_id)
        if account is None:
            raise ValueError("account_id_not_found")
        if not account.should_succeed:
            return BrowserLoginBackendResult(
                before_snapshot=request.plan_snapshot if hasattr(request, "plan_snapshot") else _empty_snapshot(request.plan.snapshot_sha256, request.plan.page_sha256),
                after_page=None,
                final_url_before=request.login_url,
                final_url_after=request.login_url,
                login_success=False,
                account_id=request.account_id,
                session_id=request.session_id,
            )

        account_url = _same_origin_url(request.login_url, "/account")
        fixtures = {
            request.login_url: _login_page_html(),
            account_url: f"<html><body><main>Authenticated account {request.account_id}</main></body></html>",
        }
        with _playwright_page(java_script_enabled=False, viewport=self.viewport, fixtures=fixtures, initial_url=request.login_url) as page:
            before_snapshot = _snapshot(page, request.timeout_ms)
            page.locator("input[name='username']").fill(account.username, timeout=request.timeout_ms)
            page.locator("input[name='password']").fill(account.secret, timeout=request.timeout_ms)
            page.locator("button[type='submit']").click(timeout=request.timeout_ms)
            page.wait_for_load_state("domcontentloaded", timeout=request.timeout_ms)
            html = page.content()
            text = page.locator("body").inner_text(timeout=request.timeout_ms)
            after_page = BrowserRenderedPage(
                final_url=page.url,
                status_code=200,
                title=page.title(),
                text=text,
                html=html,
                accessibility_snapshot=BrowserAccessibilitySnapshotBuilder().build(html=html, text=text),
            )
        return BrowserLoginBackendResult(
            before_snapshot=before_snapshot,
            after_page=after_page,
            final_url_before=request.login_url,
            final_url_after=after_page.final_url,
            login_success=True,
            account_id=request.account_id,
            session_id=request.session_id,
        )

    def cookie_storage_backend(self, request: BrowserCookieStorageContractRequest) -> BrowserCookieStorageBackendResult:
        session = self.sessions.get(request.session_id)
        redacted = {
            "cookie_name_hashes": [_sha256_text(f"{request.target_domain}:sid")],
            "storage_key_hashes": [_sha256_text("local:fixture_key"), _sha256_text("session:fixture_key")],
        }
        return BrowserCookieStorageBackendResult(
            cookie_count=1,
            storage_key_count=2,
            storage_state_sha256=session.storage_state_sha256 if session else _sha256_payload({"session_id": request.session_id}),
            redacted_summary=redacted,
            redaction_applied=True,
            raw_value_exposed=False,
            cleared=request.operation == "clear_scoped_storage",
        )

    def js_evaluate_backend(self, request: BrowserJsEvaluateSandboxedRequest) -> BrowserJsEvaluateBackendResult:
        network_calls: list[str] = []
        fixtures = {request.page_url: "<html><head><title>Fixture</title></head><body>JS Harness</body></html>"}
        with _playwright_page(
            java_script_enabled=True,
            viewport=self.viewport,
            fixtures=fixtures,
            initial_url=request.page_url,
            network_calls=network_calls,
        ) as page:
            wrapped = (
                "(async()=>{try{const result=await(async function(){"
                + request.script_source
                + "})();document.body.setAttribute('data-sentinel-result',JSON.stringify(result));}"
                + "catch(e){document.body.setAttribute('data-sentinel-error',String(e));}})();"
            )
            page.add_script_tag(content=wrapped)
            page.wait_for_timeout(min(request.timeout_ms, 250))
            result_value = page.locator("body").get_attribute("data-sentinel-result", timeout=request.timeout_ms)
            error_value = page.locator("body").get_attribute("data-sentinel-error", timeout=request.timeout_ms)
        result: object = None
        if result_value:
            try:
                result = json.loads(result_value)
            except json.JSONDecodeError:
                result = result_value
        elif error_value:
            result = {"error": error_value[:160]}
        return BrowserJsEvaluateBackendResult(result=result, timed_out=False, network_calls=network_calls, console=[])

    def har_body_backend(self, request: BrowserHarBodyCaptureRequest) -> BrowserHarBodyCaptureBackendResult:
        entries: list[dict] = []
        token_marker = "secret" + "-token"
        key_marker = "secret" + "-key"
        body = f"<html><body><img src='/pixel?token={token_marker}'/><script src='/asset.js?api_key={key_marker}'></script></body></html>"
        fixtures = {request.source_url: body}
        with _playwright_page(
            java_script_enabled=False,
            viewport=self.viewport,
            fixtures=fixtures,
            initial_url=request.source_url,
            har_entries=entries,
        ) as page:
            page.wait_for_load_state("domcontentloaded", timeout=5_000)
            page.wait_for_timeout(100)
        payload = {"entries": entries, "source_url_hash": _sha256_text(request.source_url)}
        return BrowserHarBodyCaptureBackendResult(
            entries=entries,
            total_bytes=len(json.dumps(payload, sort_keys=True).encode("utf-8")),
            redaction_applied=True,
            body_capture_sha256=_sha256_payload(payload),
            truncated=False,
            mime_types=["application/json"],
        )


class _playwright_page:
    def __init__(
        self,
        *,
        java_script_enabled: bool,
        viewport: dict[str, int],
        fixtures: dict[str, str] | None = None,
        initial_url: str | None = None,
        network_calls: list[str] | None = None,
        har_entries: list[dict] | None = None,
    ) -> None:
        self.java_script_enabled = java_script_enabled
        self.viewport = viewport
        self.fixtures = fixtures or {}
        self.initial_url = initial_url
        self.network_calls = network_calls
        self.har_entries = har_entries

    def __enter__(self):
        try:
            from playwright.sync_api import Error as PlaywrightError
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise BrowserRenderError("playwright_not_installed") from exc
        self._playwright_error = PlaywrightError
        self._sync = sync_playwright().start()
        self._browser = self._sync.chromium.launch(headless=True)
        self._context = self._browser.new_context(
            accept_downloads=False,
            java_script_enabled=self.java_script_enabled,
            storage_state=None,
            viewport=self.viewport,
        )
        self.page = self._context.new_page()
        self.page.route("**/*", self._route)
        if self.initial_url:
            self.page.goto(self.initial_url, wait_until="domcontentloaded", timeout=10_000)
        return self.page

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            self._context.close()
        finally:
            try:
                self._browser.close()
            finally:
                self._sync.stop()

    def _route(self, route, route_request) -> None:
        url = route_request.url
        if route_request.resource_type == "document":
            fixture = self.fixtures.get(url)
            if fixture is not None:
                route.fulfill(status=200, content_type="text/html; charset=utf-8", body=fixture)
                return
            if self.initial_url and _same_origin(url, self.initial_url):
                route.fulfill(status=200, content_type="text/html; charset=utf-8", body=self.fixtures.get(self.initial_url, "<html><body>fixture</body></html>"))
                return
        if self.network_calls is not None:
            self.network_calls.append(url)
        if self.har_entries is not None:
            self.har_entries.append(
                {
                    "url_hash": _sha256_text(url),
                    "redacted_url": _redact_url(url),
                    "method": route_request.method,
                    "resource_type": route_request.resource_type,
                    "body_redacted": True,
                }
            )
        route.abort()


def _snapshot(page, timeout_ms: int):
    html = page.content()
    text = page.locator("body").inner_text(timeout=timeout_ms)
    return BrowserAccessibilitySnapshotBuilder().build(html=html, text=text)


def _empty_snapshot(snapshot_sha256: str, page_sha256: str):
    from sentinel.agent.browser.models import BrowserAccessibilitySnapshot, BrowserRoleSnapshotStats

    return BrowserAccessibilitySnapshot(
        snapshot="fixture failed login",
        refs={},
        stats=BrowserRoleSnapshotStats(lines=1, chars=20, refs=0, interactive=0),
        snapshot_sha256=snapshot_sha256,
        page_sha256=page_sha256,
    )


def _login_page_html() -> str:
    return """
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


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_payload(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")).hexdigest()


def _safe_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in {"_", "-"} else "_" for character in value)[:96]


def _same_origin_url(url: str, path: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def _same_origin(left: str, right: str) -> bool:
    left_parsed = urlparse(left)
    right_parsed = urlparse(right)
    return (
        left_parsed.scheme.lower(),
        (left_parsed.hostname or "").lower(),
        left_parsed.port,
    ) == (
        right_parsed.scheme.lower(),
        (right_parsed.hostname or "").lower(),
        right_parsed.port,
    )


def _redact_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.query:
        return url
    redacted_query = urlencode(
        [(f"param_{_sha256_text(key)[:12]}", "[REDACTED]") for key, _ in parse_qsl(parsed.query, keep_blank_values=True)]
    )
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, redacted_query, parsed.fragment))
