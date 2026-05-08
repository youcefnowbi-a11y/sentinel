from __future__ import annotations

from sentinel.agent.capability_selector import capabilities_from_actions
from sentinel.agent.event_bus import EventBus
from sentinel.agent.models import CapabilityNeed, LearningProposal
from sentinel.agent.phases import AgentPhase
from sentinel.agent.state import AgentState
from sentinel.mission.models import MissionAction, MissionAuthorityEnvelope, MissionRunResult


class InvariantViolation(ValueError):
    """Raised when a Sentinel agent invariant is violated."""


class InvariantChecker:
    def check_authority(self, envelope: MissionAuthorityEnvelope, action: MissionAction) -> None:
        if action.action_type not in envelope.allowed_actions:
            raise InvariantViolation(f"Action `{action.action_type}` is outside mission allowed actions.")
        if action.tool not in envelope.allowed_tools:
            raise InvariantViolation(f"Tool `{action.tool}` is outside mission allowed tools.")

    def check_trace_chain(self, event_bus: EventBus) -> None:
        if not event_bus.verify_chain():
            raise InvariantViolation("Agent event hash chain verification failed.")

    def check_memory_not_authority(self, envelope: MissionAuthorityEnvelope, context_allowed_actions: list[str] | None = None) -> None:
        proposed = set(context_allowed_actions or [])
        allowed = set(envelope.allowed_actions)
        if not proposed.issubset(allowed):
            raise InvariantViolation("Context or memory attempted to expand mission authority.")

    def check_capabilities_derive_from_authority(self, envelope: MissionAuthorityEnvelope, context_capabilities: list[str] | None = None) -> None:
        proposed = set(context_capabilities or [])
        allowed = set(capabilities_from_actions(list(envelope.allowed_actions)))
        if not proposed.issubset(allowed):
            raise InvariantViolation("Context or memory attempted to add capabilities outside mission authority.")

    def check_capability_declarations(self, needs: list[CapabilityNeed]) -> None:
        for need in needs:
            if not need.available and not need.missing_reason:
                raise InvariantViolation(f"Missing capability `{need.name}` must explain why it is unavailable.")

    def check_completion(self, state: AgentState, mission_result: MissionRunResult | None) -> None:
        if state.phase == AgentPhase.COMPLETED and (mission_result is None or not mission_result.success):
            raise InvariantViolation("Agent cannot complete without a successful mission result.")

    def check_learning_proposals(self, proposals: list[LearningProposal]) -> None:
        for proposal in proposals:
            if not proposal.requires_human_approval:
                raise InvariantViolation("Learning proposals must require human approval.")

    def check_bounded_repair(self, state: AgentState) -> None:
        if state.repair_cycles > state.max_repair_cycles:
            raise InvariantViolation("Repair cycles exceeded the configured bound.")
