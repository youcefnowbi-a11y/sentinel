from __future__ import annotations

from sentinel.agent import AgentEventType, EventBus, MissionEntropyEstimator
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


SAFE_ACTIONS = ["create_markdown_file", "export_json", "write_trace"]


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_p5b",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P5B entropy fixture",
        "mission_objective": "Create a bounded local summary from provided evidence.",
        "success_criteria": ["Summary artifact exists"],
        "mode": MissionMode.SAFE,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer"],
        "allowed_actions": SAFE_ACTIONS,
        "forbidden_actions": ["send_email", "run_shell_command", "credential_access", "payment"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 30,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def estimate(env: MissionAuthorityEnvelope, **kwargs):
    bus = kwargs.pop("event_bus", None)
    return MissionEntropyEstimator().estimate(env, event_bus=bus, **kwargs)


def test_mission_entropy_low_fixture_emits_trace_event():
    env = envelope()
    bus = EventBus(env.id)

    result = estimate(env, evidence_refs=["ev_local_summary"], selected_tools=["safe_file_writer"], event_bus=bus)

    assert result.entropy_band == "low"
    assert result.mission_entropy < 0.25
    assert result.advisory_only is True
    assert result.authority_expansion is False
    assert result.trace_refs
    event = bus.events()[0]
    assert event.event_type == AgentEventType.MISSION_ENTROPY_ESTIMATED
    assert event.payload["mission_entropy"] == result.mission_entropy
    assert event.payload["domain_breadth"] == result.domain_breadth
    assert event.payload["evidence_gap"] == result.evidence_gap
    assert event.payload["parallelizability"] == result.parallelizability
    assert event.payload["impact_level"] == result.impact_level
    assert event.payload["tool_uncertainty"] == result.tool_uncertainty
    assert event.payload["budget_pressure"] == result.budget_pressure


def test_mission_entropy_medium_fixture():
    env = envelope(
        mission_title="Compare competitor sources",
        mission_objective="Compare multiple public web sources and create a market research summary.",
        success_criteria=["Compare competitors", "Cite sources"],
        mode=MissionMode.POWER,
        allowed_systems=["local_workspace", "public_web"],
        allowed_tools=["safe_file_writer", "browser_public_read"],
        allowed_actions=[*SAFE_ACTIONS, "browser_read_public_page"],
        allowed_domains=["example.com"],
        max_actions=20,
    )

    result = estimate(env, evidence_refs=["ev_one_source"], selected_tools=["safe_file_writer", "browser_public_read"])

    assert result.entropy_band == "medium"
    assert 0.25 <= result.mission_entropy < 0.50
    assert result.parallelizability >= 0.30


def test_mission_entropy_high_fixture():
    env = envelope(
        mission_title="Deep research audit across browser code security market and data",
        mission_objective="Research, verify, compare, and audit many sources before producing a multi-domain plan.",
        success_criteria=["Verify claims", "Compare sources", "Audit risks", "Produce plan"],
        mode=MissionMode.POWER,
        allowed_systems=["local_workspace", "public_web"],
        allowed_tools=["safe_file_writer", "browser_public_read", "browser_public_form_submit"],
        allowed_actions=[*SAFE_ACTIONS, "browser_read_public_page", "browser_form_submit", "create_watchlist"],
        allowed_domains=["example.com"],
        browser_v3_authority_grants=[{"id": "grant_form", "authority_class": "browser_form_submit", "allowed_domains": ["example.com"]}],
        max_actions=20,
        risk_appetite_score=75,
    )

    result = estimate(
        env,
        evidence_refs=["ev_seed"],
        open_questions=["Which source is reliable?", "Which risk blocks execution?"],
        selected_tools=["safe_file_writer"],
        blocked_tools=["email_sender"],
    )

    assert result.entropy_band == "high"
    assert 0.50 <= result.mission_entropy < 0.75
    assert result.evidence_gap >= 0.60
    assert result.impact_level >= 0.50


def test_mission_entropy_very_high_fixture_and_budget_pressure():
    env = envelope(
        mission_title="Extreme multi-domain production research with payment credential account and email risks",
        mission_objective="Compare many competitors, scan multiple public sources, validate unknown claims, and plan production account changes.",
        success_criteria=["Verify claims", "Compare competitors", "Audit payment risk", "Audit credentials", "Plan channels"],
        mode=MissionMode.POWER,
        allowed_systems=["local_workspace", "public_web"],
        allowed_tools=["safe_file_writer", "browser_public_read", "browser_public_form_submit", "email_draft_tool"],
        allowed_actions=[*SAFE_ACTIONS, "browser_read_public_page", "browser_form_submit", "generate_outreach_drafts_without_sending"],
        allowed_domains=["example.com"],
        allowed_accounts=["acct_demo"],
        browser_v3_authority_grants=[{"id": "grant_form", "authority_class": "browser_form_submit", "allowed_domains": ["example.com"]}],
        max_actions=5,
        max_cost_usd=0.10,
        max_recipients=20,
        risk_appetite_score=90,
    )

    result = estimate(
        env,
        open_questions=["What proof is missing?", "Which channel is safe?", "Which claim is false?"],
        selected_tools=["safe_file_writer"],
        blocked_tools=["email_sender", "payment_tool"],
        unavailable_capabilities=["credential_access"],
    )

    assert result.entropy_band == "very_high"
    assert result.mission_entropy >= 0.75
    assert result.budget_pressure >= 0.85
    assert result.tool_uncertainty >= 0.40


def test_mission_entropy_estimator_does_not_expand_authority():
    env = envelope(
        allowed_systems=["local_workspace"],
        allowed_tools=["safe_file_writer"],
        allowed_actions=SAFE_ACTIONS,
        allowed_paths=["data/generated_projects"],
        allowed_domains=[],
        allowed_accounts=[],
    )
    before = env.model_dump(mode="json")

    result = estimate(
        env,
        user_input={"idea": "Need browser email payment desktop and shell access"},
        blocked_tools=["browser_tool", "email_sender", "shell_runner"],
        unavailable_capabilities=["desktop_control"],
    )

    assert env.model_dump(mode="json") == before
    assert result.authority_expansion is False
    assert result.advisory_only is True
    assert not hasattr(result, "allowed_tools")
    assert not hasattr(result, "allowed_actions")
    assert not hasattr(result, "allowed_paths")
