# P4H-W-R Visual Benchmark Plan

Date: 2026-04-30
Status: Research plan

## Goal

Design P4H-W as a real browser-engine visual benchmark, not a contract score.

## Mission Groups

P4H-W should add a focused visual benchmark slice:

| Group | Test |
| --- | --- |
| screenshot fidelity | viewport hash, dimensions, nonblank pixels |
| crop binding | element crop bbox binds to screenshot and stable ref |
| zoom improvement | zoom crop improves small-text confidence |
| visual target grounding | choose correct duplicate visual target |
| visual uncertainty | refuse unreadable text |
| OCR fallback | image/PDF text extraction with confidence |
| chart/table visual | answer only from bounded crop |
| post-action visual delta | after screenshot confirms expected UI change |
| prompt-injected visual text | detected and confidence-limited |
| stale visual ref | rejected after DOM/screenshot epoch changes |

## Metrics

```text
visual_success_rate
grounding_correctness
crop_ref_binding_rate
ocr_accuracy_on_fixture
uncertainty_correctness
post_action_visual_verification_rate
forged_visual_event_rejection_rate
artifact_leakage_rate
authority_violation_rate
latency_p50/p95
step_count_p50/p95
Wilson interval
```

## Evidence Required

Every accepted mission needs:

```text
screenshot artifact hash
source page/snapshot hash
visual region/crop hash when used
stable ref binding when used
OCR confidence when used
post-action screenshot when action is executed
FinalGate visual proof event
```

## P4H-W Acceptance

```text
no new browser powers
no arbitrary JS
no external accounts
no host browser profile
real browser-engine screenshots are nonblank
visual crops bind to source screenshots
OCR is fallback-only
prompt-injected visual text cannot create actions
full tests pass
scans clean
```
