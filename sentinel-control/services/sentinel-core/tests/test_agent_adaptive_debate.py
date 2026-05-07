from __future__ import annotations

from sentinel.agent import (
    AdaptiveDebateRouter,
    AgentEventType,
    BayesianBeliefState,
    Belief,
    ContradictionSupport,
    DebateRoute,
    EventBus,
    MissionEntropyEstimate,
)


MISSION_ID = "mission_p5g"


def estimate(**overrides) -> MissionEntropyEstimate:
    data = {
        "mission_id": MISSION_ID,
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


def belief_state(*beliefs: Belief) -> BayesianBeliefState:
    return BayesianBeliefState.create(MISSION_ID, list(beliefs))


def route(**kwargs) -> DebateRoute:
    return AdaptiveDebateRouter().route(MISSION_ID, **kwargs)


def test_debate_off_for_low_uncertainty():
    result = route(estimate=estimate())

    assert result.debate_needed is False
    assert result.reason == "debate_off_low_uncertainty"
    assert result.debate_roles == []
    assert result.sparse_moa_plan is None


def test_debate_on_for_contradiction_and_high_impact_with_trace():
    bus = EventBus(MISSION_ID)
    belief = Belief(
        mission_id=MISSION_ID,
        hypothesis_id="hyp_claim",
        statement="Claim with contradiction.",
        belief_probability=0.55,
        belief_variance=0.5,
        contradiction_support=[ContradictionSupport(evidence_ref="ev_contra", severity=0.8, reliability=0.8)],
    )

    result = route(estimate=estimate(mission_entropy=0.6, impact_level=0.75, entropy_band="high"), belief_state=belief_state(belief), event_bus=bus)

    assert result.debate_needed is True
    assert "contradiction" in result.reason
    assert "high_impact" in result.reason
    assert {"verifier_agent", "skeptic_agent", "aggregator_agent"}.issubset({role.role for role in result.debate_roles})
    event_types = [event.event_type for event in bus.events()]
    assert AgentEventType.DEBATE_ROUTED in event_types
    assert AgentEventType.MOA_LAYER_COMPLETED in event_types
    assert AgentEventType.DEBATE_AGGREGATED in event_types


def test_sparse_fan_in_limits_are_applied():
    result = route(estimate=estimate(mission_entropy=0.8, parallelizability=0.8, entropy_band="very_high"), fan_in_limit=2)

    assert result.sparse_moa_plan is not None
    assert result.sparse_moa_plan.fan_in_limit == 2
    assert all(len(layer) <= 2 or layer == result.sparse_moa_plan.layer_role_ids[-1] for layer in result.sparse_moa_plan.layer_role_ids)
    assert len(result.sparse_moa_plan.sparse_edges) <= 2


def test_max_layers_and_rounds_are_enforced():
    result = route(estimate=estimate(mission_entropy=0.8, entropy_band="very_high"), max_layers=99, max_debate_rounds=99, fan_in_limit=99)

    assert result.max_layers == AdaptiveDebateRouter.HARD_MAX_LAYERS
    assert result.max_debate_rounds == AdaptiveDebateRouter.HARD_MAX_ROUNDS
    assert result.fan_in_limit == AdaptiveDebateRouter.HARD_FAN_IN_LIMIT
    assert result.sparse_moa_plan is not None
    assert result.sparse_moa_plan.layers <= result.max_layers


def test_unresolved_disputes_are_preserved():
    disputes = ["Source A and source B disagree on demand."]

    result = route(estimate=estimate(mission_entropy=0.6, entropy_band="high"), unresolved_disputes=disputes)

    assert result.unresolved_disputes == disputes
    assert result.aggregation_plan is not None
    assert result.aggregation_plan.unresolved_disputes == disputes


def test_adaptive_debate_does_not_execute_agents():
    result = route(estimate=estimate(mission_entropy=0.75, entropy_band="very_high"))

    assert result.advisory_only is True
    assert result.runtime_agent_execution is False
    assert result.runtime_multi_agent_execution is False
    assert all(role.runtime_agent_execution is False for role in result.debate_roles)
    assert result.sparse_moa_plan is not None
    assert result.sparse_moa_plan.runtime_agent_execution is False


def test_adaptive_debate_does_not_expand_authority():
    result = route(estimate=estimate(mission_entropy=0.75, impact_level=0.9, entropy_band="very_high"))

    assert result.authority_expansion is False
    assert not hasattr(result, "allowed_tools")
    assert not hasattr(result, "allowed_actions")
    assert all(role.authority_expansion is False for role in result.debate_roles)
