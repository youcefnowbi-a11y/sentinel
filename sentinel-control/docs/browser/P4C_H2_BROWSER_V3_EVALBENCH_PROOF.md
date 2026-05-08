# P4C-H.2 Browser V3 EvalBench Proof

Date: 2026-04-29
Status: Completed

## Goal

Use EvalBench multi-run metrics against a Browser V3 fixture backend mission.

## Implemented Case

`test_browser_v3_fixture_evalbench_multi_run_metrics` runs a Browser V3 fixture
mission for three iterations.

The runtime:

- creates a scoped project artifact;
- opens a fixture private session;
- closes and destroys the fixture profile;
- emits Browser V3 private-session events;
- checks the private-session FinalGate contract;
- returns a certified `AgentRunResult`.

## Required Checks

EvalBench verifies:

- expected success;
- expected final phase;
- required scoped artifact;
- required Browser V3 session open/close events;
- required selected browser tool;
- multi-run signature stability.

## Metrics Verified

```text
run_count = 3
accepted_rate = 1.0
success_rate = 1.0
unstable_iterations = []
```

## Verdict

Browser V3 now has a first multi-run EvalBench proof path. This is the minimum
statistical layer needed before live adapter benchmarks.
