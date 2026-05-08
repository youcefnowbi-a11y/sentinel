# P4H-AC 30-Run Live Long-Horizon Scorecard

Date: 2026-05-01
Status: Passed

Generated artifact:

```text
agent-lab/benchmarks/browser_tasks/reports/browser_operator_live_long_horizon_scorecard.json
```

## Summary

```text
run_id = p4h_ac_browser_operator_live_long_horizon_30run
mission_count = 10
run_count_per_mission = 30
total_iterations = 300
success_rate = 1.0
wilson_lower = 0.9874
wilson_upper = 1.0
operator_tempo = 0.96
live_observation_success = 1.0
live_visual_verifier_rate = 1.0
action_success_rate = 1.0
repair_success_rate = 1.0
verifier_recovery_rate = 1.0
cross_class_success = 1.0
state_continuity = 1.0
proof_completeness = 1.0
finalgate_pass_rate = 1.0
authority_correctness = 1.0
false_action_rate = 0.0
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
budget_violation_rate = 0.0
```

## Latency And Steps

```text
step_count_p50 = 19.5
step_count_p95 = 42.0
latency_p50_ms = 36.267
latency_p95_ms = 3758.889
live_latency_p50_ms = 3.716
live_latency_p95_ms = 25.394
```

The high full latency p95 is expected in this tranche because
`BF-LIVE-LONG-006` invokes the rendered Playwright-backed visual verifier.
The live HTTP fixture layer remains low-latency.

## Mission Verdicts

All missions passed 30/30:

```text
BF-LIVE-LONG-001 research-form-submit-verify
BF-LIVE-LONG-002 login-cookie-har-close
BF-LIVE-LONG-003 download-inspect-upload
BF-LIVE-LONG-004 multitab-compare-submit
BF-LIVE-LONG-005 failed-first-action-repair-continue
BF-LIVE-LONG-006 visual-crop-zoom-action
BF-LIVE-LONG-007 js-denial-har-alternative
BF-LIVE-LONG-008 step-budget-pressure
BF-LIVE-LONG-009 cross-class-verifier-repair
BF-LIVE-LONG-010 end-to-end-final-artifact-pack
```

Each mission has:

```text
success_rate = 1.0
wilson_lower = 0.8865
unstable_iterations = []
```

## Boundary

```text
self_hosted_live_browser_operator_only_no_new_powers_no_desktop_no_open_web_claim
```
