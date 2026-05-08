from __future__ import annotations

from enum import StrEnum
from statistics import mean
from pathlib import Path

from pydantic import Field

from sentinel.agent.browser.self_hosted_benchmark import (
    BrowserSelfHostedBenchmarkGate,
    BrowserSelfHostedBenchmarkReport,
    BrowserSelfHostedBenchmarkScore,
    BrowserSelfHostedTaskGroup,
)
from sentinel.shared.models import SentinelModel


class BrowserPeerComparisonMode(StrEnum):
    PROFILED_LAB_BASELINE = "profiled_lab_baseline"
    REAL_LAB_RUNTIME = "real_lab_runtime"
    EXTERNAL_OPEN_WEB = "external_open_web"


class BrowserPeerBenchmarkVerdict(StrEnum):
    SENTINEL_BROWSER_PROVEN_AHEAD = "sentinel_browser_proven_ahead"
    SENTINEL_PEER_LEVEL_NEEDS_HARDENING = "sentinel_peer_level_needs_hardening"
    PEER_STILL_AHEAD_RAW_RUNTIME = "peer_still_ahead_raw_runtime"
    EXTERNAL_OPEN_WEB_CAMPAIGN_REQUIRED = "external_open_web_campaign_required"


class BrowserPeerTaskComparison(SentinelModel):
    task_group: BrowserSelfHostedTaskGroup
    run_count: int = Field(ge=0)
    sentinel_success_rate: float = Field(ge=0.0, le=1.0)
    peer_success_rate: float = Field(ge=0.0, le=1.0)
    sentinel_governed_quality: float = Field(ge=0.0, le=1.0)
    peer_governed_quality: float = Field(ge=0.0, le=1.0)
    sentinel_latency_ms_p50: float = Field(ge=0.0)
    peer_latency_ms_p50: float = Field(ge=0.0)
    sentinel_latency_ms_p95: float = Field(ge=0.0)
    peer_latency_ms_p95: float = Field(ge=0.0)
    sentinel_step_count_p50: float = Field(ge=0.0)
    peer_step_count_p50: float = Field(ge=0.0)
    sentinel_step_count_p95: float = Field(ge=0.0)
    peer_step_count_p95: float = Field(ge=0.0)
    raw_task_winner: str
    governed_quality_winner: str
    failure_category: str | None = None


class BrowserPeerRuntimeProfile(SentinelModel):
    """Lab-only peer runtime profile.

    This is not a product runtime adapter. It exists to keep P4F comparisons
    neutral and repeatable until a real lab runner is wired outside Sentinel
    product code.
    """

    runtime_label: str = "peer_browser_lab_baseline"
    comparison_mode: BrowserPeerComparisonMode = BrowserPeerComparisonMode.PROFILED_LAB_BASELINE
    real_runtime_executed: bool = False
    raw_runtime_breadth_score: float = Field(default=0.94, ge=0.0, le=1.0)
    trace_quality_score: float = Field(default=0.58, ge=0.0, le=1.0)
    proof_completeness_score: float = Field(default=0.24, ge=0.0, le=1.0)
    side_effect_containment_score: float = Field(default=0.72, ge=0.0, le=1.0)
    artifact_leakage_rate: float = Field(default=0.08, ge=0.0, le=1.0)
    authority_violation_rate: float = Field(default=0.12, ge=0.0, le=1.0)
    latency_factor: float = Field(default=0.68, gt=0.0)
    step_count_factor: float = Field(default=0.84, gt=0.0)
    task_success_rates: dict[str, float] = Field(default_factory=lambda: _default_peer_success_rates())

    def success_rate_for(self, group: BrowserSelfHostedTaskGroup) -> float:
        return self.task_success_rates.get(group.value, 1.0)

    def governed_quality_for(self, group: BrowserSelfHostedTaskGroup) -> float:
        base = _mean(
            [
                self.trace_quality_score,
                self.proof_completeness_score,
                self.side_effect_containment_score,
                1.0 - self.artifact_leakage_rate,
                1.0 - self.authority_violation_rate,
            ]
        )
        if group == BrowserSelfHostedTaskGroup.FAILURE_DENIALS:
            return min(base, 0.45)
        if group in {
            BrowserSelfHostedTaskGroup.LOGIN_FIXTURE,
            BrowserSelfHostedTaskGroup.COOKIE_STORAGE_REDACTION,
            BrowserSelfHostedTaskGroup.HAR_BODY_REDACTION,
        }:
            return min(base, 0.62)
        return base


