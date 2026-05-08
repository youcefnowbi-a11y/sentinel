from __future__ import annotations

from sentinel.mission.models import MissionArtifactSchema
from sentinel.shared.enums import MissionType


GTM_REQUIRED_ARTIFACT_TYPES = [
    "gtm_verdict",
    "evidence",
    "icp",
    "competitor_gap",
    "landing_copy",
    "outreach_drafts",
    "watchlist",
    "roadmap",
]

GTM_REQUIRED_FILES = [
    "00_VERDICT.md",
    "01_EVIDENCE.md",
    "02_ICP.md",
    "03_COMPETITOR_GAPS.md",
    "04_LANDING_PAGE_COPY.md",
    "05_OUTREACH_MESSAGES.md",
    "07_7_DAY_ROADMAP.md",
    "08_WATCHLIST.md",
    "mission_artifacts.json",
    "mission_timeline.json",
    "artifact_manifest.json",
]

GTM_MAJOR_SECTIONS = [
    "00_VERDICT.md",
    "01_EVIDENCE.md",
    "02_ICP.md",
    "03_COMPETITOR_GAPS.md",
    "04_LANDING_PAGE_COPY.md",
    "05_OUTREACH_MESSAGES.md",
    "07_7_DAY_ROADMAP.md",
    "08_WATCHLIST.md",
]


def gtm_artifact_schema() -> MissionArtifactSchema:
    return MissionArtifactSchema(
        mission_type=MissionType.GTM,
        required_artifact_types=GTM_REQUIRED_ARTIFACT_TYPES,
        required_files=GTM_REQUIRED_FILES,
        major_sections=GTM_MAJOR_SECTIONS,
        draft_only_files=["outreach_drafts.json"],
    )
