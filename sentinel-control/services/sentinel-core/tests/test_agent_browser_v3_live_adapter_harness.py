from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from sentinel.agent import (
    AgentEventType,
    AgentPhase,
    AgentRunResult,
    AgentStateSnapshot,
    ArtifactCaptureSandbox,
    EvalCase,
    EventBus,
    RuntimeCertificationResult,
    SentinelEvalBench,
)
from sentinel.agent.browser import (
    BrowserAccessibilitySnapshotBuilder,
    BrowserCookieStorageContractExecutor,
    BrowserCookieStorageContractRequest,
    BrowserHarBodyCaptureExecutor,
    BrowserHarBodyCaptureRequest,
    BrowserInteractionDryRunPlanner,
    BrowserInteractionIntent,
    BrowserInteractionStep,
    BrowserInteractionTarget,
    BrowserJsEvaluateSandboxedExecutor,
    BrowserJsEvaluateSandboxedRequest,
    BrowserLoginAuthorityExecutor,
    BrowserLoginAuthorityRequest,
    BrowserPrivateSessionExecutor,
    BrowserPrivateSessionRequest,
    BrowserV3AuthorityClass,
    BrowserV3AuthorityGrant,
    BrowserV3LiveAdapterHarness,
    BrowserV3LiveHarnessAccount,
)
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


MISSION_ID = "mission_browser_v3_live_harness"
LOGIN_URL = "https://example.com/login"


def grant(authority_class: BrowserV3AuthorityClass, **overrides) -> BrowserV3AuthorityGrant:
    data = {
        "id": f"grant_{authority_class.value}",
        "authority_class": authority_class,
        "allowed_domains": ["example.com"],
        "allowed_accounts": ["acct_1"],
        "allowed_script_hashes": [script_hash()],
        "allowed_mime_types": ["application/json"],
        "max_bytes": 4096,
        "max_records": 20,
        "max_result_bytes": 2048,
        "storage_allowed": True,
        "redaction_required": True,
        "session_scope": "per_mission",
    }
    data.update(overrides)
    return BrowserV3AuthorityGrant(**data)


def envelope() -> MissionAuthorityEnvelope:
    grants = [
        grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        grant(BrowserV3AuthorityClass.LOGIN_AUTHORITY),
        grant(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT),
        grant(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED),
        grant(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
    ]
    return MissionAuthorityEnvelope(
        id=MISSION_ID,
        user_id="user_001",
        mission_type=MissionType.RESEARCH_SUMMARY,
        mission_title="Browser V3 live harness",
        mission_objective="Exercise Browser V3 live adapter harness.",
        success_criteria=["live harness events certify"],
        mode=MissionMode.POWER,
        allowed_systems=["public_web", "local_workspace"],
        allowed_tools=[authority.value for authority in BrowserV3AuthorityClass],
        allowed_actions=[authority.value for authority in BrowserV3AuthorityClass],
        forbidden_actions=["payment"],
        allowed_domains=["example.com"],
        allowed_accounts=["acct_1"],
        allowed_paths=["data/generated_projects"],
        max_actions=20,
        max_cost_usd=1.0,
        browser_v3_authority_grants=[item.model_dump(mode="json") for item in grants],
    )


def script_source() -> str:
    return "return { title: document.title };"


def script_hash(script: str | None = None) -> str:
    return hashlib.sha256((script or script_source()).encode("utf-8")).hexdigest()


def compiled_event(bus: EventBus, context_pack_id: str = "cpk_liveharness01"):
    return bus.append(
        AgentEventType.TOOL_INTENT_COMPILED,
        "Live harness compiled intent.",
        phase_before=AgentPhase.TOOL_SELECTING,
        phase_after=AgentPhase.TOOL_SELECTING,
        payload={
            "accepted": True,
            "context_pack_id": context_pack_id,
            "canonical_hash": "c" * 64,
            "compilation_hash": "d" * 64,
        },
    )


def login_snapshot_and_plan(bus: EventBus, snap=None):
    if snap is None:
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
        snap = BrowserAccessibilitySnapshotBuilder().build(html=html, text="Login")
    snapshot_event = bus.append(
        AgentEventType.BROWSER_SNAPSHOT_CAPTURED,
        "Live harness login snapshot.",
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
    login_ref = next(ref_id for ref_id, ref in snap.refs.items() if ref.role == "button")
    plan_result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        steps=[
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.CLICK_PLAN,
                target=BrowserInteractionTarget(ref=login_ref),
                reason="Submit fixture login form through account-id harness.",
            )
        ],
        event_bus=bus,
        final_url=LOGIN_URL,
        snapshot_trace_id=snapshot_event.id,
    )
    assert plan_result.accepted
    return snap, plan_result.plan, plan_result.trace_event_id, snapshot_event.id, login_ref


