from __future__ import annotations

import pytest
from pydantic import ValidationError

import sentinel.agent as agent_api
from sentinel.agent import AgentIdentity, AgentPhase, AgentState, CapabilityNeed, UncertaintyState
from sentinel.agent.phases import ABSORBING_PHASES, ALLOWED_PHASE_TRANSITIONS, can_transition
from sentinel.agent.uncertainty import Assumption, Fact, Hypothesis, Question


def test_agent_identity_is_immutable():
    identity = AgentIdentity()

    with pytest.raises(ValidationError):
        identity.name = "Different"


def test_agent_public_api_exports_resolve_without_duplicates():
    missing = [name for name in agent_api.__all__ if not hasattr(agent_api, name)]
    duplicates = {name for name in agent_api.__all__ if agent_api.__all__.count(name) > 1}

    assert missing == []
    assert duplicates == set()


def test_uncertainty_state_separates_known_assumed_suspected_unknown():
    uncertainty = UncertaintyState(
        known=[Fact(statement="Mission authority exists.")],
        assumed=[Assumption(statement="Evidence is sufficient.", reason="Fixture data.")],
        suspected=[Hypothesis(statement="Browser research could improve quality.", test_needed="Future P2.")],
        unknown=[Question(question="Is WTP externally verified?", blocks_completion=False)],
    )

    assert uncertainty.known[0].statement == "Mission authority exists."
    assert uncertainty.assumed[0].confidence == 0.5
    assert uncertainty.suspected[0].confidence == 0.25
    assert uncertainty.has_blocking_questions() is False


def test_agent_state_transition_is_deterministic_for_known_phase():
    state = AgentState(mission_id="mission_001")

    initialized = state.transition(AgentPhase.INITIALIZED)

    assert state.phase == AgentPhase.CREATED
    assert initialized.phase == AgentPhase.INITIALIZED


def test_agent_state_rejects_skipped_transition():
    state = AgentState(mission_id="mission_001")

    with pytest.raises(ValueError):
        state.transition(AgentPhase.EXECUTING)


def test_absorbing_phase_cannot_transition_to_new_phase():
    completed = AgentState(mission_id="mission_001", phase=AgentPhase.COMPLETED)

    with pytest.raises(ValueError):
        completed.transition(AgentPhase.EXECUTING)


def test_declared_phase_transitions_are_executable():
    for phase, allowed_next_phases in ALLOWED_PHASE_TRANSITIONS.items():
        for next_phase in allowed_next_phases:
            state = AgentState(mission_id="mission_001", phase=phase)

            transitioned = state.transition(next_phase)

            assert can_transition(phase, next_phase) is True
            assert transitioned.phase == next_phase


def test_undeclared_phase_transitions_are_rejected():
    for phase in AgentPhase:
        if phase in ABSORBING_PHASES:
            continue
        allowed = set(ALLOWED_PHASE_TRANSITIONS.get(phase, frozenset()))
        for next_phase in AgentPhase:
            if next_phase == phase or next_phase in allowed:
                continue

            assert can_transition(phase, next_phase) is False
            with pytest.raises(ValueError):
                AgentState(mission_id="mission_001", phase=phase).transition(next_phase)


def test_capability_need_missing_requires_reason_in_invariants():
    need = CapabilityNeed(name="browser_research", reason="Future research", available=False, missing_reason="Not built yet.")

    assert need.available is False
    assert need.missing_reason == "Not built yet."
