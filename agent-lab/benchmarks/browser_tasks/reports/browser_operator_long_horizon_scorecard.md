# Browser Operator Long-Horizon Scorecard

Generated: `2026-04-30T15:16:38Z`

## Summary

```text
verdict = browser_operator_long_horizon_pass
mission_count = 10
run_count_per_mission = 30
total_iterations = 300
success_rate = 1.0
wilson_lower = 0.9874
operator_tempo = 0.95
repair_success_rate = 1.0
verifier_recovery_rate = 1.0
cross_class_success = 1.0
state_continuity = 1.0
proof_completeness = 1.0
finalgate_pass_rate = 1.0
false_action_rate = 0.0
budget_violation_rate = 0.0
```

## Missions

| Mission | Runs | Success | Wilson lower | Tempo | Repair | Verifier recovery | Cross-class | State | False action |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `BF-LONG-001-research-form-submit-verify` | 30 | 1.0 | 0.8865 | 1.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| `BF-LONG-002-login-cookie-har-close` | 30 | 1.0 | 0.8865 | 0.95 | 0.0 | 0.0 | 1.0 | 1.0 | 0.0 |
| `BF-LONG-003-download-inspect-upload` | 30 | 1.0 | 0.8865 | 0.95 | 0.0 | 0.0 | 1.0 | 1.0 | 0.0 |
| `BF-LONG-004-multitab-compare-submit` | 30 | 1.0 | 0.8865 | 0.95 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| `BF-LONG-005-failed-first-action-repair-continue` | 30 | 1.0 | 0.8865 | 0.95 | 1.0 | 1.0 | 0.0 | 1.0 | 0.0 |
| `BF-LONG-006-ambiguous-crop-zoom-action` | 30 | 1.0 | 0.8865 | 0.95 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| `BF-LONG-007-js-denial-alternative-path` | 30 | 1.0 | 0.8865 | 1.0 | 0.0 | 0.0 | 1.0 | 1.0 | 0.0 |
| `BF-LONG-008-step-budget-pressure` | 30 | 1.0 | 0.8865 | 1.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| `BF-LONG-009-cross-class-verifier-repair` | 30 | 1.0 | 0.8865 | 0.9 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 |
| `BF-LONG-010-end-to-end-final-artifact-pack` | 30 | 1.0 | 0.8865 | 0.85 | 0.0 | 0.0 | 1.0 | 1.0 | 0.0 |

## Boundary

`browser_only_fixture_long_horizon_action_engine_no_new_powers`
