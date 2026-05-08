from __future__ import annotations

import pytest
from pydantic import ValidationError

from sentinel.agent import AgentEventType, EventBus
from sentinel.agent.capability_selector import CapabilitySelector
from sentinel.agent.context_builder import ContextBuilder
from sentinel.agent.method_selector import MethodSelector
from sentinel.capabilities import (
    CapabilityManifest,
    CapabilityManifestStatus,
    ToolAuthType,
    ToolExecutionStatus,
    ToolInvocation,
    ToolRegistry,
    ToolRiskClass,
    ToolSideEffect,
    default_tool_registry,
    risk_for_side_effects,
)
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
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "P1B capability registry test",
        "mission_objective": "Verify tool manifests cannot bypass mission authority.",
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_local_markdown_tool"],
        "allowed_actions": SAFE_ACTIONS,
        "forbidden_actions": ["send_email", "run_shell_command", "browser_submit_form", "credential_access"],
        "allowed_paths": ["data/generated_projects"],
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def event_bus(env: MissionAuthorityEnvelope) -> EventBus:
    return EventBus(env.id)


def test_manifest_requires_explicit_side_effects():
    with pytest.raises(ValidationError):
        CapabilityManifest(
            id="bad_manifest",
            name="Bad Manifest",
            category="test",
            provider="fixture",
            description="Missing side effects should fail.",
            capabilities=["test"],
            allowed_actions=["test"],
            status=CapabilityManifestStatus.CANDIDATE,
        )


def test_manifest_rejects_none_mixed_with_real_side_effects():
    with pytest.raises(ValidationError):
        CapabilityManifest(
            id="ambiguous_manifest",
            name="Ambiguous Manifest",
            category="test",
            provider="fixture",
            description="A manifest cannot declare no-op and mutation together.",
            capabilities=["test"],
            allowed_actions=["test"],
            side_effects=[ToolSideEffect.NONE, ToolSideEffect.FILESYSTEM_WRITE],
            status=CapabilityManifestStatus.CANDIDATE,
        )


def test_unknown_tool_blocked_and_decision_traced():
    registry = default_tool_registry()
    env = envelope()
    bus = EventBus(env.id)

    decision = registry.decide(
        ToolInvocation(tool_id="unknown_tool", action="read_public_data", requested_side_effects=[ToolSideEffect.NETWORK_READ]),
        env,
        event_bus=bus,
    )

    assert decision.allowed is False
    assert decision.status == ToolExecutionStatus.BLOCKED
    assert decision.reason == "tool_without_manifest"
    assert decision.trace_event_id is not None
    assert bus.events()[-1].event_type == AgentEventType.TOOL_POLICY_DECIDED


