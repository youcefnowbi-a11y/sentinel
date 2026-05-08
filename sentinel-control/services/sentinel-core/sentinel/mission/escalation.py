from __future__ import annotations

from sentinel.mission.models import EscalationRequest, MissionAction, MissionAuthorityEnvelope, utc_now
from sentinel.mission.scope_checker import BLACK_ZONE_ACTIONS
from sentinel.mission.trace_timeline import MissionTraceTimeline
from sentinel.shared.enums import EscalationOption, MissionTraceEventType


class EscalationGateway:
    def create_request(
        self,
        envelope: MissionAuthorityEnvelope,
        action: MissionAction,
        reason: str,
        timeline: MissionTraceTimeline | None = None,
    ) -> EscalationRequest:
        request = EscalationRequest(
            mission_id=envelope.id,
            action_id=action.id,
            reason=reason,
            user_question="What do you want Sentinel to do at this mission boundary?",
            action_preview={
                "action_type": action.action_type,
                "tool": action.tool,
                "target": action.target,
                "input": action.input,
                "expected_output": action.expected_output,
            },
            impact_summary=self._impact_summary(action, reason),
        )
        if timeline:
            timeline.emit(
                MissionTraceEventType.ACTION_ESCALATED,
                "Escalation request created.",
                action_id=action.id,
                result=request.model_dump(mode="json"),
                impact=request.impact_summary,
            )
        return request

    def allow_for_this_mission(
        self,
        envelope: MissionAuthorityEnvelope,
        action: MissionAction,
        timeline: MissionTraceTimeline | None = None,
    ) -> MissionAuthorityEnvelope:
        if self._is_black_zone(action):
            raise ValueError("allow_for_this_mission cannot grant black-zone actions.")
        if not action.action_type or not action.tool:
            raise ValueError("allow_for_this_mission cannot grant unknown scopes.")

        allowed_actions = list(dict.fromkeys([*envelope.allowed_actions, action.action_type]))
        allowed_tools = list(dict.fromkeys([*envelope.allowed_tools, action.tool]))
        updated = envelope.model_copy(update={"allowed_actions": allowed_actions, "allowed_tools": allowed_tools})
        if timeline:
            timeline.emit(
                MissionTraceEventType.USER_ALLOWED_FOR_MISSION,
                "User allowed this non-black-zone action for the current mission.",
                actor="user",
                action_id=action.id,
                result={"allowed_actions": allowed_actions, "allowed_tools": allowed_tools},
            )
        return updated

    def resolve(self, request: EscalationRequest, option: EscalationOption, timeline: MissionTraceTimeline | None = None) -> EscalationRequest:
        updated = request.model_copy(update={"resolved_at": utc_now()})
        if timeline:
            event = {
                EscalationOption.APPROVE_ONCE: MissionTraceEventType.USER_APPROVED_ONCE,
                EscalationOption.ALLOW_FOR_MISSION: MissionTraceEventType.USER_ALLOWED_FOR_MISSION,
                EscalationOption.DENY: MissionTraceEventType.USER_DENIED,
                EscalationOption.TAKE_OVER: MissionTraceEventType.USER_TAKEOVER,
            }[option]
            timeline.emit(event, f"User selected {option.value}.", actor="user", action_id=request.action_id)
        return updated

    @staticmethod
    def _is_black_zone(action: MissionAction) -> bool:
        return action.action_type.lower() in BLACK_ZONE_ACTIONS or action.tool.lower() in BLACK_ZONE_ACTIONS

    @staticmethod
    def _impact_summary(action: MissionAction, reason: str) -> str:
        return (
            f"Sentinel is asking because {reason}. "
            f"The proposed action is `{action.action_type}` via `{action.tool}` and would target `{action.target or 'mission workspace'}`."
        )
