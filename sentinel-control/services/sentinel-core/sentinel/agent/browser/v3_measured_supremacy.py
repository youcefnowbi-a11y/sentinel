from __future__ import annotations

import hashlib
from enum import StrEnum
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from pydantic import Field

from sentinel.agent.artifact_capture import ArtifactCaptureSandbox
from sentinel.agent.browser.accessibility_snapshot import BrowserAccessibilitySnapshotBuilder
from sentinel.agent.browser.download_quarantine import (
    BrowserDownloadBackendResult,
    BrowserDownloadQuarantineExecutor,
    BrowserDownloadQuarantineRequest,
)
from sentinel.agent.browser.form_submit import (
    BrowserFormSubmitBackendResult,
    BrowserFormSubmitExecutor,
    BrowserFormSubmitRequest,
)
from sentinel.agent.browser.interaction_dry_run import BrowserInteractionDryRunPlanner
from sentinel.agent.browser.interaction_execution import BrowserLimitedInteractionExecutor
from sentinel.agent.browser.models import (
    BrowserInteractionBackendResult,
    BrowserInteractionExecutionRequest,
    BrowserInteractionIntent,
    BrowserInteractionStep,
    BrowserInteractionTarget,
    BrowserRenderedPage,
)
from sentinel.agent.browser.upload_authorized import (
    BrowserUploadAuthorizedExecutor,
    BrowserUploadAuthorizedRequest,
    BrowserUploadBackendResult,
)
from sentinel.agent.browser.v3_advanced_authorities import (
    BrowserCookieStorageContractExecutor,
    BrowserCookieStorageContractRequest,
    BrowserHarBodyCaptureExecutor,
    BrowserHarBodyCaptureRequest,
    BrowserJsEvaluateSandboxedExecutor,
    BrowserJsEvaluateSandboxedRequest,
    BrowserLoginAuthorityExecutor,
    BrowserLoginAuthorityRequest,
    BrowserPrivateSessionExecutor,
    BrowserPrivateSessionRequest,
)
from sentinel.agent.browser.v3_authority import BrowserV3AuthorityClass, BrowserV3AuthorityGrant
from sentinel.agent.browser.v3_fixture_backends import BrowserV3FixtureBackendBench
from sentinel.agent.browser.v3_live_adapter_harness import BrowserV3LiveAdapterHarness, BrowserV3LiveHarnessAccount
from sentinel.agent.eval_bench import EvalCase, EvalSuiteResult, SentinelEvalBench
from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.agent.llm import (
    ContextPack,
    ContextPackActionIntent,
    ContextPackAuthorityBoundary,
    ContextPackPromptInjectionFlag,
    ContextPackStableRef,
    ToolIntentCompiler,
)
from sentinel.agent.models import AgentRunResult, AgentStateSnapshot, RuntimeCertificationResult
from sentinel.agent.phases import AgentPhase
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType
from sentinel.shared.models import SentinelModel


PNG_BYTES = b"\x89PNG\r\n\x1a\nfake"
PDF_BYTES = b"%PDF-1.7\nsentinel measured corpus\n%%EOF"
LOGIN_URL = "https://example.com/login"


class BrowserV3MeasuredMissionGroup(StrEnum):
    PUBLIC_EVIDENCE_INTERACTION = "public_evidence_interaction"
    FORM_SUBMIT = "form_submit"
    DOWNLOAD_QUARANTINE = "download_quarantine"
    UPLOAD_AUTHORIZED = "upload_authorized"
    PRIVATE_LOGIN_COOKIE = "private_login_cookie"
    JS_NO_NETWORK = "js_no_network"
    HAR_REDACTION = "har_redaction"
    CROSS_CLASS_FLOW = "cross_class_flow"
    FAILURE_DENIALS = "failure_denials"


class BrowserV3MeasuredScore(SentinelModel):
    mission_group: BrowserV3MeasuredMissionGroup
    run_count: int = Field(ge=0)
    accepted_rate: float = Field(ge=0.0, le=1.0)
    success_rate: float = Field(ge=0.0, le=1.0)
    accepted_rate_ci95_half_width: float = Field(ge=0.0)
    success_rate_ci95_half_width: float = Field(ge=0.0)
    accepted_rate_ci95_lower: float = Field(default=0.0, ge=0.0, le=1.0)
    accepted_rate_ci95_upper: float = Field(default=0.0, ge=0.0, le=1.0)
    success_rate_ci95_lower: float = Field(default=0.0, ge=0.0, le=1.0)
    success_rate_ci95_upper: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_interval_method: str = "wilson_score_95"
    event_count_min: int = Field(default=0, ge=0)
    event_count_max: int = Field(default=0, ge=0)
    event_count_mean: float = Field(default=0.0, ge=0.0)
    unstable_iterations: list[int] = Field(default_factory=list)
    trace_quality: float = Field(ge=0.0, le=1.0)
    proof_completeness: float = Field(ge=0.0, le=1.0)
    side_effect_containment: float = Field(ge=0.0, le=1.0)


class BrowserV3MeasuredSupremacyReport(SentinelModel):
    gate_id: str = "p4c_s_browser_v3_measured_supremacy"
    suite_accepted: bool
    case_count: int
    iterations: int
    scores: list[BrowserV3MeasuredScore] = Field(default_factory=list)
    measured_success_rate: float = Field(ge=0.0, le=1.0)
    measured_acceptance_rate: float = Field(ge=0.0, le=1.0)
    peer_level_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    verdict: str
    remaining_work: list[str] = Field(default_factory=list)


