from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from browser_operator_trial_runner import (
    OPERATOR_MISSIONS,
    build_operator_scorecard,
    main,
    run_operator_trial,
    wilson_interval,
    write_operator_outputs,
)


def test_browser_operator_trial_executes_perception_action_loop():
    results = run_operator_trial(run_count=2, run_id="test_p4h_y_operator_trial")
    scorecard = build_operator_scorecard(results)

    assert len(results) == len(OPERATOR_MISSIONS) * 2
    assert {result.mission_id for result in results} == set(OPERATOR_MISSIONS)
    assert all(result.binary_success for result in results)
    assert scorecard["verdict"] == "browser_operator_trial_pass"
    assert scorecard["success_rate"] == 1.0
    assert scorecard["authority_correctness"] == 1.0
    assert scorecard["false_action_rate"] == 0.0
    assert scorecard["ref_validity_rate"] == 1.0


def test_browser_operator_trial_denies_ocr_and_out_of_policy_without_execution():
    results = run_operator_trial(run_count=1, run_id="test_p4h_y_operator_denials")
    ocr = next(result for result in results if result.mission_id == "BF-OP-004-deny-ocr-only-target")
    out_of_policy = next(result for result in results if result.mission_id == "BF-OP-005-deny-out-of-policy-action")

    assert ocr.binary_success is True
    assert ocr.executed is False
    assert ocr.denial_correct is True
    assert ocr.false_action_rate == 0.0
    assert out_of_policy.binary_success is True
    assert out_of_policy.executed is False
    assert out_of_policy.denial_correct is True
    assert out_of_policy.false_action_rate == 0.0


def test_browser_operator_trial_records_repair_success():
    results = run_operator_trial(run_count=1, run_id="test_p4h_y_operator_repair")
    repair = next(result for result in results if result.mission_id == "BF-OP-003-repair-stale-ref")

    assert repair.binary_success is True
    assert repair.repair_attempted is True
    assert repair.repair_success_rate == 1.0
    assert "stale_ref_rejected_then_repaired" in repair.notes


def test_browser_operator_trial_writes_scorecard():
    results = run_operator_trial(run_count=1, run_id="test_p4h_y_operator_write")
    out_dir = Path(__file__).resolve().parent / "tmp_test_outputs" / f"trial_write_{uuid4().hex}"
    scorecard = write_operator_outputs(results, out_dir)

    assert scorecard["verdict"] == "browser_operator_trial_pass"
    assert (out_dir / "browser_operator_trial_results.jsonl").exists()
    assert (out_dir / "browser_operator_trial_scorecard.json").exists()
    assert (out_dir / "browser_operator_trial_scorecard.md").exists()

    rows = [json.loads(line) for line in (out_dir / "browser_operator_trial_results.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == len(OPERATOR_MISSIONS)


def test_browser_operator_trial_uses_small_n_safe_wilson_interval():
    lower, upper = wilson_interval(2, 2)

    assert 0.0 < lower < 1.0
    assert upper == 1.0


def test_browser_operator_trial_cli_writes_reports(monkeypatch):
    out_dir = Path(__file__).resolve().parent / "tmp_test_outputs" / f"trial_cli_{uuid4().hex}"
    monkeypatch.setattr(
        "sys.argv",
        [
            "browser_operator_trial_runner.py",
            "--run-count",
            "1",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0
    assert (out_dir / "browser_operator_trial_results.jsonl").exists()
    assert (out_dir / "browser_operator_trial_scorecard.json").exists()
