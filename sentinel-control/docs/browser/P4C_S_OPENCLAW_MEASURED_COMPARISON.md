# P4C-S OpenClaw Measured Comparison

Date: 2026-04-29
Status: Local measured comparison only

## Comparison Boundary

This document compares Sentinel Browser V3 against an OpenClaw-style browser
capability profile.

It does not import OpenClaw runtime code.
It does not claim external open-web benchmark victory.

## Measured Sentinel Result

| Metric | P4C-S local result |
| --- | ---: |
| Mission groups | 9 |
| Runs per group in targeted test | 2 |
| Accepted rate | 100% |
| Success rate | 100% |
| Unstable iterations | 0 |
| Trace quality | 100% |
| Proof completeness | 100% |
| Side-effect containment | 100% |

## Updated Capability View

| Axis | Sentinel Browser V3 measured state |
| --- | --- |
| Public evidence plus interaction | measured locally |
| Form submit | measured locally |
| Download quarantine | measured locally |
| Upload authorized | measured locally |
| Private/login/cookie | measured locally through P4C-H.3 harness |
| JS no-network denial | measured locally through runtime observation |
| HAR/body redaction | measured locally |
| Cross-class flow | measured locally |
| Failure denials | measured locally |
| External open-web robustness | not yet measured |

## Verdict

Sentinel Browser V3 is now peer-level in local measured authority-class
coverage.

It is not yet proven above a peer browser agent on external open-web tasks.

Next external proof would require a shared task suite with live public targets,
multi-run statistics, and failure injection.
