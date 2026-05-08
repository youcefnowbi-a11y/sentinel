from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from browser_operator_cross_class_runner import (
    DENIAL_MISSIONS,
    P4H_AA_MISSIONS,
    build_v3_action_routing_scorecard,
    main,
    run_v3_action_routing,
    wilson_interval,
    write_v3_action_routing_outputs,
)


def test_v3_action_routing_executes_all_missions():
    results = run_v3_action_routing(run_count=1, run_id="test_p4h_aa_routing")
    scorecard = build_v3_action_routing_scorecard(results)

    assert len(results) == len(P4H_AA_MISSIONS)
    assert {result.mission_id for result in results} == set(P4H_AA_MISSIONS)
    assert all(result.binary_success for result in results)
    assert scorecard["verdict"] == "browser_v3_action_engine_routing_pass"
    assert scorecard["v3_receipt_completeness"] == 1.0
    assert scorecard["finalgate_pass_rate"] == 1.0
    assert scorecard["false_action_rate"] == 0.0


def test_v3_action_routing_has_cross_class_flow_and_denials():
    results = run_v3_action_routing(run_count=1, run_id="test_p4h_aa_cross_denial")
    cross = next(result for result in results if result.mission_id == "BF-V3ACT-009-cross-class-authority-flow")
    denials = [result for result in results if result.mission_id in DENIAL_MISSIONS]

    assert cross.cross_class_success == 1.0
    assert cross.action_envelope_count >= 5
    assert all(result.denied for result in denials)
    assert all(result.denial_correctness == 1.0 for result in denials)


def test_v3_action_routing_writes_scorecard():
    results = run_v3_action_routing(run_count=1, run_id="test_p4h_aa_write")
    out_dir = Path(__file__).resolve().parent / "tmp_test_outputs" / f"cross_write_{uuid4().hex}"
    scorecard = write_v3_action_routing_outputs(results, out_dir)

    assert scorecard["verdict"] == "browser_v3_action_engine_routing_pass"
    assert (out_dir / "browser_v3_action_routing_results.jsonl").exists()
    assert (out_dir / "browser_v3_action_routing_scorecard.json").exists()
    assert (out_dir / "browser_v3_action_routing_scorecard.md").exists()

    rows = [json.loads(line) for line in (out_dir / "browser_v3_action_routing_results.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == len(P4H_AA_MISSIONS)


def test_v3_action_routing_uses_small_n_safe_wilson_interval():
    lower, upper = wilson_interval(1, 1)

    assert 0.0 < lower < 1.0
    assert upper == 1.0


def test_v3_action_routing_cli_writes_reports(monkeypatch):
    out_dir = Path(__file__).resolve().parent / "tmp_test_outputs" / f"cross_cli_{uuid4().hex}"
    monkeypatch.setattr(
        "sys.argv",
        [
            "browser_operator_cross_class_runner.py",
            "--run-count",
            "1",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0
    assert (out_dir / "browser_v3_action_routing_results.jsonl").exists()
    assert (out_dir / "browser_v3_action_routing_scorecard.json").exists()