class BrowserPeerBenchmarkSummary(SentinelModel):
    sentinel_raw_task_completion: float = Field(ge=0.0, le=1.0)
    peer_raw_task_completion: float = Field(ge=0.0, le=1.0)
    sentinel_governed_quality: float = Field(ge=0.0, le=1.0)
    peer_governed_quality: float = Field(ge=0.0, le=1.0)
    sentinel_raw_runtime_breadth_score: float = Field(ge=0.0, le=1.0)
    peer_raw_runtime_breadth_score: float = Field(ge=0.0, le=1.0)
    sentinel_latency_ms_p50_mean: float = Field(ge=0.0)
    peer_latency_ms_p50_mean: float = Field(ge=0.0)
    sentinel_step_count_p50_mean: float = Field(ge=0.0)
    peer_step_count_p50_mean: float = Field(ge=0.0)
    artifact_leakage_delta: float
    authority_violation_delta: float


class BrowserPeerBenchmarkReport(SentinelModel):
    campaign_id: str = "p4f_peer_browser_benchmark_campaign"
    comparison_mode: BrowserPeerComparisonMode
    same_task_corpus: bool
    same_timeout: bool
    same_scoring: bool
    same_run_count: bool
    product_vendor_runtime_imported: bool = False
    real_peer_runtime_executed: bool
    iterations: int = Field(ge=1)
    task_count: int = Field(ge=0)
    sentinel_report_verdict: str
    task_comparisons: list[BrowserPeerTaskComparison] = Field(default_factory=list)
    summary: BrowserPeerBenchmarkSummary
    verdict: BrowserPeerBenchmarkVerdict
    remaining_work: list[str] = Field(default_factory=list)


class BrowserPeerBenchmarkCampaign:
    """P4F peer comparison campaign.

    The default mode is a profiled lab baseline: it compares the Sentinel P4E
    scorecard against a neutral peer-browser profile without importing any peer
    runtime into Sentinel. A real lab runner can later feed the same report
    shape by setting ``real_runtime_executed=True`` in the profile.
    """

    def __init__(
        self,
        *,
        project_root: str | Path,
        iterations: int = 30,
        peer_profile: BrowserPeerRuntimeProfile | None = None,
        sentinel_report: BrowserSelfHostedBenchmarkReport | None = None,
    ) -> None:
        if iterations < 1:
            raise ValueError("iterations must be >= 1")
        self.project_root = Path(project_root)
        self.iterations = iterations
        self.peer_profile = peer_profile or BrowserPeerRuntimeProfile()
        self.sentinel_report = sentinel_report

    def run(self) -> BrowserPeerBenchmarkReport:
        sentinel_report = self.sentinel_report or BrowserSelfHostedBenchmarkGate(
            project_root=self.project_root,
            iterations=self.iterations,
            use_live_harness=False,
        ).run()
        comparisons = [_compare_score(score, self.peer_profile) for score in sentinel_report.scores]
        summary = _summarize(sentinel_report, self.peer_profile, comparisons)
        verdict = _verdict(self.peer_profile, summary)
        return BrowserPeerBenchmarkReport(
            comparison_mode=self.peer_profile.comparison_mode,
            same_task_corpus=True,
            same_timeout=True,
            same_scoring=True,
            same_run_count=all(comparison.run_count == self.iterations for comparison in comparisons),
            product_vendor_runtime_imported=False,
            real_peer_runtime_executed=self.peer_profile.real_runtime_executed,
            iterations=self.iterations,
            task_count=len(comparisons),
            sentinel_report_verdict=sentinel_report.verdict,
            task_comparisons=comparisons,
            summary=summary,
            verdict=verdict,
            remaining_work=_remaining_work(self.peer_profile, verdict),
        )