class BrowserV3MeasuredSupremacyGate:
    """P4C-S measured gate for Browser V3 capability surface.

    This is not a browser power. It is an EvalBench corpus that exercises the
    already-delegated Browser V3 authority classes and reports measured rates.
    """

    def __init__(self, *, project_root: str | Path, iterations: int = 3, use_live_harness: bool = True) -> None:
        if iterations < 1:
            raise ValueError("iterations must be >= 1")
        self.project_root = Path(project_root)
        self.iterations = iterations
        self.use_live_harness = use_live_harness

    def cases(self) -> list[EvalCase]:
        return [
            _eval_case(BrowserV3MeasuredMissionGroup.PUBLIC_EVIDENCE_INTERACTION),
            _eval_case(BrowserV3MeasuredMissionGroup.FORM_SUBMIT),
            _eval_case(BrowserV3MeasuredMissionGroup.DOWNLOAD_QUARANTINE),
            _eval_case(BrowserV3MeasuredMissionGroup.UPLOAD_AUTHORIZED),
            _eval_case(BrowserV3MeasuredMissionGroup.PRIVATE_LOGIN_COOKIE),
            _eval_case(BrowserV3MeasuredMissionGroup.JS_NO_NETWORK),
            _eval_case(BrowserV3MeasuredMissionGroup.HAR_REDACTION),
            _eval_case(BrowserV3MeasuredMissionGroup.CROSS_CLASS_FLOW),
            _eval_case(BrowserV3MeasuredMissionGroup.FAILURE_DENIALS),
        ]

    def run(self) -> BrowserV3MeasuredSupremacyReport:
        bench = SentinelEvalBench(
            project_root=self.project_root,
            runtime_factory=lambda root: BrowserV3MeasuredRuntime(root, use_live_harness=self.use_live_harness),
        )
        suite = bench.run_suite(self.cases(), iterations=self.iterations, include_no_op=True)
        return self.report_from_suite(suite)

    def report_from_suite(self, suite: EvalSuiteResult) -> BrowserV3MeasuredSupremacyReport:
        scores: list[BrowserV3MeasuredScore] = []
        for case in suite.case_results:
            if case.metrics is None:
                continue
            group = _group_from_case_id(case.case_id)
            checks = [
                *case.no_op_checks,
                *case.stability_checks,
                *(check for run in case.runs for check in run.checks),
            ]
            passed_checks = sum(1 for check in checks if check.passed)
            check_rate = passed_checks / len(checks) if checks else 1.0
            scores.append(
                BrowserV3MeasuredScore(
                    mission_group=group,
                    run_count=case.metrics.run_count,
                    accepted_rate=case.metrics.accepted_rate,
                    success_rate=case.metrics.success_rate,
                    accepted_rate_ci95_half_width=case.metrics.accepted_rate_ci95_half_width,
                    success_rate_ci95_half_width=case.metrics.success_rate_ci95_half_width,
                    accepted_rate_ci95_lower=case.metrics.accepted_rate_ci95_lower,
                    accepted_rate_ci95_upper=case.metrics.accepted_rate_ci95_upper,
                    success_rate_ci95_lower=case.metrics.success_rate_ci95_lower,
                    success_rate_ci95_upper=case.metrics.success_rate_ci95_upper,
                    confidence_interval_method=case.metrics.confidence_interval_method,
                    event_count_min=case.metrics.event_count_min,
                    event_count_max=case.metrics.event_count_max,
                    event_count_mean=case.metrics.event_count_mean,
                    unstable_iterations=case.metrics.unstable_iterations,
                    trace_quality=check_rate,
                    proof_completeness=case.metrics.accepted_rate,
                    side_effect_containment=1.0 if case.accepted else case.metrics.success_rate,
                )
            )
        success_rate = _mean([score.success_rate for score in scores])
        accepted_rate = _mean([score.accepted_rate for score in scores])
        ready_for_next = bool(suite.accepted and success_rate >= 0.85 and accepted_rate >= 0.85)
        return BrowserV3MeasuredSupremacyReport(
            suite_accepted=suite.accepted,
            case_count=len(suite.case_results),
            iterations=self.iterations,
            scores=scores,
            measured_success_rate=success_rate,
            measured_acceptance_rate=accepted_rate,
            verdict="browser_v3_ready_for_next_organ" if ready_for_next else "browser_v3_needs_more_hardening",
            remaining_work=[
                "External open-web benchmark remains unproven.",
                "Broader live-adapter corpus is required before claiming external browser supremacy.",
            ],
        )


