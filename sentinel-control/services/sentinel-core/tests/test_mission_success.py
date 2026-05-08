from __future__ import annotations

import json
from pathlib import Path

from sentinel.mission import MissionSuccessEvaluator
from sentinel.mission.models import ReviewResult


REQUIRED_MD = [
    "00_VERDICT.md",
    "01_EVIDENCE.md",
    "02_ICP.md",
    "03_COMPETITOR_GAPS.md",
    "04_LANDING_PAGE_COPY.md",
    "05_OUTREACH_MESSAGES.md",
    "07_7_DAY_ROADMAP.md",
    "08_WATCHLIST.md",
]


def write_complete_project(project: Path) -> None:
    project.mkdir(parents=True, exist_ok=True)
    for filename in REQUIRED_MD:
        (project / filename).write_text("# Section\n\n## Evidence refs\n\n- `ev_1`\n", encoding="utf-8")
    (project / "outreach_drafts.json").write_text(json.dumps({"sent": False}), encoding="utf-8")
    (project / "mission_artifacts.json").write_text("[]", encoding="utf-8")
    (project / "mission_timeline.json").write_text("[]", encoding="utf-8")
    (project / "artifact_manifest.json").write_text("{}", encoding="utf-8")


def test_success_evaluator_validates_complete_local_mission(tmp_path):
    project = tmp_path / "data/generated_projects/success"
    write_complete_project(project)

    success, failures = MissionSuccessEvaluator().evaluate(project, ReviewResult(mission_id="mission_1", ready=True))

    assert success is True
    assert failures == []


def test_success_evaluator_prevents_completion_if_required_artifact_missing(tmp_path):
    project = tmp_path / "data/generated_projects/success"
    write_complete_project(project)
    (project / "08_WATCHLIST.md").unlink()

    success, failures = MissionSuccessEvaluator().evaluate(project, ReviewResult(mission_id="mission_1", ready=True))

    assert success is False
    assert any("08_WATCHLIST.md" in failure for failure in failures)


def test_success_evaluator_rejects_sent_outreach(tmp_path):
    project = tmp_path / "data/generated_projects/success"
    write_complete_project(project)
    (project / "outreach_drafts.json").write_text(json.dumps({"sent": True}), encoding="utf-8")

    success, failures = MissionSuccessEvaluator().evaluate(project, ReviewResult(mission_id="mission_1", ready=True))

    assert success is False
    assert "Outreach draft payload must not be sent." in failures
