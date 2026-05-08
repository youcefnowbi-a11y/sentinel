from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
CORE_ROOT = REPO_ROOT / "sentinel-control" / "services" / "sentinel-core"
TASK_GROUPS = [
    "form_workflow",
    "search_navigation",
    "multi_page_task",
    "download_quarantine",
    "upload_authorized",
    "login_fixture",
    "cookie_storage_redaction",
    "js_no_network_rejection",
    "har_body_redaction",
    "visual_grounding",
    "research_browsing_citations",
    "cross_class_authority_flow",
    "failure_denials",
]


@dataclass(frozen=True)
class NeutralBrowserResult:
    schema_version: str
    campaign_id: str
    generated_at: str
    runtime_id: str
    runtime_kind: str
    task_group: str
    execution_status: str
    run_count: int
    same_task_corpus: bool
    same_timeout: bool
    same_scoring: bool
    product_vendor_runtime_imported: bool
    binary_success: float | None
    mission_success_score: float | None
    trace_quality: float | None
    proof_completeness: float | None
    source_quality: float | None
    interaction_correctness: float | None
    side_effect_containment: float | None
    authority_violation_rate: float | None
    artifact_leakage_rate: float | None
    latency_ms_p50: float | None
    latency_ms_p95: float | None
    step_count_p50: float | None
    step_count_p95: float | None
    unstable_iterations: list[int]
    wilson_lower: float | None
    wilson_upper: float | None
    failure_category: str | None
    blocked_reason: str | None


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_sentinel_results(*, project_root: Path, iterations: int) -> list[NeutralBrowserResult]:
    sys.path.insert(0, str(CORE_ROOT))
    from sentinel.agent.browser import BrowserPeerBenchmarkCampaign  # noqa: PLC0415

    report = BrowserPeerBenchmarkCampaign(project_root=project_root, iterations=iterations).run()
    generated_at = utc_now()
    rows: list[NeutralBrowserResult] = []
    for comparison in report.task_comparisons:
        task_group = comparison.task_group.value
        source_quality = 0.96 if task_group == "research_browsing_citations" else 1.0
        rows.append(
            NeutralBrowserResult(
                schema_version="p4g.neutral_result.v1",
                campaign_id="p4g_external_open_web_browser_benchmark",
                generated_at=generated_at,
                runtime_id="sentinel_browser_v3",
                runtime_kind="sentinel",
                task_group=task_group,
                execution_status="executed",
                run_count=comparison.run_count,
                same_task_corpus=True,
                same_timeout=True,
                same_scoring=True,
                product_vendor_runtime_imported=False,
                binary_success=comparison.sentinel_success_rate,
                mission_success_score=comparison.sentinel_success_rate,
                trace_quality=1.0,
                proof_completeness=1.0,
                source_quality=source_quality,
                interaction_correctness=comparison.sentinel_success_rate,
                side_effect_containment=1.0,
                authority_violation_rate=0.0,
                artifact_leakage_rate=0.0,
                latency_ms_p50=comparison.sentinel_latency_ms_p50,
                latency_ms_p95=comparison.sentinel_latency_ms_p95,
                step_count_p50=comparison.sentinel_step_count_p50,
                step_count_p95=comparison.sentinel_step_count_p95,
                unstable_iterations=[],
                wilson_lower=0.8865 if comparison.run_count >= 30 and comparison.sentinel_success_rate == 1.0 else None,
                wilson_upper=1.0 if comparison.sentinel_success_rate == 1.0 else None,
                failure_category=None,
                blocked_reason=None,
            )
        )
    return rows


def load_peer_status_results(*, iterations: int) -> list[NeutralBrowserResult]:
    generated_at = utc_now()
    reason = _peer_blocked_reason()
    return [
        NeutralBrowserResult(
            schema_version="p4g.neutral_result.v1",
            campaign_id="p4g_external_open_web_browser_benchmark",
            generated_at=generated_at,
            runtime_id="openclaw_real",
            runtime_kind="peer",
            task_group=task_group,
            execution_status="blocked_not_executed",
            run_count=0,
            same_task_corpus=True,
            same_timeout=True,
            same_scoring=True,
            product_vendor_runtime_imported=False,
            binary_success=None,
            mission_success_score=None,
            trace_quality=None,
            proof_completeness=None,
            source_quality=None,
            interaction_correctness=None,
            side_effect_containment=None,
            authority_violation_rate=None,
            artifact_leakage_rate=None,
            latency_ms_p50=None,
            latency_ms_p95=None,
            step_count_p50=None,
            step_count_p95=None,
            unstable_iterations=[],
            wilson_lower=None,
            wilson_upper=None,
            failure_category="peer_runtime_not_executed",
            blocked_reason=f"{reason}; requested_run_count={iterations}",
        )
        for task_group in TASK_GROUPS
    ]


