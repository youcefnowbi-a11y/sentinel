from __future__ import annotations

from types import SimpleNamespace

from sentinel.agent import (
    AgentEventType,
    AgentPhase,
    ContextPack,
    ContextPackActionIntent,
    ContextPackAssembler,
    ContextPackAuthorityBoundary,
    ContextPackBrowserEvidenceSummary,
    ContextPackCitation,
    ContextPackHypothesis,
    ContextPackPromptInjectionFlag,
    ContextPackSourceQualityFlag,
    ContextPackStableRef,
    ContextPackValidationResult,
    ContextPackValidator,
    EventBus,
)
from sentinel.agent.final_gate import CoreFinalGate
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


MISSION_ID = "mission_p3y_context"


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "id": MISSION_ID,
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "P3Y ContextPack",
        "mission_objective": "Use browser evidence through a bounded LLM context contract.",
        "success_criteria": ["ContextPack validates"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace", "public_web"],
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


def valid_pack(**overrides) -> ContextPack:
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
                source_id="src_pricing",
                selector="accessibility_ref:e1",
                digest="ref_digest",
                page_sha256="page_hash",
                snapshot_sha256="snapshot_hash",
            )
        ],
        "citations": [
            ContextPackCitation(
                id="c1",
                source_id="src_pricing",
                stable_ref_id="e1",
                support_level="full",
                excerpt="Pricing is publicly available.",
                digest="citation_digest",
            )
        ],
        "source_quality_flags": [
            ContextPackSourceQualityFlag(source_id="src_pricing", flags=["official_primary"], derived_score=0.91)
        ],
        "browser_evidence_summaries": [
            ContextPackBrowserEvidenceSummary(
                source_id="src_pricing",
                summary="Pricing page says pricing is public.",
                summary_hash="summary_hash",
                stable_ref_ids=["e1"],
            )
        ],
        "verified_hypotheses": [
            ContextPackHypothesis(
                id="hyp_1",
                statement="The pricing page supports public pricing evidence.",
                status="verified",
                confidence=0.86,
                citation_ids=["c1"],
            )
        ],
        "available_action_intents": [
            ContextPackActionIntent(id="act_browser", kind="browser_interaction_limited", impact="local_page_state")
        ],
    }
    data.update(overrides)
    return ContextPack(**data)


def test_context_pack_validator_accepts_proof_linked_pack_and_traces():
    env = envelope()
    pack = valid_pack()
    bus = EventBus(env.id)

    result = ContextPackValidator().validate(pack, env, event_bus=bus)

    assert isinstance(result, ContextPackValidationResult)
    assert result.accepted is True
    assert result.errors == []
    assert pack.context_pack_sha256
    assert bus.events()[-1].event_type == AgentEventType.CONTEXT_PACK_VALIDATED
    assert bus.events()[-1].payload["context_pack_id"] == pack.context_pack_id


def test_context_pack_rejects_verified_hypothesis_without_citation():
    env = envelope()
    pack = valid_pack(
        verified_hypotheses=[
            ContextPackHypothesis(
                id="hyp_bad",
                statement="Unsupported claim.",
                status="verified",
                confidence=0.9,
                citation_ids=[],
            )
        ]
    )

    result = ContextPackValidator().validate(pack, env)

    assert result.accepted is False
    assert "context_pack_verified_hypothesis_missing_citation:hyp_bad" in result.errors


def test_context_pack_rejects_prompt_injection_source_as_verified_hypothesis_support():
    env = envelope()
    pack = valid_pack(
        prompt_injection_flags=[
            ContextPackPromptInjectionFlag(
                source_id="src_pricing",
                risk="high",
                indicators=["ignore_previous_instructions"],
                blocked=True,
                sanitized=True,
            )
        ]
    )

    result = ContextPackValidator().validate(pack, env)

    assert result.accepted is False
    assert any("context_pack_verified_hypothesis_uses_prompt_injection_source" in error for error in result.errors)


def test_context_pack_rejects_mission_goal_mismatch():
    env = envelope()
    pack = valid_pack(mission_goal="Different objective")

    result = ContextPackValidator().validate(pack, env)

    assert result.accepted is False
    assert "context_pack_mission_goal_mismatch" in result.errors


