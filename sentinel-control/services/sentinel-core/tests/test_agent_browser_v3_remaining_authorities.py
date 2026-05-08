from __future__ import annotations

import hashlib
from types import SimpleNamespace

import pytest

from sentinel.agent import AgentEventType, ArtifactCaptureSandbox, EventBus
from sentinel.agent.browser import (
    BrowserAccessibilitySnapshotBuilder,
    BrowserCookieStorageBackendResult,
    BrowserCookieStorageContractExecutor,
    BrowserCookieStorageContractRequest,
    BrowserHarBodyCaptureBackendResult,
    BrowserHarBodyCaptureExecutor,
    BrowserHarBodyCaptureRequest,
    BrowserInteractionIntent,
    BrowserInteractionStep,
    BrowserInteractionTarget,
    BrowserJsEvaluateBackendResult,
    BrowserJsEvaluateSandboxedExecutor,
    BrowserJsEvaluateSandboxedRequest,
    BrowserLoginAuthorityExecutor,
    BrowserLoginAuthorityRequest,
    BrowserLoginBackendResult,
    BrowserPrivateSessionBackendResult,
    BrowserPrivateSessionExecutor,
    BrowserPrivateSessionRequest,
    BrowserRenderedPage,
    BrowserV3AuthorityClass,
    BrowserV3AuthorityGrant,
)
from sentinel.agent.browser.interaction_dry_run import BrowserInteractionDryRunPlanner
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.agent.llm import ContextPack, ContextPackActionIntent, ContextPackAuthorityBoundary, ContextPackStableRef, ToolIntentCompiler
from sentinel.agent.phases import AgentPhase
from sentinel.capabilities.risk import ToolSideEffect
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


MISSION_ID = "mission_browser_v3_remaining"


def grant(authority_class: BrowserV3AuthorityClass, **overrides) -> BrowserV3AuthorityGrant:
    data = {
        "id": f"grant_{authority_class.value}",
        "authority_class": authority_class,
        "allowed_domains": ["example.com"],
        "allowed_accounts": ["acct_1"],
        "allowed_script_hashes": [script_hash()],
        "allowed_mime_types": ["application/json", "text/html"],
        "max_bytes": 2048,
        "max_records": 10,
        "max_result_bytes": 1024,
        "storage_allowed": True,
        "redaction_required": True,
        "blocked_flow_types": ["payment"],
    }
    data.update(overrides)
    return BrowserV3AuthorityGrant(**data)


def envelope(authority_class: BrowserV3AuthorityClass, *, include_grant: bool = True) -> MissionAuthorityEnvelope:
    tool_id = authority_class.value
    return MissionAuthorityEnvelope(
        id=MISSION_ID,
        user_id="user_001",
        mission_type=MissionType.RESEARCH_SUMMARY,
        mission_title="Browser V3 remaining authorities",
        mission_objective="Exercise one remaining Browser V3 authority class.",
        success_criteria=["receipt exists"],
        mode=MissionMode.POWER,
        allowed_systems=["public_web", "local_workspace"],
        allowed_tools=[tool_id],
        allowed_actions=[tool_id],
        forbidden_actions=["payment"],
        allowed_domains=["example.com"],
        allowed_accounts=["acct_1"],
        allowed_paths=["data/generated_projects"],
        browser_v3_authority_grants=[grant(authority_class).model_dump(mode="json")] if include_grant else [],
    )


