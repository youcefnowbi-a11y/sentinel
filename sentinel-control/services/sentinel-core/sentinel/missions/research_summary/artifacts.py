from __future__ import annotations

from sentinel.mission.models import MissionArtifactSchema
from sentinel.shared.enums import MissionType


def research_summary_artifact_schema() -> MissionArtifactSchema:
    return MissionArtifactSchema(
        mission_type=MissionType.RESEARCH_SUMMARY,
        required_artifact_types=["research_summary"],
        required_files=[
            "RESEARCH_SUMMARY.md",
            "mission_artifacts.json",
            "mission_timeline.json",
            "artifact_manifest.json",
        ],
        major_sections=["RESEARCH_SUMMARY.md"],
        draft_only_files=[],
    )
