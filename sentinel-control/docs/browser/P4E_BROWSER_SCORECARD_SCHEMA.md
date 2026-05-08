# P4E Browser Scorecard Schema

Date: 2026-04-30
Status: Complete

## Score Model

`BrowserSelfHostedBenchmarkScore` reports:

```text
task_group
family
run_count
accepted_rate
success_rate
success_rate_ci95_lower
success_rate_ci95_upper
confidence_interval_method
latency_ms_p50
latency_ms_p95
step_count_p50
step_count_p95
unstable_iterations
trace_quality
proof_completeness
source_quality
interaction_correctness
side_effect_containment
denial_correctness
artifact_leakage_rate
authority_violation_rate
peer_comparable
```

## Report Model

`BrowserSelfHostedBenchmarkReport` reports:

```text
suite_accepted
task_count
iterations
mission_success_score
trace_quality
proof_completeness
side_effect_containment
artifact_leakage_rate
authority_violation_rate
peer_protocol
verdict
remaining_work
```

## Verdict Values

| Verdict | Meaning |
| --- | --- |
| `browser_benchmark_dry_run_only` | corpus passes but run count is below 30 |
| `browser_ready_for_peer_campaign` | 30-run self-hosted gate passed |
| `browser_benchmark_needs_more_hardening` | one or more scientific conditions failed |

## Boundary

The scorecard is an internal benchmark schema. External supremacy requires a
peer run and later open-web campaign.