def test_tool_without_manifest_blocked():
    registry = ToolRegistry()
    registry.register_unmanifested("placeholder_tool")
    env = envelope()

    decision = registry.decide(
        ToolInvocation(tool_id="placeholder_tool", action="read_public_data", requested_side_effects=[ToolSideEffect.NETWORK_READ]),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.reason == "tool_without_manifest"


def test_registry_rejects_duplicate_tool_ids():
    registry = ToolRegistry()
    manifest = default_tool_registry().get("safe_local_markdown_tool")
    registry.register(manifest)

    with pytest.raises(ValueError):
        registry.register(manifest)


def test_registry_rejects_empty_or_padded_tool_ids():
    registry = ToolRegistry()
    manifest = default_tool_registry().get("safe_local_markdown_tool")
    padded_manifest = manifest.model_copy(update={"id": " padded_tool"})

    with pytest.raises(ValueError):
        registry.register(padded_manifest)
    with pytest.raises(ValueError):
        registry.register_unmanifested("")
    with pytest.raises(ValueError):
        registry.register_unmanifested(" placeholder_tool ")


def test_registry_snapshots_registered_manifest():
    registry = ToolRegistry()
    manifest = default_tool_registry().get("safe_local_markdown_tool")
    registry.register(manifest)

    manifest.side_effects.append(ToolSideEffect.SHELL_EXECUTION)
    env = envelope()

    decision = registry.decide(
        ToolInvocation(
            tool_id="safe_local_markdown_tool",
            action="create_markdown_file",
            requested_side_effects=[ToolSideEffect.FILESYSTEM_WRITE, ToolSideEffect.LOCAL_DRAFT_WRITE],
        ),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is True


def test_registry_returned_manifest_cannot_mutate_registry_state():
    registry = default_tool_registry()
    returned = registry.get("safe_local_markdown_tool")
    returned.side_effects.append(ToolSideEffect.SHELL_EXECUTION)

    fresh = registry.get("safe_local_markdown_tool")

    assert ToolSideEffect.SHELL_EXECUTION not in fresh.side_effects


def test_public_api_candidate_imported_but_not_executed():
    registry = default_tool_registry()
    env = envelope()

    assert "public_weather_api_candidate" in registry.list_tools()
    decision = registry.decide(
        ToolInvocation(tool_id="public_weather_api_candidate", action="read_public_weather", requested_side_effects=[ToolSideEffect.NETWORK_READ]),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.status == ToolExecutionStatus.CANDIDATE_ONLY
    assert decision.reason == "candidate_tool_cannot_execute"


def test_leaked_key_source_blocked():
    registry = default_tool_registry()
    env = envelope()

    decision = registry.decide(
        ToolInvocation(tool_id="leaked_key_api_blocked", action="read_public_data", requested_side_effects=[ToolSideEffect.NETWORK_READ, ToolSideEffect.SECRET_READ]),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.status == ToolExecutionStatus.BLOCKED
    assert decision.risk_class == ToolRiskClass.CRITICAL_BLOCKED


def test_shell_tool_blocked_even_in_power_mode():
    registry = default_tool_registry()
    env = envelope(mode=MissionMode.POWER, allowed_actions=[*SAFE_ACTIONS, "run_shell_command"], allowed_tools=["shell_critical_blocked"])

    decision = registry.decide(
        ToolInvocation(tool_id="shell_critical_blocked", action="run_shell_command", requested_side_effects=[ToolSideEffect.SHELL_EXECUTION]),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.status == ToolExecutionStatus.BLOCKED
    assert decision.reason == "black_zone_side_effect"


def test_browser_submit_blocked_from_readonly_candidate():
    registry = default_tool_registry()
    env = envelope(allowed_actions=[*SAFE_ACTIONS, "browser_submit_form"], allowed_tools=["browser_readonly_candidate"])

    decision = registry.decide(
        ToolInvocation(tool_id="browser_readonly_candidate", action="browser_submit_form", requested_side_effects=[ToolSideEffect.BROWSER_SUBMIT]),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.status == ToolExecutionStatus.BLOCKED
    assert decision.reason == "undeclared_side_effect"


def test_email_send_not_executable():
    registry = default_tool_registry()
    env = envelope(allowed_actions=[*SAFE_ACTIONS, "send_email"], allowed_tools=["email_send_high_risk_candidate"])

    decision = registry.decide(
        ToolInvocation(tool_id="email_send_high_risk_candidate", action="send_email", requested_side_effects=[ToolSideEffect.EXTERNAL_SEND, ToolSideEffect.NETWORK_WRITE]),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.status == ToolExecutionStatus.BLOCKED
    assert decision.reason == "black_zone_side_effect"


def test_undeclared_side_effect_is_blocked():
    registry = default_tool_registry()
    env = envelope()

    decision = registry.decide(
        ToolInvocation(tool_id="safe_local_markdown_tool", action="create_markdown_file", requested_side_effects=[ToolSideEffect.NETWORK_READ]),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.reason == "undeclared_side_effect"


def test_approved_safe_fake_tool_can_route_through_mission_authority():
    registry = default_tool_registry()
    env = envelope()
    bus = EventBus(env.id)

    decision = registry.decide(
        ToolInvocation(
            tool_id="safe_local_markdown_tool",
            action="create_markdown_file",
            requested_side_effects=[ToolSideEffect.FILESYSTEM_WRITE, ToolSideEffect.LOCAL_DRAFT_WRITE],
        ),
        env,
        event_bus=bus,
    )

    assert decision.allowed is True
    assert decision.status == ToolExecutionStatus.ALLOWED
    assert decision.reason == "approved_tool_granted_by_mission_authority"
    assert decision.trace_event_id == bus.events()[-1].id
    assert bus.events()[-1].payload["requested_side_effects"] == [ToolSideEffect.FILESYSTEM_WRITE, ToolSideEffect.LOCAL_DRAFT_WRITE]
    assert bus.events()[-1].payload["manifest_status"] == CapabilityManifestStatus.APPROVED


def test_policy_blocks_invocation_with_missing_requested_side_effects():
    registry = default_tool_registry()
    env = envelope()

    decision = registry.decide(
        ToolInvocation(
            tool_id="safe_local_markdown_tool",
            action="create_markdown_file",
            requested_side_effects=[],
        ),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.status == ToolExecutionStatus.BLOCKED
    assert decision.reason == "requested_side_effects_missing"


def test_policy_blocks_ambiguous_none_side_effect():
    registry = default_tool_registry()
    env = envelope()

    decision = registry.decide(
        ToolInvocation(
            tool_id="safe_local_markdown_tool",
            action="create_markdown_file",
            requested_side_effects=[ToolSideEffect.NONE, ToolSideEffect.LOCAL_DRAFT_WRITE],
        ),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.reason == "ambiguous_none_side_effect"


def test_policy_blocks_approved_manifest_that_understates_side_effect_risk():
    registry = ToolRegistry()
    registry.register(
        CapabilityManifest(
            id="understated_network_writer",
            name="Understated Network Writer",
            category="network",
            provider="fixture",
            description="Approved-looking manifest that understates NETWORK_WRITE.",
            capabilities=["network_mutation_fixture"],
            auth_type=ToolAuthType.NONE,
            allowed_actions=["network_mutation_fixture"],
            side_effects=[ToolSideEffect.NETWORK_WRITE],
            risk_class=ToolRiskClass.READ_ONLY_PUBLIC,
            mission_scopes_allowed=["gtm"],
            status=CapabilityManifestStatus.APPROVED,
        )
    )
    env = envelope(
        allowed_tools=["understated_network_writer"],
        allowed_actions=[*SAFE_ACTIONS, "network_mutation_fixture"],
    )

    decision = registry.decide(
        ToolInvocation(
            tool_id="understated_network_writer",
            action="network_mutation_fixture",
            requested_side_effects=[ToolSideEffect.NETWORK_WRITE],
        ),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.reason == "risk_class_understates_side_effects"
    assert decision.risk_class == ToolRiskClass.EXTERNAL_MUTATION


def test_approved_tool_still_blocked_without_mission_authority():
    registry = default_tool_registry()
    env = envelope(allowed_tools=[], allowed_actions=SAFE_ACTIONS)

    decision = registry.decide(
        ToolInvocation(
            tool_id="safe_local_markdown_tool",
            action="create_markdown_file",
            requested_side_effects=[ToolSideEffect.FILESYSTEM_WRITE, ToolSideEffect.LOCAL_DRAFT_WRITE],
        ),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.reason == "tool_not_granted_by_mission_authority"


def test_decision_trace_must_match_mission_id():
    registry = default_tool_registry()

    with pytest.raises(ValueError):
        registry.decide(
            ToolInvocation(
                tool_id="safe_local_markdown_tool",
                action="create_markdown_file",
                requested_side_effects=[ToolSideEffect.FILESYSTEM_WRITE, ToolSideEffect.LOCAL_DRAFT_WRITE],
            ),
            envelope(),
            event_bus=EventBus("different_mission"),
        )


def test_approved_write_tool_with_broad_root_is_blocked():
    registry = ToolRegistry()
    registry.register(
        CapabilityManifest(
            id="unsafe_broad_writer",
            name="Unsafe Broad Writer",
            category="local_file",
            provider="fixture",
            description="Approved-looking fixture with unsafe broad filesystem root.",
            capabilities=["local_markdown_write"],
            auth_type=ToolAuthType.NONE,
            allowed_actions=["create_markdown_file"],
            side_effects=[ToolSideEffect.FILESYSTEM_WRITE],
            filesystem_roots=["*"],
            risk_class=ToolRiskClass.DRAFT_ONLY_WRITE,
            mission_scopes_allowed=["gtm"],
            status=CapabilityManifestStatus.APPROVED,
        )
    )

    env = envelope(allowed_tools=["unsafe_broad_writer"], allowed_paths=["*"])
    decision = registry.decide(
        ToolInvocation(
            tool_id="unsafe_broad_writer",
            action="create_markdown_file",
            requested_side_effects=[ToolSideEffect.FILESYSTEM_WRITE],
        ),
        env,
        event_bus=event_bus(env),
    )

    assert decision.allowed is False
    assert decision.reason == "filesystem_root_outside_mission_scope"


def test_side_effects_map_to_risk():
    assert risk_for_side_effects([ToolSideEffect.SHELL_EXECUTION]) == ToolRiskClass.CRITICAL_BLOCKED
    assert risk_for_side_effects([ToolSideEffect.NETWORK_READ]) == ToolRiskClass.READ_ONLY_PUBLIC
    assert risk_for_side_effects([ToolSideEffect.LOCAL_DRAFT_WRITE]) == ToolRiskClass.DRAFT_ONLY_WRITE
    assert risk_for_side_effects([ToolSideEffect.FILESYSTEM_WRITE, ToolSideEffect.LOCAL_DRAFT_WRITE]) == ToolRiskClass.DRAFT_ONLY_WRITE
    assert risk_for_side_effects([ToolSideEffect.FILESYSTEM_WRITE]) == ToolRiskClass.HOST_MUTATION


def test_registry_export_json_stub_is_serializable():
    exported = default_tool_registry().export_json()

    assert exported
    assert any(item["id"] == "safe_local_markdown_tool" for item in exported)


def test_capability_selector_uses_registry_for_missing_reason():
    registry = default_tool_registry()
    env = envelope()
    context = ContextBuilder().build(env, evidence_refs=["ev_001"])
    methods = MethodSelector().select(context)

    needs = CapabilitySelector(registry=registry).select(context, methods)
    browser_need = next(need for need in needs if need.name == "browser_research")

    assert browser_need.available is False
    assert browser_need.missing_reason == "Capability is not granted by mission authority, although an approved manifest exists."


def test_capability_selector_requires_approved_manifest_when_registry_present():
    registry = ToolRegistry()
    env = envelope()
    context = ContextBuilder().build(env, evidence_refs=["ev_001"])
    methods = MethodSelector().select(context)

    needs = CapabilitySelector(registry=registry).select(context, methods)
    gtm_need = next(need for need in needs if need.name == "gtm_pack_generation")

    assert gtm_need.available is False
    assert gtm_need.missing_reason == "Capability has no manifest in the registry."


def test_capability_selector_requires_approved_manifest_granted_by_mission():
    registry = default_tool_registry()
    env = envelope(allowed_tools=[])
    context = ContextBuilder().build(env, evidence_refs=["ev_001"])
    methods = MethodSelector().select(context)

    needs = CapabilitySelector(registry=registry).select(context, methods)
    gtm_need = next(need for need in needs if need.name == "gtm_pack_generation")

    assert gtm_need.available is False
    assert gtm_need.missing_reason == "Capability has an approved manifest, but mission authority does not grant an approved tool."
