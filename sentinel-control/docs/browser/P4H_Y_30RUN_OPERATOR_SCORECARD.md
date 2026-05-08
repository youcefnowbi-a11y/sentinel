# P4H-Y 30-Run Operator Scorecard

Date: 2026-04-30
Status: Passed

## Command

```text
python agent-lab/benchmarks/browser_tasks/browser_operator_trial_runner.py --run-count 30 --out-dir agent-lab/benchmarks/browser_tasks/reports
```

## Results

```text
verdict = browser_operator_trial_pass
mission_count = 6
run_count_per_mission = 30
total_iterations = 180
success_count = 180
success_rate = 1.0
wilson_lower = 0.9791
wilson_upper = 1.0
operator_tempo = 0.9667
ref_validity_rate = 1.0
post_action_verifier_pass_rate = 1.0
proof_completeness = 1.0
authority_correctness = 1.0
false_action_rate = 0.0
latency_p50_ms = 63.482
latency_p95_ms = 251.711
step_count_p50 = 6.0
step_count_p95 = 8.0
```

## Artifacts

```text
agent-lab/benchmarks/browser_tasks/reports/browser_operator_trial_results.jsonl
agent-lab/benchmarks/browser_tasks/reports/browser_operator_trial_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_operator_trial_scorecard.md
```

## Mission Results

Every mission completed 30/30 runs.

```text
BF-OP-001-click-visible-target       success=1.0 wilson_lower=0.8865
BF-OP-002-fill-grounded-field        success=1.0 wilson_lower=0.8865
BF-OP-003-repair-stale-ref           success=1.0 wilson_lower=0.8865
BF-OP-004-deny-ocr-only-target       success=1.0 wilson_lower=0.8865
BF-OP-005-deny-out-of-policy-action  success=1.0 wilson_lower=0.8865
BF-OP-006-multistep-fast-policy      success=1.0 wilson_lower=0.8865
```

## Interpretation

P4H-Y proves the P4H-X path is executable as an operator loop on local browser
fixtures.

It does not prove open-web or external browser supremacy.
