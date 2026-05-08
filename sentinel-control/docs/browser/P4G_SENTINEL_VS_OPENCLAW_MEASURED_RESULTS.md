# P4G Sentinel vs OpenClaw Measured Results

Date: 2026-04-30
Status: Inconclusive

## Comparison Summary

Source:

```text
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_comparison_summary.json
```

Observed summary:

```text
comparison_status = inconclusive_peer_runtime_not_executed
final_decision = D_external_campaign_inconclusive
sentinel_task_count = 13
sentinel_run_count_per_group = 30
sentinel_binary_success_mean = 1.0
peer_task_count = 13
peer_real_runtime_executed = false
peer_binary_success_mean = null
product_vendor_runtime_imported = false
same_task_corpus = true
same_timeout = true
same_scoring = true
```

## Interpretation

This is a valid P4G campaign artifact, but not a valid OpenClaw-vs-Sentinel
supremacy measurement. The Sentinel side ran; the peer side was correctly
blocked by lab policy.

## Current Decision

```text
D) external campaign inconclusive
```

## P4G-R Container Attempt

Source:

```text
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_r_container_summary.json
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_r_openclaw_container_results.jsonl
```

Observed summary:

```text
final_decision = D_campaign_inconclusive
peer_real_runtime_executed = false
container_runtime = docker
source_commit = a2288c2b09e621f89a915960398f58e200b3b69d
package_json_sha256 = 9ffd60e01a31dd9d5b40568bdbaadc0128eab18eac3e2de8f45ae915132603ac
lockfile_sha256 = bd223e18e5eed01cacca34ed211e23dfc9211aa441057223a08548196629e591
dockerfile_sha256 = e2df3230c1093e0751bdc02a754348259a5b84e532d5fa25529bf2e9728a2001
host_dependency_install = false
product_vendor_runtime_imported = false
blocked_reason = container runtime found, but no approved real peer command is defined for this machine
```

P4G-R did not fall back to host dependency install or direct vendor execution.
Docker is now available. The correct next step is to define an approved
throwaway peer command or adapter that emits only neutral JSONL, then rerun
P4G-R2.
