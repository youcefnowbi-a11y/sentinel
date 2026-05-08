from __future__ import annotations

from sentinel.agent.event_bus import EventBus
from sentinel.agent.exceptions import MissionRevokedError
from sentinel.agent.invariants import InvariantChecker
from sentinel.agent.models import AgentContext, CapabilityNeed, LearningProposal
from sentinel.agent.state import AgentState


class Supervisor:
    def __init__(self, invariants: InvariantChecker | None = None) -> None:
        self.invariants = invariants or InvariantChecker()

    def assert_mission_can_run(self, context: AgentContext) -> None:
        if context.mission.revoked_at is not None:
            raise MissionRevokedError("Mission authority has been revoked.")

    def assert_context_did_not_expand_authority(self, context: AgentContext) -> None:
        self.invariants.check_capabilities_derive_from_authority(context.mission, context.available_capabilities)

    def assert_capabilities_are_declared(self, needs: list[CapabilityNeed]) -> None:
        self.invariants.check_capability_declarations(needs)

    def assert_learning_is_safe(self, proposals: list[LearningProposal]) -> None:
        self.invariants.check_learning_proposals(proposals)

    def assert_completion(self, state: AgentState, mission_result) -> None:
        self.invariants.check_completion(state, mission_result)

    def assert_state_bounds(self, state: AgentState) -> None:
        self.invariants.check_bounded_repair(state)

    def assert_trace_integrity(self, event_bus: EventBus) -> None:
        self.invariants.check_trace_chain(event_bus)