def context_pack(authority_class: BrowserV3AuthorityClass, *, ref_id: str | None = None, snap=None) -> ContextPack:
    refs = []
    if ref_id and snap is not None:
        refs.append(
            ContextPackStableRef(
                id=ref_id,
                source_id="source_v3",
                selector=f"accessibility_ref:{ref_id}",
                digest="d" * 64,
                page_sha256=snap.page_sha256,
                snapshot_sha256=snap.snapshot_sha256,
            )
        )
    return ContextPack(
        context_pack_id=f"cpk_{authority_class.value.replace('browser_', '').replace('_', '')[:20]}",
        mission_id=MISSION_ID,
        mission_goal="Exercise one remaining Browser V3 authority class.",
        authority_boundary=ContextPackAuthorityBoundary(
            allowed_actions=[authority_class.value],
            forbidden_actions=["payment"],
            allowed_tools=[authority_class.value],
            allowed_domains=["example.com"],
        ),
        browser_stable_refs=refs,
        available_action_intents=[
            ContextPackActionIntent(
                id=f"act_{authority_class.value}",
                kind=authority_class.value,
                impact="browser_v3_authority_class",
                authorization_conditions=["browser_v3_authority_grant"],
            )
        ],
    )


def compile_intent(bus: EventBus, authority_class: BrowserV3AuthorityClass, pack: ContextPack, env: MissionAuthorityEnvelope, **arguments):
    raw = {
        "tool_id": authority_class.value,
        "action": authority_class.value,
        "capability": authority_class.value,
        "target": arguments.get("target", "https://example.com"),
        "requested_side_effects": [effect.value if hasattr(effect, "value") else effect for effect in arguments.pop("effects", [ToolSideEffect.BROWSER_READ])],
        "arguments": {
            "context_pack_id": pack.context_pack_id,
            "context_pack_sha256": pack.context_pack_sha256,
            "authority_grant_id": f"grant_{authority_class.value}",
            **arguments,
        },
    }
    return ToolIntentCompiler().compile(raw, pack, env, event_bus=bus)


def sandbox(tmp_path) -> ArtifactCaptureSandbox:
    return ArtifactCaptureSandbox(mission_id=MISSION_ID, capture_root=tmp_path / "captures")


def snapshot():
    return BrowserAccessibilitySnapshotBuilder().build(
        html="<html><body><form><input aria-label='Email'/><button>Login</button></form></body></html>",
        text="Email Login",
    )


def first_button_ref(snap) -> str:
    for ref_id, ref in snap.refs.items():
        if ref.role == "button":
            return ref_id
    raise AssertionError("button ref missing")


def create_plan(bus: EventBus, snap):
    snapshot_event = bus.append(
        AgentEventType.BROWSER_SNAPSHOT_CAPTURED,
        "Rendered browser snapshot captured.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_snapshot",
            "snapshot_artifact_id": "artifact_snapshot",
            "snapshot_artifact_sha256": "a" * 64,
            "accessibility_snapshot_sha256": snap.snapshot_sha256,
            "accessibility_page_sha256": snap.page_sha256,
            "accessibility_ref_count": snap.stats.refs,
            "accessibility_interactive_count": snap.stats.interactive,
            "accessibility_ref_ids": sorted(snap.refs),
        },
    )
    ref_id = first_button_ref(snap)
    plan_result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        steps=[
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.CLICK_PLAN,
                target=BrowserInteractionTarget(ref=ref_id),
                reason="Use runtime-minted login ref.",
            )
        ],
        event_bus=bus,
        final_url="https://example.com/login",
        snapshot_trace_id=snapshot_event.id,
    )
    assert plan_result.accepted
    return plan_result.plan, plan_result.trace_event_id, snapshot_event.id, ref_id


def script_source() -> str:
    return "return { title: document.title };"


def script_hash() -> str:
    return hashlib.sha256(script_source().encode("utf-8")).hexdigest()


