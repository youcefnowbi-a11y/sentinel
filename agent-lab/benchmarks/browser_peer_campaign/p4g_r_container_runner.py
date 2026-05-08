from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
OPENCLAW_SOURCE = REPO_ROOT / "agent-lab" / "vendors" / "openclaw" / "source"
REPORT_DIR = REPO_ROOT / "agent-lab" / "benchmarks" / "browser_peer_campaign" / "reports"
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
class P4GRContainerRunRecord:
    schema_version: str
    campaign_id: str
    generated_at: str
    runtime_id: str
    runtime_kind: str
    task_group: str
    execution_status: str
    run_count: int
    container_runtime: str | None
    container_runtime_version: str | None
    source_commit: str | None
    package_json_sha256: str | None
    lockfile_sha256: str | None
    dockerfile_sha256: str | None
    container_image_id: str | None
    network_policy: str
    fake_env_only: bool
    host_dependency_install: bool
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
    failure_category: str
    blocked_reason: str | None


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def find_container_runtime(preferred: str | None = None) -> tuple[str | None, str | None]:
    candidates = [preferred] if preferred else ["docker", "podman"]
    for candidate in candidates:
        if not candidate:
            continue
        executable = shutil.which(candidate)
        if executable is None:
            continue
        try:
            result = subprocess.run(
                [executable, "--version"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        return candidate, result.stdout.strip()
    return None, None


def build_blocked_records(*, iterations: int, preferred_runtime: str | None = None) -> list[P4GRContainerRunRecord]:
    runtime, version = find_container_runtime(preferred_runtime)
    generated_at = utc_now()
    blocked_reason = _blocked_reason(runtime)
    metadata = _source_metadata()
    return [
        P4GRContainerRunRecord(
            schema_version="p4g-r.container_peer_result.v1",
            campaign_id="p4g_r_containerized_peer_runtime_run",
            generated_at=generated_at,
            runtime_id="openclaw_real_container",
            runtime_kind="peer",
            task_group=task_group,
            execution_status="blocked_no_container_runtime" if runtime is None else "blocked_no_approved_runtime_command",
            run_count=0,
            container_runtime=runtime,
            container_runtime_version=version,
            source_commit=metadata["source_commit"],
            package_json_sha256=metadata["package_json_sha256"],
            lockfile_sha256=metadata["lockfile_sha256"],
            dockerfile_sha256=metadata["dockerfile_sha256"],
            container_image_id=None,
            network_policy="none_until_peer_run_approved",
            fake_env_only=True,
            host_dependency_install=False,
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
            failure_category="peer_container_runtime_unavailable" if runtime is None else "peer_runtime_command_not_approved",
            blocked_reason=f"{blocked_reason}; requested_run_count={iterations}",
        )
        for task_group in TASK_GROUPS
    ]


def write_jsonl(path: Path, records: list[P4GRContainerRunRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")


def write_summary(out_dir: Path, records: list[P4GRContainerRunRecord]) -> dict[str, Any]:
    first = records[0] if records else None
    summary = {
        "campaign_id": "p4g_r_containerized_peer_runtime_run",
        "final_decision": "D_campaign_inconclusive",
        "peer_real_runtime_executed": False,
        "container_runtime": first.container_runtime if first else None,
        "container_runtime_version": first.container_runtime_version if first else None,
        "source_commit": first.source_commit if first else None,
        "package_json_sha256": first.package_json_sha256 if first else None,
        "lockfile_sha256": first.lockfile_sha256 if first else None,
        "dockerfile_sha256": first.dockerfile_sha256 if first else None,
        "host_dependency_install": False,
        "product_vendor_runtime_imported": False,
        "fake_env_only": True,
        "network_policy": first.network_policy if first else "none_until_peer_run_approved",
        "task_count": len(records),
        "blocked_reason": first.blocked_reason if first else "no records generated",
    }
    (out_dir / "p4g_r_container_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "p4g_r_container_report.md").write_text(render_markdown(summary), encoding="utf-8")
    return summary


def render_markdown(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# P4G-R Containerized Peer Runtime Run",
            "",
            f"Generated: `{utc_now()}`",
            "",
            "## Verdict",
            "",
            "```text",
            f"final_decision = {summary['final_decision']}",
            f"peer_real_runtime_executed = {str(summary['peer_real_runtime_executed']).lower()}",
            f"container_runtime = {summary['container_runtime']}",
            f"host_dependency_install = {str(summary['host_dependency_install']).lower()}",
            f"product_vendor_runtime_imported = {str(summary['product_vendor_runtime_imported']).lower()}",
            "```",
            "",
            "## Source Pinning",
            "",
            f"- source commit: `{summary['source_commit']}`",
            f"- package hash: `{summary['package_json_sha256']}`",
            f"- lockfile hash: `{summary['lockfile_sha256']}`",
            f"- Dockerfile hash: `{summary['dockerfile_sha256']}`",
            "",
            "## Blocked Reason",
            "",
            f"`{summary['blocked_reason']}`",
            "",
            "## Interpretation",
            "",
            "P4G-R did not fall back to host install or direct vendor execution. The peer runtime remains unexecuted until a container runtime is available and an approved runtime command exists.",
            "",
        ]
    )


def _source_metadata() -> dict[str, str | None]:
    return {
        "source_commit": git_commit(OPENCLAW_SOURCE),
        "package_json_sha256": sha256_file(OPENCLAW_SOURCE / "package.json"),
        "lockfile_sha256": sha256_file(OPENCLAW_SOURCE / "pnpm-lock.yaml"),
        "dockerfile_sha256": sha256_file(OPENCLAW_SOURCE / "Dockerfile.sandbox-browser"),
    }


def _blocked_reason(runtime: str | None) -> str:
    if runtime is None:
        return "no docker or podman executable found on PATH"
    return "container runtime found, but no approved real peer command is defined for this machine"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--container-runtime", default=None)
    parser.add_argument("--out-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()

    records = build_blocked_records(iterations=args.iterations, preferred_runtime=args.container_runtime)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "p4g_r_openclaw_container_results.jsonl", records)
    summary = write_summary(args.out_dir, records)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
