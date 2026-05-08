import hashlib
from pathlib import Path

from sentinel.mission import MissionArtifact, MissionAuthorityEnvelope, ReviewerLite
from sentinel.shared.enums import MissionMode


def envelope() -> MissionAuthorityEnvelope:
    return MissionAuthorityEnvelope(
        user_id="user_001",
        mission_title="Review mission",
        mission_objective="Review local GTM pack.",
        success_criteria=["All expected artifacts exist."],
        mode=MissionMode.OPERATOR,
        allowed_tools=["safe_file_writer"],
        allowed_actions=["generate_gtm_pack"],
        allowed_paths=["data/generated_projects"],
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_reviewer_lite_passes_complete_pack_with_gaps_or_refs(tmp_path):
    project = tmp_path / "data/generated_projects/review"
    artifacts = []
    files = {
        "00_VERDICT.md": "gtm_verdict",
        "01_EVIDENCE.md": "evidence",
        "02_ICP.md": "icp",
        "03_COMPETITOR_GAPS.md": "competitor_gap",
        "04_LANDING_PAGE_COPY.md": "landing_copy",
        "05_OUTREACH_MESSAGES.md": "outreach_drafts",
        "07_7_DAY_ROADMAP.md": "roadmap",
        "08_WATCHLIST.md": "watchlist",
    }
    for filename, artifact_type in files.items():
        write(project / filename, "# Section\n\n## Evidence refs\n\n- `ev_1`\n")
        artifacts.append(MissionArtifact(type=artifact_type, path=filename, evidence_refs=["ev_1"]))

    result = ReviewerLite().review(envelope(), project, artifacts)

    assert result.ready is True
    assert result.issues == []


def test_reviewer_lite_flags_missing_artifact_and_missing_evidence(tmp_path):
    project = tmp_path / "data/generated_projects/review"
    write(project / "00_VERDICT.md", "# Verdict\n\nNo refs here.")
    artifacts = [MissionArtifact(type="gtm_verdict", path="00_VERDICT.md")]

    result = ReviewerLite().review(envelope(), project, artifacts)

    assert result.ready is False
    codes = {issue.code for issue in result.issues}
    assert "missing_artifact" in codes
    assert "missing_evidence_reference" in codes


def test_reviewer_lite_rejects_artifact_path_escape_without_reading_outside_project(tmp_path):
    project = tmp_path / "data/generated_projects/review"
    outside = tmp_path / "outside.md"
    write(outside, "# Outside\n\n## Evidence refs\n\n- `ev_1`\n")
    artifacts = [MissionArtifact(type="gtm_verdict", path="../outside.md")]

    result = ReviewerLite().review(envelope(), project, artifacts)

    codes = {issue.code for issue in result.issues}
    assert result.ready is False
    assert "artifact_path_out_of_scope" in codes


def test_reviewer_lite_rejects_artifact_hash_mismatch(tmp_path):
    project = tmp_path / "data/generated_projects/review"
    write(project / "00_VERDICT.md", "# Verdict\n\n## Evidence refs\n\n- `ev_1`\n")
    bad_hash = hashlib.sha256(b"different").hexdigest()
    artifacts = [
        MissionArtifact(
            type="gtm_verdict",
            path="00_VERDICT.md",
            evidence_refs=["ev_1"],
            sha256=bad_hash,
        )
    ]

    result = ReviewerLite().review(envelope(), project, artifacts)

    codes = {issue.code for issue in result.issues}
    assert result.ready is False
    assert "artifact_hash_mismatch" in codes