def test_private_session_open_close_is_finalgate_certified(tmp_path):
    bus = EventBus(MISSION_ID)
    env = envelope(BrowserV3AuthorityClass.PRIVATE_SESSION)
    pack = context_pack(BrowserV3AuthorityClass.PRIVATE_SESSION)
    compiled = compile_intent(bus, BrowserV3AuthorityClass.PRIVATE_SESSION, pack, env)
    assert compiled.accepted
    sbox = sandbox(tmp_path)

    def backend(request):
        return BrowserPrivateSessionBackendResult(
            session_id=request.session_id or "sess_1",
            profile_id=request.profile_id or "prof_1",
            operation=request.operation,
            created=request.operation == "open",
            destroyed=request.operation == "close",
            profile_destroyed=request.operation == "close",
            storage_enabled=request.storage_enabled,
            storage_state_sha256="0" * 64,
            allowed_domains=["example.com"],
        )

    executor = BrowserPrivateSessionExecutor(backend=backend)
    opened = executor.execute(
        BrowserPrivateSessionRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
            context_pack_id=pack.context_pack_id,
            compiled_intent_trace_id=compiled.trace_event_id,
            operation="open",
            allowed_domains=["example.com"],
            storage_enabled=True,
        ),
        authority_grant=grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        event_bus=bus,
        artifact_capture=sbox,
    )
    assert opened.accepted
    closed = executor.execute(
        BrowserPrivateSessionRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
            context_pack_id=pack.context_pack_id,
            compiled_intent_trace_id=compiled.trace_event_id,
            operation="close",
            session_id=opened.receipt.session_id,
            profile_id=opened.receipt.profile_id,
            allowed_domains=["example.com"],
            storage_enabled=True,
        ),
        authority_grant=grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        event_bus=bus,
        artifact_capture=sbox,
    )
    assert closed.accepted
    check = CoreFinalGate._browser_v3_private_session_contract(SimpleNamespace(trace=tuple(bus.events())))
    assert check.passed, check.details