def test_p4c_h3_live_private_login_cookie_har_flow(tmp_path):
    pytest.importorskip("playwright.sync_api")
    bus = EventBus(MISSION_ID)
    compiled = compiled_event(bus)
    capture = ArtifactCaptureSandbox(mission_id=MISSION_ID, capture_root=tmp_path / "captures")
    harness = BrowserV3LiveAdapterHarness(
        root=tmp_path / "live",
        accounts={"acct_1": BrowserV3LiveHarnessAccount(account_id="acct_1", username="operator", secret="password=fixture-secret")},
    )

    opened = BrowserPrivateSessionExecutor(backend=harness.private_session_backend).execute(
        BrowserPrivateSessionRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
            context_pack_id="cpk_liveharness01",
            compiled_intent_trace_id=compiled.id,
            operation="open",
            allowed_domains=["example.com"],
            storage_enabled=True,
        ),
        authority_grant=grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        event_bus=bus,
        artifact_capture=capture,
    )
    assert opened.accepted
    profile_path = harness.profile_path(opened.receipt.profile_id)
    assert profile_path.exists()

    login_snap = harness.capture_login_snapshot(LOGIN_URL)
    _, plan, plan_trace_id, snapshot_trace_id, login_ref = login_snapshot_and_plan(bus, login_snap)
    login = BrowserLoginAuthorityExecutor(backend=harness.login_backend).execute(
        BrowserLoginAuthorityRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.LOGIN_AUTHORITY.value}",
            context_pack_id="cpk_liveharness01",
            compiled_intent_trace_id=compiled.id,
            session_id=opened.receipt.session_id,
            profile_id=opened.receipt.profile_id,
            private_session_trace_event_id=opened.trace_event_id,
            account_id="acct_1",
            login_url=LOGIN_URL,
            plan=plan,
            plan_trace_event_id=plan_trace_id,
            before_snapshot_trace_event_id=snapshot_trace_id,
            login_ref_id=login_ref,
        ),
        authority_grant=grant(BrowserV3AuthorityClass.LOGIN_AUTHORITY),
        event_bus=bus,
        artifact_capture=capture,
    )
    assert login.accepted

    cookie = BrowserCookieStorageContractExecutor(backend=harness.cookie_storage_backend).execute(
        BrowserCookieStorageContractRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value}",
            context_pack_id="cpk_liveharness01",
            compiled_intent_trace_id=compiled.id,
            session_id=opened.receipt.session_id,
            profile_id=opened.receipt.profile_id,
            private_session_trace_event_id=opened.trace_event_id,
            target_domain="example.com",
        ),
        authority_grant=grant(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT),
        event_bus=bus,
        artifact_capture=capture,
    )
    assert cookie.accepted

    har = BrowserHarBodyCaptureExecutor(backend=harness.har_body_backend).execute(
        BrowserHarBodyCaptureRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value}",
            context_pack_id="cpk_liveharness01",
            compiled_intent_trace_id=compiled.id,
            source_url="https://example.com/har",
            allowed_mime_types=["application/json"],
        ),
        authority_grant=grant(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
        event_bus=bus,
        artifact_capture=capture,
    )
    assert har.accepted

    closed = BrowserPrivateSessionExecutor(backend=harness.private_session_backend).execute(
        BrowserPrivateSessionRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
            context_pack_id="cpk_liveharness01",
            compiled_intent_trace_id=compiled.id,
            operation="close",
            session_id=opened.receipt.session_id,
            profile_id=opened.receipt.profile_id,
            allowed_domains=["example.com"],
            storage_enabled=True,
        ),
        authority_grant=grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        event_bus=bus,
        artifact_capture=capture,
    )
    assert closed.accepted
    assert not profile_path.exists()

    trace = tuple(bus.events())
    assert CoreFinalGate._browser_v3_private_session_contract(SimpleNamespace(trace=trace)).passed
    assert CoreFinalGate._browser_v3_login_authority_contract(SimpleNamespace(trace=trace)).passed
    assert CoreFinalGate._browser_v3_cookie_storage_contract(SimpleNamespace(trace=trace)).passed
    assert CoreFinalGate._browser_v3_har_body_capture_contract(SimpleNamespace(trace=trace)).passed
    artifact_text = "\n".join(path.read_text(encoding="utf-8") for path in (tmp_path / "captures").rglob("*.json"))
    assert "fixture-secret" not in artifact_text
    assert "secret-token" not in artifact_text
    assert "secret-key" not in artifact_text


