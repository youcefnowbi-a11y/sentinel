from __future__ import annotations

from pathlib import Path

from sentinel.mission.registry import MissionDefinition
from sentinel.mission.safe_executors import SafeMissionExecutors
from sentinel.missions.gtm.artifacts import gtm_artifact_schema
from sentinel.missions.gtm.planner import GTMMissionPlanner
from sentinel.missions.gtm.reviewer import GTMReviewer
from sentinel.missions.gtm.success import GTMSuccessEvaluator
from sentinel.shared.enums import MissionType


def create_gtm_definition(project_root: str | Path | None = None) -> MissionDefinition:
    return MissionDefinition(
        mission_type=MissionType.GTM,
        planner=GTMMissionPlanner(),
        executor=SafeMissionExecutors(project_root),
        reviewer=GTMReviewer(),
        success_evaluator=GTMSuccessEvaluator(),
        artifact_schema=gtm_artifact_schema(),
    )


__all__ = ["GTMMissionPlanner", "GTMReviewer", "GTMSuccessEvaluator", "create_gtm_definition"]
