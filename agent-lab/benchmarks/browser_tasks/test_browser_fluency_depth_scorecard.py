from __future__ import annotations

import json
from pathlib import Path

from browser_fluency_runner import build_scorecard, load_catalog, main, run_fluency


P4H_T_HARDENED_MISSIONS = {
    "BF-LIFE-004",
    "BF-NAV-005",
    "BF-VIS-004",
    "BF-VIS-005",
    "BF-FORM-003",
    "BF-FILE-006",
    "BF-NET-006",
    "BF-TAB-001",
    "BF-TAB-002",
    "BF-TAB-005",
    "BF-TAB-006",
    "BF-RES-002",
    "BF-RES-003",
    "BF-RES-004",
    "BF-SAFE-004",
    "BF-COG-001",
    "BF-COG-005",
    "BF-COG-006",
}


def all_groups(catalog: dict) -> list[str]:
    return [group["id"] for group in catalog["groups"]]


def test_browser_fluency_depth_profile_meets_all_72_mission_targets():
    catalog = load_catalog()
    results = run_fluency(catalog, groups=all_groups(catalog), profile="depth_hardened")
    scorecard = build_scorecard(results)

    assert len(results) == 72
    assert scorecard["run_id"] == "p4h_t_depth_scorecard"
    assert scorecard["executed_count"] == 72
    assert scorecard["not_run_count"] == 0
    assert scorecard["partial_count"] == 0
    assert scorecard["target_met_count"] == 72
    assert scorecard["target_met_rate_executed"] == 1.0
    assert scorecard["verdict"] == "browser_fluency_depth_contract_ready"

    rows = {result.mission_id: result for result in results}
    for mission_id in P4H_T_HARDENED_MISSIONS:
        assert rows[mission_id].mission_status == "target_met"
        assert rows[mission_id].proof_missing == []


def test_browser_fluency_depth_profile_writes_depth_reports(tmp_path: Path, monkeypatch):
    out_dir = tmp_path / "reports"
    monkeypatch.setattr(
        "sys.argv",
        [
            "browser_fluency_runner.py",
            "--profile",
            "depth_hardened",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0

    results_path = out_dir / "browser_fluency_depth_results.jsonl"
    scorecard_path = out_dir / "browser_fluency_depth_scorecard.json"
    markdown_path = out_dir / "browser_fluency_depth_scorecard.md"

    assert results_path.exists()
    assert scorecard_path.exists()
    assert markdown_path.exists()

    rows = [json.loads(line) for line in results_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))

    assert len(rows) == 72
    assert scorecard["executed_count"] == 72
    assert scorecard["target_met_count"] == 72
    assert scorecard["partial_count"] == 0
    assert scorecard["verdict"] == "browser_fluency_depth_contract_ready"
    assert "Browser Fluency Depth Scorecard" in markdown_path.read_text(encoding="utf-8")