class BrowserV3MeasuredRuntime:
    def __init__(self, project_root: str | Path, *, use_live_harness: bool = True) -> None:
        self.project_root = Path(project_root)
        self.use_live_harness = use_live_harness

    def run(
        self,
        envelope: MissionAuthorityEnvelope,
        user_input: dict[str, Any] | None = None,
        *,
        evidence_refs: list[str] | None = None,
        memory_items: list[dict[str, Any]] | None = None,
    ) -> AgentRunResult:
        group = BrowserV3MeasuredMissionGroup((user_input or {})["mission_group"])
        project_path = self.project_root / "data" / "generated_projects" / _short_project_slug("p4cs", group.value)
        project_path.mkdir(parents=True, exist_ok=True)
        artifact_name = f"{group.value}.txt"
        (project_path / artifact_name).write_text(f"p4c-s:{group.value}:ok", encoding="utf-8")

        bus = EventBus(envelope.id)
        capture = ArtifactCaptureSandbox(mission_id=envelope.id, capture_root=self.project_root / "captures")
        success, selected_tools = self._execute_group(group, envelope, bus, capture)
        bus.append(
            AgentEventType.AGENT_COMPLETED if success else AgentEventType.AGENT_FAILED,
            f"P4C-S measured mission {group.value} {'completed' if success else 'failed'}.",
            phase_after=AgentPhase.COMPLETED if success else AgentPhase.FAILED,
        )
        trace = list(bus.events())
        return AgentRunResult(
            mission_id=envelope.id,
            final_phase=AgentPhase.COMPLETED if success else AgentPhase.FAILED,
            success=success,
            project_path=str(project_path),
            selected_tools=selected_tools,
            trace=trace,
            runtime_certification=RuntimeCertificationResult(
                mission_id=envelope.id,
                event_count=len(trace),
                certified=success,
                integrity_ok=success,
                terminal_ok=success,
                execution_seen=True,
                planning_seen=True,
                event_types=[event.event_type for event in trace],
                errors=[] if success else [f"p4c_s_group_failed:{group.value}"],
            ),
            state_snapshot=AgentStateSnapshot(
                mission_id=envelope.id,
                event_count=len(trace),
                final_phase=AgentPhase.COMPLETED if success else AgentPhase.FAILED,
                trace_hash=trace[-1].event_hash if trace else None,
                selected_tools=selected_tools,
                project_path=str(project_path),
                success=success,
            ),
        )

    def _execute_group(
        self,
        group: BrowserV3MeasuredMissionGroup,
        envelope: MissionAuthorityEnvelope,
        bus: EventBus,
        capture: ArtifactCaptureSandbox,
    ) -> tuple[bool, list[str]]:
        if group == BrowserV3MeasuredMissionGroup.PUBLIC_EVIDENCE_INTERACTION:
            return self._public_evidence_interaction(envelope.id, bus, capture), ["browser_public_operator_limited"]
        if group == BrowserV3MeasuredMissionGroup.FORM_SUBMIT:
            return self._form_submit(envelope.id, bus, capture), ["browser_form_submit"]
        if group == BrowserV3MeasuredMissionGroup.DOWNLOAD_QUARANTINE:
            return self._download(envelope.id, bus, capture), ["browser_download_quarantine"]
        if group == BrowserV3MeasuredMissionGroup.UPLOAD_AUTHORIZED:
            return self._upload(envelope.id, bus, capture), ["browser_upload_authorized"]
        if group == BrowserV3MeasuredMissionGroup.PRIVATE_LOGIN_COOKIE:
            return self._private_login_cookie(envelope.id, bus, capture), ["browser_private_session", "browser_login_authority", "browser_cookie_storage_contract"]
        if group == BrowserV3MeasuredMissionGroup.JS_NO_NETWORK:
            return self._js_no_network(envelope.id, bus, capture), ["browser_js_evaluate_sandboxed"]
        if group == BrowserV3MeasuredMissionGroup.HAR_REDACTION:
            return self._har_redaction(envelope.id, bus, capture), ["browser_har_body_capture"]
        if group == BrowserV3MeasuredMissionGroup.CROSS_CLASS_FLOW:
            return self._cross_class_flow(envelope.id, bus, capture), ["browser_private_session", "browser_login_authority", "browser_cookie_storage_contract", "browser_har_body_capture"]
        if group == BrowserV3MeasuredMissionGroup.FAILURE_DENIALS:
            return self._failure_denials(envelope.id, bus, capture), ["browser_form_submit", "browser_login_authority", "tool_intent_compiler"]
        raise ValueError(f"Unsupported mission group: {group}")

    def _public_evidence_interaction(self, mission_id: str, bus: EventBus, capture: ArtifactCaptureSandbox) -> bool:
        snap = _interaction_snapshot()
        bus.append(
            AgentEventType.BROWSER_EVIDENCE_COLLECTED,
            "P4C-S public evidence collected.",
            payload={"url": "https://example.com/form", "citation_count": 1, "source_quality_score": 0.92},
        )
        plan, plan_trace, snapshot_trace = _interaction_plan(mission_id, bus, snap)
        result = BrowserLimitedInteractionExecutor(backend=_InteractionBackend(snap)).execute(
            BrowserInteractionExecutionRequest(
                mission_id=mission_id,
                plan=plan,
                plan_trace_event_id=plan_trace,
                before_snapshot_trace_event_id=snapshot_trace,
                final_url="https://example.com/form",
                capture_screenshot=False,
            ),
            event_bus=bus,
            artifact_capture=capture,
        )
        return bool(result.accepted and CoreFinalGate._browser_interaction_execution_contract(SimpleNamespace(trace=tuple(bus.events()))).passed)

    def _form_submit(self, mission_id: str, bus: EventBus, capture: ArtifactCaptureSandbox) -> bool:
        snap = _form_snapshot()
        plan, plan_trace, snapshot_trace, textbox, button = _form_plan(mission_id, bus, snap)
        compiled = _compiled_event(bus)
        result = BrowserFormSubmitExecutor(backend=_FormSubmitBackend(snap)).execute(
            BrowserFormSubmitRequest(
                mission_id=mission_id,
                authority_grant_id="grant_browser_form_submit",
                context_pack_id="cpk_p4cs0001",
                compiled_intent_trace_id=compiled.id,
                plan=plan,
                plan_trace_event_id=plan_trace,
                before_snapshot_trace_event_id=snapshot_trace,
                final_url="https://example.com/form",
                form_ref_id=textbox,
                submit_ref_id=button,
                expected_effect="confirmation text appears",
                capture_screenshot=False,
            ),
            authority_grant=_grant(BrowserV3AuthorityClass.FORM_SUBMIT),
            event_bus=bus,
            artifact_capture=capture,
        )
        return bool(result.accepted and CoreFinalGate._browser_v3_form_submit_contract(SimpleNamespace(trace=tuple(bus.events()))).passed)

    def _download(self, mission_id: str, bus: EventBus, capture: ArtifactCaptureSandbox) -> bool:
        compiled = _compiled_event(bus)
        result = BrowserDownloadQuarantineExecutor(backend=_DownloadBackend()).execute(
            BrowserDownloadQuarantineRequest(
                mission_id=mission_id,
                authority_grant_id="grant_browser_download_quarantine",
                context_pack_id="cpk_p4cs0001",
                compiled_intent_trace_id=compiled.id,
                source_url="https://example.com/report.pdf",
                allowed_mime_types=["application/pdf"],
                max_bytes=2048,
                expected_effect="PDF captured into quarantine",
            ),
            authority_grant=_grant(BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE, max_bytes=2048),
            event_bus=bus,
            artifact_capture=capture,
        )
        return bool(result.accepted and CoreFinalGate._browser_v3_download_quarantine_contract(SimpleNamespace(trace=tuple(bus.events()))).passed)

    def _upload(self, mission_id: str, bus: EventBus, capture: ArtifactCaptureSandbox) -> bool:
        snap = _upload_snapshot()
        source = capture.capture_binary(
            relative_path="browser/download_quarantine/source.pdf",
            data=PDF_BYTES,
            artifact_type="browser_download_quarantine",
            content_type="application/pdf",
            event_bus=bus,
            phase=AgentPhase.EXECUTING,
        ).artifact
        if source is None:
            return False
        plan, plan_trace, snapshot_trace, upload_ref = _upload_plan(mission_id, bus, snap)
        compiled = _compiled_event(bus)
        result = BrowserUploadAuthorizedExecutor(backend=_UploadBackend(snap)).execute(
            BrowserUploadAuthorizedRequest(
                mission_id=mission_id,
                authority_grant_id="grant_browser_upload_authorized",
                context_pack_id="cpk_p4cs0001",
                compiled_intent_trace_id=compiled.id,
                plan=plan,
                plan_trace_event_id=plan_trace,
                before_snapshot_trace_event_id=snapshot_trace,
                final_url="https://example.com/upload",
                upload_ref_id=upload_ref,
                source_artifact=source,
                expected_effect="upload confirmation appears",
                capture_screenshot=False,
            ),
            authority_grant=_grant(BrowserV3AuthorityClass.UPLOAD_AUTHORIZED, allowed_artifact_ids=[source.id], max_bytes=2048),
            event_bus=bus,
            artifact_capture=capture,
        )
        return bool(result.accepted and CoreFinalGate._browser_v3_upload_authorized_contract(SimpleNamespace(trace=tuple(bus.events()))).passed)

    def _private_login_cookie(self, mission_id: str, bus: EventBus, capture: ArtifactCaptureSandbox) -> bool:
        harness = self._harness()
        opened = _open_private_session(mission_id, harness, bus, capture)
        if not opened.accepted:
            return False
        login = _login(mission_id, harness, opened, bus, capture)
        cookie = _cookie(mission_id, harness, opened, bus, capture) if login.accepted else None
        closed = _close_private_session(mission_id, harness, opened, bus, capture)
        trace = SimpleNamespace(trace=tuple(bus.events()))
        return bool(
            login.accepted
            and cookie is not None
            and cookie.accepted
            and closed.accepted
            and CoreFinalGate._browser_v3_private_session_contract(trace).passed
            and CoreFinalGate._browser_v3_login_authority_contract(trace).passed
            and CoreFinalGate._browser_v3_cookie_storage_contract(trace).passed
        )

    def _js_no_network(self, mission_id: str, bus: EventBus, capture: ArtifactCaptureSandbox) -> bool:
        harness = self._harness()
        script = "return fetch('/leak');"
        result = BrowserJsEvaluateSandboxedExecutor(backend=harness.js_evaluate_backend).execute(
            BrowserJsEvaluateSandboxedRequest(
                mission_id=mission_id,
                authority_grant_id="grant_browser_js_evaluate_sandboxed",
                context_pack_id="cpk_p4cs0001",
                compiled_intent_trace_id=_compiled_event(bus).id,
                page_url="https://example.com/js",
                script_source=script,
            ),
            authority_grant=_grant(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED, allowed_script_hashes=[_script_hash(script)]),
            event_bus=bus,
            artifact_capture=capture,
        )
        return result.accepted is False and result.reason == "browser_js_evaluate_network_call_detected"

    def _har_redaction(self, mission_id: str, bus: EventBus, capture: ArtifactCaptureSandbox) -> bool:
        harness = self._harness()
        result = _har(mission_id, harness, bus, capture)
        if not result.accepted:
            return False
        artifact_text = _capture_text(capture.capture_root)
        return _fixture_secret("token") not in artifact_text and _fixture_secret("key") not in artifact_text and CoreFinalGate._browser_v3_har_body_capture_contract(SimpleNamespace(trace=tuple(bus.events()))).passed

    def _cross_class_flow(self, mission_id: str, bus: EventBus, capture: ArtifactCaptureSandbox) -> bool:
        harness = self._harness()
        opened = _open_private_session(mission_id, harness, bus, capture)
        if not opened.accepted:
            return False
        login = _login(mission_id, harness, opened, bus, capture)
        cookie = _cookie(mission_id, harness, opened, bus, capture) if login.accepted else None
        har = _har(mission_id, harness, bus, capture) if cookie and cookie.accepted else None
        closed = _close_private_session(mission_id, harness, opened, bus, capture)
        trace = SimpleNamespace(trace=tuple(bus.events()))
        artifact_text = _capture_text(capture.capture_root)
        return bool(
            login.accepted
            and cookie is not None
            and cookie.accepted
            and har is not None
            and har.accepted
            and closed.accepted
            and _fixture_secret("fixture") not in artifact_text
            and _fixture_secret("token") not in artifact_text
            and _fixture_secret("key") not in artifact_text
            and CoreFinalGate._browser_v3_private_session_contract(trace).passed
            and CoreFinalGate._browser_v3_login_authority_contract(trace).passed
            and CoreFinalGate._browser_v3_cookie_storage_contract(trace).passed
            and CoreFinalGate._browser_v3_har_body_capture_contract(trace).passed
        )

    def _failure_denials(self, mission_id: str, bus: EventBus, capture: ArtifactCaptureSandbox) -> bool:
        snap = _form_snapshot()
        stale = BrowserAccessibilitySnapshotBuilder().build(html="<html><body><button>Other</button></body></html>", text="Other")
        plan, plan_trace, snapshot_trace, textbox, button = _form_plan(mission_id, bus, snap)
        stale_result = BrowserFormSubmitExecutor(backend=_FormSubmitBackend(stale)).execute(
            BrowserFormSubmitRequest(
                mission_id=mission_id,
                authority_grant_id="grant_browser_form_submit",
                context_pack_id="cpk_p4cs0001",
                compiled_intent_trace_id=_compiled_event(bus).id,
                plan=plan,
                plan_trace_event_id=plan_trace,
                before_snapshot_trace_event_id=snapshot_trace,
                final_url="https://example.com/form",
                form_ref_id=textbox,
                submit_ref_id=button,
                expected_effect="confirmation text appears",
            ),
            authority_grant=_grant(BrowserV3AuthorityClass.FORM_SUBMIT),
            event_bus=bus,
            artifact_capture=capture,
        )

        cross_origin = BrowserFormSubmitExecutor(backend=_FormSubmitBackend(snap, after_url="https://other.example/form")).execute(
            BrowserFormSubmitRequest(
                mission_id=mission_id,
                authority_grant_id="grant_browser_form_submit",
                context_pack_id="cpk_p4cs0001",
                compiled_intent_trace_id=_compiled_event(bus).id,
                plan=plan,
                plan_trace_event_id=plan_trace,
                before_snapshot_trace_event_id=snapshot_trace,
                final_url="https://example.com/form",
                form_ref_id=textbox,
                submit_ref_id=button,
                expected_effect="confirmation text appears",
            ),
            authority_grant=_grant(BrowserV3AuthorityClass.FORM_SUBMIT),
            event_bus=bus,
            artifact_capture=capture,
        )

        pack = _injected_form_context_pack(mission_id, snap, textbox, button)
        injected = ToolIntentCompiler().compile(
            {
                "tool_id": "browser_public_form_submit",
                "action": "browser_form_submit",
                "capability": "public_web_form_submit",
                "target": "https://example.com/form",
                "requested_side_effects": ["browser_submit"],
                "arguments": {
                    "context_pack_id": pack.context_pack_id,
                    "context_pack_sha256": pack.context_pack_sha256,
                    "authority_grant_id": "grant_browser_form_submit",
                    "stable_ref_ids": [textbox, button],
                    "page_sha256": snap.page_sha256,
                    "snapshot_sha256": snap.snapshot_sha256,
                },
            },
            pack,
            _envelope(mission_id, BrowserV3MeasuredMissionGroup.FAILURE_DENIALS),
            event_bus=bus,
        )

        _, login_plan, login_plan_trace, login_snapshot_trace, login_ref = _login_plan(mission_id, bus)

        def leaking_backend(_request):
            raise RuntimeError(f"password={_fixture_secret('raw')} Authorization: {'Bearer'} raw-{'token'}")

        login_leak = BrowserLoginAuthorityExecutor(backend=leaking_backend).execute(
            BrowserLoginAuthorityRequest(
                mission_id=mission_id,
                authority_grant_id="grant_browser_login_authority",
                context_pack_id="cpk_p4cs0001",
                compiled_intent_trace_id=_compiled_event(bus).id,
                session_id="sess_1",
                profile_id="prof_1",
                private_session_trace_event_id="evt_private",
                account_id="acct_1",
                login_url=LOGIN_URL,
                plan=login_plan,
                plan_trace_event_id=login_plan_trace,
                before_snapshot_trace_event_id=login_snapshot_trace,
                login_ref_id=login_ref,
            ),
            authority_grant=_grant(BrowserV3AuthorityClass.LOGIN_AUTHORITY),
            event_bus=bus,
            artifact_capture=capture,
        )
        errors_text = " ".join(str(event.payload.get("errors", "")) for event in bus.events())
        return bool(
            stale_result.accepted is False
            and stale_result.reason == "browser_form_submit_stale_snapshot"
            and cross_origin.accepted is False
            and cross_origin.reason == "browser_form_submit_cross_origin_result"
            and injected.accepted is False
            and any("runtime_ref_from_injection_source" in error for error in injected.errors)
            and login_leak.accepted is False
            and _fixture_secret("raw") not in errors_text
            and f"raw-{'token'}" not in errors_text
        )

    def _harness(self):
        if not self.use_live_harness:
            return BrowserV3FixtureBackendBench(root=self.project_root / "fixture")
        accounts = {
            "acct_1": BrowserV3LiveHarnessAccount(
                account_id="acct_1",
                username="operator",
                secret=f"password={_fixture_secret('fixture')}",
            )
        }
        return BrowserV3LiveAdapterHarness(root=self.project_root / "live", accounts=accounts)


