from __future__ import annotations

import json
from pathlib import Path

from sentinel.mission.models import MissionArtifactSchema, ReviewResult


class MissionSuccessEvaluator:
    DEFAULT_REQUIRED_FILES = {
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
    }

    DEFAULT_MAJOR_SECTIONS = {
        "00_VERDICT.md",
        "01_EVIDENCE.md",
        "02_ICP.md",
        "03_COMPETITOR_GAPS.md",
        "04_LANDING_PAGE_COPY.md",
        "05_OUTREACH_MESSAGES.md",
        "07_7_DAY_ROADMAP.md",
        "08_WATCHLIST.md",
    }

    def __init__(self, schema: MissionArtifactSchema | None = None) -> None:
        self.schema = schema

    def evaluate(self, project_dir: str | Path, review: ReviewResult, *, unresolved_critical_escalations: int = 0) -> tuple[bool, list[str]]:
        project_path = Path(project_dir)
        failures: list[str] = []
        required_files = set(self.schema.required_files if self.schema else self.DEFAULT_REQUIRED_FILES)
        major_sections = set(self.schema.major_sections if self.schema else self.DEFAULT_MAJOR_SECTIONS)
        draft_only_files = set(self.schema.draft_only_files if self.schema else ["outreach_drafts.json"])

        for filename in sorted(required_files):
            if not (project_path / filename).exists():
                failures.append(f"Missing required file: {filename}.")

        for filename in sorted(major_sections):
            path = project_path / filename
            if not path.exists():
                continue
            content = path.read_text(encoding="utf-8")
            if "Evidence refs" not in content and "EVIDENCE_GAP" not in content:
                failures.append(f"{filename} has no evidence refs or Evidence gap.")

        for filename in sorted(draft_only_files):
            draft_path = project_path / filename
            if draft_path.exists():
                payload = json.loads(draft_path.read_text(encoding="utf-8"))
                if payload.get("sent") is not False:
                    if filename == "outreach_drafts.json":
                        failures.append("Outreach draft payload must not be sent.")
                    else:
                        failures.append(f"{filename} must not be sent.")
            else:
                failures.append(f"Missing {filename}.")

        if unresolved_critical_escalations:
            failures.append("Unresolved critical escalation remains.")

        if not review.ready:
            failures.append("ReviewerLite did not mark the mission ready.")

        return not failures, failures
