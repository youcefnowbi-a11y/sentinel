# Browser V3 ActionEngine Routing Scorecard

Generated: `2026-04-30T14:14:02Z`

## Summary

```text
verdict = browser_v3_action_engine_routing_pass
mission_count = 10
run_count_per_mission = 1
total_iterations = 10
success_rate = 1.0
wilson_lower = 0.7225
operator_tempo = 0.94
v3_receipt_completeness = 1.0
finalgate_pass_rate = 1.0
authority_correctness = 1.0
false_action_rate = 0.0
cross_class_success = 1.0
```

## Missions

| Mission | Runs | Success | Wilson lower | Tempo | V3 receipts | FinalGate | Denial | False action |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `BF-V3ACT-001-form-submit-envelope` | 1 | 1.0 | 0.2065 | 0.9 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-V3ACT-002-download-quarantine-envelope` | 1 | 1.0 | 0.2065 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-V3ACT-003-upload-authorized-envelope` | 1 | 1.0 | 0.2065 | 0.9 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-V3ACT-004-private-session-open-close-envelope` | 1 | 1.0 | 0.2065 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-V3ACT-005-login-authority-envelope` | 1 | 1.0 | 0.2065 | 0.9 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-V3ACT-006-cookie-storage-envelope` | 1 | 1.0 | 0.2065 | 0.9 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-V3ACT-007-js-sandbox-no-network-denial` | 1 | 1.0 | 0.2065 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 |
| `BF-V3ACT-008-har-body-redaction-envelope` | 1 | 1.0 | 0.2065 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-V3ACT-009-cross-class-authority-flow` | 1 | 1.0 | 0.2065 | 0.8 | 1.0 | 1.0 | 0.0 | 0.0 |
| `BF-V3ACT-010-out-of-policy-v3-denial` | 1 | 1.0 | 0.2065 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 |

## Boundary

`browser_only_fixture_v3_action_engine_routing_no_new_powers`
