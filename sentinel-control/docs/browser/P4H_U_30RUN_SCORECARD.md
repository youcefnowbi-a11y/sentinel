# P4H-U 30-Run Live Self-Hosted Scorecard

Date: 2026-04-30
Status: Complete

## Source

```text
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_live_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_live_results.jsonl
```

## Summary

```text
run_id = p4h_u_live_self_hosted_30run
verdict = browser_fluency_live_self_hosted_pass
mission_count = 12
run_count_per_mission = 30
total_iterations = 360
success_count = 360
success_rate = 1.0
wilson_lower = 0.9894
wilson_upper = 1.0
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
latency_p50_ms = 2.392
latency_p95_ms = 14.21
step_count_p50 = 3.0
step_count_p95 = 4.0
```

## Per-Group Result

Every group ran 30 times with:

```text
success_rate = 1.0
wilson_lower = 0.8865
wilson_upper = 1.0
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
unstable_iterations = []
```

Groups covered:

```text
life
nav
perc
vis
form
state
file
net
tab
res
safe
cog
```

## Scientific Meaning

P4H-U improves the evidence level from:

```text
contract fixture only
```

to:

```text
self-hosted live fixture with repeated measurements
```

The Wilson lower bound is intentionally reported instead of a false
`CI95 = 0.0` certainty.