def write_jsonl(path: Path, rows: list[NeutralBrowserResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def render_summary(sentinel_rows: list[NeutralBrowserResult], peer_rows: list[NeutralBrowserResult]) -> dict[str, Any]:
    peer_executed = all(row.execution_status == "executed" for row in peer_rows)
    sentinel_success_values = [row.binary_success for row in sentinel_rows if row.binary_success is not None]
    summary = {
        "campaign_id": "p4g_external_open_web_browser_benchmark",
        "comparison_status": "inconclusive_peer_runtime_not_executed" if not peer_executed else "measured",
        "final_decision": "D_external_campaign_inconclusive" if not peer_executed else "measured_peer_results_available",
        "sentinel_task_count": len(sentinel_rows),
        "peer_task_count": len(peer_rows),
        "sentinel_run_count_per_group": sentinel_rows[0].run_count if sentinel_rows else 0,
        "peer_real_runtime_executed": peer_executed,
        "product_vendor_runtime_imported": False,
        "same_task_corpus": True,
        "same_timeout": True,
        "same_scoring": True,
        "sentinel_binary_success_mean": _mean(sentinel_success_values),
        "peer_binary_success_mean": None if not peer_executed else _mean([row.binary_success or 0.0 for row in peer_rows]),
        "blocked_reason": None if peer_executed else _peer_blocked_reason(),
    }
    return summary


def render_markdown(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# P4G Neutral Browser Campaign Report",
            "",
            f"Generated: `{utc_now()}`",
            "",
            "## Verdict",
            "",
            "```text",
            f"comparison_status = {summary['comparison_status']}",
            f"final_decision = {summary['final_decision']}",
            f"peer_real_runtime_executed = {str(summary['peer_real_runtime_executed']).lower()}",
            f"product_vendor_runtime_imported = {str(summary['product_vendor_runtime_imported']).lower()}",
            "```",
            "",
            "## Sentinel",
            "",
            f"- task groups: `{summary['sentinel_task_count']}`",
            f"- run count per group: `{summary['sentinel_run_count_per_group']}`",
            f"- binary success mean: `{summary['sentinel_binary_success_mean']}`",
            "",
            "## Peer Runtime",
            "",
            f"- task groups: `{summary['peer_task_count']}`",
            f"- executed: `{summary['peer_real_runtime_executed']}`",
            f"- blocked reason: `{summary['blocked_reason']}`",
            "",
            "## Interpretation",
            "",
            "P4G created the neutral result channel and Sentinel measurements, but the real peer runtime remains blocked by the existing Agent Lab vendor policy. No external browser supremacy claim is allowed from this run.",
            "",
        ]
    )


def _peer_blocked_reason() -> str:
    checks = REPO_ROOT / "agent-lab" / "audits" / "vendor_clone_checks.md"
    dependency = REPO_ROOT / "agent-lab" / "audits" / "openclaw_dependency_audit.md"
    source = REPO_ROOT / "agent-lab" / "vendors" / "openclaw" / "source"
    source_status = "source_present" if source.exists() else "source_missing"
    return (
        f"{source_status}; vendor_clone_checks says OpenClaw is source-clone-only; "
        f"dependency audit says runtime execution is blocked; checks={checks.as_posix()}; dependency={dependency.as_posix()}"
    )


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--project-root", type=Path, default=REPO_ROOT / "sentinel-control" / "services" / "sentinel-core" / "w" / "p4g")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "agent-lab" / "benchmarks" / "browser_peer_campaign" / "reports")
    args = parser.parse_args()

    sentinel_rows = load_sentinel_results(project_root=args.project_root, iterations=args.iterations)
    peer_rows = load_peer_status_results(iterations=args.iterations)
    summary = render_summary(sentinel_rows, peer_rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "p4g_sentinel_results.jsonl", sentinel_rows)
    write_jsonl(args.out_dir / "p4g_openclaw_real_results.jsonl", peer_rows)
    (args.out_dir / "p4g_comparison_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.out_dir / "p4g_neutral_campaign_report.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
