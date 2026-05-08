from __future__ import annotations

from sentinel.mission.reviewer import ReviewerLite
from sentinel.missions.research_summary.artifacts import research_summary_artifact_schema


class ResearchSummaryReviewer(ReviewerLite):
    def __init__(self) -> None:
        super().__init__(schema=research_summary_artifact_schema())
