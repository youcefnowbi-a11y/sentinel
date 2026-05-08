from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from sentinel.agent.browser import (
    BrowserPeerBenchmarkCampaign,
    BrowserPeerBenchmarkVerdict,
    BrowserPeerComparisonMode,
    BrowserPeerRuntimeProfile,
    BrowserSelfHostedTaskGroup,
)


def workspace(name: str) -> Path:
    path = Path("w") / f"{name[:2]}_{uuid4().hex[:6]}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_p4f_profiled_peer_campaign_is_lab_only_and_honest():
    root = workspace("profiled")
    try:
        report = BrowserPeerBenchmarkCampaign(project_root=root, iterations=3).run()

        assert report.comparison_mode == BrowserPeerComparisonMode.PROFILED_LAB_BASELINE
        assert report.product_vendor_runtime_imported is False
        assert report.real_peer_runtime_executed is False
        assert report.same_task_corpus is True
        assert report.same_timeout is True
        assert report.same_scoring is True
        assert report.same_run_count is True
        assert report.task_count == len(BrowserSelfHostedTaskGroup)
        assert report.verdict == BrowserPeerBenchmarkVerdict.EXTERNAL_OPEN_WEB_CAMPAIGN_REQUIRED
        assert report.summary.sentinel_governed_quality > report.summary.peer_governed_quality
        assert report.summary.peer_raw_runtime_breadth_score > report.summary.sentinel_raw_runtime_breadth_score
        assert any("real lab-only peer runner" in item for item in report.remaining_work)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_p4f_real_peer_profile_keeps_raw_runtime_verdict_separate():
    root = workspace("real_peer")
    profile = BrowserPeerRuntimeProfile(
        comparison_mode=BrowserPeerComparisonMode.REAL_LAB_RUNTIME,
        real_runtime_executed=True,
        raw_runtime_breadth_score=0.96,
    )
    try:
        report = BrowserPeerBenchmarkCampaign(project_root=root, iterations=3, peer_profile=profile).run()

        assert report.real_peer_runtime_executed is True
        assert report.verdict == BrowserPeerBenchmarkVerdict.PEER_STILL_AHEAD_RAW_RUNTIME
        assert report.summary.sentinel_governed_quality > report.summary.peer_governed_quality
        assert report.summary.peer_raw_runtime_breadth_score > report.summary.sentinel_raw_runtime_breadth_score
        assert {comparison.task_group for comparison in report.task_comparisons} == set(BrowserSelfHostedTaskGroup)
        failure_denials = next(
            comparison for comparison in report.task_comparisons if comparison.task_group == BrowserSelfHostedTaskGroup.FAILURE_DENIALS
        )
        assert failure_denials.failure_category == "peer_policy_denial_gap"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_p4f_30run_scorecard_is_ready_for_external_campaign_not_supremacy_claim():
    root = workspace("run30")
    try:
        report = BrowserPeerBenchmarkCampaign(project_root=root, iterations=30).run()

        assert report.iterations == 30
        assert report.task_count == 13
        assert report.sentinel_report_verdict == "browser_ready_for_peer_campaign"
        assert report.verdict == BrowserPeerBenchmarkVerdict.EXTERNAL_OPEN_WEB_CAMPAIGN_REQUIRED
        assert report.summary.sentinel_raw_task_completion == 1.0
        assert report.summary.sentinel_governed_quality == 1.0
        assert report.summary.peer_governed_quality < report.summary.sentinel_governed_quality
        assert report.summary.artifact_leakage_delta < 0.0
        assert report.summary.authority_violation_delta < 0.0
        assert all(comparison.run_count == 30 for comparison in report.task_comparisons)
    finally:
        shutil.rmtree(root, ignore_errors=True)