class _InteractionBackend:
    def __init__(self, before_snapshot) -> None:
        self.before_snapshot = before_snapshot

    def __call__(self, request: BrowserInteractionExecutionRequest) -> BrowserInteractionBackendResult:
        return BrowserInteractionBackendResult(
            before_snapshot=self.before_snapshot,
            after_page=BrowserRenderedPage(
                final_url="https://example.com/form",
                status_code=200,
                title="After",
                text="Submitted local form state.",
                links=[],
                html="<html><body><main><h1>Submitted local form state.</h1></main></body></html>",
                screenshot_png=None,
            ),
            final_url_before=request.final_url,
            final_url_after="https://example.com/form",
            executed_step_ids=[step.id for step in request.plan.steps],
        )


class _FormSubmitBackend:
    def __init__(self, before_snapshot, *, after_url: str = "https://example.com/form/thanks") -> None:
        self.before_snapshot = before_snapshot
        self.after_url = after_url

    def __call__(self, request: BrowserFormSubmitRequest) -> BrowserFormSubmitBackendResult:
        return BrowserFormSubmitBackendResult(
            before_snapshot=self.before_snapshot,
            after_page=BrowserRenderedPage(
                final_url=self.after_url,
                status_code=200,
                title="Thanks",
                text="Thanks, request received.",
                links=[],
                html="<html><body><main><h1>Thanks, request received.</h1></main></body></html>",
                screenshot_png=None,
            ),
            final_url_before=request.final_url,
            final_url_after=self.after_url,
            submitted=True,
            submitted_ref_ids=[request.form_ref_id, request.submit_ref_id],
        )


