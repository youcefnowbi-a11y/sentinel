# P4H-T Browser Fluency Depth Scorecard

Date: 2026-04-30
Status: Complete

## Scope

P4H-T hardens the 18 missions that remained partial after P4H-S.

No new browser power was added. This gate only changes the Browser Fluency
fixture profile used to score existing, already-authorized browser surfaces.

## Runner Output

Source:

```text
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_depth_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_depth_results.jsonl
```

Observed result:

```text
run_id = p4h_t_depth_scorecard
verdict = browser_fluency_depth_contract_ready
catalog_mission_count = 72
executed_count = 72
target_met_count = 72
partial_count = 0
not_run_count = 0
target_met_rate_executed = 1.0
latency_ms_mean = 17.989
step_count_mean = 7.944
```

## Metric Summary

| Metric | Score |
| --- | ---: |
| `task_success` | 1.0 |
| `authority_correctness` | 1.0 |
| `proof_completeness` | 1.0 |
| `grounding_correctness` | 1.0 |
| `state_hygiene` | 1.0 |
| `visual_accuracy` | 1.0 |
| `research_quality` | 1.0 |
| `repair_quality` | 1.0 |
| `safety_denial` | 1.0 |

## Group Levels

| Group | Missions | Target met | Group level |
| --- | ---: | ---: | --- |
| `life` | 6 | 6 | `F3` |
| `nav` | 6 | 6 | `F3` |
| `perc` | 6 | 6 | `F3` |
| `vis` | 6 | 6 | `F3` |
| `form` | 6 | 6 | `F3` |
| `state` | 6 | 6 | `F4` |
| `file` | 6 | 6 | `F3` |
| `net` | 6 | 6 | `F3` |
| `tab` | 6 | 6 | `F3` |
| `res` | 6 | 6 | `F3` |
| `safe` | 6 | 6 | `F4` |
| `cog` | 6 | 6 | `F4` |

## Interpretation

P4H-T proves that the full 72-mission Browser Fluency catalog has a complete
contract-fixture path. Every mission now has enough authority, proof, grounding,
repair, safety, or cognition evidence to meet its declared target level.

This is not an external browser supremacy claim. It is a contract readiness
claim for the Sentinel-owned fluency exam.
