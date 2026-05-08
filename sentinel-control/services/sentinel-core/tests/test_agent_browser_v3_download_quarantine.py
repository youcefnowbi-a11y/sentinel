from __future__ import annotations

from types import SimpleNamespace

from sentinel.agent import AgentEventType, ArtifactCaptureSandbox, EventBus
from sentinel.agent.browser import (
    BrowserControlledCapabilityRunner,
    BrowserDownloadBackendResult,
    BrowserDownloadQuarantineExecutor,
    BrowserDownloadQuarantineRequest,
    BrowserV3AuthorityClass,
    BrowserV3AuthorityGrant,
)
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.agent.llm import (
    ContextPack,
    ContextPackActionIntent,
    ContextPackAuthorityBoundary,
    ContextPackPromptInjectionFlag,
    ContextPackStableRef,
    ToolIntentCompiler,
)
from sentinel.agent.tool_call_protocol import CanonicalToolCall
from sentinel.capabilities import default_tool_registry
from sentinel.capabilities.risk import ToolSideEffect
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


MISSION_ID = "mission_browser_v3_download"
PDF_BYTES = b"%PDF-1.7\nsentinel quarantine\n%%EOF"
PAGE_SHA = "a" * 64
SNAP_SHA = "b" * 64
LINK_REF = "e1"


def grant(**overrides) -> BrowserV3AuthorityGrant:
    data = {
        "id": "grant_download",
        "authority_class": BrowserV3AuthorityClass.DOWNLOAD_QUARANTINE,
        "allowed_domains": ["example.com", "cdn.example.com"],
        "allowed_mime_types": ["application/pdf"],
        "max_bytes": 1024,
        "quarantine_path": "browser/download_quarantine",
        "blocked_flow_types": ["payment", "credential", "login", "upload"],
    }
    data.update(overrides)
    return BrowserV3AuthorityGrant(**data)


