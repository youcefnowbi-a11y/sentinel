from __future__ import annotations

from sentinel.agent import AgentEventType, ContextBuilder, EventBus, ToolSelectionStatus
from sentinel.agent.capability_selector import CapabilitySelector
from sentinel.agent.method_selector import MethodSelector
from sentinel.agent.models import CapabilityNeed
from sentinel.agent.review_loop import ReviewLoop
from sentinel.agent.tool_selector import ToolSelector
from sentinel.capabilities import default_tool_registry
from sentinel.mission import MissionAction, MissionAuthorityEnvelope, MissionPlan, MissionPlanStep
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
        "mission_title": "P1C tool selection test",
        "mission_objective": "Verify AgentRuntime tool selection stays declarative.",
        "success_criteria": ["Decision trace exists"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer"],
        "allowed_actions": SAFE_ACTIONS,
        "forbidden_actions": ["send_email", "run_shell_command", "browser_submit_form", "credential_access"],
        "allowed_paths": ["data/generated_projects"],
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def select_for(env: MissionAuthorityEnvelope, needs: list[CapabilityNeed]):
    context = ContextBuilder().build(env, evidence_refs=["ev_001"])
    bus = EventBus(env.id)
    result = ToolSelector(default_tool_registry()).select(context, needs, event_bus=bus)
    return result, bus


def gtm_needs(env: MissionAuthorityEnvelope) -> list[CapabilityNeed]:
    context = ContextBuilder().build(env, evidence_refs=["ev_001"])
    methods = MethodSelector().select(context)
    return CapabilitySelector(registry=default_tool_registry()).select(context, methods)


def test_gtm_tool_selection_selects_safe_writer_and_reports_future_candidates():
    env = envelope()
    result, bus = select_for(env, gtm_needs(env))
    event_types = [event.event_type for event in bus.events()]

    assert "safe_file_writer" in result.selected_tools
    assert "browser_readonly_candidate" in result.candidate_tools
    assert "image_generation_candidate" in result.candidate_tools
    assert "local_workspace_write" not in result.unavailable_capabilities
    assert "browser_research" not in result.missing_capabilities
    assert "image_generation" not in result.missing_capabilities
    assert AgentEventType.TOOL_POLICY_DECIDED in event_types
    assert AgentEventType.TOOLS_SELECTED in event_types
    assert AgentEventType.WORKER_STARTED not in event_types

    safe_decision = next(
        decision
        for decision in result.decisions
        if decision.candidate_tool_id == "safe_file_writer" and decision.capability_name == "gtm_pack_generation"
    )
    assert safe_decision.decision == ToolSelectionStatus.ELIGIBLE_FOR_SAFE_WORKER
    assert safe_decision.trace_id is not None


def test_email_send_candidate_is_blocked_not_selected():
    env = envelope(allowed_tools=["email_send_high_risk_candidate"], allowed_actions=[*SAFE_ACTIONS, "send_email"])
    need = CapabilityNeed(name="email_send", reason="Outbound send must remain blocked.", required=True, available=True)

    result, _bus = select_for(env, [need])

    assert "email_send_high_risk_candidate" in result.blocked_tools
    assert "email_send_high_risk_candidate" not in result.selected_tools
    assert result.missing_capabilities == ["email_send"]
    decision = result.decisions[0]
    assert decision.decision == ToolSelectionStatus.BLOCKED
    assert decision.reason == "black_zone_side_effect"


def test_shell_tool_is_blocked_even_in_power_mode():
    env = envelope(
        mode=MissionMode.POWER,
        allowed_tools=["shell_critical_blocked"],
        allowed_actions=[*SAFE_ACTIONS, "run_shell_command"],
    )
    need = CapabilityNeed(name="shell_execution", reason="Shell must remain blocked.", required=True, available=True)

    result, _bus = select_for(env, [need])

    assert "shell_critical_blocked" in result.blocked_tools
    assert "shell_critical_blocked" not in result.selected_tools
    assert result.decisions[0].decision == ToolSelectionStatus.BLOCKED
    assert result.decisions[0].reason == "black_zone_side_effect"


def test_approved_tool_not_in_mission_authority_is_unavailable():
    env = envelope(allowed_tools=[], allowed_actions=SAFE_ACTIONS)
    need = CapabilityNeed(name="local_markdown_write", reason="Needs scoped markdown write.", required=True, available=True)

    result, _bus = select_for(env, [need])

    assert result.selected_tools == []
    assert result.missing_capabilities == ["local_markdown_write"]
    assert all(decision.decision == ToolSelectionStatus.UNAVAILABLE for decision in result.decisions)
    assert {decision.reason for decision in result.decisions} == {"tool_not_granted_by_mission_authority"}


def test_approved_manifest_with_action_outside_authority_is_unavailable():
    env = envelope(allowed_tools=["safe_file_writer"], allowed_actions=["create_project_folder"])
    need = CapabilityNeed(name="local_markdown_write", reason="Needs markdown action.", required=True, available=True)

    result, _bus = select_for(env, [need])

    assert result.selected_tools == []
    assert result.missing_capabilities == ["local_markdown_write"]
    safe_file_decision = next(decision for decision in result.decisions if decision.candidate_tool_id == "safe_file_writer")
    assert safe_file_decision.decision == ToolSelectionStatus.UNAVAILABLE
    assert safe_file_decision.reason == "action_not_granted_by_mission_authority"


def test_candidate_manifest_cannot_become_selected_tool():
    env = envelope(
        allowed_tools=["browser_readonly_candidate"],
        allowed_actions=[*SAFE_ACTIONS, "browser_read_public_page"],
    )
    need = CapabilityNeed(name="browser_research", reason="Read-only browser is future candidate.", required=False, available=False)

    result, _bus = select_for(env, [need])

    assert "browser_readonly_candidate" in result.candidate_tools
    assert "browser_readonly_candidate" not in result.selected_tools
    assert result.missing_capabilities == []
    assert result.decisions[0].decision == ToolSelectionStatus.CANDIDATE


def test_required_unavailable_tool_creates_critical_review_finding():
    env = envelope(allowed_tools=[], allowed_actions=SAFE_ACTIONS)
    need = CapabilityNeed(name="local_markdown_write", reason="Needs markdown.", required=True, available=True)
    result, _bus = select_for(env, [need])

    findings = ReviewLoop().review_tool_selection([need], result)

    assert [finding.code for finding in findings] == ["required_tool_unavailable"]
    assert findings[0].severity == "critical"
    assert findings[0].trace_refs


def test_plan_review_rejects_tools_not_selected_by_firewall():
    env = envelope()
    allowed_need = CapabilityNeed(name="gtm_pack_generation", reason="Needs GTM pack.", required=True, available=True)
    result, _bus = select_for(env, [allowed_need])
    plan = MissionPlan(
        mission_id=env.id,
        steps=[
            MissionPlanStep(
                id="step_001",
                action=MissionAction(
                    mission_id=env.id,
                    action_type="send_email",
                    tool="email_send_high_risk_candidate",
                    intent="Try to bypass selected tools.",
                    expected_output="Email sent.",
                ),
            )
        ],
    )

    findings = ReviewLoop().review_plan(ContextBuilder().build(env), plan, [allowed_need], tool_selection=result)

    assert [finding.code for finding in findings] == ["plan_uses_unselected_tool"]
    assert findings[0].severity == "critical"
