# P4H-R First Browser Fluency Scorecard

Date: 2026-04-30
Status: Complete

## Summary

```text
verdict = browser_fluency_first_subset_partial
catalog_mission_count = 72
executed_count = 42
target_met_count = 27
partial_count = 15
not_run_count = 30
target_met_rate_executed = 0.643
```

## Metric Summary

| Metric | Score |
| --- | ---: |
| `task_success` | 0.912 |
| `authority_correctness` | 0.917 |
| `proof_completeness` | 0.912 |
| `grounding_correctness` | 0.982 |
| `state_hygiene` | 1.000 |
| `visual_accuracy` | 0.996 |
| `research_quality` | 0.996 |
| `repair_quality` | 0.954 |
| `safety_denial` | 0.987 |

## Group Levels

| Group | Executed | Target met | Partial | Not run | Level |
| --- | ---: | ---: | ---: | ---: | --- |
| `life` | 6 | 5 | 1 | 0 | `F2` |
| `nav` | 6 | 4 | 2 | 0 | `F2` |
| `perc` | 6 | 4 | 2 | 0 | `F3` |
| `vis` | 0 | 0 | 0 | 6 | `F0` |
| `form` | 6 | 4 | 2 | 0 | `F1` |
| `state` | 0 | 0 | 0 | 6 | `F0` |
| `file` | 0 | 0 | 0 | 6 | `F0` |
| `net` | 6 | 4 | 2 | 0 | `F2` |
| `tab` | 0 | 0 | 0 | 6 | `F0` |
| `res` | 0 | 0 | 0 | 6 | `F0` |
| `safe` | 6 | 5 | 1 | 0 | `F1` |
| `cog` | 6 | 1 | 5 | 0 | `F1` |

## Interpretation

Sentinel is strongest in:

```text
perception / grounding
safety denial
proof / authority metrics
```

Sentinel is still partial in:

```text
forms as a full fluency group
network failure repair
cognitive integration as measured fluency
crash recovery
SPA route handling
autocomplete
CAPTCHA/bot-wall stop fixtures
modality escalation
```

Not yet executed in P4H-R:

```text
visual/OCR
cookies/storage/sessions
files/PDF/uploads/downloads
multi-tab comparison
research browsing
```
