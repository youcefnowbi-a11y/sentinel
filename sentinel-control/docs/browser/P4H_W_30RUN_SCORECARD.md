# P4H-W 30-Run Visual Scorecard

Date: 2026-04-30
Status: Pass

Source report:

```text
agent-lab/benchmarks/browser_tasks/reports/browser_visual_engine_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_visual_engine_scorecard.md
```

## Summary

```text
run_id = p4h_w_real_visual_engine_30run
mission_count = 6
run_count_per_mission = 30
total_iterations = 180
success_count = 180
success_rate = 1.0
wilson_lower = 0.9791
wilson_upper = 1.0
visual_accuracy = 1.0
grounding_correctness = 1.0
proof_completeness = 1.0
repair_quality = 0.1667
verdict = browser_visual_engine_local_pass
boundary = local_playwright_readonly_fixture_not_open_web_not_ocr_primary
```

## Mission Results

| Mission | Runs | Success | Wilson lower | Visual | Grounding | Proof | Repair |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `BF-VIS-001` | 30 | 1.0 | 0.8865 | 1.0 | 1.0 | 1.0 | 0.0 |
| `BF-VIS-002` | 30 | 1.0 | 0.8865 | 1.0 | 1.0 | 1.0 | 0.0 |
| `BF-VIS-003` | 30 | 1.0 | 0.8865 | 1.0 | 1.0 | 1.0 | 0.0 |
| `BF-VIS-004` | 30 | 1.0 | 0.8865 | 1.0 | 1.0 | 1.0 | 0.0 |
| `BF-VIS-005` | 30 | 1.0 | 0.8865 | 1.0 | 1.0 | 1.0 | 0.0 |
| `BF-VIS-006` | 30 | 1.0 | 0.8865 | 1.0 | 1.0 | 1.0 | 1.0 |

## Interpretation

This scorecard proves local browser-engine visual grounding stability. It does
not prove open-web visual fluency or OCR model quality.
