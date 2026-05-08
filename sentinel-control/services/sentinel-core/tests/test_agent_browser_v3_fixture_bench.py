from __future__ import annotations

import hashlib
from pathlib import Path

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
    BrowserCookieStorageContractExecutor,
    BrowserCookieStorageContractRequest,
    BrowserHarBodyCaptureExecutor,
    BrowserHarBodyCaptureRequest,
    BrowserJsEvaluateSandboxedExecutor,
    BrowserJsEvaluateSandboxedRequest,
    BrowserPrivateSessionExecutor,
    BrowserPrivateSessionRequest,
    BrowserV3AuthorityClass,
    BrowserV3AuthorityGrant,
    BrowserV3FixtureBackendBench,
)
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


MISSION_ID = "mission_browser_v3_fixture_bench"


def grant(authority_class: BrowserV3AuthorityClass) -> BrowserV3AuthorityGrant:
    return BrowserV3AuthorityGrant(
        id=f"grant_{authority_class.value}",
        authority_class=authority_class,
        allowed_domains=["example.com"],
        allowed_accounts=["acct_1"],
        allowed_script_hashes=[script_hash()],
        allowed_mime_types=["application/json"],
        max_bytes=2048,
        max_records=10,
        max_result_bytes=1024,
        storage_allowed=True,
        redaction_required=True,
        session_scope="per_mission",
    )


def envelope() -> MissionAuthorityEnvelope:
    grants = [
        grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        grant(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT),
        grant(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED),
        grant(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
    ]
    return MissionAuthorityEnvelope(
        id=MISSION_ID,
        user_id="user_001",
        mission_type=MissionType.RESEARCH_SUMMARY,
        mission_title="Browser V3 fixture bench",
        mission_objective="Run Browser V3 fixture backend proof.",
        success_criteria=["profile destroyed", "events certified"],
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


def script_hash() -> str:
    return hashlib.sha256(script_source().encode("utf-8")).hexdigest()


def compiled_event(bus: EventBus, context_pack_id: str = "cpk_fixturebench01"):
    return bus.append(
        AgentEventType.TOOL_INTENT_COMPILED,
        "Fixture compiled intent.",
        phase_before=AgentPhase.TOOL_SELECTING,
        phase_after=AgentPhase.TOOL_SELECTING,
        payload={
            "accepted": True,
            "context_pack_id": context_pack_id,
            "canonical_hash": "c" * 64,
            "compilation_hash": "d" * 64,
        },
    )


def test_browser_v3_fixture_backend_profile_lifecycle_js_and_redaction(tmp_path):
    bench = BrowserV3FixtureBackendBench(root=tmp_path / "fixture")
    bus = EventBus(MISSION_ID)
    compiled = compiled_event(bus)
    capture = ArtifactCaptureSandbox(mission_id=MISSION_ID, capture_root=tmp_path / "captures")

    opened = BrowserPrivateSessionExecutor(backend=bench.private_session_backend).execute(
        BrowserPrivateSessionRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
            context_pack_id="cpk_fixturebench01",
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
    profile_path = bench.profile_path(opened.receipt.profile_id)
    assert profile_path.exists()

    closed = BrowserPrivateSessionExecutor(backend=bench.private_session_backend).execute(
        BrowserPrivateSessionRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
            context_pack_id="cpk_fixturebench01",
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
    assert CoreFinalGate._browser_v3_private_session_contract(AgentRunResult(mission_id=MISSION_ID, final_phase=AgentPhase.COMPLETED, success=True, trace=tuple(bus.events()))).passed

    js = BrowserJsEvaluateSandboxedExecutor(backend=bench.js_evaluate_backend).execute(
        BrowserJsEvaluateSandboxedRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value}",
            context_pack_id="cpk_fixturebench01",
            compiled_intent_trace_id=compiled.id,
            page_url="https://example.com",
            script_source=script_source(),
        ),
        authority_grant=grant(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED),
        event_bus=bus,
        artifact_capture=capture,
    )
    assert js.accepted

    bad_js = BrowserJsEvaluateSandboxedExecutor(backend=bench.js_evaluate_backend).execute(
        BrowserJsEvaluateSandboxedRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value}",
            context_pack_id="cpk_fixturebench01",
            compiled_intent_trace_id=compiled.id,
            page_url="https://example.com",
            script_source="return fetch('/leak');",
        ),
        authority_grant=_grant_with_script("return fetch('/leak');"),
        event_bus=bus,
        artifact_capture=capture,
    )
    assert bad_js.accepted is False
    assert bad_js.reason == "browser_js_evaluate_network_call_detected"


