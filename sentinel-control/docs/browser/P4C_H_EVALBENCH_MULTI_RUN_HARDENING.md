# P4C-H EvalBench Multi-Run Hardening

Date: 2026-04-29
Status: Completed

## Goal

P4C-H makes EvalBench report multi-run statistics instead of only pass/fail
checks.

## Implementation

`EvalCaseResult` now carries `EvalMetricSummary`:

- `run_count`;
- `accepted_count`;
- `success_count`;
- `accepted_rate`;
- `success_rate`;
- `accepted_rate_ci95_half_width`;
- `success_rate_ci95_half_width`;
- `unstable_iterations`.

The confidence interval is a binomial normal-approximation half width:

```text
CI95_half_width = 1.96 * sqrt(p * (1 - p) / n)
```

## Why This Matters

Browser V3 cannot be called strong only because one deterministic test passes.
P4C-H starts measuring:

- whether repeated runs are accepted;
- whether repeated runs succeed;
- whether signatures drift;
- how wide the statistical uncertainty is.

## Tests Added

- successful repeated EvalBench case exposes run count, accepted rate, success
  rate, and no unstable iterations;
- artifact drift case exposes unstable iteration metadata in metrics.

## Verdict

EvalBench now has the minimum statistical surface needed for Browser V3
multi-run hardening. The next step is to add V3 browser-specific EvalBench cases
that use these metrics.