def test_login_cookie_js_and_har_authorities_are_certified(tmp_path):
    bus = EventBus(MISSION_ID)
    sbox = sandbox(tmp_path)
    snap = snapshot()
    plan, plan_event_id, before_snapshot_event_id, login_ref = create_plan(bus, snap)

    private_pack = context_pack(BrowserV3AuthorityClass.PRIVATE_SESSION)
    private_env = envelope(BrowserV3AuthorityClass.PRIVATE_SESSION)
    private_compiled = compile_intent(bus, BrowserV3AuthorityClass.PRIVATE_SESSION, private_pack, private_env)
    private_open = BrowserPrivateSessionExecutor(
        backend=lambda request: BrowserPrivateSessionBackendResult(
            session_id="sess_login",
            profile_id="prof_login",
            operation=request.operation,
            created=True,
            destroyed=False,
            profile_destroyed=False,
            storage_enabled=True,
            storage_state_sha256="1" * 64,
            allowed_domains=["example.com"],
        )
    ).execute(
        BrowserPrivateSessionRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
            context_pack_id=private_pack.context_pack_id,
            compiled_intent_trace_id=private_compiled.trace_event_id,
            operation="open",
            allowed_domains=["example.com"],
            storage_enabled=True,
        ),
        authority_grant=grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        event_bus=bus,
        artifact_capture=sbox,
    )
    assert private_open.accepted

    login_pack = context_pack(BrowserV3AuthorityClass.LOGIN_AUTHORITY, ref_id=login_ref, snap=snap)
    login_env = envelope(BrowserV3AuthorityClass.LOGIN_AUTHORITY)
    login_compiled = compile_intent(
        bus,
        BrowserV3AuthorityClass.LOGIN_AUTHORITY,
        login_pack,
        login_env,
        effects=[ToolSideEffect.BROWSER_READ],
        login_ref_id=login_ref,
        page_sha256=snap.page_sha256,
        snapshot_sha256=snap.snapshot_sha256,
    )
    assert login_compiled.accepted
    login = BrowserLoginAuthorityExecutor(
        backend=lambda request: BrowserLoginBackendResult(
            before_snapshot=snap,
            after_page=BrowserRenderedPage(
                final_url="https://example.com/account",
                status_code=200,
                content_type="text/html",
                title="Account",
                text="Logged in",
                html="<html><body>Logged in</body></html>",
            ),
            final_url_before="https://example.com/login",
            final_url_after="https://example.com/account",
            login_success=True,
            account_id=request.account_id,
            session_id=request.session_id,
        )
    ).execute(
        BrowserLoginAuthorityRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.LOGIN_AUTHORITY.value}",
            context_pack_id=login_pack.context_pack_id,
            compiled_intent_trace_id=login_compiled.trace_event_id,
            session_id="sess_login",
            profile_id="prof_login",
            private_session_trace_event_id=private_open.trace_event_id,
            account_id="acct_1",
            login_url="https://example.com/login",
            plan=plan,
            plan_trace_event_id=plan_event_id,
            before_snapshot_trace_event_id=before_snapshot_event_id,
            login_ref_id=login_ref,
        ),
        authority_grant=grant(BrowserV3AuthorityClass.LOGIN_AUTHORITY),
        event_bus=bus,
        artifact_capture=sbox,
    )
    assert login.accepted
    assert CoreFinalGate._browser_v3_login_authority_contract(SimpleNamespace(trace=tuple(bus.events()))).passed

    cookie_pack = context_pack(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT)
    cookie_env = envelope(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT)
    cookie_compiled = compile_intent(bus, BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT, cookie_pack, cookie_env)
    assert cookie_compiled.accepted
    cookie = BrowserCookieStorageContractExecutor(
        backend=lambda request: BrowserCookieStorageBackendResult(
            cookie_count=2,
            storage_key_count=3,
            storage_state_sha256="2" * 64,
            redacted_summary={"cookies": ["name_hash"], "storage": ["key_hash"]},
            redaction_applied=True,
            raw_value_exposed=False,
        )
    ).execute(
        BrowserCookieStorageContractRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value}",
            context_pack_id=cookie_pack.context_pack_id,
            compiled_intent_trace_id=cookie_compiled.trace_event_id,
            session_id="sess_login",
            profile_id="prof_login",
            private_session_trace_event_id=private_open.trace_event_id,
            target_domain="example.com",
        ),
        authority_grant=grant(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT),
        event_bus=bus,
        artifact_capture=sbox,
    )
    assert cookie.accepted
    assert CoreFinalGate._browser_v3_cookie_storage_contract(SimpleNamespace(trace=tuple(bus.events()))).passed

    js_pack = context_pack(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED)
    js_env = envelope(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED)
    js_compiled = compile_intent(bus, BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED, js_pack, js_env)
    assert js_compiled.accepted
    js = BrowserJsEvaluateSandboxedExecutor(
        backend=lambda request: BrowserJsEvaluateBackendResult(result={"title": "Example"}, network_calls=[])
    ).execute(
        BrowserJsEvaluateSandboxedRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value}",
            context_pack_id=js_pack.context_pack_id,
            compiled_intent_trace_id=js_compiled.trace_event_id,
            page_url="https://example.com",
            script_source=script_source(),
        ),
        authority_grant=grant(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED),
        event_bus=bus,
        artifact_capture=sbox,
    )
    assert js.accepted
    assert CoreFinalGate._browser_v3_js_evaluate_sandboxed_contract(SimpleNamespace(trace=tuple(bus.events()))).passed

    har_pack = context_pack(BrowserV3AuthorityClass.HAR_BODY_CAPTURE)
    har_env = envelope(BrowserV3AuthorityClass.HAR_BODY_CAPTURE)
    har_compiled = compile_intent(bus, BrowserV3AuthorityClass.HAR_BODY_CAPTURE, har_pack, har_env)
    assert har_compiled.accepted
    har = BrowserHarBodyCaptureExecutor(
        backend=lambda request: BrowserHarBodyCaptureBackendResult(
            entries=[{"url_hash": "u" * 64, "status": 200, "body_redacted": True}],
            total_bytes=128,
            redaction_applied=True,
            mime_types=["application/json"],
        )
    ).execute(
        BrowserHarBodyCaptureRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value}",
            context_pack_id=har_pack.context_pack_id,
            compiled_intent_trace_id=har_compiled.trace_event_id,
            source_url="https://example.com/api",
            allowed_mime_types=["application/json"],
        ),
        authority_grant=grant(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
        event_bus=bus,
        artifact_capture=sbox,
    )
    assert har.accepted
    assert CoreFinalGate._browser_v3_har_body_capture_contract(SimpleNamespace(trace=tuple(bus.events()))).passed


