from __future__ import annotations

import json

from sentinel.agent import (
    AgentEventType,
    EventBus,
    ToolCallParseMethod,
    ToolCallParseStatus,
    ToolCallProtocol,
)
from sentinel.capabilities import ToolExecutionStatus, ToolSideEffect
from sentinel.capabilities.manifest import default_tool_registry
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "P1L tool protocol test",
        "mission_objective": "Canonicalize tool-call intentions without granting execution.",
        "success_criteria": ["Tool calls are canonicalized", "Unsafe tools stay blocked"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer"],
        "allowed_actions": ["create_markdown_file", "write_trace"],
        "forbidden_actions": ["send_email", "run_shell_command", "browser_submit_form", "credential_access"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 20,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def test_tool_call_protocol_accepts_strict_json_and_traces_canonical_form():
    bus = EventBus("mission_001")
    raw = json.dumps(
        {
            "tool_id": "safe_file_writer",
            "action": "create_markdown_file",
            "capability": "local_markdown_write",
            "target": "data/generated_projects/demo/README.md",
            "arguments": {"path": "README.md", "content": "hello"},
            "requested_side_effects": ["filesystem_write", "local_draft_write"],
        }
    )

    result = ToolCallProtocol().canonicalize(raw, event_bus=bus)

    assert result.accepted is True
    assert result.status == ToolCallParseStatus.CANONICAL
    assert result.method == ToolCallParseMethod.JSON
    assert result.call is not None
    assert result.call.tool_id == "safe_file_writer"
    assert result.call.to_invocation().tool_id == "safe_file_writer"
    assert result.call.requested_side_effects == [ToolSideEffect.FILESYSTEM_WRITE, ToolSideEffect.LOCAL_DRAFT_WRITE]
    assert bus.events()[-1].event_type == AgentEventType.TOOL_CALL_CANONICALIZED
    assert bus.events()[-1].payload["argument_keys"] == ["content", "path"]
    assert AgentEventType.TOOL_POLICY_DECIDED not in [event.event_type for event in bus.events()]


def test_tool_call_protocol_recovers_xml_with_raw_argument_text():
    raw = """
    <tool_call>
      <tool_id>safe_file_writer</tool_id>
      <action>create_markdown_file</action>
      <capability>local_markdown_write</capability>
      <arguments>path=README.md; content=quote "inside" value</arguments>
    </tool_call>
    """

    result = ToolCallProtocol().canonicalize(raw)

    assert result.accepted is True
    assert result.status == ToolCallParseStatus.RECOVERED
    assert result.method == ToolCallParseMethod.XML
    assert result.call is not None
    assert result.call.arguments == {"raw": 'path=README.md; content=quote "inside" value'}
    assert "arguments_preserved_as_raw_text" in result.warnings


def test_tool_call_protocol_recovers_regex_fields():
    raw = "tool=safe_file_writer; action=create_markdown_file; capability=local_markdown_write; args={\"path\":\"README.md\"}"

    result = ToolCallProtocol().canonicalize(raw)

    assert result.accepted is True
    assert result.status == ToolCallParseStatus.RECOVERED
    assert result.method == ToolCallParseMethod.REGEX
    assert result.call is not None
    assert result.call.tool_id == "safe_file_writer"
    assert result.call.arguments == {"path": "README.md"}


def test_tool_call_protocol_recovers_embedded_json_object():
    raw = """
    I will not execute this directly.
    {"tool_id":"safe_file_writer","action":"create_markdown_file","arguments":{"path":"README.md"}}
    """

    result = ToolCallProtocol().canonicalize(raw)

    assert result.accepted is True
    assert result.status == ToolCallParseStatus.RECOVERED
    assert result.method == ToolCallParseMethod.JSON
    assert result.call is not None
    assert result.call.tool_id == "safe_file_writer"
    assert "recovered_embedded_json_object" in result.warnings


def test_tool_call_protocol_rejects_conflicting_aliases():
    raw = json.dumps(
        {
            "tool_id": "safe_file_writer",
            "tool": "shell_critical_blocked",
            "action": "create_markdown_file",
        }
    )

    result = ToolCallProtocol().canonicalize(raw)

    assert result.accepted is False
    assert "conflicting_tool_id_fields" in result.errors


def test_tool_call_protocol_rejects_duplicate_xml_core_field():
    raw = """
    <tool_call>
      <tool_id>safe_file_writer</tool_id>
      <tool_id>shell_critical_blocked</tool_id>
      <action>create_markdown_file</action>
    </tool_call>
    """

    result = ToolCallProtocol().canonicalize(raw)

    assert result.accepted is False
    assert "duplicate_field:tool_id" in result.errors


def test_tool_call_protocol_rejects_duplicate_regex_core_field():
    raw = "tool=safe_file_writer; tool=shell_critical_blocked; action=create_markdown_file"

    result = ToolCallProtocol().canonicalize(raw)

    assert result.accepted is False
    assert "duplicate_field:tool" in result.errors


def test_tool_call_protocol_rejects_malformed_or_unknown_shape_with_trace():
    bus = EventBus("mission_001")

    result = ToolCallProtocol().canonicalize("please use something maybe", event_bus=bus)

    assert result.accepted is False
    assert result.status == ToolCallParseStatus.REJECTED
    assert result.method == ToolCallParseMethod.REJECTED
    assert result.errors == ["tool_call_not_parseable"]
    assert bus.events()[-1].event_type == AgentEventType.TOOL_CALL_CANONICALIZED
    assert bus.events()[-1].payload["accepted"] is False


def test_tool_call_protocol_preserves_structured_rejection_reason():
    result = ToolCallProtocol().canonicalize(json.dumps({"tool_id": "safe_file_writer"}))

    assert result.accepted is False
    assert result.method == ToolCallParseMethod.JSON
    assert result.errors == ["missing_action"]


def test_tool_call_protocol_never_overrides_registry_policy_for_blocked_tools():
    bus = EventBus("mission_001")
    raw = json.dumps(
        {
            "tool_id": "shell_critical_blocked",
            "action": "run_shell_command",
            "arguments": {"command": "whoami"},
            "requested_side_effects": ["shell_execution"],
        }
    )

    result = ToolCallProtocol().canonicalize(raw, event_bus=bus)
    assert result.accepted is True
    assert result.call is not None

    decision = default_tool_registry().decide(result.call.to_invocation(), envelope(id="mission_001"), event_bus=bus)

    assert decision.allowed is False
    assert decision.status == ToolExecutionStatus.BLOCKED
    assert decision.reason == "black_zone_side_effect"
    assert [event.event_type for event in bus.events()] == [
        AgentEventType.TOOL_CALL_CANONICALIZED,
        AgentEventType.TOOL_POLICY_DECIDED,
    ]
