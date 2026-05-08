# P4H-Z Failure Analysis

Date: 2026-04-30
Status: No observed failures in 30-run fixture campaign

## Observed Failures

```text
unstable_iterations = []
false_action_rate = 0.0
authority_violation_rate = 0.0
```

## Negative Cases Covered

```text
low confidence ambiguous target -> denied
OCR-only target -> denied
fabricated runtime ref -> denied
step budget exceeded -> denied
first verifier miss -> repaired inside policy
```

## Remaining Gaps

P4H-Z does not prove:

```text
open-web robustness
real dynamic site compatibility
real visual coordinate actuation
full form submit authority through ActionEngine
download/upload cross-class workflows through ActionEngine
desktop/image/pdf/video runtime
external peer superiority
```

## Next Hardening Candidates

```text
open-web-safe live corpus
dynamic DOM mutation between perception and action
multi-tab perception/action chain
real visual crop selection under small targets
form_submit authority path through ActionEngine
download/upload authority path through ActionEngine
latency stress with larger scene graphs
```
