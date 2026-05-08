# P4C-S Cross-Class Eval Missions

Date: 2026-04-29
Status: Implemented

## EvalBench Contract

P4C-S uses `SentinelEvalBench`.

Each mission group declares:

- expected success;
- expected final phase;
- required artifact file;
- stable artifact file;
- required Browser V3 events;
- required selected tools.

## Required Event Examples

```text
public_evidence_interaction:
  BROWSER_EVIDENCE_COLLECTED
  BROWSER_INTERACTION_EXECUTED

form_submit:
  BROWSER_FORM_SUBMIT_EXECUTED

download_quarantine:
  BROWSER_DOWNLOAD_QUARANTINED

upload_authorized:
  BROWSER_UPLOAD_AUTHORIZED_EXECUTED

cross_class_flow:
  BROWSER_PRIVATE_SESSION_STARTED
  BROWSER_LOGIN_AUTHORITY_EXECUTED
  BROWSER_COOKIE_STORAGE_CONTRACT_APPLIED
  BROWSER_HAR_BODY_CAPTURED
  BROWSER_PRIVATE_SESSION_CLOSED

failure_denials:
  BROWSER_FORM_SUBMIT_REJECTED
  TOOL_INTENT_COMPILATION_REJECTED
  BROWSER_LOGIN_AUTHORITY_REJECTED
```

## Denial Missions

The failure group succeeds only if denials occur:

- stale form-submit snapshot is rejected;
- cross-origin post-action result is rejected;
- prompt-injected stable refs cannot compile an action intent;
- backend exception containing secret-like strings is redacted before trace
  exposure.

## Stability Rule

Repeated runs must produce stable behavioral signatures:

```text
same success
same final phase
same selected tools
same event type sequence
same stable artifact hashes
same certification status
```
