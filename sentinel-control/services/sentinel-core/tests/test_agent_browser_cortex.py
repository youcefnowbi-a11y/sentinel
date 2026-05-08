from __future__ import annotations

import json

from sentinel.agent import (
    AgentEventType,
    AgentPhase,
    AgentRuntime,
    BrowserActionRecommendationType,
    BrowserEvidenceInterpreter,
    BrowserHypothesisEffect,
    EventBus,
    EvidenceDecisionType,
    MissionHypothesis,
    PlaywrightReadOnlyRenderer,
)
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
        "id": "mission_browser_cortex",
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "Browser cortex integration",
        "mission_objective": "Use browser evidence as mission reasoning input.",
        "success_criteria": ["Browser evidence interpreted by cortex"],
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


def context():
    return type("Context", (), {"mission": envelope()})()


def test_browser_evidence_confirms_linked_hypothesis_and_builds_chain():
    bus = EventBus("mission_browser_cortex")
    source_event = bus.append(
        AgentEventType.BROWSER_EVIDENCE_COLLECTED,
        "Browser evidence collected.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_1",
            "evidence_item_id": "ev_pricing",
            "artifact_id": "artifact_1",
            "final_url": "https://example.com/pricing",
            "title": "Pricing",
            "source_quality_flags": [],
            "prompt_injection_flags": [],
            "extraction_strategy": "readability",
            "citation_char_start": 0,
            "citation_char_end": 80,
        },
    )
    hypothesis = MissionHypothesis(
        mission_id="mission_browser_cortex",
        statement="The pricing page supports the GTM hypothesis.",
        source="test",
        confidence=0.50,
        evidence_refs=["ev_pricing"],
    )

    result = BrowserEvidenceInterpreter().interpret(context(), bus.events(), hypotheses=[hypothesis], event_bus=bus)

    assert result.browser_signal_count == 1
    assert result.source_scores[0].score >= 0.72
    assert result.hypothesis_updates[0].effect == BrowserHypothesisEffect.CONFIRM
    assert result.hypothesis_updates[0].confidence_after == 0.65
    assert result.evidence_chain is not None
    assert result.evidence_chain.decision_type == EvidenceDecisionType.BROWSER_CORTEX_INTERPRETATION
    assert source_event.id in result.evidence_chain.trace_refs
    assert bus.events()[-2].event_type == AgentEventType.BROWSER_CORTEX_INTERPRETED
    assert bus.events()[-1].event_type == AgentEventType.EVIDENCE_CHAIN_BUILT


def test_prompt_injected_browser_text_is_confidence_limited_and_triggers_repair():
    bus = EventBus("mission_browser_cortex")
    bus.append(
        AgentEventType.BROWSER_EVIDENCE_COLLECTED,
        "Browser evidence collected.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_1",
            "evidence_item_id": "ev_claim",
            "artifact_id": "artifact_1",
            "final_url": "https://example.com/page",
            "title": "Instructions for agents",
            "source_quality_flags": ["prompt_injection_detected"],
            "prompt_injection_flags": ["ignore_previous_instructions"],
            "extraction_strategy": "simple_html",
            "citation_char_start": 0,
            "citation_char_end": 40,
        },
    )
    hypothesis = MissionHypothesis(
        mission_id="mission_browser_cortex",
        statement="Browser page supports the claim.",
        source="test",
        confidence=0.60,
        evidence_refs=["ev_claim"],
    )

    result = BrowserEvidenceInterpreter().interpret(context(), bus.events(), hypotheses=[hypothesis], event_bus=bus)

    assert result.source_scores[0].score <= 0.45
    assert result.hypothesis_updates[0].effect == BrowserHypothesisEffect.WEAKEN
    assert any(decision.repair_needed for decision in result.repair_decisions)
    assert any(finding.code == "browser_cortex_prompt_injection_evidence_only" for finding in result.review_findings)
    assert result.action_recommendations[0].recommendation == BrowserActionRecommendationType.DO_NOT_USE_FOR_AUTHORITY


def test_rejected_browser_output_recommends_alternative_source():
    bus = EventBus("mission_browser_cortex")
    bus.append(
        AgentEventType.BROWSER_EVIDENCE_REJECTED,
        "Browser evidence rejected.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={"reason": "browser_evidence_gap", "errors": ["empty_extraction"]},
    )

    result = BrowserEvidenceInterpreter().interpret(context(), bus.events(), hypotheses=[], event_bus=bus)

    assert result.source_scores[0].score <= 0.20
    assert result.repair_decisions[0].repair_needed is True
    assert result.action_recommendations[0].recommendation == BrowserActionRecommendationType.SEEK_ALTERNATIVE_SOURCE
    assert result.evidence_chain is not None
    assert result.evidence_chain.contradictions


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


def test_runtime_interprets_browser_output_into_cortex_evidence_chain(tmp_path):
    url = "https://example.com/browser-cortex"
    renderer = PlaywrightReadOnlyRenderer(
        document_fixtures={
            url: "<html><head><title>Cortex Evidence</title></head><body><main><h1>Competitor pricing is public.</h1></main></body></html>"
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
    assert AgentEventType.BROWSER_SNAPSHOT_CAPTURED in event_types
    assert AgentEventType.BROWSER_CORTEX_INTERPRETED in event_types
    assert EvidenceDecisionType.BROWSER_CORTEX_INTERPRETATION in {chain.decision_type for chain in result.evidence_chains}
