# P4H-X-R GUI Grounding Benchmark Research

Date: 2026-04-30
Status: Research lock

## Benchmark Goal

P4H-X must test whether Sentinel can perceive and act, not only whether it can
store visual proof.

## Research Signals

| Benchmark / paper | What Sentinel should learn |
| --- | --- |
| VisualWebArena | Web tasks require realistic visual grounding, not only DOM extraction. |
| OSWorld | Computer-use agents must be evaluated by execution in real environments. |
| SeeClick / ScreenSpot | GUI grounding is the core skill: map instruction to screen element. |
| ScreenSpot-Pro | Professional high-resolution UIs expose small target and complex layout weakness. |
| UI-E2I / UI-I2E | Existing benchmarks can overestimate agents because elements are too large and instructions too explicit. |
| UI-Vision | Desktop benchmarks should measure element grounding, layout grounding, and action prediction separately. |

## Source References

```text
VisualWebArena: https://aclanthology.org/2024.acl-long.50/
OSWorld: https://os-world.github.io/
SeeClick / ScreenSpot: https://arxiv.org/abs/2401.10935
ScreenSpot-Pro: https://arxiv.org/abs/2504.07981
UI-E2I / UI-I2E: https://www.microsoft.com/en-us/research/articles/ui-e2i-synth-realistic-and-challenging-ui-grounding-benchmark-for-computer-use-agents/
UI-Vision: https://proceedings.mlr.press/v267/nayak25a.html
```

## Required Scenario Families

```text
small UI element grounding
high-resolution target search
ambiguous repeated targets
implicit instruction target selection
DOM/AX missing or incomplete
OCR weak or contradictory
visual prompt injection
stale visual refs
chart/table/image text
post-action visual verification
auto-repair after failed action
```

## Metrics

```text
mission_success
action_success_rate
visual_accuracy
grounding_correctness
target_ref_validity
ocr_confidence_calibration
implicit_instruction_success
small_element_success
false_action_rate
authority_violation_rate
repair_quality
step_count_p50_p95
latency_p50_p95
proof_completeness
Wilson interval
```

## Score Split

Sentinel should report two separate scores:

```text
raw operator score
governed operator score
```

Raw operator score measures completion and speed.

Governed operator score measures authority correctness, receipt completeness,
and boundary adherence.

## Next Benchmark Step

After P4H-X-R, the first code benchmark should be:

```text
Browser-backed PerceptionEngine v0 + ActionEngine v0
```

with:

```text
30-run local visual/action tasks
Wilson intervals
step count p50/p95
latency p50/p95
post-action verifier pass rate
```