def test_remaining_v3_negative_boundaries(tmp_path):
    bus = EventBus(MISSION_ID)
    snap = snapshot()
    plan, plan_event_id, before_snapshot_event_id, login_ref = create_plan(bus, snap)
    pack = context_pack(BrowserV3AuthorityClass.LOGIN_AUTHORITY, ref_id=login_ref, snap=snap)
    no_grant_env = envelope(BrowserV3AuthorityClass.LOGIN_AUTHORITY, include_grant=False)
    rejected_compile = compile_intent(bus, BrowserV3AuthorityClass.LOGIN_AUTHORITY, pack, no_grant_env, login_ref_id=login_ref)
    assert rejected_compile.accepted is False
    assert "browser_v3_authority_grant_missing" in rejected_compile.errors

    private_pack = context_pack(BrowserV3AuthorityClass.PRIVATE_SESSION)
    private_env = envelope(BrowserV3AuthorityClass.PRIVATE_SESSION)
    private_compiled = compile_intent(bus, BrowserV3AuthorityClass.PRIVATE_SESSION, private_pack, private_env)
    opened = BrowserPrivateSessionExecutor(
        backend=lambda request: BrowserPrivateSessionBackendResult(
            session_id="sess_unclosed",
            profile_id="prof_unclosed",
            operation="open",
            created=True,
            destroyed=False,
            profile_destroyed=False,
            storage_enabled=False,
            storage_state_sha256="3" * 64,
            allowed_domains=["example.com"],
        )
    ).execute(
        BrowserPrivateSessionRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
            context_pack_id=private_pack.context_pack_id,
            compiled_intent_trace_id=private_compiled.trace_event_id,
            operation="open",
            allowed_domains=["example.com"],
        ),
        authority_grant=grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )
    assert opened.accepted
    private_check = CoreFinalGate._browser_v3_private_session_contract(SimpleNamespace(trace=tuple(bus.events())))
    assert private_check.passed is False
    assert any("missing_close" in error for error in private_check.details["errors"])

    bad_login_event = bus.append(
        AgentEventType.BROWSER_LOGIN_AUTHORITY_EXECUTED,
        "Forged login with credential payload.",
        payload={
            "receipt_id": "receipt_bad",
            "authority_class": "browser_login_authority",
            "authority_grant_id": "grant_browser_login_authority",
            "context_pack_id": pack.context_pack_id,
            "compiled_intent_trace_id": private_compiled.trace_event_id,
            "private_session_trace_event_id": opened.trace_event_id,
            "account_id": "acct_1",
            "login_url_hash": "l" * 64,
            "password": "not-allowed",
            "login_success": True,
            "post_login_snapshot_artifact_id": "missing",
            "post_login_snapshot_artifact_sha256": "x" * 64,
        },
        trace_refs=[private_compiled.trace_event_id],
    )
    assert bad_login_event.id
    login_check = CoreFinalGate._browser_v3_login_authority_contract(SimpleNamespace(trace=tuple(bus.events())))
    assert login_check.passed is False
    assert any("credential_leak" in error for error in login_check.details["errors"])

    js_pack = context_pack(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED)
    js_env = envelope(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED)
    js_compiled = compile_intent(bus, BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED, js_pack, js_env)
    bad_js = BrowserJsEvaluateSandboxedExecutor(
        backend=lambda request: BrowserJsEvaluateBackendResult(result={"ok": True}, network_calls=["https://example.com/leak"])
    ).execute(
        BrowserJsEvaluateSandboxedRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value}",
            context_pack_id=js_pack.context_pack_id,
            compiled_intent_trace_id=js_compiled.trace_event_id,
            page_url="https://example.com",
            script_source=script_source(),
        ),
        authority_grant=grant(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )
    assert bad_js.accepted is False
    assert bad_js.reason == "browser_js_evaluate_network_call_detected"

    har_pack = context_pack(BrowserV3AuthorityClass.HAR_BODY_CAPTURE)
    har_env = envelope(BrowserV3AuthorityClass.HAR_BODY_CAPTURE)
    har_compiled = compile_intent(bus, BrowserV3AuthorityClass.HAR_BODY_CAPTURE, har_pack, har_env)
    bad_har = BrowserHarBodyCaptureExecutor(
        backend=lambda request: BrowserHarBodyCaptureBackendResult(
            entries=[{"status": 200}],
            total_bytes=128,
            redaction_applied=False,
            mime_types=["application/json"],
        )
    ).execute(
        BrowserHarBodyCaptureRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value}",
            context_pack_id=har_pack.context_pack_id,
            compiled_intent_trace_id=har_compiled.trace_event_id,
            source_url="https://example.com/api",
        ),
        authority_grant=grant(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )
    assert bad_har.accepted is False
    assert bad_har.reason == "browser_har_capture_redaction_missing"


