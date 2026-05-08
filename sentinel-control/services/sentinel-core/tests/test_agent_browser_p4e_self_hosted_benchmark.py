from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from sentinel.agent.browser import (
    BrowserPeerRunnerProtocol,
    BrowserSelfHostedBenchmarkFamily,
    BrowserSelfHostedBenchmarkGate,
    BrowserSelfHostedTaskGroup,
)


def workspace(name: str) -> Path:
    path = Path("w") / f"{name[:2]}_{uuid4().hex[:6]}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_p4e_cases_cover_self_hosted_browser_task_corpus():
    root = workspace("cases")
    gate = BrowserSelfHostedBenchmarkGate(project_root=root, iterations=1, use_live_harness=False)

    try:
        groups = {case.user_input["task_group"] for case in gate.cases()}

        assert groups == {group.value for group in BrowserSelfHostedTaskGroup}
        assert len(gate.cases()) == 13
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_p4e_peer_runner_protocol_is_lab_only_and_metric_complete():
    protocol = BrowserPeerRunnerProtocol()

    assert protocol.same_task_corpus_required is True
    assert protocol.same_timeout_required is True
    assert protocol.same_scoring_required is True
    assert protocol.product_runtime_import_allowed is False
    assert protocol.lab_only is True
    assert "mission_success_score" in protocol.required_metrics
    assert "authority_violation_rate" in protocol.required_metrics
    assert "wilson_interval" in protocol.required_metrics


def test_p4e_self_hosted_benchmark_dry_run_reports_scientific_metrics():
    root = workspace("dry_run")
    try:
        report = BrowserSelfHostedBenchmarkGate(project_root=root, iterations=3, use_live_harness=False).run()

        assert report.suite_accepted is True
        assert report.task_count == len(BrowserSelfHostedTaskGroup)
        assert report.iterations == 3
        assert report.verdict == "browser_benchmark_dry_run_only"
        assert report.mission_success_score == 1.0
        assert report.trace_quality == 1.0
        assert report.proof_completeness == 1.0
        assert report.artifact_leakage_rate == 0.0
        assert report.authority_violation_rate == 0.0
        assert {score.task_group for score in report.scores} == set(BrowserSelfHostedTaskGroup)
        for score in report.scores:
            assert score.run_count == 3
            assert score.success_rate == 1.0
            assert score.success_rate_ci95_lower < 1.0
            assert score.confidence_interval_method == "wilson_score_95"
            assert score.latency_ms_p50 >= 0.0
            assert score.latency_ms_p95 >= score.latency_ms_p50
            assert score.step_count_p50 > 0.0
            assert score.step_count_p95 >= score.step_count_p50
            assert score.unstable_iterations == []
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_p4e_30run_scorecard_reaches_peer_campaign_gate():
    root = workspace("run30")
    try:
        report = BrowserSelfHostedBenchmarkGate(project_root=root, iterations=30, use_live_harness=False).run()

        assert report.suite_accepted is True
        assert report.verdict == "browser_ready_for_peer_campaign"
        assert report.mission_success_score == 1.0
        assert report.side_effect_containment == 1.0
        assert report.artifact_leakage_rate == 0.0
        assert report.authority_violation_rate == 0.0

        families = {score.family for score in report.scores}
        assert BrowserSelfHostedBenchmarkFamily.WEB_ARENA_STYLE in families
        assert BrowserSelfHostedBenchmarkFamily.VISUAL_GROUNDING in families
        assert BrowserSelfHostedBenchmarkFamily.RESEARCH_BROWSING in families
        assert BrowserSelfHostedBenchmarkFamily.V3_AUTHORITY in families
        assert BrowserSelfHostedBenchmarkFamily.ADVERSARIAL_DENIAL in families
        for score in report.scores:
            assert score.run_count == 30
            assert score.success_rate == 1.0
            assert score.success_rate_ci95_lower < 1.0
            assert score.artifact_leakage_rate == 0.0
            assert score.authority_violation_rate == 0.0
    finally:
        shutil.rmtree(root, ignore_errors=True)
