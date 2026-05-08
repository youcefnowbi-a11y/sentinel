from __future__ import annotations

import json
from pathlib import Path

from browser_fluency_runner import DEFAULT_GROUPS, build_scorecard, load_catalog, main, run_fluency


def test_browser_fluency_runner_loads_catalog_and_executes_critical_subset():
    catalog = load_catalog()
    results = run_fluency(catalog, groups=DEFAULT_GROUPS)

    executed = [result for result in results if result.mission_status != "not_run"]
    not_run = [result for result in results if result.mission_status == "not_run"]

    assert len(results) == 72
    assert len(executed) == 42
    assert len(not_run) == 30
    assert {result.group_id for result in executed} == set(DEFAULT_GROUPS)
    assert all(result.execution_mode == "contract_fixture" for result in executed)
    assert any(result.mission_status == "partial" for result in executed)


def test_browser_fluency_scorecard_reports_f0_f5_group_levels():
    catalog = load_catalog()
    results = run_fluency(catalog, groups=DEFAULT_GROUPS)
    scorecard = build_scorecard(results)

    assert scorecard["schema_version"] == "browser_fluency_scorecard.v1"
    assert scorecard["catalog_mission_count"] == 72
    assert scorecard["executed_count"] == 42
    assert scorecard["not_run_count"] == 30
    assert scorecard["verdict"] == "browser_fluency_first_subset_partial"
    assert scorecard["metric_summary"]["authority_correctness"] > 0.9
    assert scorecard["metric_summary"]["proof_completeness"] > 0.8

    groups = {group["group_id"]: group for group in scorecard["group_scores"]}
    assert groups["life"]["group_level"] == "F2"
    assert groups["form"]["group_level"] == "F1"
    assert groups["net"]["group_level"] == "F2"
    assert groups["safe"]["group_level"] == "F1"
    assert groups["vis"]["group_level"] == "F0"


def test_browser_fluency_runner_writes_reports(tmp_path: Path, monkeypatch):
    out_dir = tmp_path / "reports"
    monkeypatch.setattr(
        "sys.argv",
        [
            "browser_fluency_runner.py",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0

    results_path = out_dir / "browser_fluency_first_results.jsonl"
    scorecard_path = out_dir / "browser_fluency_first_scorecard.json"
    markdown_path = out_dir / "browser_fluency_first_scorecard.md"

    assert results_path.exists()
    assert scorecard_path.exists()
    assert markdown_path.exists()

    rows = [json.loads(line) for line in results_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))

    assert len(rows) == 72
    assert scorecard["executed_count"] == 42
    assert "Browser Fluency First Scorecard" in markdown_path.read_text(encoding="utf-8")