def test_browser_v3_fixture_backend_rejects_adversarial_redaction_leaks(tmp_path):
    bus = EventBus(MISSION_ID)
    compiled = compiled_event(bus)
    capture = ArtifactCaptureSandbox(mission_id=MISSION_ID, capture_root=tmp_path / "captures")
    leaky_cookie = BrowserV3FixtureBackendBench(root=tmp_path / "leaky_cookie", leak_cookie_summary=True)

    opened = BrowserPrivateSessionExecutor(backend=leaky_cookie.private_session_backend).execute(
        BrowserPrivateSessionRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
            context_pack_id="cpk_fixturebench01",
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
    cookie = BrowserCookieStorageContractExecutor(backend=leaky_cookie.cookie_storage_backend).execute(
        BrowserCookieStorageContractRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value}",
            context_pack_id="cpk_fixturebench01",
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
    assert cookie.accepted is False
    assert cookie.reason == "browser_cookie_storage_backend_reality_failed"

    leaky_har = BrowserV3FixtureBackendBench(root=tmp_path / "leaky_har", leak_har_entry=True)
    har = BrowserHarBodyCaptureExecutor(backend=leaky_har.har_body_backend).execute(
        BrowserHarBodyCaptureRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value}",
            context_pack_id="cpk_fixturebench01",
            compiled_intent_trace_id=compiled.id,
            source_url="https://example.com/api",
            allowed_mime_types=["application/json"],
        ),
        authority_grant=grant(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
        event_bus=bus,
        artifact_capture=capture,
    )
    assert har.accepted is False
    assert har.reason == "browser_har_capture_backend_reality_failed"


def test_browser_v3_fixture_evalbench_multi_run_metrics(tmp_path):
    class BrowserV3FixtureRuntime:
        def __init__(self, project_root: Path) -> None:
            self.project_root = project_root

        def run(self, envelope, user_input=None, *, evidence_refs=None, memory_items=None):
            project_path = self.project_root / "data" / "generated_projects" / "browser-v3-fixture"
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "browser_v3_eval.txt").write_text("browser-v3-fixture-ok", encoding="utf-8")

            bus = EventBus(envelope.id)
            compiled = compiled_event(bus)
            bench = BrowserV3FixtureBackendBench(root=self.project_root / "browser_v3_fixture")
            capture = ArtifactCaptureSandbox(mission_id=envelope.id, capture_root=self.project_root / "captures")
            opened = BrowserPrivateSessionExecutor(backend=bench.private_session_backend).execute(
                BrowserPrivateSessionRequest(
                    mission_id=envelope.id,
                    authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
                    context_pack_id="cpk_fixturebench01",
                    compiled_intent_trace_id=compiled.id,
                    operation="open",
                    allowed_domains=["example.com"],
                    storage_enabled=True,
                ),
                authority_grant=grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
                event_bus=bus,
                artifact_capture=capture,
            )
            BrowserPrivateSessionExecutor(backend=bench.private_session_backend).execute(
                BrowserPrivateSessionRequest(
                    mission_id=envelope.id,
                    authority_grant_id=f"grant_{BrowserV3AuthorityClass.PRIVATE_SESSION.value}",
                    context_pack_id="cpk_fixturebench01",
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
            bus.append(AgentEventType.AGENT_COMPLETED, "Browser V3 fixture mission completed.", phase_after=AgentPhase.COMPLETED)
            trace = tuple(bus.events())
            private_check = CoreFinalGate._browser_v3_private_session_contract(AgentRunResult(mission_id=envelope.id, final_phase=AgentPhase.COMPLETED, success=True, trace=trace))
            certified = private_check.passed
            return AgentRunResult(
                mission_id=envelope.id,
                final_phase=AgentPhase.COMPLETED,
                success=certified,
                project_path=str(project_path),
                selected_tools=["browser_private_session"],
                trace=list(trace),
                runtime_certification=RuntimeCertificationResult(
                    mission_id=envelope.id,
                    event_count=len(trace),
                    certified=certified,
                    integrity_ok=certified,
                    terminal_ok=certified,
                    execution_seen=True,
                    planning_seen=True,
                    event_types=[event.event_type for event in trace],
                    errors=[] if certified else private_check.details["errors"],
                ),
                state_snapshot=AgentStateSnapshot(mission_id=envelope.id, final_phase=AgentPhase.COMPLETED, success=certified),
            )

    case = EvalCase(
        id="browser_v3_fixture_multirun",
        name="Browser V3 fixture multi-run proof",
        envelope=envelope(),
        expected_success=True,
        expected_final_phase=AgentPhase.COMPLETED,
        required_artifact_files=["browser_v3_eval.txt"],
        stable_artifact_files=["browser_v3_eval.txt"],
        required_event_types=[
            AgentEventType.BROWSER_PRIVATE_SESSION_STARTED,
            AgentEventType.BROWSER_PRIVATE_SESSION_CLOSED,
            AgentEventType.AGENT_COMPLETED,
        ],
        required_selected_tools=["browser_private_session"],
    )

    bench = SentinelEvalBench(project_root=tmp_path, runtime_factory=BrowserV3FixtureRuntime)
    result = bench.run_case(case, iterations=3, include_no_op=True)

    assert result.accepted is True
    assert result.metrics is not None
    assert result.metrics.run_count == 3
    assert result.metrics.accepted_rate == 1.0
    assert result.metrics.success_rate == 1.0
    assert result.metrics.unstable_iterations == []


def _grant_with_script(script: str) -> BrowserV3AuthorityGrant:
    data = grant(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED).model_dump(mode="json")
    data["allowed_script_hashes"] = [hashlib.sha256(script.encode("utf-8")).hexdigest()]
    return BrowserV3AuthorityGrant(**data)
