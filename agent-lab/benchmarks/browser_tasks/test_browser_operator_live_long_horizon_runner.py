from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from browser_operator_live_long_horizon_runner import (
    P4H_AC_MISSIONS,
    build_live_long_horizon_scorecard,
    main,
    run_operator_live_long_horizon,
    wilson_interval,
    write_live_long_horizon_outputs,
)


def test_browser_operator_live_long_horizon_executes_all_missions():
    results = run_operator_live_long_horizon(run_count=1, run_id="test_p4h_ac_live")
    scorecard = build_live_long_horizon_scorecard(results)

    assert len(results) == len(P4H_AC_MISSIONS)
    assert {result.mission_id for result in results} == set(P4H_AC_MISSIONS)
    assert all(result.binary_success for result in results)
    assert scorecard["verdict"] == "browser_operator_live_long_horizon_pass"
    assert scorecard["live_observation_success"] == 1.0
    assert scorecard["false_action_rate"] == 0.0
    assert scorecard["authority_violation_rate"] == 0.0
    assert scorecard["artifact_leakage_rate"] == 0.0


def test_browser_operator_live_long_horizon_repairs_and_recovers():
    results = run_operator_live_long_horizon(run_count=1, run_id="test_p4h_ac_repair")
    failed_first = next(result for result in results if result.mission_id == "BF-LIVE-LONG-005-failed-first-action-repair-continue")
    cross_repair = next(result for result in results if result.mission_id == "BF-LIVE-LONG-009-cross-class-verifier-repair")

    assert failed_first.repaired is True
    assert failed_first.repair_success_rate == 1.0
    assert failed_first.verifier_recovery_rate == 1.0
    assert cross_repair.repaired is True
    assert cross_repair.cross_class_success == 1.0
    assert cross_repair.verifier_recovery_rate == 1.0


def test_browser_operator_live_long_horizon_visual_probe_is_bound():
    results = run_operator_live_long_horizon(run_count=1, run_id="test_p4h_ac_visual")
    visual = next(result for result in results if result.mission_id == "BF-LIVE-LONG-006-visual-crop-zoom-action")

    assert visual.binary_success is True
    assert visual.live_visual_verifier_rate == 1.0
    assert visual.live_observation_success == 1.0
    assert visual.live_artifact_count >= 2
    assert visual.finalgate_pass_rate == 1.0


def test_browser_operator_live_long_horizon_cross_class_and_final_pack():
    results = run_operator_live_long_horizon(run_count=1, run_id="test_p4h_ac_cross")
    e2e = next(result for result in results if result.mission_id == "BF-LIVE-LONG-010-end-to-end-final-artifact-pack")
    js = next(result for result in results if result.mission_id == "BF-LIVE-LONG-007-js-denial-har-alternative")

    assert e2e.final_artifact_pack_rate == 1.0
    assert e2e.cross_class_success == 1.0
    assert e2e.action_envelope_count >= 7
    assert js.denied is True
    assert js.cross_class_success == 1.0
    assert js.authority_violation_rate == 0.0


def test_browser_operator_live_long_horizon_writes_scorecard():
    results = run_operator_live_long_horizon(run_count=1, run_id="test_p4h_ac_write")
    out_dir = Path(__file__).resolve().parent / "tmp_test_outputs" / f"p4hac_write_{uuid4().hex}"
    scorecard = write_live_long_horizon_outputs(results, out_dir)

    assert scorecard["verdict"] == "browser_operator_live_long_horizon_pass"
    assert (out_dir / "browser_operator_live_long_horizon_results.jsonl").exists()
    assert (out_dir / "browser_operator_live_long_horizon_scorecard.json").exists()
    assert (out_dir / "browser_operator_live_long_horizon_scorecard.md").exists()

    rows = [
        json.loads(line)
        for line in (out_dir / "browser_operator_live_long_horizon_results.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(rows) == len(P4H_AC_MISSIONS)
    assert all(row["live_observation_success"] == 1.0 for row in rows)


def test_browser_operator_live_long_horizon_uses_small_n_safe_wilson_interval():
    lower, upper = wilson_interval(1, 1)

    assert 0.0 < lower < 1.0
    assert upper == 1.0


def test_browser_operator_live_long_horizon_cli_writes_reports(monkeypatch):
    out_dir = Path(__file__).resolve().parent / "tmp_test_outputs" / f"p4hac_cli_{uuid4().hex}"
    monkeypatch.setattr(
        "sys.argv",
        [
            "browser_operator_live_long_horizon_runner.py",
            "--run-count",
            "1",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0
    assert (out_dir / "browser_operator_live_long_horizon_results.jsonl").exists()
    assert (out_dir / "browser_operator_live_long_horizon_scorecard.json").exists()
