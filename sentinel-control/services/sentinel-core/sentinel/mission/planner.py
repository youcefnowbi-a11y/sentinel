from __future__ import annotations

from sentinel.mission.models import MissionAuthorityEnvelope, MissionPlan
from sentinel.missions.gtm.planner import GTMMissionPlanner


class MissionPlanner:
    """Compatibility wrapper for the first registered mission type.

    New mission execution should go through MissionRegistry. This wrapper keeps
    earlier G12B tests and imports stable while GTM moves out of the generic
    runner.
    """

    def __init__(self) -> None:
        self.gtm = GTMMissionPlanner()

    def create_gtm_plan(
        self,
        envelope: MissionAuthorityEnvelope,
        *,
        idea: str | None = None,
        evidence_refs: list[str] | None = None,
    ) -> MissionPlan:
        return self.gtm.create_plan(envelope, idea=idea, evidence_refs=evidence_refs)