class _DownloadBackend:
    def __call__(self, request: BrowserDownloadQuarantineRequest) -> BrowserDownloadBackendResult:
        return BrowserDownloadBackendResult(
            final_url=request.source_url,
            status_code=200,
            content_type="application/pdf",
            data=PDF_BYTES,
            filename="report.pdf",
            redirect_chain=[],
            compressed_bytes_read=len(PDF_BYTES),
            uncompressed_bytes_read=len(PDF_BYTES),
        )


class _UploadBackend:
    def __init__(self, before_snapshot) -> None:
        self.before_snapshot = before_snapshot

    def __call__(self, request: BrowserUploadAuthorizedRequest) -> BrowserUploadBackendResult:
        return BrowserUploadBackendResult(
            before_snapshot=self.before_snapshot,
            after_page=BrowserRenderedPage(
                final_url="https://example.com/upload/thanks",
                status_code=200,
                title="Upload complete",
                text="Upload complete.",
                links=[],
                html="<html><body><main><h1>Upload complete.</h1></main></body></html>",
                screenshot_png=None,
            ),
            final_url_before=request.final_url,
            final_url_after="https://example.com/upload/thanks",
            uploaded=True,
            uploaded_ref_ids=[request.upload_ref_id],
        )


def _eval_case(group: BrowserV3MeasuredMissionGroup) -> EvalCase:
    return EvalCase(
        id=_case_id(group),
        name=f"P4C-S {group.value}",
        envelope=_envelope(f"mission_p4c_s_{group.value}", group),
        user_input={"mission_group": group.value},
        expected_success=True,
        expected_final_phase=AgentPhase.COMPLETED,
        required_artifact_files=[f"{group.value}.txt"],
        stable_artifact_files=[f"{group.value}.txt"],
        required_event_types=[*_required_events(group), AgentEventType.AGENT_COMPLETED],
        required_selected_tools=_required_tools(group),
    )


def _case_id(group: BrowserV3MeasuredMissionGroup) -> str:
    return f"p4cs_{hashlib.sha256(group.value.encode('utf-8')).hexdigest()[:10]}"


