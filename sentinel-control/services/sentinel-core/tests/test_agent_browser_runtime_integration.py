from __future__ import annotations

import json

from sentinel.agent import AgentEventType, AgentRuntime, PlaywrightReadOnlyRenderer, certify_core_final_gate
from sentinel.capabilities import default_tool_registry
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


SAFE_ACTIONS = [
    "create_project_folder",
    "create_markdown_file",
    "export_json",
    "generate_gtm_pack",
    "generate_landing_copy",
    "generate_outreach_drafts_without_sending",
    "create_watchlist",
    "generate_research_questions",
    "write_trace",
]


class FakeResolver:
    def __call__(self, host: str) -> list[str]:
        if host == "example.com":
            return ["93.184.216.34"]
        return []


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "Browser runtime integration",
        "mission_objective": "Generate a GTM pack and collect public browser evidence.",
        "success_criteria": ["GTM pack exists", "Browser evidence is traced"],
        "mode": MissionMode.POWER,
        "risk_appetite_score": 80,
        "allowed_systems": ["local_workspace", "public_web"],
        "allowed_tools": ["safe_file_writer", "browser_readonly_public"],
        "allowed_actions": [*SAFE_ACTIONS, "browser_render_public_page"],
        "forbidden_actions": ["send_email", "run_shell_command", "browser_submit_form", "credential_access"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 40,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def browser_tool_call(url: str) -> str:
    return json.dumps(
        {
            "tool_id": "browser_readonly_public",
            "action": "browser_render_public_page",
            "target": url,
            "capability": "browser_research",
            "arguments": {
                "url": url,
                "purpose": "Collect public rendered page evidence.",
                "allowed_domains": ["example.com"],
            },
        }
    )


def test_agent_runtime_can_use_governed_browser_render_capability(tmp_path):
    url = "https://example.com/browser-proof"
    renderer = PlaywrightReadOnlyRenderer(
        document_fixtures={
            url: """
            <html>
              <head><title>Browser Proof</title></head>
              <body><h1>Rendered public evidence survives Browser V1.</h1></body>
            </html>
            """
        }
    )
    runtime = AgentRuntime(
        project_root=tmp_path,
        tool_registry=default_tool_registry(),
        browser_renderer=renderer,
        browser_resolver=FakeResolver(),
    )

    result = runtime.run(envelope(), user_input={"tool_calls": [browser_tool_call(url)]})

    event_types = [event.event_type for event in result.trace]
    assert result.success is True
    assert AgentEventType.TOOL_CALL_CANONICALIZED in event_types
    assert AgentEventType.TOOL_POLICY_DECIDED in event_types
    assert AgentEventType.BROWSER_URL_CLASSIFIED in event_types
    assert AgentEventType.BROWSER_SNAPSHOT_CAPTURED in event_types
    assert any(item.get("accepted") is True and item.get("tool_id") == "browser_readonly_public" for item in result.controlled_capability_results)
    browser_event = next(event for event in result.trace if event.event_type == AgentEventType.BROWSER_SNAPSHOT_CAPTURED)
    assert browser_event.payload["title"] == "Browser Proof"
    assert browser_event.payload["screenshot_artifact_id"]

    gate = certify_core_final_gate(result, allowed_project_root=tmp_path)
    assert gate.accepted is True
    assert gate.errors == []


def test_agent_runtime_blocks_browser_when_mission_authority_does_not_grant_tool(tmp_path):
    url = "https://example.com/browser-proof"
    runtime = AgentRuntime(
        project_root=tmp_path,
        tool_registry=default_tool_registry(),
        browser_renderer=PlaywrightReadOnlyRenderer(document_fixtures={url: "<html><body>blocked</body></html>"}),
        browser_resolver=FakeResolver(),
    )

    result = runtime.run(
        envelope(allowed_tools=["safe_file_writer"]),
        user_input={"tool_calls": [browser_tool_call(url)]},
    )

    event_types = [event.event_type for event in result.trace]
    assert AgentEventType.BROWSER_SNAPSHOT_CAPTURED not in event_types
    assert AgentEventType.CONTROLLED_CAPABILITY_REJECTED in event_types
    rejected = [item for item in result.controlled_capability_results if item.get("tool_id") == "browser_readonly_public"]
    assert rejected
    assert rejected[0]["accepted"] is False
    assert rejected[0]["reason"] == "tool_not_granted_by_mission_authority"


def test_final_gate_rejects_browser_result_without_registry_policy_trace(tmp_path):
    url = "https://example.com/browser-proof"
    runtime = AgentRuntime(
        project_root=tmp_path,
        tool_registry=default_tool_registry(),
        browser_renderer=PlaywrightReadOnlyRenderer(document_fixtures={url: "<html><body>policy bound</body></html>"}),
        browser_resolver=FakeResolver(),
    )
    result = runtime.run(envelope(), user_input={"tool_calls": [browser_tool_call(url)]})
    forged_results = []
    for item in result.controlled_capability_results:
        forged = dict(item)
        if forged.get("accepted") and forged.get("tool_id") == "browser_readonly_public":
            forged["policy_trace_id"] = "forged-policy-event"
        forged_results.append(forged)
    tampered = result.model_copy(update={"controlled_capability_results": forged_results})

    gate = certify_core_final_gate(tampered, allowed_project_root=tmp_path)

    assert gate.accepted is False
    assert "browser_capability_receipts" in gate.errors


def test_final_gate_rejects_forged_browser_network_ledger_hash(tmp_path):
    url = "https://example.com/browser-proof"
    runtime = AgentRuntime(
        project_root=tmp_path,
        tool_registry=default_tool_registry(),
        browser_renderer=PlaywrightReadOnlyRenderer(document_fixtures={url: "<html><body>ledger bound</body></html>"}),
        browser_resolver=FakeResolver(),
    )
    result = runtime.run(envelope(), user_input={"tool_calls": [browser_tool_call(url)]})
    tampered = _tamper_browser_snapshot_payload(
        result,
        lambda payload: payload.update({"network_ledger_sha256": "0" * 64}),
    )

    gate = certify_core_final_gate(tampered, allowed_project_root=tmp_path)

    assert gate.accepted is False
    assert "browser_capability_receipts" in gate.errors


def test_final_gate_rejects_browser_snapshot_missing_network_ledger_metadata(tmp_path):
    url = "https://example.com/browser-proof"
    runtime = AgentRuntime(
        project_root=tmp_path,
        tool_registry=default_tool_registry(),
        browser_renderer=PlaywrightReadOnlyRenderer(document_fixtures={url: "<html><body>ledger required</body></html>"}),
        browser_resolver=FakeResolver(),
    )
    result = runtime.run(envelope(), user_input={"tool_calls": [browser_tool_call(url)]})

    def remove_ledger(payload: dict) -> None:
        payload.pop("network_ledger", None)
        payload.pop("network_ledger_sha256", None)

    tampered = _tamper_browser_snapshot_payload(result, remove_ledger)

    gate = certify_core_final_gate(tampered, allowed_project_root=tmp_path)

    assert gate.accepted is False
    assert "browser_capability_receipts" in gate.errors


def _tamper_browser_snapshot_payload(result, mutate_payload):
    trace = []
    for event in result.trace:
        if event.event_type == AgentEventType.BROWSER_SNAPSHOT_CAPTURED:
            payload = dict(event.payload)
            mutate_payload(payload)
            trace.append(event.model_copy(update={"payload": payload}))
        else:
            trace.append(event)
    return result.model_copy(update={"trace": trace})
