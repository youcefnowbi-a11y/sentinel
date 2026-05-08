# P4H-V 72-Mission 30-Run Scorecard

Date: 2026-04-30
Status: Complete

## Source

```text
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_live_full_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_live_full_results.jsonl
```

## Summary

```text
run_id = p4h_v_full_live_self_hosted_30run
verdict = browser_fluency_full_live_self_hosted_pass
mission_count = 72
run_count_per_mission = 30
total_iterations = 2160
success_count = 2160
success_rate = 1.0
wilson_lower = 0.9982
wilson_upper = 1.0
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
latency_p50_ms = 2.514
latency_p95_ms = 6.653
step_count_p50 = 3.0
step_count_p95 = 4.0
```

## Group Score

Each group ran 180 times:

```text
success_rate = 1.0
wilson_lower = 0.9791
wilson_upper = 1.0
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
```

## Mission Score

Each of the 72 missions ran 30 times:

```text
success_rate = 1.0
wilson_lower = 0.8865
wilson_upper = 1.0
unstable_iterations = []
```

## Scientific Meaning

P4H-V establishes a complete self-hosted local Browser Fluency baseline:

```text
full corpus
repeated measurement
small-n-safe Wilson intervals
zero report leakage
zero authority violation
```

The result is strong enough to say Sentinel passes its own self-hosted Browser
Fluency exam. It is not enough to claim open-web supremacy.