def envelope(*, include_grant: bool = True, **overrides) -> MissionAuthorityEnvelope:
    authority_grants = [grant().model_dump(mode="json")] if include_grant else []
    data = {
        "id": MISSION_ID,
        "user_id": "user_001",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "Browser V3 download quarantine",
        "mission_objective": "Capture one public file into quarantine.",
        "success_criteria": ["Quarantine receipt exists"],
        "mode": MissionMode.POWER,
        "risk_appetite_score": 85,
        "allowed_systems": ["local_workspace", "public_web"],
        "allowed_tools": ["browser_download_quarantine"],
        "allowed_actions": ["browser_download_quarantine"],
        "forbidden_actions": ["browser_form_submit", "browser_private_session", "browser_login_authority"],
        "allowed_paths": ["data/generated_projects"],
        "allowed_domains": ["example.com", "cdn.example.com"],
        "browser_v3_authority_grants": authority_grants,
        "max_actions": 20,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def context_pack(*, injection: bool = False) -> ContextPack:
    source_id = "source_download"
    return ContextPack(
        context_pack_id="cpk_download01",
        mission_id=MISSION_ID,
        mission_goal="Capture one public file into quarantine.",
        authority_boundary=ContextPackAuthorityBoundary(
            allowed_actions=["browser_download_quarantine"],
            forbidden_actions=["browser_form_submit", "browser_private_session", "browser_login_authority"],
            allowed_tools=["browser_download_quarantine"],
            allowed_domains=["example.com", "cdn.example.com"],
        ),
        browser_stable_refs=[
            ContextPackStableRef(
                id=LINK_REF,
                source_id=source_id,
                selector=f"accessibility_ref:{LINK_REF}",
                digest="d" * 64,
                page_sha256=PAGE_SHA,
                snapshot_sha256=SNAP_SHA,
            )
        ],
        available_action_intents=[
            ContextPackActionIntent(
                id="act_download",
                kind="browser_download_quarantine",
                impact="public_file_quarantine",
                authorization_conditions=["browser_v3_authority_grant", "mime_allowlist", "max_bytes"],
            )
        ],
        prompt_injection_flags=[
            ContextPackPromptInjectionFlag(source_id=source_id, risk="high", indicators=["download_instruction"], blocked=True, sanitized=True)
        ]
        if injection
        else [],
    )


def compile_download_intent(bus: EventBus, pack: ContextPack, env: MissionAuthorityEnvelope):
    raw = {
        "tool_id": "browser_download_quarantine",
        "action": "browser_download_quarantine",
        "capability": "public_web_download_quarantine",
        "target": "https://example.com/report.pdf",
        "requested_side_effects": ["network_read", "browser_read", "filesystem_write", "local_draft_write"],
        "arguments": {
            "context_pack_id": pack.context_pack_id,
            "context_pack_sha256": pack.context_pack_sha256,
            "authority_grant_id": "grant_download",
            "source_url": "https://example.com/report.pdf",
            "source_ref_id": LINK_REF,
            "page_sha256": PAGE_SHA,
            "snapshot_sha256": SNAP_SHA,
            "allowed_mime_types": ["application/pdf"],
            "max_bytes": 1024,
            "expected_effect": "PDF captured into quarantine",
        },
    }
    return ToolIntentCompiler().compile(raw, pack, env, event_bus=bus)


def sandbox(tmp_path) -> ArtifactCaptureSandbox:
    return ArtifactCaptureSandbox(mission_id=MISSION_ID, capture_root=tmp_path / "captures")


class FakeDownloadBackend:
    def __init__(
        self,
        *,
        data: bytes = PDF_BYTES,
        content_type: str = "application/pdf",
        final_url: str = "https://example.com/report.pdf",
        status_code: int = 200,
        redirect_chain: list[str] | None = None,
    ) -> None:
        self.data = data
        self.content_type = content_type
        self.final_url = final_url
        self.status_code = status_code
        self.redirect_chain = redirect_chain or []

    def __call__(self, request: BrowserDownloadQuarantineRequest) -> BrowserDownloadBackendResult:
        return BrowserDownloadBackendResult(
            final_url=self.final_url,
            status_code=self.status_code,
            content_type=self.content_type,
            data=self.data,
            filename="report.pdf",
            redirect_chain=self.redirect_chain,
            compressed_bytes_read=len(self.data),
            uncompressed_bytes_read=len(self.data),
        )


def v3_check(trace):
    return CoreFinalGate._browser_v3_download_quarantine_contract(SimpleNamespace(trace=tuple(trace)))


def test_download_quarantine_accepted_with_full_authority_and_proof(tmp_path):
    bus = EventBus(MISSION_ID)
    env = envelope()
    pack = context_pack()
    compiled = compile_download_intent(bus, pack, env)
    assert compiled.accepted is True
    assert compiled.trace_event_id is not None

    result = BrowserDownloadQuarantineExecutor(backend=FakeDownloadBackend()).execute(
        BrowserDownloadQuarantineRequest(
            mission_id=MISSION_ID,
            authority_grant_id="grant_download",
            context_pack_id=pack.context_pack_id,
            compiled_intent_trace_id=compiled.trace_event_id,
            source_url="https://example.com/report.pdf",
            source_ref_id=LINK_REF,
            allowed_mime_types=["application/pdf"],
            max_bytes=1024,
            expected_effect="PDF captured into quarantine",
        ),
        authority_grant=grant(),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
        policy_trace_id="policy_1",
    )

    assert result.accepted is True
    assert result.receipt is not None
    assert result.receipt.promoted is False
    assert result.receipt.quarantine_relative_path.startswith("browser/download_quarantine/")
    assert result.artifact_ids
    assert bus.events()[-1].event_type == AgentEventType.BROWSER_DOWNLOAD_QUARANTINED
    assert v3_check(bus.events()).passed is True


def test_controlled_runner_rejects_download_without_v3_authority(tmp_path):
    bus = EventBus(MISSION_ID)
    call = CanonicalToolCall(
        tool_id="browser_download_quarantine",
        action="browser_download_quarantine",
        capability="public_web_download_quarantine",
        target="https://example.com/report.pdf",
        requested_side_effects=[
            ToolSideEffect.NETWORK_READ,
            ToolSideEffect.BROWSER_READ,
            ToolSideEffect.FILESYSTEM_WRITE,
            ToolSideEffect.LOCAL_DRAFT_WRITE,
        ],
        arguments={
            "authority_grant_id": "grant_download",
            "context_pack_id": "cpk_download01",
            "compiled_intent_trace_id": "compiled_trace",
            "source_url": "https://example.com/report.pdf",
            "allowed_mime_types": ["application/pdf"],
            "max_bytes": 1024,
        },
        canonical_hash="hash",
    )

    result = BrowserControlledCapabilityRunner(
        registry=default_tool_registry(),
        capture_root=tmp_path / "captures",
        download_backend=FakeDownloadBackend(),
    ).run(call, envelope(include_grant=False), event_bus=bus)

    assert result.accepted is False
    assert result.reason in {"action_not_granted_by_mission_authority", "browser_v3_authority_grant_missing"}


def test_download_rejects_mime_and_size(tmp_path):
    bus = EventBus(MISSION_ID)
    base_request = BrowserDownloadQuarantineRequest(
        mission_id=MISSION_ID,
        authority_grant_id="grant_download",
        context_pack_id="cpk_download01",
        compiled_intent_trace_id="compiled_trace",
        source_url="https://example.com/report.pdf",
        allowed_mime_types=["application/pdf"],
        max_bytes=10,
    )

    mime_result = BrowserDownloadQuarantineExecutor(backend=FakeDownloadBackend(content_type="text/html")).execute(
        base_request.model_copy(update={"max_bytes": 1024}),
        authority_grant=grant(),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )
    assert mime_result.accepted is False
    assert mime_result.reason == "browser_download_mime_type_not_allowed"

    size_result = BrowserDownloadQuarantineExecutor(backend=FakeDownloadBackend(data=b"x" * 64)).execute(
        base_request,
        authority_grant=grant(max_bytes=10),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path / "second"),
    )
    assert size_result.accepted is False
    assert size_result.reason == "browser_download_body_too_large"


