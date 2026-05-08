# P4G Sentinel Results

Date: 2026-04-30
Status: Complete

## Source

```text
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_sentinel_results.jsonl
```

## Summary

```text
runtime_id = sentinel_browser_v3
runtime_kind = sentinel
task_groups = 13
run_count_per_group = 30
binary_success_mean = 1.0
product_vendor_runtime_imported = false
```

## Proof Boundary

Sentinel results preserve the P4E/P4F proof model:

```text
trace_quality = 1.0
proof_completeness = 1.0
side_effect_containment = 1.0
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
```

## Interpretation

Sentinel remains strong on the self-hosted/open-web-prep corpus. These results
are usable as the Sentinel side of the campaign, but they cannot prove external
supremacy until the peer runtime is executed under the same rules.