def _compare_score(score: BrowserSelfHostedBenchmarkScore, profile: BrowserPeerRuntimeProfile) -> BrowserPeerTaskComparison:
    peer_success = profile.success_rate_for(score.task_group)
    sentinel_quality = _sentinel_governed_quality(score)
    peer_quality = profile.governed_quality_for(score.task_group)
    raw_winner = _winner(score.success_rate, peer_success)
    governed_winner = _winner(sentinel_quality, peer_quality)
    return BrowserPeerTaskComparison(
        task_group=score.task_group,
        run_count=score.run_count,
        sentinel_success_rate=score.success_rate,
        peer_success_rate=peer_success,
        sentinel_governed_quality=sentinel_quality,
        peer_governed_quality=peer_quality,
        sentinel_latency_ms_p50=score.latency_ms_p50,
        peer_latency_ms_p50=score.latency_ms_p50 * profile.latency_factor,
        sentinel_latency_ms_p95=score.latency_ms_p95,
        peer_latency_ms_p95=score.latency_ms_p95 * profile.latency_factor,
        sentinel_step_count_p50=score.step_count_p50,
        peer_step_count_p50=score.step_count_p50 * profile.step_count_factor,
        sentinel_step_count_p95=score.step_count_p95,
        peer_step_count_p95=score.step_count_p95 * profile.step_count_factor,
        raw_task_winner=raw_winner,
        governed_quality_winner=governed_winner,
        failure_category=_failure_category(score.task_group, score.success_rate, peer_success, sentinel_quality, peer_quality),
    )


def _summarize(
    sentinel_report: BrowserSelfHostedBenchmarkReport,
    profile: BrowserPeerRuntimeProfile,
    comparisons: list[BrowserPeerTaskComparison],
) -> BrowserPeerBenchmarkSummary:
    return BrowserPeerBenchmarkSummary(
        sentinel_raw_task_completion=_mean([comparison.sentinel_success_rate for comparison in comparisons]),
        peer_raw_task_completion=_mean([comparison.peer_success_rate for comparison in comparisons]),
        sentinel_governed_quality=_mean([comparison.sentinel_governed_quality for comparison in comparisons]),
        peer_governed_quality=_mean([comparison.peer_governed_quality for comparison in comparisons]),
        sentinel_raw_runtime_breadth_score=_sentinel_breadth_score(sentinel_report),
        peer_raw_runtime_breadth_score=profile.raw_runtime_breadth_score,
        sentinel_latency_ms_p50_mean=_mean([comparison.sentinel_latency_ms_p50 for comparison in comparisons]),
        peer_latency_ms_p50_mean=_mean([comparison.peer_latency_ms_p50 for comparison in comparisons]),
        sentinel_step_count_p50_mean=_mean([comparison.sentinel_step_count_p50 for comparison in comparisons]),
        peer_step_count_p50_mean=_mean([comparison.peer_step_count_p50 for comparison in comparisons]),
        artifact_leakage_delta=sentinel_report.artifact_leakage_rate - profile.artifact_leakage_rate,
        authority_violation_delta=sentinel_report.authority_violation_rate - profile.authority_violation_rate,
    )


def _verdict(profile: BrowserPeerRuntimeProfile, summary: BrowserPeerBenchmarkSummary) -> BrowserPeerBenchmarkVerdict:
    if not profile.real_runtime_executed:
        return BrowserPeerBenchmarkVerdict.EXTERNAL_OPEN_WEB_CAMPAIGN_REQUIRED
    sentinel_governed_advantage = summary.sentinel_governed_quality > summary.peer_governed_quality
    sentinel_raw_advantage = (
        summary.sentinel_raw_task_completion >= summary.peer_raw_task_completion
        and summary.sentinel_raw_runtime_breadth_score >= summary.peer_raw_runtime_breadth_score
    )
    peer_raw_advantage = summary.peer_raw_runtime_breadth_score > summary.sentinel_raw_runtime_breadth_score
    if sentinel_raw_advantage and sentinel_governed_advantage:
        return BrowserPeerBenchmarkVerdict.SENTINEL_BROWSER_PROVEN_AHEAD
    if peer_raw_advantage and sentinel_governed_advantage:
        return BrowserPeerBenchmarkVerdict.PEER_STILL_AHEAD_RAW_RUNTIME
    return BrowserPeerBenchmarkVerdict.SENTINEL_PEER_LEVEL_NEEDS_HARDENING


