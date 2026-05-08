# P4H-Z 30-Run Operator Hardening Scorecard

Date: 2026-04-30
Status: Passed

## Command

```text
python agent-lab/benchmarks/browser_tasks/browser_operator_hardening_runner.py --run-count 30 --out-dir agent-lab/benchmarks/browser_tasks/reports
```

## Result

```text
verdict = browser_operator_hardening_pass
mission_count = 8
run_count_per_mission = 30
total_iterations = 240
success_count = 240
success_rate = 1.0
wilson_lower = 0.9842
wilson_upper = 1.0
operator_tempo = 0.9375
action_success_rate = 1.0
repair_success_rate = 1.0
verifier_recovery_rate = 1.0
ambiguous_target_accuracy = 1.0
visual_target_accuracy = 1.0
budget_enforcement_rate = 1.0
proof_completeness = 1.0
authority_correctness = 1.0
false_action_rate = 0.0
latency_p50_ms = 11.785
latency_p95_ms = 38.577
step_count_p50 = 5.0
step_count_p95 = 9.0
```

## Artifacts

```text
agent-lab/benchmarks/browser_tasks/reports/browser_operator_hardening_results.jsonl
agent-lab/benchmarks/browser_tasks/reports/browser_operator_hardening_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_operator_hardening_scorecard.md
```

## Interpretation

P4H-Z proves the operator path holds under the first hardening set:

```text
duplicate labels
low-confidence rejection
weak structural target plus visual ref binding
failed verifier repair
multi-step budgeted chain
step budget rejection
OCR-only target denial
fabricated ref denial
```

The result remains local and fixture-backed. It is not an open-web claim.