def _group_from_case_id(case_id: str) -> BrowserV3MeasuredMissionGroup:
    for group in BrowserV3MeasuredMissionGroup:
        if _case_id(group) == case_id:
            return group
    if case_id.startswith("p4c_s_"):
        return BrowserV3MeasuredMissionGroup(case_id.replace("p4c_s_", "", 1))
    raise ValueError(f"Unsupported P4C-S case id: {case_id}")


def _envelope(mission_id: str, group: BrowserV3MeasuredMissionGroup) -> MissionAuthorityEnvelope:
    grants = [
        _grant(BrowserV3AuthorityClass.FORM_SUBMIT),
        _grant(BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE, max_bytes=2048),
        _grant(BrowserV3AuthorityClass.UPLOAD_AUTHORIZED, max_bytes=2048),
        _grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        _grant(BrowserV3AuthorityClass.LOGIN_AUTHORITY),
        _grant(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT),
        _grant(BrowserV3AuthorityClass.JS_EVALUATE_SANDBOXED, allowed_script_hashes=[_script_hash(), _script_hash("return fetch('/leak');")]),
        _grant(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
    ]
    return MissionAuthorityEnvelope(
        id=mission_id,
        user_id="user_001",
        mission_type=MissionType.RESEARCH_SUMMARY,
        mission_title=f"P4C-S {group.value}",
        mission_objective=f"Measure Browser V3 group {group.value}.",
        success_criteria=["Measured Browser V3 group succeeds with proof."],
        mode=MissionMode.POWER,
        allowed_systems=["public_web", "local_workspace"],
        allowed_tools=[tool for tool in _all_tools()],
        allowed_actions=[authority.value for authority in BrowserV3AuthorityClass],
        forbidden_actions=["payment"],
        allowed_domains=["example.com"],
        allowed_accounts=["acct_1"],
        allowed_paths=["data/generated_projects"],
        max_actions=50,
        max_cost_usd=1.0,
        browser_v3_authority_grants=[grant.model_dump(mode="json") for grant in grants],
    )


def _grant(authority_class: BrowserV3AuthorityClass, **overrides: Any) -> BrowserV3AuthorityGrant:
    data: dict[str, Any] = {
        "id": f"grant_{authority_class.value}",
        "authority_class": authority_class,
        "allowed_domains": ["example.com"],
        "allowed_accounts": ["acct_1"],
        "allowed_mime_types": ["application/pdf", "application/json"],
        "allowed_script_hashes": [_script_hash()],
        "allowed_artifact_ids": [],
        "max_bytes": 4096,
        "max_records": 20,
        "max_result_bytes": 2048,
        "storage_allowed": True,
        "redaction_required": True,
        "session_scope": "per_mission",
        "quarantine_path": "browser/download_quarantine",
    }
    data.update(overrides)
    return BrowserV3AuthorityGrant(**data)


def _all_tools() -> list[str]:
    return [
        "browser_public_operator_limited",
        "browser_form_submit",
        "browser_download_quarantine",
        "browser_upload_authorized",
        "browser_private_session",
        "browser_login_authority",
        "browser_cookie_storage_contract",
        "browser_js_evaluate_sandboxed",
        "browser_har_body_capture",
    ]


def _required_tools(group: BrowserV3MeasuredMissionGroup) -> list[str]:
    return {
        BrowserV3MeasuredMissionGroup.PUBLIC_EVIDENCE_INTERACTION: ["browser_public_operator_limited"],
        BrowserV3MeasuredMissionGroup.FORM_SUBMIT: ["browser_form_submit"],
        BrowserV3MeasuredMissionGroup.DOWNLOAD_QUARANTINE: ["browser_download_quarantine"],
        BrowserV3MeasuredMissionGroup.UPLOAD_AUTHORIZED: ["browser_upload_authorized"],
        BrowserV3MeasuredMissionGroup.PRIVATE_LOGIN_COOKIE: ["browser_private_session", "browser_login_authority", "browser_cookie_storage_contract"],
        BrowserV3MeasuredMissionGroup.JS_NO_NETWORK: ["browser_js_evaluate_sandboxed"],
        BrowserV3MeasuredMissionGroup.HAR_REDACTION: ["browser_har_body_capture"],
        BrowserV3MeasuredMissionGroup.CROSS_CLASS_FLOW: ["browser_private_session", "browser_login_authority", "browser_cookie_storage_contract", "browser_har_body_capture"],
        BrowserV3MeasuredMissionGroup.FAILURE_DENIALS: ["browser_form_submit", "browser_login_authority", "tool_intent_compiler"],
    }[group]


def _required_events(group: BrowserV3MeasuredMissionGroup) -> list[AgentEventType]:
    return {
        BrowserV3MeasuredMissionGroup.PUBLIC_EVIDENCE_INTERACTION: [AgentEventType.BROWSER_EVIDENCE_COLLECTED, AgentEventType.BROWSER_INTERACTION_EXECUTED],
        BrowserV3MeasuredMissionGroup.FORM_SUBMIT: [AgentEventType.BROWSER_FORM_SUBMIT_EXECUTED],
        BrowserV3MeasuredMissionGroup.DOWNLOAD_QUARANTINE: [AgentEventType.BROWSER_DOWNLOAD_QUARANTINED],
        BrowserV3MeasuredMissionGroup.UPLOAD_AUTHORIZED: [AgentEventType.BROWSER_UPLOAD_AUTHORIZED_EXECUTED],
        BrowserV3MeasuredMissionGroup.PRIVATE_LOGIN_COOKIE: [
            AgentEventType.BROWSER_PRIVATE_SESSION_STARTED,
            AgentEventType.BROWSER_LOGIN_AUTHORITY_EXECUTED,
            AgentEventType.BROWSER_COOKIE_STORAGE_CONTRACT_APPLIED,
            AgentEventType.BROWSER_PRIVATE_SESSION_CLOSED,
        ],
        BrowserV3MeasuredMissionGroup.JS_NO_NETWORK: [AgentEventType.BROWSER_JS_EVALUATE_SANDBOXED_REJECTED],
        BrowserV3MeasuredMissionGroup.HAR_REDACTION: [AgentEventType.BROWSER_HAR_BODY_CAPTURED],
        BrowserV3MeasuredMissionGroup.CROSS_CLASS_FLOW: [
            AgentEventType.BROWSER_PRIVATE_SESSION_STARTED,
            AgentEventType.BROWSER_LOGIN_AUTHORITY_EXECUTED,
            AgentEventType.BROWSER_COOKIE_STORAGE_CONTRACT_APPLIED,
            AgentEventType.BROWSER_HAR_BODY_CAPTURED,
            AgentEventType.BROWSER_PRIVATE_SESSION_CLOSED,
        ],
        BrowserV3MeasuredMissionGroup.FAILURE_DENIALS: [
            AgentEventType.BROWSER_FORM_SUBMIT_REJECTED,
            AgentEventType.TOOL_INTENT_COMPILATION_REJECTED,
            AgentEventType.BROWSER_LOGIN_AUTHORITY_REJECTED,
        ],
    }[group]


def _interaction_snapshot():
    return BrowserAccessibilitySnapshotBuilder().build(
        html="<html><body><main><h1>Contact</h1><input placeholder='Email'/><button>Continue</button></main></body></html>",
        text="Contact Email Continue",
    )


def _form_snapshot():
    return BrowserAccessibilitySnapshotBuilder().build(
        html="<html><body><main><h1>Contact</h1><input placeholder='Email'/><button>Send request</button></main></body></html>",
        text="Contact Email Send request",
    )


def _upload_snapshot():
    return BrowserAccessibilitySnapshotBuilder().build(
        html="<html><body><main><input type='file' aria-label='Upload file'/><button>Upload</button></main></body></html>",
        text="Upload file Upload",
    )


def _append_snapshot_event(mission_id: str, bus: EventBus, snap) -> str:
    event = bus.append(
        AgentEventType.BROWSER_SNAPSHOT_CAPTURED,
        "P4C-S snapshot captured.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": f"receipt_{mission_id}",
            "snapshot_artifact_id": f"artifact_{mission_id}",
            "snapshot_artifact_sha256": "a" * 64,
            "accessibility_snapshot_sha256": snap.snapshot_sha256,
            "accessibility_page_sha256": snap.page_sha256,
            "accessibility_ref_count": snap.stats.refs,
            "accessibility_interactive_count": snap.stats.interactive,
            "accessibility_ref_ids": sorted(snap.refs),
        },
    )
    return event.id