def test_context_pack_cannot_expand_mission_authority():
    env = envelope()
    pack = valid_pack(
        authority_boundary=ContextPackAuthorityBoundary(
            allowed_actions=[*env.allowed_actions, "browser_download_quarantine"],
            forbidden_actions=list(env.forbidden_actions),
            allowed_tools=list(env.allowed_tools),
            allowed_domains=list(env.allowed_domains),
        ),
        available_action_intents=[
            ContextPackActionIntent(id="act_browser", kind="browser_interaction_limited", impact="local_page_state"),
            ContextPackActionIntent(id="act_download", kind="browser_download_quarantine", impact="file_transfer"),
        ],
    )

    result = ContextPackValidator().validate(pack, env)

    assert result.accepted is False
    assert "context_pack_allowed_actions_mismatch" in result.errors
    assert any("context_pack_action_intents_outside_authority:browser_download_quarantine" in error for error in result.errors)


def test_context_pack_rejects_citation_without_stable_runtime_ref():
    env = envelope()
    pack = valid_pack(
        citations=[
            ContextPackCitation(
                id="c_missing_ref",
                source_id="src_pricing",
                stable_ref_id="missing_ref",
                support_level="full",
                excerpt="Pricing is publicly available.",
                digest="citation_digest",
            )
        ],
        verified_hypotheses=[
            ContextPackHypothesis(
                id="hyp_1",
                statement="The pricing page supports public pricing evidence.",
                status="verified",
                confidence=0.86,
                citation_ids=["c_missing_ref"],
            )
        ],
    )

    result = ContextPackValidator().validate(pack, env)

    assert result.accepted is False
    assert "context_pack_citation_unknown_stable_ref:c_missing_ref:missing_ref" in result.errors


def test_context_pack_assembler_never_includes_raw_browser_text():
    env = envelope()
    context = SimpleNamespace(mission=env, user_input={"tool_calls": ["raw should not enter pack"], "note": "keep"})
    bus = EventBus(env.id)
    bus.append(
        AgentEventType.BROWSER_EVIDENCE_COLLECTED,
        "Browser evidence collected.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_1",
            "evidence_item_id": "src_page",
            "title": "Useful page",
            "final_url": "https://example.com",
            "extracted_text": "This raw text must stay out of the ContextPack.",
        },
    )

    pack = ContextPackAssembler().assemble(context, bus.events())

    assert pack.current_state.facts == {"note": "keep"}
    assert all("raw text must stay out" not in summary.summary for summary in pack.browser_evidence_summaries)
    assert pack.browser_evidence_summaries[0].summary == "Useful page"


def test_final_gate_rejects_compiled_intent_without_validated_context_pack():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.TOOL_INTENT_COMPILED,
        "Forged compiled intent.",
        phase_before=AgentPhase.TOOL_SELECTING,
        phase_after=AgentPhase.TOOL_SELECTING,
        payload={
            "accepted": True,
            "context_pack_id": "cpk_missing000000",
            "context_pack_sha256": "a" * 64,
            "canonical_hash": "b" * 64,
            "compilation_hash": "c" * 64,
        },
    )

    check = CoreFinalGate._llm_context_pack_and_tool_intent_contract(SimpleNamespace(trace=tuple(bus.events())))

    assert check.passed is False
    assert any("tool_intent_compiled_without_validated_context_pack" in error for error in check.details["errors"])


def test_final_gate_rejects_forged_validated_context_pack_without_assembly():
    bus = EventBus(MISSION_ID)
    bus.append(
        AgentEventType.CONTEXT_PACK_VALIDATED,
        "Forged validation event.",
        phase_before=AgentPhase.CONTEXT_BUILDING,
        phase_after=AgentPhase.CONTEXT_BUILDING,
        payload={
            "accepted": True,
            "context_pack_id": "cpk_forged000000",
            "context_pack_sha256": "a" * 64,
            "errors": [],
            "warnings": [],
        },
    )

    check = CoreFinalGate._llm_context_pack_and_tool_intent_contract(SimpleNamespace(trace=tuple(bus.events())))

    assert check.passed is False
    assert any("context_pack_validated_without_assembly:cpk_forged000000" in error for error in check.details["errors"])