def test_p4c_h3_live_js_runtime_network_attempt_is_rejected(tmp_path):
    pytest.importorskip("playwright.sync_api")
    bus = EventBus(MISSION_ID)
    compiled = compiled_event(bus)
    capture = ArtifactCaptureSandbox(mission_id=MISSION_ID, capture_root=tmp_path / "captures")
    harness = BrowserV3LiveAdapterHarness(root=tmp_path / "live")
    network_script = "return fetch('/leak');"

    result = BrowserJsEvaluateSandboxedExecutor(backend=harness.js_evaluate_backend).execute(
        BrowserJsEvaluateSandboxedRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value}",
            context_pack_id="cpk_liveharness01",
            compiled_intent_trace_id=compiled.id,
            page_url="https://example.com/js",
            script_source=network_script,
        ),
        authority_grant=grant(
            BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED,
            allowed_script_hashes=[script_hash(network_script)],
        ),
        event_bus=bus,
        artifact_capture=capture,
    )

    assert result.accepted is False
    assert result.reason == "browser_js_evaluate_network_call_detected"


def test_p4c_h3_backend_exception_redacts_secret_like_strings(tmp_path):
    bus = EventBus(MISSION_ID)
    compiled = compiled_event(bus)
    capture = ArtifactCaptureSandbox(mission_id=MISSION_ID, capture_root=tmp_path / "captures")
    _, plan, plan_trace_id, snapshot_trace_id, login_ref = login_snapshot_and_plan(bus)

    def leaking_backend(_request):
        raise RuntimeError("password=raw-secret Authorization: Bearer raw-token")

    result = BrowserLoginAuthorityExecutor(backend=leaking_backend).execute(
        BrowserLoginAuthorityRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.LOGIN_AUTHORITY.value}",
            context_pack_id="cpk_liveharness01",
            compiled_intent_trace_id=compiled.id,
            session_id="sess_1",
            profile_id="prof_1",
            private_session_trace_event_id="evt_private",
            account_id="acct_1",
            login_url=LOGIN_URL,
            plan=plan,
            plan_trace_event_id=plan_trace_id,
            before_snapshot_trace_event_id=snapshot_trace_id,
            login_ref_id=login_ref,
        ),
        authority_grant=grant(BrowserV3AuthorityClass.LOGIN_AUTHORITY),
        event_bus=bus,
        artifact_capture=capture,
    )

    assert result.accepted is False
    assert result.reason == "browser_login_backend_failed"
    payload = bus.events()[-1].payload
    errors_text = " ".join(payload["errors"])
    assert "raw-secret" not in errors_text
    assert "raw-token" not in errors_text
    assert "[REDACTED]" in errors_text