@pytest.mark.parametrize(
    "authority_class",
    [
        BrowserV3AuthorityClass.PRIVATE_SESSION,
        BrowserV3AuthorityClass.LOGIN_AUTHORITY,
        BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT,
        BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED,
        BrowserV3AuthorityClass.HAR_BODY_CAPTURE,
    ],
)
def test_p4c_review_compiler_rejects_missing_authority_for_each_remaining_v3_class(authority_class):
    bus = EventBus(MISSION_ID)
    snap = snapshot()
    ref_id = first_button_ref(snap)
    pack = context_pack(authority_class, ref_id=ref_id, snap=snap)
    env = envelope(authority_class, include_grant=False)

    result = compile_intent(
        bus,
        authority_class,
        pack,
        env,
        ref_id=ref_id,
        login_ref_id=ref_id,
        page_sha256=snap.page_sha256,
        snapshot_sha256=snap.snapshot_sha256,
        script_source=script_source(),
        source_url="https://example.com/api",
        target_domain="example.com",
    )

    assert result.accepted is False
    assert "browser_v3_authority_grant_missing" in result.errors


def test_p4c_review_finalgate_rejects_forged_cookie_js_and_har_events():
    bus = EventBus(MISSION_ID)
    compiled = bus.append(
        AgentEventType.TOOL_INTENT_COMPILED,
        "compiled",
        phase_before=AgentPhase.TOOL_SELECTING,
        phase_after=AgentPhase.TOOL_SELECTING,
        payload={"accepted": True, "context_pack_id": "cpk_p4creview01", "canonical_hash": "c", "compilation_hash": "d"},
    )
    private = bus.append(
        AgentEventType.BROWSER_PRIVATE_SESSION_STARTED,
        "private session started",
        payload={
            "receipt_id": "receipt_private",
            "authority_class": "browser_private_session",
            "authority_grant_id": "grant_private",
            "context_pack_id": "cpk_p4creview01",
            "compiled_intent_trace_id": compiled.id,
            "operation": "open",
            "session_id": "sess_1",
            "profile_id": "prof_1",
            "session_scope": "per_mission",
            "storage_state_sha256": "s" * 64,
            "created": True,
            "receipt_artifact_id": "missing_private",
            "receipt_artifact_sha256": "p" * 64,
        },
        trace_refs=[compiled.id],
    )
    bus.append(
        AgentEventType.BROWSER_COOKIE_STORAGE_CONTRACT_APPLIED,
        "forged cookie storage event",
        payload={
            "receipt_id": "receipt_cookie",
            "authority_class": "browser_cookie_storage_contract",
            "authority_grant_id": "grant_cookie",
            "context_pack_id": "cpk_p4creview01",
            "compiled_intent_trace_id": compiled.id,
            "private_session_trace_event_id": private.id,
            "operation": "redacted_summary",
            "target_domain": "example.com",
            "redaction_applied": False,
            "raw_value_exposed": True,
            "summary_artifact_id": "missing_cookie",
            "summary_artifact_sha256": "c" * 64,
        },
        trace_refs=[compiled.id, private.id],
    )
    bus.append(
        AgentEventType.BROWSER_JS_EVALUATE_SANDBOXED_EXECUTED,
        "forged js event",
        payload={
            "receipt_id": "receipt_js",
            "authority_class": "browser_js_evaluate_sandboxed",
            "authority_grant_id": "grant_js",
            "context_pack_id": "cpk_p4creview01",
            "compiled_intent_trace_id": compiled.id,
            "script_hash_allowed": False,
            "network_calls_blocked": False,
            "result_size_bytes": 10,
            "max_result_bytes": 100,
            "result_artifact_id": "missing_js",
            "result_artifact_sha256": "j" * 64,
        },
        trace_refs=[compiled.id],
    )
    bus.append(
        AgentEventType.BROWSER_HAR_BODY_CAPTURED,
        "forged har event",
        payload={
            "receipt_id": "receipt_har",
            "authority_class": "browser_har_body_capture",
            "authority_grant_id": "grant_har",
            "context_pack_id": "cpk_p4creview01",
            "compiled_intent_trace_id": compiled.id,
            "redaction_applied": False,
            "record_count": 20,
            "max_records": 10,
            "total_bytes": 2000,
            "max_bytes": 1000,
            "har_artifact_id": "missing_har",
            "har_artifact_sha256": "h" * 64,
        },
        trace_refs=[compiled.id],
    )

    cookie_check = CoreFinalGate._browser_v3_cookie_storage_contract(SimpleNamespace(trace=tuple(bus.events())))
    js_check = CoreFinalGate._browser_v3_js_evaluate_sandboxed_contract(SimpleNamespace(trace=tuple(bus.events())))
    har_check = CoreFinalGate._browser_v3_har_body_capture_contract(SimpleNamespace(trace=tuple(bus.events())))

    assert cookie_check.passed is False
    assert any("redaction_invalid" in error for error in cookie_check.details["errors"])
    assert js_check.passed is False
    assert any("script_hash_not_allowed" in error for error in js_check.details["errors"])
    assert any("network_calls_not_blocked" in error for error in js_check.details["errors"])
    assert har_check.passed is False
    assert any("redaction_missing" in error for error in har_check.details["errors"])
    assert any("record_limit_exceeded" in error for error in har_check.details["errors"])
    assert any("byte_limit_exceeded" in error for error in har_check.details["errors"])


