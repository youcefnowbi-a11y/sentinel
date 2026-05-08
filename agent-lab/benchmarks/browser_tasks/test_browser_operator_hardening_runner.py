from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from browser_operator_hardening_runner import (
    HARDENING_MISSIONS,
    build_hardening_scorecard,
    main,
    run_operator_hardening,
    wilson_interval,
    write_hardening_outputs,
)


def test_browser_operator_hardening_executes_all_missions():
    results = run_operator_hardening(run_count=2, run_id="test_p4h_z_hardening")
    scorecard = build_hardening_scorecard(results)

    assert len(results) == len(HARDENING_MISSIONS) * 2
    assert {result.mission_id for result in results} == set(HARDENING_MISSIONS)
    assert all(result.binary_success for result in results)
    assert scorecard["verdict"] == "browser_operator_hardening_pass"
    assert scorecard["false_action_rate"] == 0.0
    assert scorecard["authority_correctness"] == 1.0


def test_browser_operator_hardening_repairs_failed_verifier():
    results = run_operator_hardening(run_count=1, run_id="test_p4h_z_repair")
    repair = next(result for result in results if result.mission_id == "BF-HARD-004-failed-verifier-repair-loop")

    assert repair.binary_success is True
    assert repair.repaired is True
    assert repair.repair_success_rate == 1.0
    assert repair.verifier_recovery_rate == 1.0


def test_browser_operator_hardening_handles_ambiguous_targets_and_denials():
    results = run_operator_hardening(run_count=1, run_id="test_p4h_z_ambiguous")
    ambiguous = next(result for result in results if result.mission_id == "BF-HARD-001-ambiguous-context-target")
    low_confidence = next(result for result in results if result.mission_id == "BF-HARD-002-low-confidence-ambiguous-reject")
    budget = next(result for result in results if result.mission_id == "BF-HARD-006-step-budget-pressure-reject")
    ocr = next(result for result in results if result.mission_id == "BF-HARD-007-visual-ocr-ref-denial")

    assert ambiguous.ambiguous_target_accuracy == 1.0
    assert ambiguous.executed is True
    assert low_confidence.denied is True
    assert budget.denied is True
    assert budget.budget_enforcement_rate == 1.0
    assert ocr.denied is True
    assert ocr.false_action_rate == 0.0


def test_browser_operator_hardening_writes_scorecard():
    results = run_operator_hardening(run_count=1, run_id="test_p4h_z_write")
    out_dir = Path(__file__).resolve().parent / "tmp_test_outputs" / f"hardening_write_{uuid4().hex}"
    scorecard = write_hardening_outputs(results, out_dir)

    assert scorecard["verdict"] == "browser_operator_hardening_pass"
    assert (out_dir / "browser_operator_hardening_results.jsonl").exists()
    assert (out_dir / "browser_operator_hardening_scorecard.json").exists()
    assert (out_dir / "browser_operator_hardening_scorecard.md").exists()

    rows = [json.loads(line) for line in (out_dir / "browser_operator_hardening_results.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == len(HARDENING_MISSIONS)


def test_browser_operator_hardening_uses_small_n_safe_wilson_interval():
    lower, upper = wilson_interval(2, 2)

    assert 0.0 < lower < 1.0
    assert upper == 1.0


def test_browser_operator_hardening_cli_writes_reports(monkeypatch):
    out_dir = Path(__file__).resolve().parent / "tmp_test_outputs" / f"hardening_cli_{uuid4().hex}"
    monkeypatch.setattr(
        "sys.argv",
        [
            "browser_operator_hardening_runner.py",
            "--run-count",
            "1",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0
    assert (out_dir / "browser_operator_hardening_results.jsonl").exists()
    assert (out_dir / "browser_operator_hardening_scorecard.json").exists()
