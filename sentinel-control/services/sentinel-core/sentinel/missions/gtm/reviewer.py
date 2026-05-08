from __future__ import annotations

from sentinel.mission.reviewer import ReviewerLite
from sentinel.missions.gtm.artifacts import gtm_artifact_schema


class GTMReviewer(ReviewerLite):
    def __init__(self) -> None:
        super().__init__(schema=gtm_artifact_schema())
