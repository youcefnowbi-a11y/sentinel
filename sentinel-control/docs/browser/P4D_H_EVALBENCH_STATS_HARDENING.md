# P4D-H EvalBench Statistics Hardening

Date: 2026-04-29
Status: Complete

## Purpose

P4D found that the old EvalBench confidence interval could report `0.0`
uncertainty when the observed rate was `1.0`, even with only two runs.

P4D-H fixes that.

## Code Changes

`sentinel/agent/eval_bench.py` now reports Wilson score intervals:

```text
accepted_rate_ci95_lower
accepted_rate_ci95_upper
success_rate_ci95_lower
success_rate_ci95_upper
confidence_interval_method = wilson_score_95
```

The legacy half-width fields remain for compatibility, but they are now derived
from the Wilson interval.

EvalBench also reports simple step proxies:

```text
event_count_min
event_count_max
event_count_mean
```

## Why Wilson

The normal approximation:

```text
1.96 * sqrt(p * (1-p) / n)
```

collapses to zero when `p = 1.0`.

Wilson does not. With 10/10 observed successes, the observed rate is still
`1.0`, but the lower bound is approximately `0.7225`.

That is the right posture: strong local result, no fake certainty.

## Test Coverage

Added `test_eval_bench_reports_wilson_interval_for_small_n_perfect_rate`.

The test verifies that a 2/2 perfect run reports:

- observed success rate = `1.0`;
- method = `wilson_score_95`;
- lower bound < `1.0`;
- half-width > `0.0`;
- event count metrics exist.

## Verdict

P4D-H closes the false-certainty issue.

Future external benchmark reports must use Wilson or a more conservative
interval, not the old normal approximation.
