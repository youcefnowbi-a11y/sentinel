from __future__ import annotations

from sentinel.mission.success import MissionSuccessEvaluator
from sentinel.missions.research_summary.artifacts import research_summary_artifact_schema


class ResearchSummarySuccessEvaluator(MissionSuccessEvaluator):
    def __init__(self) -> None:
        super().__init__(schema=research_summary_artifact_schema())
