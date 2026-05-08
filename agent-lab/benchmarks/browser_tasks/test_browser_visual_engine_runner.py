from __future__ import annotations

import pytest

from browser_visual_engine_runner import (
    BrowserVisualEngineUnavailable,
    build_visual_scorecard,
    run_visual_engine_benchmark,
    write_visual_outputs,
)


def test_visual_engine_runner_executes_all_visual_missions(tmp_path):
    try:
        results = run_visual_engine_benchmark(run_count=1, run_id="test_p4h_w_visual_engine")
    except BrowserVisualEngineUnavailable as exc:
        pytest.skip(f"Playwright visual backend unavailable: {exc}")

    assert len(results) == 6
    assert {result.mission_id for result in results} == {
        "BF-VIS-001",
        "BF-VIS-002",
        "BF-VIS-003",
        "BF-VIS-004",
        "BF-VIS-005",
        "BF-VIS-006",
    }
    assert all(result.binary_success for result in results)
    assert all(result.final_gate_passed for result in results)
    assert all(result.stable_ref_bound for result in results)
    assert all(result.ocr_authority_blocked for result in results)
    assert all(result.screenshot_sha256 and result.crop_sha256 for result in results)

    scorecard = build_visual_scorecard(results)

    assert scorecard["verdict"] == "browser_visual_engine_local_pass"
    assert scorecard["success_rate"] == 1.0
    assert scorecard["wilson_lower"] < 1.0

    written = write_visual_outputs(results, tmp_path)

    assert written["verdict"] == "browser_visual_engine_local_pass"
    assert (tmp_path / "browser_visual_engine_results.jsonl").exists()
    assert (tmp_path / "browser_visual_engine_scorecard.json").exists()
    assert (tmp_path / "browser_visual_engine_scorecard.md").exists()


def test_visual_engine_repair_mission_rejects_ocr_only_ref():
    try:
        results = run_visual_engine_benchmark(run_count=1, run_id="test_p4h_w_visual_repair")
    except BrowserVisualEngineUnavailable as exc:
        pytest.skip(f"Playwright visual backend unavailable: {exc}")

    repair = next(result for result in results if result.mission_id == "BF-VIS-006")

    assert repair.binary_success is True
    assert repair.repair_quality == 1.0
    assert repair.stale_ref_rejected is True
    assert "OCR-only target" in repair.notes