def _first_ref(snap, role: str) -> str:
    for ref_id, ref in snap.refs.items():
        if ref.role == role:
            return ref_id
    raise ValueError(f"missing ref for role {role}")


def _interaction_plan(mission_id: str, bus: EventBus, snap):
    snapshot_event_id = _append_snapshot_event(mission_id, bus, snap)
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=mission_id,
        snapshot=snap,
        steps=[
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.FILL_PLAN,
                target=BrowserInteractionTarget(ref=_first_ref(snap, "textbox")),
                text="user@example.com",
                reason="Measure public interaction proof.",
            )
        ],
        event_bus=bus,
        final_url="https://example.com/form",
        snapshot_trace_id=snapshot_event_id,
    )
    if not result.accepted or result.plan is None or result.trace_event_id is None:
        raise RuntimeError("interaction plan rejected")
    return result.plan, result.trace_event_id, snapshot_event_id


def _form_plan(mission_id: str, bus: EventBus, snap):
    snapshot_event_id = _append_snapshot_event(mission_id, bus, snap)
    textbox = _first_ref(snap, "textbox")
    button = _first_ref(snap, "button")
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=mission_id,
        snapshot=snap,
        steps=[
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.FILL_PLAN,
                target=BrowserInteractionTarget(ref=textbox),
                text="lead@example.com",
                reason="Fill public form field.",
            ),
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.CLICK_PLAN,
                target=BrowserInteractionTarget(ref=button),
                reason="Commit public form after authority checks.",
            ),
        ],
        event_bus=bus,
        final_url="https://example.com/form",
        snapshot_trace_id=snapshot_event_id,
    )
    if not result.accepted or result.plan is None or result.trace_event_id is None:
        raise RuntimeError("form plan rejected")
    return result.plan, result.trace_event_id, snapshot_event_id, textbox, button


def _upload_plan(mission_id: str, bus: EventBus, snap):
    snapshot_event_id = _append_snapshot_event(mission_id, bus, snap)
    upload_ref = _first_ref(snap, "button")
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=mission_id,
        snapshot=snap,
        steps=[
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.CLICK_PLAN,
                target=BrowserInteractionTarget(ref=upload_ref),
                reason="Use certified artifact on upload control.",
            )
        ],
        event_bus=bus,
        final_url="https://example.com/upload",
        snapshot_trace_id=snapshot_event_id,
    )
    if not result.accepted or result.plan is None or result.trace_event_id is None:
        raise RuntimeError("upload plan rejected")
    return result.plan, result.trace_event_id, snapshot_event_id, upload_ref


def _login_plan(mission_id: str, bus: EventBus, snap=None):
    if snap is None:
        snap = BrowserAccessibilitySnapshotBuilder().build(
            html="<html><body><form><input name='username'/><input name='password' type='password'/><button>Login</button></form></body></html>",
            text="Login",
        )
    snapshot_event_id = _append_snapshot_event(mission_id, bus, snap)
    login_ref = _first_ref(snap, "button")
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=mission_id,
        snapshot=snap,
        steps=[
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.CLICK_PLAN,
                target=BrowserInteractionTarget(ref=login_ref),
                reason="Submit login through account-id harness.",
            )
        ],
        event_bus=bus,
        final_url=LOGIN_URL,
        snapshot_trace_id=snapshot_event_id,
    )
    if not result.accepted or result.plan is None or result.trace_event_id is None:
        raise RuntimeError("login plan rejected")
    return snap, result.plan, result.trace_event_id, snapshot_event_id, login_ref


def _compiled_event(bus: EventBus):
    return bus.append(
        AgentEventType.TOOL_INTENT_COMPILED,
        "P4C-S compiled intent.",
        phase_before=AgentPhase.TOOL_SELECTING,
        phase_after=AgentPhase.TOOL_SELECTING,
        payload={
            "accepted": True,
            "context_pack_id": "cpk_p4cs0001",
            "canonical_hash": "c" * 64,
            "compilation_hash": "d" * 64,
        },
    )


