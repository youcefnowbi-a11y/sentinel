from __future__ import annotations

from pathlib import Path

from sentinel.mission.registry import MissionDefinition
from sentinel.mission.safe_executors import SafeMissionExecutors
from sentinel.missions.research_summary.artifacts import research_summary_artifact_schema
from sentinel.missions.research_summary.planner import ResearchSummaryMissionPlanner
from sentinel.missions.research_summary.reviewer import ResearchSummaryReviewer
from sentinel.missions.research_summary.success import ResearchSummarySuccessEvaluator
from sentinel.shared.enums import MissionType


def create_research_summary_definition(project_root: str | Path | None = None) -> MissionDefinition:
    return MissionDefinition(
        mission_type=MissionType.RESEARCH_SUMMARY,
        planner=ResearchSummaryMissionPlanner(),
        executor=SafeMissionExecutors(project_root),
        reviewer=ResearchSummaryReviewer(),
        success_evaluator=ResearchSummarySuccessEvaluator(),
        artifact_schema=research_summary_artifact_schema(),
    )


__all__ = [
    "ResearchSummaryMissionPlanner",
    "ResearchSummaryReviewer",
    "ResearchSummarySuccessEvaluator",
    "create_research_summary_definition",
]
