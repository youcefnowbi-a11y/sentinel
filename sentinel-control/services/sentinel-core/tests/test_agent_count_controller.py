from __future__ import annotations

from sentinel.agent import AgentCountController, AgentEventType, BrainMode, EventBus, MissionEntropyEstimate
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_p5c",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P5C agent count fixture",
        "mission_objective": "Route advisory agent count.",
        "success_criteria": ["Route exists"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer"],
        "allowed_actions": ["create_markdown_file", "write_trace"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 50,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def estimate(env: MissionAuthorityEnvelope, **overrides) -> MissionEntropyEstimate:
    data = {
        "mission_id": env.id,
        "mission_entropy": 0.1,
        "domain_breadth": 0.1,
        "evidence_gap": 0.1,
        "parallelizability": 0.1,
        "impact_level": 0.1,
        "tool_uncertainty": 0.1,
        "budget_pressure": 0.15,
        "entropy_band": "low",
    }
    data.update(overrides)
    return MissionEntropyEstimate(**data)


def route(env: MissionAuthorityEnvelope, ent: MissionEntropyEstimate, **kwargs):
    bus = kwargs.pop("event_bus", None)
    return AgentCountController().route(env, ent, event_bus=bus, **kwargs)


def test_agent_count_routes_one_agent_for_low_entropy_and_emits_trace():
    env = envelope()
    ent = estimate(env, mission_entropy=0.12, entropy_band="low")
    bus = EventBus(env.id)

    result = route(env, ent, event_bus=bus)

    assert result.recommended_agent_count == 1
    assert result.brain_mode == BrainMode.FAST_BRAIN
    assert result.max_parallel_agents == 1
    assert result.agent_budget == 1
    assert result.advisory_only is True
    assert result.agent_spawning is False
    assert result.runtime_multi_agent_execution is False
    assert bus.events()[0].event_type == AgentEventType.AGENT_COUNT_ROUTED


def test_agent_count_routes_three_to_five_for_medium_entropy():
    env = envelope()
    ent = estimate(env, mission_entropy=0.38, parallelizability=0.45, entropy_band="medium")

    result = route(env, ent)

    assert 3 <= result.recommended_agent_count <= 5
    assert result.brain_mode == BrainMode.SMALL_SOCIETY


def test_agent_count_routes_eight_to_twenty_for_high_entropy():
    env = envelope()
    ent = estimate(env, mission_entropy=0.64, parallelizability=0.55, entropy_band="high")

    result = route(env, ent)

    assert 8 <= result.recommended_agent_count <= 20
    assert result.brain_mode == BrainMode.SLOW_BRAIN


def test_agent_count_routes_twenty_to_one_hundred_for_very_high_entropy():
    env = envelope()
    ent = estimate(env, mission_entropy=0.82, parallelizability=0.60, entropy_band="very_high")

    result = route(env, ent)

    assert 20 <= result.recommended_agent_count <= 100
    assert result.brain_mode == BrainMode.VERY_HIGH_SOCIETY
    assert result.extreme_swarm_blocked is False


def test_agent_count_blocks_extreme_swarm_by_default():
    env = envelope(max_actions=500)
    ent = estimate(env, mission_entropy=0.95, parallelizability=0.92, entropy_band="very_high")

    result = route(env, ent)

    assert result.brain_mode == BrainMode.EXTREME_SWARM_BLOCKED
    assert result.extreme_swarm_blocked is True
    assert result.recommended_agent_count == 0
    assert result.max_parallel_agents == 0
    assert result.agent_budget == 0
    assert "extreme_swarm_disabled_by_default" in result.reason


def test_agent_count_budget_pressure_reduces_count():
    env = envelope()
    roomy = estimate(env, mission_entropy=0.70, parallelizability=0.70, budget_pressure=0.15, entropy_band="high")
    constrained = estimate(env, mission_entropy=0.70, parallelizability=0.70, budget_pressure=0.85, entropy_band="high")

    roomy_result = route(env, roomy)
    constrained_result = route(env, constrained)

    assert constrained_result.recommended_agent_count < roomy_result.recommended_agent_count
    assert "budget_pressure_reduced_count" in constrained_result.reason


def test_agent_count_controller_does_not_expand_authority():
    env = envelope(
        allowed_systems=["local_workspace"],
        allowed_tools=["safe_file_writer"],
        allowed_actions=["create_markdown_file"],
        allowed_paths=["data/generated_projects"],
    )
    before = env.model_dump(mode="json")
    ent = estimate(env, mission_entropy=0.74, parallelizability=0.9, entropy_band="high")

    result = route(env, ent)

    assert env.model_dump(mode="json") == before
    assert result.authority_expansion is False
    assert result.advisory_only is True
    assert result.agent_spawning is False
    assert result.runtime_multi_agent_execution is False
    assert not hasattr(result, "allowed_tools")
    assert not hasattr(result, "allowed_actions")
    assert not hasattr(result, "allowed_paths")
