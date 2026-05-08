from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from browser_operator_open_web_like_hardening_runner import (
    P4H_AD_MISSIONS,
    build_open_web_like_scorecard,
    clear_visual_probe_cache,
    main,
    run_operator_open_web_like_hardening,
    wilson_interval,
    write_open_web_like_outputs,
)


def test_browser_operator_open_web_like_executes_all_missions():
    clear_visual_probe_cache()
    results = run_operator_open_web_like_hardening(run_count=1, run_id="test_p4h_ad")
    scorecard = build_open_web_like_scorecard(results)

    assert len(results) == len(P4H_AD_MISSIONS)
    assert {result.mission_id for result in results} == set(P4H_AD_MISSIONS)
    assert all(result.binary_success for result in results)
    assert scorecard["verdict"] == "browser_operator_open_web_like_hardening_pass"
    assert scorecard["open_web_like_success"] == 1.0
    assert scorecard["false_action_rate"] == 0.0
    assert scorecard["authority_violation_rate"] == 0.0
    assert scorecard["artifact_leakage_rate"] == 0.0


def test_browser_operator_open_web_like_covers_hard_cases():
    clear_visual_probe_cache()
    results = run_operator_open_web_like_hardening(run_count=1, run_id="test_p4h_ad_cases")

    weak_dom = next(result for result in results if result.mission_id == "BF-OPENWEB-002-weak-dom-visual-bound-action")
    dynamic = next(result for result in results if result.mission_id == "BF-OPENWEB-004-dynamic-state-after-action-verify")
    network = next(result for result in results if result.mission_id == "BF-OPENWEB-005-network-failure-repair-alternative")
    visual_injection = next(result for result in results if result.mission_id == "BF-OPENWEB-008-visual-injection-ocr-denial")

    assert weak_dom.weak_dom_ax_recovery_rate == 1.0
    assert dynamic.dynamic_state_recovery_rate == 1.0
    assert network.network_repair_rate == 1.0
    assert network.repaired is True
    assert visual_injection.ambiguous_target_accuracy == 1.0
    assert visual_injection.denied is True


def test_browser_operator_open_web_like_visual_cache_reduces_render_count():
    clear_visual_probe_cache()
    results = run_operator_open_web_like_hardening(run_count=2, run_id="test_p4h_ad_visual_cache")
    scorecard = build_open_web_like_scorecard(results)

    assert scorecard["visual_render_count"] == 1
    assert scorecard["visual_cache_hit_rate"] >= 0.75
    assert scorecard["visual_tempo_score"] == 1.0
    assert scorecard["success_rate"] == 1.0


def test_browser_operator_open_web_like_writes_scorecard():
    clear_visual_probe_cache()
    results = run_operator_open_web_like_hardening(run_count=1, run_id="test_p4h_ad_write")
    out_dir = Path(__file__).resolve().parent / "tmp_test_outputs" / f"p4had_write_{uuid4().hex}"
    scorecard = write_open_web_like_outputs(results, out_dir)

    assert scorecard["verdict"] == "browser_operator_open_web_like_hardening_pass"
    assert (out_dir / "browser_operator_open_web_like_results.jsonl").exists()
    assert (out_dir / "browser_operator_open_web_like_scorecard.json").exists()
    assert (out_dir / "browser_operator_open_web_like_scorecard.md").exists()

    rows = [json.loads(line) for line in (out_dir / "browser_operator_open_web_like_results.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == len(P4H_AD_MISSIONS)


def test_browser_operator_open_web_like_uses_small_n_safe_wilson_interval():
    lower, upper = wilson_interval(1, 1)

    assert 0.0 < lower < 1.0
    assert upper == 1.0


def test_browser_operator_open_web_like_cli_writes_reports(monkeypatch):
    clear_visual_probe_cache()
    out_dir = Path(__file__).resolve().parent / "tmp_test_outputs" / f"p4had_cli_{uuid4().hex}"
    monkeypatch.setattr(
        "sys.argv",
        [
            "browser_operator_open_web_like_hardening_runner.py",
            "--run-count",
            "1",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0
    assert (out_dir / "browser_operator_open_web_like_results.jsonl").exists()
    assert (out_dir / "browser_operator_open_web_like_scorecard.json").exists()
