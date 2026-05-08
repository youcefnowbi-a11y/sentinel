from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from sentinel.agent import (
    AgentEventType,
    AgentPhase,
    AgentRunResult,
    AgentStateSnapshot,
    BrowserActionRecommendationType,
    BrowserCortexSourceKind,
    BrowserEvidenceInterpreter,
    ContextPackAssembler,
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
    BrowserV3AuthorityClass,
    BrowserV3AuthorityGrant,
    BrowserV3FixtureBackendBench,
    BrowserV3MeasuredMissionGroup,
    BrowserV3MeasuredSupremacyGate,
)
from sentinel.agent.artifact_capture import ArtifactCaptureSandbox
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


MISSION_ID = "mission_p4d_h_browser_hardening"


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "id": MISSION_ID,
        "user_id": "user_001",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P4D-H browser hardening",
        "mission_objective": "Harden Browser V3 scientific proof.",
        "success_criteria": ["hardening signal exists"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["public_web", "local_workspace"],
        "allowed_tools": ["browser_form_submit", "browser_js_evaluate_sandboxed", "browser_har_body_capture", "browser_cookie_storage_contract"],
        "allowed_actions": ["browser_form_submit", "browser_js_evaluate_sandboxed", "browser_har_body_capture", "browser_cookie_storage_contract"],
        "forbidden_actions": ["payment", "credential_access"],
        "allowed_domains": ["example.com"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 20,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def context():
    return type("Context", (), {"mission": envelope(), "user_input": {}})()


def grant(authority_class: BrowserV3AuthorityClass, **overrides) -> BrowserV3AuthorityGrant:
    data = {
        "id": f"grant_{authority_class.value}",
        "authority_class": authority_class,
        "allowed_domains": ["example.com"],
        "allowed_script_hashes": [],
        "allowed_mime_types": ["application/json"],
        "max_bytes": 4096,
        "max_records": 20,
        "max_result_bytes": 2048,
        "storage_allowed": True,
        "redaction_required": True,
    }
    data.update(overrides)
    return BrowserV3AuthorityGrant(**data)


def compiled_event(bus: EventBus, context_pack_id: str = "cpk_p4dh0001"):
    return bus.append(
        AgentEventType.TOOL_INTENT_COMPILED,
        "P4D-H compiled intent.",
        phase_before=AgentPhase.TOOL_SELECTING,
        phase_after=AgentPhase.TOOL_SELECTING,
        payload={
            "accepted": True,
            "context_pack_id": context_pack_id,
            "canonical_hash": "c" * 64,
            "compilation_hash": "d" * 64,
        },
    )


def sandbox(tmp_path) -> ArtifactCaptureSandbox:
    return ArtifactCaptureSandbox(mission_id=MISSION_ID, capture_root=tmp_path / "captures")


def script_hash(script: str) -> str:
    return hashlib.sha256(script.encode("utf-8")).hexdigest()


def test_eval_bench_reports_wilson_interval_for_small_n_perfect_rate(tmp_path):
    class StableRuntime:
        def __init__(self, project_root: Path) -> None:
            self.project_root = project_root

        def run(self, envelope, user_input=None, *, evidence_refs=None, memory_items=None):
            bus = EventBus(envelope.id)
            bus.append(AgentEventType.AGENT_COMPLETED, "Completed.", phase_after=AgentPhase.COMPLETED)
            return AgentRunResult(
                mission_id=envelope.id,
                final_phase=AgentPhase.COMPLETED,
                success=True,
                trace=list(bus.events()),
                runtime_certification=RuntimeCertificationResult(mission_id=envelope.id, certified=True),
                state_snapshot=AgentStateSnapshot(mission_id=envelope.id),
            )

    case = EvalCase(id="wilson_small_n", name="Wilson small-n", envelope=envelope(), expected_success=True, expected_final_phase=AgentPhase.COMPLETED)
    result = SentinelEvalBench(project_root=tmp_path, runtime_factory=StableRuntime).run_case(case, iterations=2, include_no_op=False)

    assert result.accepted is True
    assert result.metrics is not None
    assert result.metrics.success_rate == 1.0
    assert result.metrics.confidence_interval_method == "wilson_score_95"
    assert 0.0 < result.metrics.success_rate_ci95_half_width < 1.0
    assert result.metrics.success_rate_ci95_lower < 1.0
    assert result.metrics.success_rate_ci95_upper == 1.0
    assert result.metrics.event_count_mean > 0


def test_browser_cortex_maps_v3_events_to_mission_cognition():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.BROWSER_FORM_SUBMIT_EXECUTED,
        "Form submitted.",
        payload={
            "receipt_id": "rec_form",
            "context_pack_id": "cpk_1",
            "compiled_intent_trace_id": "evt_compiled",
            "post_submit_snapshot_artifact_id": "art_post",
            "expected_effect": "confirmation text appears",
        },
    )
    bus.append(
        AgentEventType.BROWSER_DOWNLOAD_QUARANTINED,
        "Download quarantined.",
        payload={"receipt_id": "rec_dl", "artifact_id": "art_dl", "promoted": False},
    )
    bus.append(
        AgentEventType.BROWSER_COOKIE_STORAGE_CONTRACT_APPLIED,
        "Cookie storage summarized.",
        payload={"receipt_id": "rec_cookie", "redaction_applied": True, "raw_value_exposed": False, "summary_artifact_id": "art_cookie"},
    )
    bus.append(
        AgentEventType.BROWSER_HAR_BODY_CAPTURED,
        "HAR body captured.",
        payload={"receipt_id": "rec_har", "redaction_applied": True, "har_artifact_id": "art_har"},
    )

    result = BrowserEvidenceInterpreter().interpret(context(), bus.events())
    kinds = [score.source_kind for score in result.source_scores]
    recommendations = [item.recommendation for item in result.action_recommendations]
    reasons = [item.reason for item in result.action_recommendations]

    assert kinds == [
        BrowserCortexSourceKind.FORM_SUBMIT,
        BrowserCortexSourceKind.DOWNLOAD_QUARANTINE,
        BrowserCortexSourceKind.COOKIE_STORAGE,
        BrowserCortexSourceKind.HAR_BODY,
    ]
    assert recommendations[0] == BrowserActionRecommendationType.TREAT_INTERACTION_AS_PROGRESS
    assert recommendations[1] == BrowserActionRecommendationType.USE_AS_EVIDENCE
    assert recommendations[2] == BrowserActionRecommendationType.DO_NOT_USE_FOR_AUTHORITY
    assert recommendations[3] == BrowserActionRecommendationType.USE_AS_EVIDENCE
    assert "not_promoted_trust" in reasons[1]
    assert "tainted_redacted_session_metadata" in reasons[2]


def test_browser_cortex_treats_js_network_rejection_as_repair_signal():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.BROWSER_JS_EVALUATE_SANDBOXED_REJECTED,
        "Sandboxed JS rejected.",
        payload={
            "reason": "browser_js_evaluate_network_call_detected",
            "authority_class": "browser_js_evaluate_sandboxed",
            "network_calls": ["https://example.com/leak"],
            "network_calls_blocked": True,
        },
    )

    result = BrowserEvidenceInterpreter().interpret(context(), bus.events())

    assert result.source_scores[0].source_kind == BrowserCortexSourceKind.JS_SANDBOX
    assert result.source_scores[0].score >= 0.62
    assert result.repair_decisions[0].repair_needed is True
    assert result.repair_decisions[0].reason == "browser_js_network_attempt_blocked"
    assert result.action_recommendations[0].recommendation == BrowserActionRecommendationType.SEEK_ALTERNATIVE_SOURCE