def test_p4c_h3_live_evalbench_runs_ten_iterations(tmp_path):
    pytest.importorskip("playwright.sync_api")

    class LiveHarnessRuntime:
        def __init__(self, project_root: Path) -> None:
            self.project_root = project_root

        def run(self, mission, user_input=None, *, evidence_refs=None, memory_items=None):
            project_path = self.project_root / "data" / "generated_projects" / "browser-v3-live-harness"
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "browser_v3_live_eval.txt").write_text("browser-v3-live-harness-ok", encoding="utf-8")
            bus = EventBus(mission.id)
            compiled = compiled_event(bus)
            capture = ArtifactCaptureSandbox(mission_id=mission.id, capture_root=self.project_root / "captures")
            harness = BrowserV3LiveAdapterHarness(root=self.project_root / "live")
            opened = BrowserPrivateSessionExecutor(backend=harness.private_session_backend).execute(
                BrowserPrivateSessionRequest(
                    mission_id=mission.id,
                    authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
                    context_pack_id="cpk_liveharness01",
                    compiled_intent_trace_id=compiled.id,
                    operation="open",
                    allowed_domains=["example.com"],
                    storage_enabled=True,
                ),
                authority_grant=grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
                event_bus=bus,
                artifact_capture=capture,
            )
            BrowserPrivateSessionExecutor(backend=harness.private_session_backend).execute(
                BrowserPrivateSessionRequest(
                    mission_id=mission.id,
                    authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
                    context_pack_id="cpk_liveharness01",
                    compiled_intent_trace_id=compiled.id,
                    operation="close",
                    session_id=opened.receipt.session_id,
                    profile_id=opened.receipt.profile_id,
                    allowed_domains=["example.com"],
                    storage_enabled=True,
                ),
                authority_grant=grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
                event_bus=bus,
                artifact_capture=capture,
            )
            bus.append(AgentEventType.AGENT_COMPLETED, "Live harness EvalBench mission completed.", phase_after=AgentPhase.COMPLETED)
            trace = tuple(bus.events())
            gate = CoreFinalGate._browser_v3_private_session_contract(SimpleNamespace(trace=trace))
            return AgentRunResult(
                mission_id=mission.id,
                final_phase=AgentPhase.COMPLETED,
                success=gate.passed,
                project_path=str(project_path),
                selected_tools=["browser_private_session"],
                trace=list(trace),
                runtime_certification=RuntimeCertificationResult(
                    mission_id=mission.id,
                    event_count=len(trace),
                    certified=gate.passed,
                    integrity_ok=gate.passed,
                    terminal_ok=gate.passed,
                    execution_seen=True,
                    planning_seen=True,
                    event_types=[event.event_type for event in trace],
                    errors=[] if gate.passed else gate.details["errors"],
                ),
                state_snapshot=AgentStateSnapshot(mission_id=mission.id, final_phase=AgentPhase.COMPLETED, success=gate.passed),
            )

    case = EvalCase(
        id="browser_v3_live_harness_multirun",
        name="Browser V3 live harness multi-run proof",
        envelope=envelope(),
        expected_success=True,
        expected_final_phase=AgentPhase.COMPLETED,
        required_artifact_files=["browser_v3_live_eval.txt"],
        stable_artifact_files=["browser_v3_live_eval.txt"],
        required_event_types=[
            AgentEventType.BROWSER_PRIVATE_SESSION_STARTED,
            AgentEventType.BROWSER_PRIVATE_SESSION_CLOSED,
            AgentEventType.AGENT_COMPLETED,
        ],
        required_selected_tools=["browser_private_session"],
    )
    result = SentinelEvalBench(project_root=tmp_path, runtime_factory=LiveHarnessRuntime).run_case(case, iterations=10, include_no_op=True)

    assert result.accepted is True
    assert result.metrics is not None
    assert result.metrics.run_count == 10
    assert result.metrics.accepted_rate == 1.0
    assert result.metrics.success_rate == 1.0
    assert result.metrics.unstable_iterations == []
