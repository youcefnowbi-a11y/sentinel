from __future__ import annotations

from sentinel.mission.success import MissionSuccessEvaluator
from sentinel.missions.gtm.artifacts import gtm_artifact_schema


class GTMSuccessEvaluator(MissionSuccessEvaluator):
    def __init__(self) -> None:
        super().__init__(schema=gtm_artifact_schema())