def test_v3_login_event_does_not_create_context_pack_credential_evidence():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.BROWSER_LOGIN_AUTHORITY_EXECUTED,
        "Login completed with account id only.",
        payload={
            "account_id": "acct_1",
            "login_success": True,
            "login_url_hash": "a" * 64,
            "post_login_snapshot_artifact_id": "art_login",
        },
    )

    pack = ContextPackAssembler().assemble(context(), bus.events())
    dumped = str(pack.model_dump(mode="json")).lower()

    assert pack.browser_evidence_summaries == []
    assert pack.citations == []
    assert "password" not in dumped
    assert "password=" not in dumped
    assert "secret" not in dumped


def test_browser_v3_measured_gate_supports_local_10_run_scorecard(tmp_path):
    report = BrowserV3MeasuredSupremacyGate(project_root=tmp_path, iterations=10, use_live_harness=False).run()

    assert report.verdict == "browser_v3_ready_for_next_organ"
    assert {score.mission_group for score in report.scores} == set(BrowserV3MeasuredMissionGroup)
    for score in report.scores:
        assert score.run_count == 10
        assert score.accepted_rate == 1.0
        assert score.success_rate == 1.0
        assert score.confidence_interval_method == "wilson_score_95"
        assert score.success_rate_ci95_lower < 1.0
        assert score.success_rate_ci95_half_width > 0.0
        assert score.event_count_mean > 0.0


