from __future__ import annotations

import hashlib
from pathlib import Path

from sentinel.mission.models import MissionArtifact, MissionArtifactSchema, MissionAuthorityEnvelope, ReviewResult, ReviewerIssue


GENERIC_MARKERS = {
    "businesses",
    "users",
    "everyone",
    "all companies",
    "generic assistant",
}


class ReviewerLite:
    DEFAULT_REQUIRED_ARTIFACT_TYPES = {
        "gtm_verdict",
        "evidence",
        "icp",
        "competitor_gap",
        "landing_copy",
        "outreach_drafts",
        "watchlist",
        "roadmap",
    }

    def __init__(self, schema: MissionArtifactSchema | None = None) -> None:
        self.schema = schema

    def review(
        self,
        envelope: MissionAuthorityEnvelope,
        project_dir: str | Path,
        artifacts: list[MissionArtifact],
        *,
        unresolved_critical_escalations: int = 0,
    ) -> ReviewResult:
        project_path = Path(project_dir)
        issues: list[ReviewerIssue] = []
        required_artifact_types = set(
            self.schema.required_artifact_types if self.schema else self.DEFAULT_REQUIRED_ARTIFACT_TYPES
        )

        present_types = {artifact.type for artifact in artifacts}
        for artifact_type in sorted(required_artifact_types - present_types):
            issues.append(ReviewerIssue(code="missing_artifact", severity="high", message=f"Missing required artifact type: {artifact_type}."))

        for artifact in artifacts:
            path = self._artifact_path(project_path, artifact.path)
            if path is None:
                issues.append(
                    ReviewerIssue(
                        code="artifact_path_out_of_scope",
                        severity="critical",
                        message=f"Artifact path escapes the mission project folder: {artifact.path}.",
                        artifact_path=artifact.path,
                    )
                )
                continue
            if artifact.type in required_artifact_types and not path.exists():
                issues.append(ReviewerIssue(code="missing_file", severity="high", message=f"Artifact file does not exist: {artifact.path}.", artifact_path=artifact.path))
                continue
            if path.exists() and artifact.sha256:
                actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual_hash != artifact.sha256:
                    issues.append(
                        ReviewerIssue(
                            code="artifact_hash_mismatch",
                            severity="critical",
                            message=f"Artifact hash mismatch: {artifact.path}.",
                            artifact_path=artifact.path,
                        )
                    )
            if path.suffix.lower() == ".md":
                content = path.read_text(encoding="utf-8").lower()
                if "evidence refs" not in content and "evidence_gap" not in content:
                    issues.append(ReviewerIssue(code="missing_evidence_reference", severity="medium", message="Section has no evidence refs or Evidence gap.", artifact_path=artifact.path))
                if any(marker in content for marker in GENERIC_MARKERS) and "evidence_gap" not in content:
                    issues.append(ReviewerIssue(code="too_generic", severity="medium", message="Section may be too generic without an explicit evidence gap.", artifact_path=artifact.path))

        if unresolved_critical_escalations:
            issues.append(ReviewerIssue(code="critical_escalation_open", severity="critical", message="Mission has unresolved critical escalation requests."))

        if not envelope.success_criteria:
            issues.append(ReviewerIssue(code="success_criteria_missing", severity="medium", message="Mission success criteria are not explicit."))

        ready = not any(issue.severity in {"high", "critical"} for issue in issues)
        return ReviewResult(mission_id=envelope.id, ready=ready, issues=issues)

    @staticmethod
    def _artifact_path(project_path: Path, artifact_path: str) -> Path | None:
        raw_path = Path(artifact_path)
        if raw_path.is_absolute() or ".." in raw_path.parts:
            return None
        resolved = (project_path / raw_path).resolve()
        try:
            resolved.relative_to(project_path.resolve())
        except ValueError:
            return None
        return resolved