def test_p4c_review_compiler_rejects_sensitive_v3_payload_fields():
    bus = EventBus(MISSION_ID)
    snap = snapshot()
    login_ref = first_button_ref(snap)

    login_pack = context_pack(BrowserV3AuthorityClass.LOGIN_AUTHORITY, ref_id=login_ref, snap=snap)
    login_result = compile_intent(
        bus,
        BrowserV3AuthorityClass.LOGIN_AUTHORITY,
        login_pack,
        envelope(BrowserV3AuthorityClass.LOGIN_AUTHORITY),
        login_ref_id=login_ref,
        page_sha256=snap.page_sha256,
        snapshot_sha256=snap.snapshot_sha256,
        credential_value="password=not-for-context-pack",
    )
    assert login_result.accepted is False
    assert any(error.startswith("credential_payload_not_allowed:") for error in login_result.errors)

    cookie_pack = context_pack(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT)
    cookie_result = compile_intent(
        bus,
        BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT,
        cookie_pack,
        envelope(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT),
        target_domain="example.com",
        operation="redacted_summary",
        cookie_value="Set-Cookie: sid=raw",
    )
    assert cookie_result.accepted is False
    assert any(error.startswith("raw_cookie_storage_value_not_allowed:") for error in cookie_result.errors)

    har_pack = context_pack(BrowserV3AuthorityClass.HAR_BODY_CAPTURE)
    har_result = compile_intent(
        bus,
        BrowserV3AuthorityClass.HAR_BODY_CAPTURE,
        har_pack,
        envelope(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
        source_url="https://example.com/api",
        raw_body="Authorization: Bearer raw-token",
    )
    assert har_result.accepted is False
    assert any(error.startswith("raw_har_body_value_not_allowed:") for error in har_result.errors)


def test_p4c_h_rejects_private_session_backend_reality_mismatch(tmp_path):
    bus = EventBus(MISSION_ID)
    pack = context_pack(BrowserV3AuthorityClass.PRIVATE_SESSION)
    compiled = compile_intent(bus, BrowserV3AuthorityClass.PRIVATE_SESSION, pack, envelope(BrowserV3AuthorityClass.PRIVATE_SESSION))
    assert compiled.accepted

    result = BrowserPrivateSessionExecutor(
        backend=lambda request: BrowserPrivateSessionBackendResult(
            session_id="different_session",
            profile_id="different_profile",
            operation="open",
            created=True,
            destroyed=False,
            profile_destroyed=False,
            storage_enabled=False,
            storage_state_sha256="not-a-sha",
            allowed_domains=["outside.example.net"],
        )
    ).execute(
        BrowserPrivateSessionRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
            context_pack_id=pack.context_pack_id,
            compiled_intent_trace_id=compiled.trace_event_id,
            operation="close",
            session_id="sess_expected",
            profile_id="prof_expected",
            allowed_domains=["example.com"],
        ),
        authority_grant=grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )

    assert result.accepted is False
    assert result.reason == "private_session_backend_reality_failed"
    assert "private_session_backend_operation_mismatch" in result.errors
    assert "private_session_backend_storage_hash_invalid" in result.errors
    assert "private_session_backend_close_session_mismatch" in result.errors


