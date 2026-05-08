# P4H-AD 30-Run Open-Web-Like Scorecard

Date: 2026-05-01
Status: Passed

Generated artifact:

```text
agent-lab/benchmarks/browser_tasks/reports/browser_operator_open_web_like_scorecard.json
```

## Summary

```text
run_id = p4h_ad_browser_operator_open_web_like_30run
mission_count = 10
run_count_per_mission = 30
total_iterations = 300
success_rate = 1.0
wilson_lower = 0.9874
wilson_upper = 1.0
operator_tempo = 0.9698
open_web_like_success = 1.0
weak_dom_ax_recovery_rate = 1.0
ambiguous_target_accuracy = 1.0
dynamic_state_recovery_rate = 1.0
network_repair_rate = 1.0
visual_cache_hit_rate = 0.9833
visual_render_count = 1
visual_tempo_score = 1.0
action_success_rate = 1.0
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
step_count_p50 = 18.0
step_count_p95 = 47.0
latency_p50_ms = 27.131
latency_p95_ms = 121.866
live_latency_p50_ms = 4.079
live_latency_p95_ms = 29.557
visual_latency_p50_ms = 0.5
visual_latency_p95_ms = 0.5
```

## Visual Tempo Result

```text
visual_render_count = 1
visual_cache_hit_rate = 0.9833
```

The cold visual render still exists, but repeated static visual verifier checks
do not force a full Playwright render on every mission step.

## Mission Verdicts

All missions passed 30/30:

```text
BF-OPENWEB-001 messy-duplicate-context-submit
BF-OPENWEB-002 weak-dom-visual-bound-action
BF-OPENWEB-003 overlay-covered-target-repair
BF-OPENWEB-004 dynamic-state-after-action-verify
BF-OPENWEB-005 network-failure-repair-alternative
BF-OPENWEB-006 redirect-revalidate-submit
BF-OPENWEB-007 deep-scroll-budget-pressure
BF-OPENWEB-008 visual-injection-ocr-denial
BF-OPENWEB-009 state-cookie-har-no-leak
BF-OPENWEB-010 end-to-end-openweblike-pack
```

Each mission has:

```text
success_rate = 1.0
wilson_lower = 0.8865
unstable_iterations = []
```

## Boundary

```text
self_hosted_open_web_like_browser_operator_only_no_new_powers_no_external_claim
```
