# P4H-AB 30-Run Long-Horizon Scorecard

Date: 2026-04-30
Status: Passed

Source:

```text
agent-lab/benchmarks/browser_tasks/reports/browser_operator_long_horizon_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_operator_long_horizon_scorecard.md
agent-lab/benchmarks/browser_tasks/reports/browser_operator_long_horizon_results.jsonl
```

## Summary

```text
verdict = browser_operator_long_horizon_pass
mission_count = 10
run_count_per_mission = 30
total_iterations = 300
success_rate = 1.0
wilson_lower = 0.9874
operator_tempo = 0.95
action_success_rate = 1.0
repair_success_rate = 1.0
verifier_recovery_rate = 1.0
cross_class_success = 1.0
state_continuity = 1.0
proof_completeness = 1.0
finalgate_pass_rate = 1.0
authority_correctness = 1.0
false_action_rate = 0.0
budget_violation_rate = 0.0
latency_p50_ms = 30.841
latency_p95_ms = 107.343
step_count_p50 = 14.0
step_count_p95 = 26.0
```

## Mission Results

| Mission | Runs | Success | Wilson lower | Tempo | Repair | Cross-class | State | False action |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `BF-LONG-001-research-form-submit-verify` | 30 | 1.0 | 0.8865 | 1.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| `BF-LONG-002-login-cookie-har-close` | 30 | 1.0 | 0.8865 | 0.95 | 0.0 | 1.0 | 1.0 | 0.0 |
| `BF-LONG-003-download-inspect-upload` | 30 | 1.0 | 0.8865 | 0.95 | 0.0 | 1.0 | 1.0 | 0.0 |
| `BF-LONG-004-multitab-compare-submit` | 30 | 1.0 | 0.8865 | 0.95 | 0.0 | 0.0 | 1.0 | 0.0 |
| `BF-LONG-005-failed-first-action-repair-continue` | 30 | 1.0 | 0.8865 | 0.95 | 1.0 | 0.0 | 1.0 | 0.0 |
| `BF-LONG-006-ambiguous-crop-zoom-action` | 30 | 1.0 | 0.8865 | 0.95 | 0.0 | 0.0 | 1.0 | 0.0 |
| `BF-LONG-007-js-denial-alternative-path` | 30 | 1.0 | 0.8865 | 1.0 | 0.0 | 1.0 | 1.0 | 0.0 |
| `BF-LONG-008-step-budget-pressure` | 30 | 1.0 | 0.8865 | 1.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| `BF-LONG-009-cross-class-verifier-repair` | 30 | 1.0 | 0.8865 | 0.9 | 1.0 | 1.0 | 1.0 | 0.0 |
| `BF-LONG-010-end-to-end-final-artifact-pack` | 30 | 1.0 | 0.8865 | 0.85 | 0.0 | 1.0 | 1.0 | 0.0 |

## Interpretation

P4H-AB proves that the central operator can preserve state continuity and proof
across mixed long-horizon flows:

```text
research evidence
form submit
private session lifecycle
login authority
cookie/storage redacted summary
HAR/body capture
download quarantine
upload certified artifact
JS no-network denial
budget denial and repair
final artifact pack
```

This is still local fixture proof, not open-web supremacy.
