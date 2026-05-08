# P4D-H Local 10-Run Scorecard

Date: 2026-04-29
Status: Complete

## Scope

This scorecard uses the local Browser V3 measured corpus with 10 runs per
mission group and Wilson score intervals.

It is a local proof, not an external open-web benchmark.

## Result

```text
verdict = browser_v3_ready_for_next_organ
measured_success_rate = 1.0
measured_acceptance_rate = 1.0
run_count_per_group = 10
confidence_interval_method = wilson_score_95
```

## Mission Group Scorecard

| Mission group | Runs | Observed success | Wilson lower | Wilson upper | CI half-width | Mean event count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| public evidence + interaction | 10 | 1.0 | 0.7225 | 1.0 | 0.1388 | 6.0 |
| form submit | 10 | 1.0 | 0.7225 | 1.0 | 0.1388 | 6.0 |
| download quarantine | 10 | 1.0 | 0.7225 | 1.0 | 0.1388 | 5.0 |
| upload authorized | 10 | 1.0 | 0.7225 | 1.0 | 0.1388 | 7.0 |
| private/login/cookie | 10 | 1.0 | 0.7225 | 1.0 | 0.1388 | 15.0 |
| JS no-network | 10 | 1.0 | 0.7225 | 1.0 | 0.1388 | 3.0 |
| HAR redaction | 10 | 1.0 | 0.7225 | 1.0 | 0.1388 | 4.0 |
| cross-class flow | 10 | 1.0 | 0.7225 | 1.0 | 0.1388 | 18.0 |
| failure denials | 10 | 1.0 | 0.7225 | 1.0 | 0.1388 | 13.0 |

## Interpretation

The observed result is excellent.

The Wilson lower bound is the important correction: it prevents the project from
pretending that 10 local successes prove a 100% true success rate.

## Verdict

P4D-H materially improves the scientific quality of the local Browser V3 proof.

External supremacy remains unproven until a broader self-hosted or open-web
benchmark campaign runs.
