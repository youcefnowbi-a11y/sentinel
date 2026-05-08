from __future__ import annotations

from pathlib import Path

from sentinel.mission.models import MissionAction, MissionAuthorityEnvelope, MissionState
from sentinel.mission.posture import MissionExecutionPosture
from sentinel.mission.risk import RiskRouter, RouteDecision
from sentinel.mission.trace_timeline import MissionTraceTimeline


class AutonomyEngine:
    def __init__(self, project_root: str | Path | None = None) -> None:
        self.router = RiskRouter(project_root)

    def decide(
        self,
        envelope: MissionAuthorityEnvelope,
        state: MissionState,
        action: MissionAction,
        timeline: MissionTraceTimeline | None = None,
        posture: MissionExecutionPosture | None = None,
    ) -> RouteDecision:
        return self.router.route(envelope, state, action, timeline=timeline, posture=posture)
