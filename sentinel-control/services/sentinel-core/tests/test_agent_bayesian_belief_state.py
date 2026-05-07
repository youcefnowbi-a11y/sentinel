from __future__ import annotations

from sentinel.agent import (
    AgentEventType,
    BayesianBeliefState,
    Belief,
    ContradictionSupport,
    EventBus,
    EvidenceSupport,
)


MISSION_ID = "mission_p5f"


def belief(**overrides) -> Belief:
    data = {
        "mission_id": MISSION_ID,
        "hypothesis_id": "hyp_revenue_signal",
        "statement": "The opportunity has validated demand.",
        "belief_probability": 0.5,
        "belief_variance": 0.5,
    }
    data.update(overrides)
    return Belief(**data)


def state(seed: Belief | None = None) -> BayesianBeliefState:
    return BayesianBeliefState.create(MISSION_ID, [seed or belief()])


def support(**overrides) -> EvidenceSupport:
    data = {"evidence_ref": "ev_support", "summary": "Observed positive signal.", "weight": 0.8, "reliability": 0.8}
    data.update(overrides)
    return EvidenceSupport(**data)


def contradiction(**overrides) -> ContradictionSupport:
    data = {"evidence_ref": "ev_contra", "summary": "Observed contradiction.", "severity": 0.8, "reliability": 0.8}
    data.update(overrides)
    return ContradictionSupport(**data)


def test_prior_posterior_update_emits_trace_event():
    seed = belief()
    bus = EventBus(MISSION_ID)

    updated, update = state(seed).update_belief(seed.id, evidence_support=[support()], event_bus=bus)

    assert update.prior_probability == 0.5
    assert update.posterior_probability > update.prior_probability
    assert update.posterior_variance < update.prior_variance
    assert update.posterior_update_reason == "supporting_evidence_narrowed_variance"
    assert AgentEventType.BELIEF_STATE_UPDATED in [event.event_type for event in bus.events()]
    assert updated.beliefs[0].trace_refs


def test_contradiction_widens_variance():
    seed = belief()

    updated, update = state(seed).update_belief(seed.id, contradiction_support=[contradiction()])

    assert update.posterior_probability < update.prior_probability
    assert update.posterior_variance > update.prior_variance
    assert updated.beliefs[0].posterior_update_reason == "contradiction_widened_variance"


def test_supporting_evidence_narrows_variance():
    seed = belief(belief_variance=0.6)

    updated, _ = state(seed).update_belief(seed.id, evidence_support=[support(weight=1.0, reliability=0.9)])

    assert updated.beliefs[0].belief_variance < 0.6
    assert updated.beliefs[0].supporting_evidence


def test_unsupported_posterior_jump_is_rejected():
    seed = belief(belief_probability=0.4, belief_variance=0.5)

    updated, update = state(seed).update_belief(seed.id, proposed_posterior_probability=0.95)

    assert update.rejected is True
    assert "unsupported_posterior_jump" in update.errors
    assert updated.beliefs[0].belief_probability == 0.4
    assert updated.authority_expansion is False


def test_binary_verified_rejected_compatibility_view():
    verified = belief(hypothesis_id="hyp_verified", belief_probability=0.82, belief_variance=0.2)
    rejected = belief(hypothesis_id="hyp_rejected", belief_probability=0.18, belief_variance=0.3)
    uncertain = belief(hypothesis_id="hyp_uncertain", belief_probability=0.55, belief_variance=0.5)

    view = BayesianBeliefState.create(MISSION_ID, [verified, rejected, uncertain]).compatibility_view()

    assert view["verified"] == ["hyp_verified"]
    assert view["rejected"] == ["hyp_rejected"]
    assert view["uncertain"] == ["hyp_uncertain"]


def test_bayesian_belief_state_does_not_expand_authority():
    seed = belief()
    original = seed.model_dump(mode="json")

    updated, update = state(seed).update_belief(seed.id, evidence_support=[support(evidence_ref="ev_safe")])

    assert seed.model_dump(mode="json") == original
    assert updated.advisory_only is True
    assert updated.authority_expansion is False
    assert update.advisory_only is True
    assert update.authority_expansion is False
    assert not hasattr(updated, "allowed_tools")
    assert not hasattr(updated, "allowed_actions")