@pytest.mark.parametrize(
    "script",
    [
        "return fetch('/leak');",
        "return new XMLHttpRequest().open('GET','/leak');",
        "return navigator.sendBeacon('/leak','x');",
        "return new WebSocket('wss://example.com/leak');",
        "const img = new Image(); img.src = '/leak'; return 'x';",
        "const s = document.createElement('script'); s.src = '/leak.js'; document.body.appendChild(s); return 'x';",
        "return import('/leak.js');",
    ],
)
def test_js_adversarial_network_corpus_is_rejected(tmp_path, script):
    bus = EventBus(MISSION_ID)
    compiled = compiled_event(bus)
    bench = BrowserV3FixtureBackendBench(root=tmp_path / "fixture")

    result = BrowserJsEvaluateSandboxedExecutor(backend=bench.js_evaluate_backend).execute(
        BrowserJsEvaluateSandboxedRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED.value}",
            context_pack_id="cpk_p4dh0001",
            compiled_intent_trace_id=compiled.id,
            page_url="https://example.com/js",
            script_source=script,
        ),
        authority_grant=grant(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED, allowed_script_hashes=[script_hash(script)]),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )

    assert result.accepted is False
    assert result.reason == "browser_js_evaluate_network_call_detected"


def test_cookie_and_har_adversarial_redaction_corpus_is_rejected(tmp_path):
    bus = EventBus(MISSION_ID)
    compiled = compiled_event(bus)
    capture = sandbox(tmp_path)
    cookie_leak = BrowserV3FixtureBackendBench(
        root=tmp_path / "cookie",
        leak_cookie_summary=True,
        cookie_leak_payload={
            "nested": {"MixedCaseToken": "abc"},
            "headers": {"Set-Cookie": "sid=raw"},
            "form": "password=raw",
        },
    )
    har_leak = BrowserV3FixtureBackendBench(
        root=tmp_path / "har",
        leak_har_entry=True,
        har_leak_entry_payload={
            "request_headers": {"Authorization": "Bearer raw"},
            "json": {"access_token": "abc", "api_key": "abc"},
            "form": "credential=raw",
        },
    )

    cookie = BrowserCookieStorageContractExecutor(backend=cookie_leak.cookie_storage_backend).execute(
        BrowserCookieStorageContractRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT.value}",
            context_pack_id="cpk_p4dh0001",
            compiled_intent_trace_id=compiled.id,
            session_id="sess_1",
            profile_id="prof_1",
            private_session_trace_event_id="evt_private",
            target_domain="example.com",
        ),
        authority_grant=grant(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT),
        event_bus=bus,
        artifact_capture=capture,
    )
    har = BrowserHarBodyCaptureExecutor(backend=har_leak.har_body_backend).execute(
        BrowserHarBodyCaptureRequest(
            mission_id=MISSION_ID,
            authority_grant_id=f"grant_{BrowserV3AuthorityClass.HAR_BODY_CAPTURE.value}",
            context_pack_id="cpk_p4dh0001",
            compiled_intent_trace_id=compiled.id,
            source_url="https://example.com/api",
            allowed_mime_types=["application/json"],
        ),
        authority_grant=grant(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
        event_bus=bus,
        artifact_capture=capture,
    )

    assert cookie.accepted is False
    assert cookie.reason == "browser_cookie_storage_backend_reality_failed"
    assert har.accepted is False
    assert har.reason == "browser_har_capture_backend_reality_failed"
