from __future__ import annotations

from sentinel.mission.models import MissionAuthorityEnvelope, MissionState, utc_now
from sentinel.mission.trace_timeline import MissionTraceTimeline
from sentinel.shared.enums import MissionStatus, MissionTraceEventType


class MissionKillSwitch:
    def pause(self, state: MissionState, timeline: MissionTraceTimeline | None = None) -> MissionState:
        updated = state.model_copy(update={"status": MissionStatus.PAUSED, "updated_at": utc_now()})
        if timeline:
            timeline.emit(MissionTraceEventType.MISSION_PAUSED, "Mission paused after current safe step.")
        return updated

    def stop(self, state: MissionState, timeline: MissionTraceTimeline | None = None) -> MissionState:
        updated = state.model_copy(update={"status": MissionStatus.STOPPED, "updated_at": utc_now(), "ended_at": utc_now()})
        if timeline:
            timeline.emit(MissionTraceEventType.MISSION_STOPPED, "Mission stopped and queued work interrupted.")
        return updated

    def revoke(
        self,
        envelope: MissionAuthorityEnvelope,
        state: MissionState,
        timeline: MissionTraceTimeline | None = None,
    ) -> tuple[MissionAuthorityEnvelope, MissionState]:
        revoked_at = utc_now()
        updated_envelope = envelope.model_copy(update={"revoked_at": revoked_at})
        updated_state = state.model_copy(update={"status": MissionStatus.REVOKED, "updated_at": revoked_at, "ended_at": revoked_at})
        if timeline:
            timeline.emit(MissionTraceEventType.MISSION_REVOKED, "Mission authority revoked; all future actions are blocked.")
        return updated_envelope, updated_state
