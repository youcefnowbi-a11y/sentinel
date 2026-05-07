from __future__ import annotations

from sentinel.agent import (
    AgentCountRoute,
    AgentEventType,
    AgentOutputContract,
    AgentRoleAssignment,
    AgentRolePurpose,
    AgentSocietyManager,
    AgentSocietyPlan,
    AgentSocietyPlanStatus,
    BrainMode,
    EventBus,
    MissionEntropyEstimate,
)
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


SAFE_ACTIONS = ["create_markdown_file", "export_json", "write_trace"]


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_p5d",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P5D agent society fixture",
        "mission_objective": "Create advisory role plan.",
        "success_criteria": ["Plan exists"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer", "browser_public_read"],
        "allowed_actions": [*SAFE_ACTIONS, "browser_read_public_page"],
        "forbidden_actions": ["send_email", "run_shell_command", "credential_access", "payment"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 50,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def entropy(env: MissionAuthorityEnvelope, **overrides) -> MissionEntropyEstimate:
    data = {
        "mission_id": env.id,
        "mission_entropy": 0.2,
        "domain_breadth": 0.2,
        "evidence_gap": 0.2,
        "parallelizability": 0.2,
        "impact_level": 0.2,
        "tool_uncertainty": 0.2,
        "budget_pressure": 0.15,
        "entropy_band": "low",
    }
    data.update(overrides)
    return MissionEntropyEstimate(**data)


def count_route(env: MissionAuthorityEnvelope, ent: MissionEntropyEstimate, count: int, mode: BrainMode, **overrides) -> AgentCountRoute:
    data = {
        "mission_id": env.id,
        "entropy_estimate_id": ent.id,
        "recommended_agent_count": count,
        "brain_mode": mode,
        "max_parallel_agents": count,
        "agent_budget": count,
        "reason": f"test_count={count}",
        "entropy_band": ent.entropy_band,
    }
    data.update(overrides)
    return AgentCountRoute(**data)


def plan(env: MissionAuthorityEnvelope, route: AgentCountRoute, ent: MissionEntropyEstimate, **kwargs) -> AgentSocietyPlan:
    return AgentSocietyManager().plan(env, route, ent, **kwargs)


def role_names(result: AgentSocietyPlan) -> set[str]:
    return {role.role for role in result.roles}


def test_low_entropy_route_creates_one_agent_plan_and_trace():
    env = envelope()
    ent = entropy(env, mission_entropy=0.1, entropy_band="low")
    route = count_route(env, ent, 1, BrainMode.FAST_BRAIN)
    bus = EventBus(env.id)

    result = plan(env, route, ent, event_bus=bus)

    assert result.status == AgentSocietyPlanStatus.PLANNED
    assert result.agent_count == 1
    assert result.roles[0].role == "planner_agent"
    assert result.roles[0].first_principles_purpose == [AgentRolePurpose.EXPLORATION]
    assert AgentEventType.AGENT_ROLE_ASSIGNED in [event.event_type for event in bus.events()]
    assert AgentEventType.AGENT_SOCIETY_PLANNED in [event.event_type for event in bus.events()]


def test_medium_entropy_route_creates_three_to_five_role_plan_with_aggregator():
    env = envelope()
    ent = entropy(env, mission_entropy=0.4, entropy_band="medium")
    route = count_route(env, ent, 4, BrainMode.SMALL_SOCIETY)

    result = plan(env, route, ent)

    assert 3 <= result.agent_count <= 5
    assert "aggregator_agent" in role_names(result)


def test_high_entropy_route_includes_verifier_skeptic_and_aggregator():
    env = envelope()
    ent = entropy(env, mission_entropy=0.65, entropy_band="high")
    route = count_route(env, ent, 8, BrainMode.SLOW_BRAIN)

    result = plan(env, route, ent)

    names = role_names(result)
    assert {"verifier_agent", "skeptic_agent", "aggregator_agent"}.issubset(names)


def test_very_high_entropy_respects_max_parallel_agents():
    env = envelope()
    ent = entropy(env, mission_entropy=0.82, entropy_band="very_high")
    route = count_route(env, ent, 60, BrainMode.VERY_HIGH_SOCIETY, max_parallel_agents=22, agent_budget=22)

    result = plan(env, route, ent)

    assert result.agent_count == 22
    assert result.agent_count <= result.max_parallel_agents
    assert "context_compression_agent" in role_names(result)


def test_budget_pressure_adds_cost_control_or_reduces_role_allocation():
    env = envelope()
    ent = entropy(env, mission_entropy=0.7, entropy_band="high", budget_pressure=0.85)
    route = count_route(env, ent, 8, BrainMode.SLOW_BRAIN, max_parallel_agents=6, agent_budget=6)

    result = plan(env, route, ent)

    assert result.agent_count <= route.recommended_agent_count
    assert "cost_control_agent" in role_names(result)


def test_every_role_receives_only_subset_of_mission_authority():
    env = envelope()
    ent = entropy(env, mission_entropy=0.7, entropy_band="high")
    route = count_route(env, ent, 8, BrainMode.SLOW_BRAIN)

    result = plan(env, route, ent)

    allowed_tools = set(env.allowed_tools)
    allowed_actions = set(env.allowed_actions)
    for role in result.roles:
        assert set(role.allowed_tools).issubset(allowed_tools)
        assert set(role.allowed_actions).issubset(allowed_actions)


def test_forbidden_tools_and_actions_never_appear_in_roles():
    env = envelope(
        allowed_tools=["safe_file_writer", "browser_public_read"],
        allowed_actions=[*SAFE_ACTIONS, "browser_read_public_page"],
        forbidden_actions=["send_email", "browser_form_submit", "run_shell_command"],
    )
    ent = entropy(env, mission_entropy=0.7, entropy_band="high")
    route = count_route(env, ent, 8, BrainMode.SLOW_BRAIN)

    result = plan(env, route, ent)

    for role in result.roles:
        assert "send_email" not in role.allowed_actions
        assert "browser_form_submit" not in role.allowed_actions
        assert "run_shell_command" not in role.allowed_actions
        assert "email_sender" not in role.allowed_tools


def test_each_role_maps_to_first_principles_purpose():
    env = envelope()
    ent = entropy(env, mission_entropy=0.82, entropy_band="very_high", budget_pressure=0.85, tool_uncertainty=0.7)
    route = count_route(env, ent, 10, BrainMode.VERY_HIGH_SOCIETY)

    result = plan(env, route, ent, blocked_tools=["email_sender"], uncertain_path_detected=True)

    allowed_purposes = {item.value for item in AgentRolePurpose}
    for role in result.roles:
        assert role.first_principles_purpose
        assert {purpose.value for purpose in role.first_principles_purpose}.issubset(allowed_purposes)


def test_missing_aggregator_in_multi_role_plan_is_rejected():
    env = envelope()
    roles = [
        AgentRoleAssignment(
            role="planner_agent",
            mission_id=env.id,
            scope="Plan.",
            first_principles_purpose=[AgentRolePurpose.EXPLORATION],
            allowed_tools=["safe_file_writer"],
            allowed_actions=["create_markdown_file"],
            context_budget=2000,
            output_contract=AgentOutputContract(required_sections=["summary"]),
            timeout=60,
        ),
        AgentRoleAssignment(
            role="verifier_agent",
            mission_id=env.id,
            scope="Verify.",
            first_principles_purpose=[AgentRolePurpose.VERIFICATION],
            allowed_tools=["safe_file_writer"],
            allowed_actions=["create_markdown_file"],
            context_budget=2000,
            output_contract=AgentOutputContract(required_sections=["summary"]),
            timeout=60,
        ),
    ]
    bad_plan = AgentSocietyPlan(
        mission_id=env.id,
        status=AgentSocietyPlanStatus.PLANNED,
        agent_count=2,
        max_parallel_agents=2,
        roles=roles,
    )

    result = AgentSocietyManager().validate_plan(bad_plan)

    assert result.status == AgentSocietyPlanStatus.REJECTED
    assert "multi_role_plan_missing_aggregator" in result.errors


def test_agent_society_manager_does_not_execute_or_spawn_agents():
    env = envelope()
    ent = entropy(env, mission_entropy=0.65, entropy_band="high")
    route = count_route(env, ent, 8, BrainMode.SLOW_BRAIN)

    result = plan(env, route, ent)

    assert result.advisory_only is True
    assert result.agent_spawning is False
    assert result.runtime_multi_agent_execution is False
    assert all(role.authority_level == "mission_envelope_subset" for role in result.roles)


def test_agent_society_manager_does_not_expand_authority():
    env = envelope(
        allowed_tools=["safe_file_writer"],
        allowed_actions=["create_markdown_file"],
        allowed_paths=["data/generated_projects"],
    )
    before = env.model_dump(mode="json")
    ent = entropy(env, mission_entropy=0.82, entropy_band="very_high", tool_uncertainty=0.8)
    route = count_route(env, ent, 10, BrainMode.VERY_HIGH_SOCIETY)

    result = plan(env, route, ent, blocked_tools=["browser_tool"], unavailable_capabilities=["desktop_control"])

    assert env.model_dump(mode="json") == before
    assert result.authority_expansion is False
    for role in result.roles:
        assert set(role.allowed_tools).issubset({"safe_file_writer"})
        assert set(role.allowed_actions).issubset({"create_markdown_file"})
