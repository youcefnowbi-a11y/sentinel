# P4H-S Full Browser Fluency Scorecard

Date: 2026-04-30
Status: Complete

## Summary

Source:

```text
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_full_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_full_results.jsonl
```

Result:

```text
verdict = browser_fluency_full_scorecard_partial
catalog_mission_count = 72
executed_count = 72
target_met_count = 54
partial_count = 18
not_run_count = 0
target_met_rate_executed = 0.75
```

## Metrics

| Metric | Score |
| --- | ---: |
| `task_success` | 0.952 |
| `authority_correctness` | 0.952 |
| `proof_completeness` | 0.952 |
| `grounding_correctness` | 0.992 |
| `state_hygiene` | 1.000 |
| `visual_accuracy` | 0.995 |
| `research_quality` | 0.989 |
| `repair_quality` | 0.984 |
| `safety_denial` | 0.997 |

## Group Levels

| Group | Level | Target met | Partial |
| --- | --- | ---: | ---: |
| `life` | `F3` | 5 | 1 |
| `nav` | `F3` | 5 | 1 |
| `perc` | `F3` | 6 | 0 |
| `vis` | `F3` | 4 | 2 |
| `form` | `F3` | 5 | 1 |
| `state` | `F4` | 6 | 0 |
| `file` | `F3` | 5 | 1 |
| `net` | `F3` | 5 | 1 |
| `tab` | `F3` | 2 | 4 |
| `res` | `F3` | 3 | 3 |
| `safe` | `F3` | 5 | 1 |
| `cog` | `F3` | 3 | 3 |

## Interpretation

P4H-S removes the old F0/F1/F2 group floor from the first scorecard. Every group
now has at least F3 contract-fixture coverage, and state/session hygiene reaches
F4.

This is not a final Browser Fluency claim because 18 missions remain partial and
the scorecard is still fixture-bound, not open-web F5.