def test_p4c_h_rejects_redaction_markers_in_cookie_storage_summary_and_har_entries(tmp_path):
    bus = EventBus(MISSION_ID)

    cookie_pack = context_pack(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT)
    cookie_compiled = compile_intent(bus, BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT, cookie_pack, envelope(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT))
    assert cookie_compiled.accepted
    cookie = BrowserCookieStorageContractExecutor(
        backend=lambda request: BrowserCookieStorageBackendResult(
            cookie_count=1,
            storage_key_count=0,
            storage_state_sha256="a" * 64,
            redacted_summary={"cookies": ["Set-Cookie: sid=raw"]},
            redaction_applied=True,
            raw_value_exposed=False,
        )
    ).execute(
        BrowserCookieStorageContractRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value}",
            context_pack_id=cookie_pack.context_pack_id,
            compiled_intent_trace_id=cookie_compiled.trace_event_id,
            session_id="sess_1",
            profile_id="prof_1",
            private_session_trace_event_id="evt_private",
            target_domain="example.com",
        ),
        authority_grant=grant(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )
    assert cookie.accepted is False
    assert cookie.reason == "browser_cookie_storage_backend_reality_failed"
    assert "browser_cookie_storage_redacted_summary_contains_sensitive_payload" in cookie.errors

    har_pack = context_pack(BrowserV3AuthorityClass.HAR_BODY_CAPTURE)
    har_compiled = compile_intent(bus, BrowserV3AuthorityClass.HAR_BODY_CAPTURE, har_pack, envelope(BrowserV3AuthorityClass.HAR_BODY_CAPTURE))
    assert har_compiled.accepted
    har = BrowserHarBodyCaptureExecutor(
        backend=lambda request: BrowserHarBodyCaptureBackendResult(
            entries=[{"request_headers": {"authorization": "Bearer raw-token"}, "status": 200}],
            total_bytes=128,
            redaction_applied=True,
            mime_types=["application/json"],
        )
    ).execute(
        BrowserHarBodyCaptureRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value}",
            context_pack_id=har_pack.context_pack_id,
            compiled_intent_trace_id=har_compiled.trace_event_id,
            source_url="https://example.com/api",
            allowed_mime_types=["application/json"],
        ),
        authority_grant=grant(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )
    assert har.accepted is False
    assert har.reason == "browser_har_capture_backend_reality_failed"
    assert "browser_har_entries_contain_sensitive_payload" in har.errors
