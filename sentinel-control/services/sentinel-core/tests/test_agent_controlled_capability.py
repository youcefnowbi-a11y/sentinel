from __future__ import annotations

import json

from sentinel.agent import (
    AgentEventType,
    AgentRuntime,
    EventBus,
    LocalControlledCapabilityRunner,
    ToolCallProtocol,
    certify_core_final_gate,
)
from sentinel.capabilities import ToolExecutionStatus, default_tool_registry
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


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "id": "mission_001",
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "P2A controlled local capability",
        "mission_objective": "Execute the first controlled local capability.",
        "success_criteria": ["Local artifact is created after policy approval"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_local_markdown_tool"],
        "allowed_actions": SAFE_ACTIONS,
        "forbidden_actions": ["send_email", "run_shell_command", "browser_submit_form", "credential_access"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 20,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    if data.get("id") is None:
        data.pop("id")
    return MissionAuthorityEnvelope(**data)


def canonical_call(payload: dict, bus: EventBus):
    result = ToolCallProtocol().canonicalize(json.dumps(payload), event_bus=bus)
    assert result.accepted is True
    assert result.call is not None
    return result.call


def test_controlled_runner_executes_safe_local_markdown_after_policy_approval(tmp_path):
    env = envelope()
    bus = EventBus(env.id)
    call = canonical_call(
        {
            "tool_id": "safe_local_markdown_tool",
            "action": "create_markdown_file",
            "capability": "local_markdown_write",
            "arguments": {"path": "notes/hello.md", "content": "hello controlled world"},
        },
        bus,
    )

    result = LocalControlledCapabilityRunner(
        registry=default_tool_registry(),
        capture_root=tmp_path,
    ).run(call, env, event_bus=bus)

    assert result.accepted is True
    assert result.policy_status == ToolExecutionStatus.ALLOWED
    assert (tmp_path / "notes" / "hello.md").read_text(encoding="utf-8") == "hello controlled world"
    assert result.artifact_result is not None
    assert result.artifact_result.artifact is not None
    assert result.artifact_result.artifact.relative_path == "notes/hello.md"
    assert result.receipt is not None
    assert result.receipt.tool_call_id == call.id
    assert result.receipt.canonical_call_hash == call.canonical_hash
    assert result.receipt.artifact_id == result.artifact_result.artifact.id
    assert result.receipt.policy_trace_id is not None
    assert result.receipt.capture_trace_id == result.artifact_result.trace_event_id
    assert result.receipt.artifact_sha256 == result.artifact_result.artifact.sha256
    assert result.receipt.rollback_strategy == "delete_captured_artifact_if_hash_matches"
    assert [event.event_type for event in bus.events()] == [
        AgentEventType.TOOL_CALL_CANONICALIZED,
        AgentEventType.TOOL_POLICY_DECIDED,
        AgentEventType.ARTIFACT_CAPTURED,
        AgentEventType.CONTROLLED_CAPABILITY_EXECUTED,
    ]
    assert bus.events()[-1].payload["tool_call_id"] == call.id
    assert bus.events()[-1].payload["canonical_call_hash"] == call.canonical_hash
    assert bus.events()[-1].payload["artifact_id"] == result.artifact_result.artifact.id
    assert "hello controlled world" not in json.dumps([event.payload for event in bus.events()], default=str)


def test_controlled_runner_uses_manifest_side_effects_when_model_omits_them(tmp_path):
    env = envelope(
        allowed_tools=["shell_critical_blocked"],
        allowed_actions=[*SAFE_ACTIONS, "run_shell_command"],
    )
    bus = EventBus(env.id)
    call = canonical_call(
        {
            "tool_id": "shell_critical_blocked",
            "action": "run_shell_command",
            "arguments": {"command": "whoami"},
        },
        bus,
    )

    result = LocalControlledCapabilityRunner(
        registry=default_tool_registry(),
        capture_root=tmp_path,
    ).run(call, env, event_bus=bus)

    assert result.accepted is False
    assert result.policy_status == ToolExecutionStatus.BLOCKED
    assert result.reason == "black_zone_side_effect"
    assert AgentEventType.ARTIFACT_CAPTURED not in [event.event_type for event in bus.events()]
    assert bus.events()[-1].event_type == AgentEventType.CONTROLLED_CAPABILITY_REJECTED


def test_controlled_runner_rejects_candidate_tool_without_artifact_write(tmp_path):
    env = envelope(
        allowed_tools=["browser_readonly_candidate"],
        allowed_actions=[*SAFE_ACTIONS, "browser_read_public_page"],
    )
    bus = EventBus(env.id)
    call = canonical_call(
        {
            "tool_id": "browser_readonly_candidate",
            "action": "browser_read_public_page",
            "arguments": {"path": "browser.txt", "content": "not created"},
        },
        bus,
    )

    result = LocalControlledCapabilityRunner(
        registry=default_tool_registry(),
        capture_root=tmp_path,
    ).run(call, env, event_bus=bus)

    assert result.accepted is False
    assert result.policy_status == ToolExecutionStatus.CANDIDATE_ONLY
    assert result.reason == "candidate_tool_cannot_execute"
    assert not (tmp_path / "browser.txt").exists()


def test_controlled_runner_rejects_path_escape_after_policy_approval(tmp_path):
    env = envelope()
    bus = EventBus(env.id)
    call = canonical_call(
        {
            "tool_id": "safe_local_markdown_tool",
            "action": "create_markdown_file",
            "arguments": {"path": "../escape.md", "content": "nope"},
        },
        bus,
    )

    result = LocalControlledCapabilityRunner(
        registry=default_tool_registry(),
        capture_root=tmp_path,
    ).run(call, env, event_bus=bus)

    assert result.accepted is False
    assert result.reason == "path_outside_capture_root"
    assert not (tmp_path.parent / "escape.md").exists()
    assert AgentEventType.ARTIFACT_CAPTURE_REJECTED in [event.event_type for event in bus.events()]


def test_controlled_runner_executes_safe_json_export(tmp_path):
    env = envelope(allowed_tools=["safe_file_writer"], allowed_actions=[*SAFE_ACTIONS, "export_json"])
    bus = EventBus(env.id)
    call = canonical_call(
        {
            "tool_id": "safe_file_writer",
            "action": "export_json",
            "arguments": {"path": "data/result.json", "payload": {"b": 2, "a": 1}},
        },
        bus,
    )

    result = LocalControlledCapabilityRunner(
        registry=default_tool_registry(),
        capture_root=tmp_path,
    ).run(call, env, event_bus=bus)

    assert result.accepted is True
    assert (tmp_path / "data" / "result.json").read_text(encoding="utf-8") == '{\n  "a": 1,\n  "b": 2\n}'


def test_core_final_gate_still_accepts_agent_runtime_after_p2a_module_exists(tmp_path):
    env = envelope(
        id=None,
        mission_title="P2A gate smoke",
        allowed_tools=["safe_file_writer"],
        allowed_actions=SAFE_ACTIONS,
    )

    result = AgentRuntime(project_root=tmp_path).run(env, {"idea": "P2A"}, evidence_refs=["ev_wtp"])
    gate = certify_core_final_gate(result, allowed_project_root=tmp_path)

    assert gate.accepted is True


def test_core_final_gate_accepts_controlled_capability_receipt(tmp_path):
    env = envelope(
        id=None,
        mission_title="P2C receipt gate",
        allowed_tools=["safe_file_writer", "safe_local_markdown_tool"],
    )

    result = AgentRuntime(project_root=tmp_path).run(
        env,
        {
            "idea": "P2C",
            "tool_calls": [
                {
                    "tool_id": "safe_local_markdown_tool",
                    "action": "create_markdown_file",
                    "capability": "local_markdown_write",
                    "arguments": {"path": "runtime/receipt.md", "content": "receipt proof"},
                }
            ],
        },
        evidence_refs=["ev_wtp"],
    )
    gate = certify_core_final_gate(result, allowed_project_root=tmp_path)

    assert result.success is True
    assert result.controlled_capability_results[0]["accepted"] is True
    assert result.controlled_capability_results[0]["receipt"]["artifact_path"] == "runtime/receipt.md"
    assert gate.accepted is True


def test_agent_runtime_controlled_capture_uses_manifest_scoped_generated_root(tmp_path):
    env = envelope(
        id=None,
        mission_title="P2 authority root ordering",
        allowed_tools=["safe_file_writer", "safe_local_markdown_tool"],
        allowed_paths=["tmp_untrusted_first", "data/generated_projects"],
    )

    result = AgentRuntime(project_root=tmp_path).run(
        env,
        {
            "idea": "root order",
            "tool_calls": [
                {
                    "tool_id": "safe_local_markdown_tool",
                    "action": "create_markdown_file",
                    "arguments": {"path": "runtime/root.md", "content": "root proof"},
                }
            ],
        },
        evidence_refs=["ev_wtp"],
    )

    expected = tmp_path / "data" / "generated_projects" / "p2-authority-root-ordering" / "runtime" / "root.md"
    wrong = tmp_path / "tmp_untrusted_first" / "p2-authority-root-ordering" / "runtime" / "root.md"
    assert result.success is True
    assert expected.exists()
    assert not wrong.exists()


def test_core_final_gate_rejects_controlled_capability_execution_without_receipt(tmp_path):
    env = envelope(
        id=None,
        mission_title="P2C bad receipt gate",
        allowed_tools=["safe_file_writer", "safe_local_markdown_tool"],
    )
    result = AgentRuntime(project_root=tmp_path).run(
        env,
        {
            "idea": "P2C",
            "tool_calls": [
                {
                    "tool_id": "safe_local_markdown_tool",
                    "action": "create_markdown_file",
                    "arguments": {"path": "runtime/no-receipt.md", "content": "receipt missing"},
                }
            ],
        },
        evidence_refs=["ev_wtp"],
    )
    unsafe_results = [dict(item) for item in result.controlled_capability_results]
    unsafe_results[0].pop("receipt", None)
    unsafe = result.model_copy(update={"controlled_capability_results": unsafe_results})

    gate = certify_core_final_gate(unsafe, allowed_project_root=tmp_path)

    assert gate.accepted is False
    assert "controlled_capability_receipts" in gate.errors


def test_core_final_gate_rejects_controlled_capability_receipt_canonical_hash_mismatch(tmp_path):
    env = envelope(
        id=None,
        mission_title="P2C forged canonical hash",
        allowed_tools=["safe_file_writer", "safe_local_markdown_tool"],
    )
    result = AgentRuntime(project_root=tmp_path).run(
        env,
        {
            "idea": "P2C",
            "tool_calls": [
                {
                    "tool_id": "safe_local_markdown_tool",
                    "action": "create_markdown_file",
                    "arguments": {"path": "runtime/forged-hash.md", "content": "hash proof"},
                }
            ],
        },
        evidence_refs=["ev_wtp"],
    )
    unsafe_results = [dict(item) for item in result.controlled_capability_results]
    unsafe_receipt = dict(unsafe_results[0]["receipt"])
    unsafe_receipt["canonical_call_hash"] = "forged"
    unsafe_results[0]["receipt"] = unsafe_receipt
    unsafe = result.model_copy(update={"controlled_capability_results": unsafe_results})

    gate = certify_core_final_gate(unsafe, allowed_project_root=tmp_path)

    assert gate.accepted is False
    assert "controlled_capability_receipts" in gate.errors
