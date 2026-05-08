from __future__ import annotations

import json
from pathlib import Path

from browser_fluency_runner import build_scorecard, load_catalog, main, run_fluency


def all_groups(catalog: dict) -> list[str]:
    return [group["id"] for group in catalog["groups"]]


def test_browser_fluency_hardened_profile_executes_full_72_mission_corpus():
    catalog = load_catalog()
    results = run_fluency(catalog, groups=all_groups(catalog), profile="hardened_full")
    scorecard = build_scorecard(results)

    assert len(results) == 72
    assert scorecard["executed_count"] == 72
    assert scorecard["not_run_count"] == 0
    assert scorecard["target_met_count"] > 50
    assert scorecard["partial_count"] > 0
    assert scorecard["verdict"] == "browser_fluency_full_scorecard_partial"

    groups = {group["group_id"]: group for group in scorecard["group_scores"]}
    assert all(group["group_level"] in {"F3", "F4"} for group in groups.values())
    assert groups["vis"]["group_level"] == "F3"
    assert groups["state"]["group_level"] == "F4"
    assert groups["file"]["group_level"] == "F3"
    assert groups["tab"]["group_level"] == "F3"
    assert groups["res"]["group_level"] == "F3"
    assert groups["cog"]["group_level"] == "F3"


def test_browser_fluency_hardened_profile_writes_full_reports(tmp_path: Path, monkeypatch):
    out_dir = tmp_path / "reports"
    monkeypatch.setattr(
        "sys.argv",
        [
            "browser_fluency_runner.py",
            "--profile",
            "hardened_full",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0

    results_path = out_dir / "browser_fluency_full_results.jsonl"
    scorecard_path = out_dir / "browser_fluency_full_scorecard.json"
    markdown_path = out_dir / "browser_fluency_full_scorecard.md"

    assert results_path.exists()
    assert scorecard_path.exists()
    assert markdown_path.exists()

    rows = [json.loads(line) for line in results_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))

    assert len(rows) == 72
    assert scorecard["executed_count"] == 72
    assert scorecard["not_run_count"] == 0
    assert scorecard["verdict"] == "browser_fluency_full_scorecard_partial"
