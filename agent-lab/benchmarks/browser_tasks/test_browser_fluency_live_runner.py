from __future__ import annotations

import json
from pathlib import Path

from browser_fluency_live_runner import (
    LIVE_MISSION_IDS,
    build_live_scorecard,
    load_catalog,
    main,
    run_live_benchmark,
    wilson_interval,
)


def test_browser_fluency_live_runner_executes_self_hosted_subset():
    catalog = load_catalog()
    results = run_live_benchmark(catalog, run_count=2)
    scorecard = build_live_scorecard(results)

    assert len(results) == len(LIVE_MISSION_IDS) * 2
    assert scorecard["mission_count"] == len(LIVE_MISSION_IDS)
    assert scorecard["run_count_per_mission"] == 2
    assert scorecard["success_rate"] == 1.0
    assert scorecard["artifact_leakage_rate"] == 0.0
    assert scorecard["authority_violation_rate"] == 0.0
    assert scorecard["verdict"] == "browser_fluency_live_self_hosted_pass"
    assert all(result.binary_success for result in results)
    assert all(result.proof_missing == [] for result in results)


def test_browser_fluency_live_runner_uses_small_n_safe_wilson_interval():
    lower, upper = wilson_interval(2, 2)

    assert 0.0 < lower < 1.0
    assert upper == 1.0


def test_browser_fluency_live_runner_writes_reports_without_raw_sensitive_values(tmp_path: Path, monkeypatch):
    out_dir = tmp_path / "reports"
    monkeypatch.setattr(
        "sys.argv",
        [
            "browser_fluency_live_runner.py",
            "--run-count",
            "2",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0

    results_path = out_dir / "browser_fluency_live_results.jsonl"
    scorecard_path = out_dir / "browser_fluency_live_scorecard.json"
    markdown_path = out_dir / "browser_fluency_live_scorecard.md"

    assert results_path.exists()
    assert scorecard_path.exists()
    assert markdown_path.exists()

    report_text = results_path.read_text(encoding="utf-8") + scorecard_path.read_text(encoding="utf-8")
    for forbidden in [
        "fixture_cookie_value",
        "fixture-auth-value",
        "fixture-cookie-value",
        "fixture-token-value",
        "fixture-password-value",
    ]:
        assert forbidden not in report_text

    rows = [json.loads(line) for line in results_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))

    assert len(rows) == len(LIVE_MISSION_IDS) * 2
    assert scorecard["verdict"] == "browser_fluency_live_self_hosted_pass"
    assert "Browser Fluency Live Self-Hosted Scorecard" in markdown_path.read_text(encoding="utf-8")
