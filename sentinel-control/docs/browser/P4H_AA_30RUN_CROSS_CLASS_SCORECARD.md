# P4H-AA 30-Run Cross-Class Scorecard

Date: 2026-04-30
Status: Passed

## Summary

```text
verdict = browser_v3_action_engine_routing_pass
mission_count = 10
run_count_per_mission = 30
total_iterations = 300
success_rate = 1.0
wilson_lower = 0.9874
operator_tempo = 0.94
action_success_rate = 1.0
v3_receipt_completeness = 1.0
finalgate_pass_rate = 1.0
authority_correctness = 1.0
proof_completeness = 1.0
false_action_rate = 0.0
denial_correctness = 1.0
cross_class_success = 1.0
latency_p50_ms = 35.828
latency_p95_ms = 84.196
step_count_p50 = 7.0
step_count_p95 = 14.0
```

## Missions

```text
BF-V3ACT-001-form-submit-envelope
BF-V3ACT-002-download-quarantine-envelope
BF-V3ACT-003-upload-authorized-envelope
BF-V3ACT-004-private-session-open-close-envelope
BF-V3ACT-005-login-authority-envelope
BF-V3ACT-006-cookie-storage-envelope
BF-V3ACT-007-js-sandbox-no-network-denial
BF-V3ACT-008-har-body-redaction-envelope
BF-V3ACT-009-cross-class-authority-flow
BF-V3ACT-010-out-of-policy-v3-denial
```

## Artifacts

```text
agent-lab/benchmarks/browser_tasks/reports/browser_v3_action_routing_results.jsonl
agent-lab/benchmarks/browser_tasks/reports/browser_v3_action_routing_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_v3_action_routing_scorecard.md
```

## Interpretation

P4H-AA proves that Browser V3 authority classes are no longer only separate
specialized executor paths. They can be prepared as `ActionEnvelope`s and
dispatched through the central browser operator path.

The cross-class mission proves:

```text
private session
-> login authority
-> cookie/storage redacted summary
-> HAR/body redacted capture
-> private session close
```

through `ActionEngine` with V3 receipts and FinalGate checks.
