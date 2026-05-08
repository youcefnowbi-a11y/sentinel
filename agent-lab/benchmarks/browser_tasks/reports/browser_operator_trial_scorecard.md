# Browser Operator Trial Scorecard

Generated: `2026-04-30T13:26:36Z`

## Summary

```text
verdict = browser_operator_trial_pass
mission_count = 6
run_count_per_mission = 30
total_iterations = 180
success_rate = 1.0
operator_tempo = 0.9667
ref_validity_rate = 1.0
post_action_verifier_pass_rate = 1.0
repair_success_rate = 0.1667
authority_correctness = 1.0
false_action_rate = 0.0
```

## Missions

| Mission | Runs | Success | Wilson lower | Tempo | Ref validity | Verifier | Repair | False action |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `BF-OP-001-click-visible-target` | 30 | 1.0 | 0.8865 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-OP-002-fill-grounded-field` | 30 | 1.0 | 0.8865 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-OP-003-repair-stale-ref` | 30 | 1.0 | 0.8865 | 0.9 | 1.0 | 1.0 | 1.0 | 0.0 |
| `BF-OP-004-deny-ocr-only-target` | 30 | 1.0 | 0.8865 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-OP-005-deny-out-of-policy-action` | 30 | 1.0 | 0.8865 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-OP-006-multistep-fast-policy` | 30 | 1.0 | 0.8865 | 0.9 | 1.0 | 1.0 | 0.0 | 0.0 |

## Boundary

`browser_only_fixture_operator_trial_uses_existing_controlled_runner`
