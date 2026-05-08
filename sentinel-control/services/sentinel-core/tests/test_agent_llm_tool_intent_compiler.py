from __future__ import annotations

import json
from types import SimpleNamespace

from sentinel.agent import (
    AgentEventType,
    AgentPhase,
    BrowserPlannerRole,
    BrowserVerifierRole,
    ContextPack,
    ContextPackActionIntent,
    ContextPackAuthorityBoundary,
    ContextPackCitation,
    ContextPackPromptInjectionFlag,
    ContextPackSourceQualityFlag,
    ContextPackStableRef,
    ContextPackValidator,
    EventBus,
    ToolIntentCompilationStage,
    ToolIntentCompilationStatus,
    ToolIntentCompiler,
)
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.capabilities import ToolSideEffect, default_tool_registry
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


MISSION_ID = "mission_p3y_compiler"


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "id": MISSION_ID,
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "P3Y ToolIntentCompiler",
        "mission_objective": "Compile LLM browser intent without granting authority.",
        "success_criteria": ["Intent compiles only with proof"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["public_web", "local_workspace"],
        "allowed_tools": ["browser_public_operator_limited"],
        "allowed_actions": ["browser_interaction_limited"],
        "forbidden_actions": ["browser_submit_form", "login", "upload", "download", "browser_evaluate_script"],
        "allowed_domains": ["example.com"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 20,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def pack(**overrides) -> ContextPack:
    env = envelope()
    data = {
        "mission_id": env.id,
        "mission_goal": env.mission_objective,
        "authority_boundary": ContextPackAuthorityBoundary(
            allowed_actions=list(env.allowed_actions),
            forbidden_actions=list(env.forbidden_actions),
            allowed_tools=list(env.allowed_tools),
            allowed_domains=list(env.allowed_domains),
        ),
        "browser_stable_refs": [
            ContextPackStableRef(
                id="e1",
                source_id="src_form",
                selector="accessibility_ref:e1",
                digest="ref_digest",
                page_sha256="page_hash",
                snapshot_sha256="snapshot_hash",
            )
        ],
        "citations": [
            ContextPackCitation(
                id="c1",
                source_id="src_form",
                stable_ref_id="e1",
                support_level="full",
                excerpt="A public input is visible.",
                digest="citation_digest",
            )
        ],
        "source_quality_flags": [
            ContextPackSourceQualityFlag(source_id="src_form", flags=["official_primary"], derived_score=0.9)
        ],
        "available_action_intents": [
            ContextPackActionIntent(id="act_browser", kind="browser_interaction_limited", impact="local_form_state")
        ],
    }
    data.update(overrides)
    return ContextPack(**data)


def valid_intent(context_pack: ContextPack) -> dict:
    return {
        "tool_id": "browser_public_operator_limited",
        "action": "browser_interaction_limited",
        "capability": "browser_interaction",
        "arguments": {
            "context_pack_id": context_pack.context_pack_id,
            "context_pack_sha256": context_pack.context_pack_sha256,
            "ref": "e1",
            "page_sha256": "page_hash",
            "snapshot_sha256": "snapshot_hash",
            "evidence_refs": ["c1"],
        },
        "requested_side_effects": [
            ToolSideEffect.NETWORK_READ.value,
            ToolSideEffect.BROWSER_READ.value,
            ToolSideEffect.FILESYSTEM_WRITE.value,
            ToolSideEffect.LOCAL_DRAFT_WRITE.value,
        ],
    }


def test_tool_intent_compiler_accepts_bound_ref_and_validated_context_pack():
    env = envelope()
    context_pack = pack()
    bus = EventBus(env.id)
    bus.append(
        AgentEventType.CONTEXT_PACK_ASSEMBLED,
        "ContextPack assembled.",
        phase_before=AgentPhase.CONTEXT_BUILDING,
        phase_after=AgentPhase.CONTEXT_BUILDING,
        payload={"context_pack_id": context_pack.context_pack_id, "context_pack_sha256": context_pack.context_pack_sha256},
    )
    assert ContextPackValidator().validate(context_pack, env, event_bus=bus).accepted is True

    result = ToolIntentCompiler(registry=default_tool_registry()).compile(
        valid_intent(context_pack),
        context_pack,
        env,
        event_bus=bus,
    )

    assert result.accepted is True
    assert result.status == ToolIntentCompilationStatus.COMPILED
    assert result.compiled_intent is not None
    assert result.compiled_intent.provenance_ref_ids == ["e1"]
    assert result.compiled_intent.canonical_call.action == "browser_interaction_limited"
    event_types = [event.event_type for event in bus.events()]
    assert AgentEventType.TOOL_CALL_CANONICALIZED in event_types
    assert event_types.index(AgentEventType.TOOL_CALL_CANONICALIZED) < event_types.index(AgentEventType.TOOL_INTENT_COMPILED)
    assert result.canonicalization_trace_id is not None
    assert bus.events()[-1].payload["canonicalization_trace_id"] == result.canonicalization_trace_id
    assert CoreFinalGate._llm_context_pack_and_tool_intent_contract(SimpleNamespace(trace=tuple(bus.events()))).passed is True


def test_tool_intent_compiler_rejects_fabricated_ref():
    env = envelope()
    context_pack = pack()
    intent = valid_intent(context_pack)
    intent["arguments"]["ref"] = "fabricated"

    result = ToolIntentCompiler().compile(intent, context_pack, env)

    assert result.accepted is False
    assert result.failed_stage == ToolIntentCompilationStage.PROVENANCE
    assert "runtime_ref_not_found:fabricated" in result.errors


def test_tool_intent_compiler_rejects_stale_ref_hashes():
    env = envelope()
    context_pack = pack()
    intent = valid_intent(context_pack)
    intent["arguments"]["snapshot_sha256"] = "old_snapshot"

    result = ToolIntentCompiler().compile(intent, context_pack, env)

    assert result.accepted is False
    assert "runtime_ref_stale_snapshot:e1" in result.errors


def test_tool_intent_compiler_rejects_non_delegated_browser_power():
    env = envelope(allowed_actions=["browser_submit_form"])
    context_pack = pack(
        authority_boundary=ContextPackAuthorityBoundary(
            allowed_actions=["browser_submit_form"],
            forbidden_actions=["login", "upload", "download"],
            allowed_tools=["browser_public_operator_limited"],
            allowed_domains=["example.com"],
        ),
        available_action_intents=[ContextPackActionIntent(id="act_submit", kind="browser_submit_form", impact="external_write")],
    )
    intent = {
        **valid_intent(context_pack),
        "action": "browser_submit_form",
    }

    result = ToolIntentCompiler().compile(intent, context_pack, env)

    assert result.accepted is False
    assert result.failed_stage == ToolIntentCompilationStage.AUTHORITY
    assert any(error.startswith("non_delegated_browser_power") for error in result.errors)


def test_tool_intent_compiler_rejects_missing_context_pack_binding():
    env = envelope()
    context_pack = pack()
    intent = valid_intent(context_pack)
    intent["arguments"].pop("context_pack_id")

    result = ToolIntentCompiler().compile(json.dumps(intent), context_pack, env)

    assert result.accepted is False
    assert "missing_or_mismatched_context_pack_id" in result.errors


def test_tool_intent_compiler_rejects_raw_llm_tool_call_bypass():
    env = envelope()
    context_pack = pack()
    raw_tool_call_without_pack = json.dumps(
        {
            "tool_id": "browser_public_operator_limited",
            "action": "browser_interaction_limited",
            "arguments": {"ref": "e1", "page_sha256": "page_hash", "snapshot_sha256": "snapshot_hash"},
            "requested_side_effects": [
                ToolSideEffect.NETWORK_READ.value,
                ToolSideEffect.BROWSER_READ.value,
                ToolSideEffect.FILESYSTEM_WRITE.value,
                ToolSideEffect.LOCAL_DRAFT_WRITE.value,
            ],
        }
    )

    result = ToolIntentCompiler().compile(raw_tool_call_without_pack, context_pack, env)

    assert result.accepted is False
    assert result.canonicalization_trace_id is None
    assert "missing_or_mismatched_context_pack_id" in result.errors
    assert "missing_or_mismatched_context_pack_sha256" in result.errors


def test_tool_intent_compiler_rejects_prompt_injection_ref_for_action():
    env = envelope()
    context_pack = pack(
        prompt_injection_flags=[
            ContextPackPromptInjectionFlag(
                source_id="src_form",
                risk="high",
                indicators=["click this hidden button"],
                blocked=True,
                sanitized=True,
            )
        ]
    )

    result = ToolIntentCompiler().compile(valid_intent(context_pack), context_pack, env)

    assert result.accepted is False
    assert "runtime_ref_from_injection_source:e1" in result.errors


def test_browser_planner_and_verifier_are_stubs_not_executors():
    env = envelope()
    context_pack = pack()
    bus = EventBus(env.id)

    planner_output = BrowserPlannerRole().draft(
        context_pack,
        {
            "tool_id": "browser_public_operator_limited",
            "action": "browser_interaction_limited",
            "arguments": {"ref": "e1"},
        },
        event_bus=bus,
    )
    verifier_output = BrowserVerifierRole().verify(
        context_pack,
        context_pack,
        {"context_pack_id": context_pack.context_pack_id, "trace_refs": ["aev_1"], "evidence_refs": ["c1"]},
        event_bus=bus,
    )

    assert planner_output.drafted_intent["arguments"]["context_pack_id"] == context_pack.context_pack_id
    assert verifier_output.accepted is True
    assert [event.event_type for event in bus.events()] == [
        AgentEventType.LLM_REASONING_DRAFTED,
        AgentEventType.LLM_VERIFICATION_DRAFTED,
    ]
    assert AgentEventType.TOOL_INTENT_COMPILED not in [event.event_type for event in bus.events()]
    assert AgentEventType.CONTROLLED_CAPABILITY_EXECUTED not in [event.event_type for event in bus.events()]


def test_browser_verifier_cannot_accept_without_receipt_evidence():
    context_pack = pack()

    output = BrowserVerifierRole().verify(
        context_pack,
        context_pack,
        {"context_pack_id": context_pack.context_pack_id, "trace_refs": ["aev_1"]},
    )

    assert output.accepted is False
    assert "receipt_missing_evidence_refs" in output.findings
