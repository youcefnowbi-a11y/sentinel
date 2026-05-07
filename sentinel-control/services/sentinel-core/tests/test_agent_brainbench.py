from __future__ import annotations

from sentinel.agent import AgentEventType, BrainBench, BrainBenchCase, EventBus


MISSION_ID = "mission_p5k"


def run(*cases: BrainBenchCase):
    return BrainBench().run(list(cases))


def case(name: str, category: str, expected: dict, observed: dict, **kwargs) -> BrainBenchCase:
    return BrainBenchCase(name=name, category=category, expected=expected, observed=observed, **kwargs)


def test_p5b_p5c_allocation_cases():
    report = run(case("medium allocation", "allocation", {"allowed_counts": [3, 4, 5]}, {"recommended_agent_count": 4}))

    assert report.accepted is True
    assert report.allocation_accuracy == 1.0


def test_p5f_belief_update_cases():
    report = run(case("support raises probability", "belief_update", {"probability_direction": "increase"}, {"prior_probability": 0.5, "posterior_probability": 0.72}))

    assert report.accepted is True
    assert report.belief_update_quality == 1.0


def test_p5g_debate_trigger_cases():
    report = run(case("contradiction triggers debate", "debate_trigger", {"debate_needed": True}, {"debate_needed": True}))

    assert report.accepted is True
    assert report.debate_trigger_precision == 1.0


def test_p5h_information_gain_cases():
    report = run(case("safe probe preferred", "information_gain", {"preferred_action": "safe_probe"}, {"preferred_action": "safe_probe"}))

    assert report.accepted is True
    assert report.information_gain_score == 1.0


def test_p5i_resourcefulness_cases():
    report = run(case("authorized substitution", "resourcefulness", {"level": "D2_substitute"}, {"level": "D2_substitute"}))

    assert report.accepted is True
    assert report.resourcefulness_score == 1.0


def test_p5j_procedure_matching_cases():
    report = run(case("research procedure", "procedure_match", {"procedure_name": "Research Summary Procedure"}, {"procedure_name": "Research Summary Procedure"}))

    assert report.accepted is True
    assert report.procedure_match_score == 1.0


def test_forged_l4_trace_rejected_and_traced():
    bus = EventBus(MISSION_ID)
    report = BrainBench().run(
        [case("forged trace", "trace_integrity", {"trace_integrity_ok": True}, {"trace_integrity_ok": False}, forged_trace=True)],
        event_bus=bus,
    )

    assert report.accepted is False
    assert "forged_l4_trace_rejected" in report.errors
    assert report.trace_integrity == 0.0
    event_types = [event.event_type for event in bus.events()]
    assert AgentEventType.BRAINBENCH_CASE_RUN in event_types
    assert AgentEventType.BRAINBENCH_REPORT_CREATED in event_types


def test_authority_expansion_negative_cases():
    report = run(
        case(
            "authority expansion attempt",
            "authority_negative",
            {"authority_expansion": False},
            {"authority_expansion": True},
            authority_expansion_attempt=True,
        )
    )

    assert report.accepted is False
    assert "authority_expansion_attempt_rejected" in report.errors
    assert report.authority_expansion is False


def test_brainbench_cost_efficiency_and_trace_integrity_pass():
    report = run(
        case(
            "efficient uncertainty reduction",
            "cost_efficiency",
            {"max_cost_per_uncertainty_reduction": 0.4},
            {"cost_per_uncertainty_reduction": 0.25},
        ),
        case("valid trace", "trace_integrity", {"trace_integrity_ok": True}, {"trace_integrity_ok": True}),
    )

    assert report.accepted is True
    assert report.cost_efficiency == 1.0
    assert report.trace_integrity == 1.0