def _open_private_session(mission_id: str, harness: BrowserV3LiveAdapterHarness, bus: EventBus, capture: ArtifactCaptureSandbox):
    return BrowserPrivateSessionExecutor(backend=harness.private_session_backend).execute(
        BrowserPrivateSessionRequest(
            mission_id=mission_id,
            authority_grant_id="grant_browser_private_session",
            context_pack_id="cpk_p4cs0001",
            compiled_intent_trace_id=_compiled_event(bus).id,
            operation="open",
            allowed_domains=["example.com"],
            storage_enabled=True,
        ),
        authority_grant=_grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        event_bus=bus,
        artifact_capture=capture,
    )


def _close_private_session(mission_id: str, harness: BrowserV3LiveAdapterHarness, opened, bus: EventBus, capture: ArtifactCaptureSandbox):
    return BrowserPrivateSessionExecutor(backend=harness.private_session_backend).execute(
        BrowserPrivateSessionRequest(
            mission_id=mission_id,
            authority_grant_id="grant_browser_private_session",
            context_pack_id="cpk_p4cs0001",
            compiled_intent_trace_id=_compiled_event(bus).id,
            operation="close",
            session_id=opened.receipt.session_id,
            profile_id=opened.receipt.profile_id,
            allowed_domains=["example.com"],
            storage_enabled=True,
        ),
        authority_grant=_grant(BrowserV3AuthorityClass.PRIVATE_SESSION),
        event_bus=bus,
        artifact_capture=capture,
    )


def _login(mission_id: str, harness: BrowserV3LiveAdapterHarness, opened, bus: EventBus, capture: ArtifactCaptureSandbox):
    snap = harness.capture_login_snapshot(LOGIN_URL)
    _, plan, plan_trace, snapshot_trace, login_ref = _login_plan(mission_id, bus, snap)
    return BrowserLoginAuthorityExecutor(backend=harness.login_backend).execute(
        BrowserLoginAuthorityRequest(
            mission_id=mission_id,
            authority_grant_id="grant_browser_login_authority",
            context_pack_id="cpk_p4cs0001",
            compiled_intent_trace_id=_compiled_event(bus).id,
            session_id=opened.receipt.session_id,
            profile_id=opened.receipt.profile_id,
            private_session_trace_event_id=opened.trace_event_id,
            account_id="acct_1",
            login_url=LOGIN_URL,
            plan=plan,
            plan_trace_event_id=plan_trace,
            before_snapshot_trace_event_id=snapshot_trace,
            login_ref_id=login_ref,
        ),
        authority_grant=_grant(BrowserV3AuthorityClass.LOGIN_AUTHORITY),
        event_bus=bus,
        artifact_capture=capture,
    )


def _cookie(mission_id: str, harness: BrowserV3LiveAdapterHarness, opened, bus: EventBus, capture: ArtifactCaptureSandbox):
    return BrowserCookieStorageContractExecutor(backend=harness.cookie_storage_backend).execute(
        BrowserCookieStorageContractRequest(
            mission_id=mission_id,
            authority_grant_id="grant_browser_cookie_storage_contract",
            context_pack_id="cpk_p4cs0001",
            compiled_intent_trace_id=_compiled_event(bus).id,
            session_id=opened.receipt.session_id,
            profile_id=opened.receipt.profile_id,
            private_session_trace_event_id=opened.trace_event_id,
            target_domain="example.com",
        ),
        authority_grant=_grant(BrowserV3AuthorityClass.COOKIE_STORAGE_CONTRACT),
        event_bus=bus,
        artifact_capture=capture,
    )


def _har(mission_id: str, harness: BrowserV3LiveAdapterHarness, bus: EventBus, capture: ArtifactCaptureSandbox):
    return BrowserHarBodyCaptureExecutor(backend=harness.har_body_backend).execute(
        BrowserHarBodyCaptureRequest(
            mission_id=mission_id,
            authority_grant_id="grant_browser_har_body_capture",
            context_pack_id="cpk_p4cs0001",
            compiled_intent_trace_id=_compiled_event(bus).id,
            source_url="https://example.com/har",
            allowed_mime_types=["application/json"],
        ),
        authority_grant=_grant(BrowserV3AuthorityClass.HAR_BODY_CAPTURE),
        event_bus=bus,
        artifact_capture=capture,
    )


def _injected_form_context_pack(mission_id: str, snap, textbox: str, button: str) -> ContextPack:
    source_id = "source_injected"
    return ContextPack(
        context_pack_id="cpk_p4cs0001",
        mission_id=mission_id,
        mission_goal="Measure injected source denial.",
        authority_boundary=ContextPackAuthorityBoundary(
            allowed_actions=["browser_form_submit"],
            forbidden_actions=["payment"],
            allowed_tools=["browser_form_submit"],
            allowed_domains=["example.com"],
        ),
        browser_stable_refs=[
            ContextPackStableRef(
                id=textbox,
                source_id=source_id,
                selector=f"accessibility_ref:{textbox}",
                digest="d" * 64,
                page_sha256=snap.page_sha256,
                snapshot_sha256=snap.snapshot_sha256,
            ),
            ContextPackStableRef(
                id=button,
                source_id=source_id,
                selector=f"accessibility_ref:{button}",
                digest="e" * 64,
                page_sha256=snap.page_sha256,
                snapshot_sha256=snap.snapshot_sha256,
            ),
        ],
        available_action_intents=[
            ContextPackActionIntent(
                id="act_submit",
                kind="browser_form_submit",
                impact="external_public_commit",
                authorization_conditions=["browser_v3_authority_grant"],
            )
        ],
        prompt_injection_flags=[
            ContextPackPromptInjectionFlag(
                source_id=source_id,
                risk="high",
                indicators=["tool_instruction"],
                blocked=True,
                sanitized=True,
            )
        ],
    )


def _script_hash(script: str = "return { title: document.title };") -> str:
    return hashlib.sha256(script.encode("utf-8")).hexdigest()


def _fixture_secret(kind: str) -> str:
    if kind == "token":
        return "secret" + "-token"
    if kind == "key":
        return "secret" + "-key"
    if kind == "raw":
        return "raw" + "-secret"
    if kind == "fixture":
        return "fixture" + "-secret"
    raise ValueError(f"unsupported fixture secret kind: {kind}")


def _capture_text(root: Path) -> str:
    if not root.exists():
        return ""
    chunks: list[str] = []
    for path in root.rglob("*.json"):
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _short_project_slug(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{digest}"
