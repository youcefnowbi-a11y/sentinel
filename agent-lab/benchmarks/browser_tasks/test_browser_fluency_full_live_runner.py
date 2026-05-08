from __future__ import annotations

import json
from pathlib import Path

from browser_fluency_live_runner import _MISSION_HANDLERS, build_live_scorecard, load_catalog, main, run_live_benchmark


def all_mission_ids(catalog: dict) -> list[str]:
    return [mission["id"] for group in catalog["groups"] for mission in group["missions"]]


def test_browser_fluency_full_live_runner_has_handler_for_every_catalog_mission():
    catalog = load_catalog()

    assert set(all_mission_ids(catalog)) == set(_MISSION_HANDLERS)


def test_browser_fluency_full_live_runner_executes_all_72_missions():
    catalog = load_catalog()
    results = run_live_benchmark(catalog, run_count=1, scope="full")
    scorecard = build_live_scorecard(results)

    assert len(results) == 72
    assert scorecard["run_id"] == "p4h_v_full_live_self_hosted_30run"
    assert scorecard["mission_count"] == 72
    assert scorecard["run_count_per_mission"] == 1
    assert scorecard["total_iterations"] == 72
    assert scorecard["success_rate"] == 1.0
    assert scorecard["artifact_leakage_rate"] == 0.0
    assert scorecard["authority_violation_rate"] == 0.0
    assert scorecard["verdict"] == "browser_fluency_full_live_self_hosted_pass"
    assert all(result.binary_success for result in results)
    assert all(result.proof_missing == [] for result in results)


def test_browser_fluency_full_live_runner_writes_full_reports(tmp_path: Path, monkeypatch):
    out_dir = tmp_path / "reports"
    monkeypatch.setattr(
        "sys.argv",
        [
            "browser_fluency_live_runner.py",
            "--scope",
            "full",
            "--run-count",
            "1",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0

    results_path = out_dir / "browser_fluency_live_full_results.jsonl"
    scorecard_path = out_dir / "browser_fluency_live_full_scorecard.json"
    markdown_path = out_dir / "browser_fluency_live_full_scorecard.md"

    assert results_path.exists()
    assert scorecard_path.exists()
    assert markdown_path.exists()

    rows = [json.loads(line) for line in results_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
    report_text = results_path.read_text(encoding="utf-8") + scorecard_path.read_text(encoding="utf-8")

    assert len(rows) == 72
    assert scorecard["verdict"] == "browser_fluency_full_live_self_hosted_pass"
    assert "Browser Fluency Full Live Self-Hosted Scorecard" in markdown_path.read_text(encoding="utf-8")
    for forbidden in [
        "fixture_cookie_value",
        "fixture-auth-value",
        "fixture-cookie-value",
        "fixture-token-value",
        "fixture-password-value",
        "fixture-login-secret",
    ]:
        assert forbidden not in report_text