def test_prompt_injected_source_cannot_compile_download_intent():
    bus = EventBus(MISSION_ID)
    env = envelope()
    pack = context_pack(injection=True)

    result = compile_download_intent(bus, pack, env)

    assert result.accepted is False
    assert any("runtime_ref_from_injection_source" in error for error in result.errors)


def test_cross_origin_download_is_rejected_without_grant(tmp_path):
    bus = EventBus(MISSION_ID)
    result = BrowserDownloadQuarantineExecutor(
        backend=FakeDownloadBackend(final_url="https://cdn.example.com/report.pdf", redirect_chain=["https://cdn.example.com/report.pdf"])
    ).execute(
        BrowserDownloadQuarantineRequest(
            mission_id=MISSION_ID,
            authority_grant_id="grant_download",
            context_pack_id="cpk_download01",
            compiled_intent_trace_id="compiled_trace",
            source_url="https://example.com/report.pdf",
            allowed_mime_types=["application/pdf"],
            max_bytes=1024,
        ),
        authority_grant=grant(),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )

    assert result.accepted is False
    assert result.reason == "browser_download_cross_origin_result"


def test_final_gate_rejects_forged_download_receipt(tmp_path):
    bus = EventBus(MISSION_ID)
    compiled = bus.append(
        AgentEventType.TOOL_INTENT_COMPILED,
        "compiled",
        payload={"accepted": True, "context_pack_id": "cpk_download01", "canonical_hash": "c", "compilation_hash": "d"},
    )
    result = BrowserDownloadQuarantineExecutor(backend=FakeDownloadBackend()).execute(
        BrowserDownloadQuarantineRequest(
            mission_id=MISSION_ID,
            authority_grant_id="grant_download",
            context_pack_id="cpk_download01",
            compiled_intent_trace_id=compiled.id,
            source_url="https://example.com/report.pdf",
            allowed_mime_types=["application/pdf"],
            max_bytes=1024,
        ),
        authority_grant=grant(),
        event_bus=bus,
        artifact_capture=sandbox(tmp_path),
    )
    assert result.accepted is True
    events = list(bus.events())
    payload = dict(events[-1].payload)
    payload["artifact_sha256"] = "0" * 64
    events[-1] = events[-1].model_copy(update={"payload": payload})

    check = v3_check(events)

    assert check.passed is False
    assert any("browser_v3_download_artifact_hash_mismatch" in error for error in check.details["errors"])


def test_raw_llm_download_call_and_other_v3_power_are_rejected():
    bus = EventBus(MISSION_ID)
    env = envelope()
    pack = context_pack()

    raw_missing_contract = {
        "tool_id": "browser_download_quarantine",
        "action": "browser_download_quarantine",
        "requested_side_effects": ["network_read", "filesystem_write"],
        "arguments": {"source_url": "https://example.com/report.pdf"},
    }
    download_result = ToolIntentCompiler().compile(raw_missing_contract, pack, env, event_bus=bus)
    assert download_result.accepted is False
    assert "missing_or_mismatched_context_pack_id" in download_result.errors

    raw_upload = {
        "tool_id": "browser_download_quarantine",
        "action": "browser_upload_authorized",
        "requested_side_effects": ["network_read", "filesystem_write"],
        "arguments": {
            "context_pack_id": pack.context_pack_id,
            "context_pack_sha256": pack.context_pack_sha256,
        },
    }
    upload_result = ToolIntentCompiler().compile(raw_upload, pack, env, event_bus=bus)
    assert upload_result.accepted is False
    assert any("non_delegated_browser_power" in error or "action_outside_mission_authority" in error for error in upload_result.errors)