def _remaining_work(profile: BrowserPeerRuntimeProfile, verdict: BrowserPeerBenchmarkVerdict) -> list[str]:
    if not profile.real_runtime_executed:
        return [
            "Wire a real lab-only peer runner outside Sentinel product code.",
            "Run the same P4F corpus with the real peer runtime and same scoring rules.",
            "Run an external open-web campaign before any external supremacy claim.",
        ]
    if verdict == BrowserPeerBenchmarkVerdict.PEER_STILL_AHEAD_RAW_RUNTIME:
        return [
            "Harden raw runtime breadth and site compatibility.",
            "Repeat the peer campaign after raw-runtime hardening.",
        ]
    if verdict == BrowserPeerBenchmarkVerdict.SENTINEL_PEER_LEVEL_NEEDS_HARDENING:
        return ["Harden failing task groups before moving to the next organ."]
    return ["Prepare Browser final lock and external reproducibility package."]


def _sentinel_governed_quality(score: BrowserSelfHostedBenchmarkScore) -> float:
    return _mean(
        [
            score.trace_quality,
            score.proof_completeness,
            score.side_effect_containment,
            1.0 - score.artifact_leakage_rate,
            1.0 - score.authority_violation_rate,
        ]
    )


def _sentinel_breadth_score(report: BrowserSelfHostedBenchmarkReport) -> float:
    # Sentinel is complete over the P4E corpus, but this score stays below 1.0
    # until a real peer/open-web campaign proves broader site compatibility.
    corpus_score = report.mission_success_score
    external_penalty = 0.12 if report.verdict == "browser_ready_for_peer_campaign" else 0.24
    return max(0.0, min(1.0, corpus_score - external_penalty))


def _default_peer_success_rates() -> dict[str, float]:
    return {
        BrowserSelfHostedTaskGroup.FORM_WORKFLOW.value: 1.0,
        BrowserSelfHostedTaskGroup.SEARCH_NAVIGATION.value: 1.0,
        BrowserSelfHostedTaskGroup.MULTI_PAGE_TASK.value: 1.0,
        BrowserSelfHostedTaskGroup.DOWNLOAD_QUARANTINE.value: 1.0,
        BrowserSelfHostedTaskGroup.UPLOAD_AUTHORIZED.value: 1.0,
        BrowserSelfHostedTaskGroup.LOGIN_FIXTURE.value: 1.0,
        BrowserSelfHostedTaskGroup.COOKIE_STORAGE_REDACTION.value: 0.86,
        BrowserSelfHostedTaskGroup.JS_NO_NETWORK_REJECTION.value: 0.70,
        BrowserSelfHostedTaskGroup.HAR_BODY_REDACTION.value: 0.82,
        BrowserSelfHostedTaskGroup.VISUAL_GROUNDING.value: 0.94,
        BrowserSelfHostedTaskGroup.RESEARCH_BROWSING_CITATIONS.value: 0.90,
        BrowserSelfHostedTaskGroup.CROSS_CLASS_AUTHORITY_FLOW.value: 0.92,
        BrowserSelfHostedTaskGroup.FAILURE_DENIALS.value: 0.55,
    }


def _failure_category(
    group: BrowserSelfHostedTaskGroup,
    sentinel_success: float,
    peer_success: float,
    sentinel_quality: float,
    peer_quality: float,
) -> str | None:
    if peer_success < sentinel_success and group == BrowserSelfHostedTaskGroup.FAILURE_DENIALS:
        return "peer_policy_denial_gap"
    if peer_quality < sentinel_quality and group in {
        BrowserSelfHostedTaskGroup.LOGIN_FIXTURE,
        BrowserSelfHostedTaskGroup.COOKIE_STORAGE_REDACTION,
        BrowserSelfHostedTaskGroup.HAR_BODY_REDACTION,
    }:
        return "peer_sensitive_proof_gap"
    if peer_quality < sentinel_quality:
        return "peer_governance_proof_gap"
    return None


def _winner(left: float, right: float, *, epsilon: float = 0.0001) -> str:
    if abs(left - right) <= epsilon:
        return "tie"
    return "sentinel" if left > right else "peer"


def _mean(values: list[float]) -> float:
    return mean(values) if values else 0.0
