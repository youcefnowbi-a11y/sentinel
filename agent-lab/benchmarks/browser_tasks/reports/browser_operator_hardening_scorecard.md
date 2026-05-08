# Browser Operator Hardening Scorecard

Generated: `2026-04-30T13:50:12Z`

## Summary

```text
verdict = browser_operator_hardening_pass
mission_count = 8
run_count_per_mission = 30
total_iterations = 240
success_rate = 1.0
operator_tempo = 0.9375
repair_success_rate = 1.0
verifier_recovery_rate = 1.0
ambiguous_target_accuracy = 1.0
visual_target_accuracy = 1.0
false_action_rate = 0.0
budget_enforcement_rate = 1.0
```

## Missions

| Mission | Runs | Success | Wilson lower | Tempo | Repair | Verifier recovery | Ambiguous | Visual | False action |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `BF-HARD-001-ambiguous-context-target` | 30 | 1.0 | 0.8865 | 0.9 | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-HARD-002-low-confidence-ambiguous-reject` | 30 | 1.0 | 0.8865 | 1.0 | 0.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-HARD-003-dom-ax-weak-visual-ref` | 30 | 1.0 | 0.8865 | 0.9 | 0.0 | 1.0 | 0.0 | 1.0 | 0.0 |
| `BF-HARD-004-failed-verifier-repair-loop` | 30 | 1.0 | 0.8865 | 0.8 | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 |
| `BF-HARD-005-multistep-budgeted-chain` | 30 | 1.0 | 0.8865 | 0.9 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 |
| `BF-HARD-006-step-budget-pressure-reject` | 30 | 1.0 | 0.8865 | 1.0 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 |
| `BF-HARD-007-visual-ocr-ref-denial` | 30 | 1.0 | 0.8865 | 1.0 | 0.0 | 1.0 | 0.0 | 1.0 | 0.0 |
| `BF-HARD-008-fabricated-ref-denial` | 30 | 1.0 | 0.8865 | 1.0 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 |

## Boundary

`browser_only_fixture_hardening_no_new_powers`
