# P4H-U Failure Analysis

Date: 2026-04-30
Status: Complete

## Final Failure State

```text
total_iterations = 360
failed_iterations = 0
unstable_iterations = []
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
```

## Issue Found During Development

The first local run exposed a Windows-specific hash mismatch in the download
quarantine fixture.

Cause:

```text
network body hash was computed over bytes
quarantine fixture used text write
Windows line-ending translation changed the file bytes
artifact hash mismatch triggered failure
```

Fix:

```text
download quarantine now writes bytes exactly as fetched
artifact hash matches response body hash
```

Why this matters:

```text
P4H-U caught a real proof bug
the runner did not mask the failure
the fix preserves byte-level artifact integrity
```

## Remaining Failure Classes Not Yet Covered

```text
real browser rendering failure
real OCR model errors
external DNS/network instability
JavaScript-heavy SPA timing
third-party cookie/storage behavior
large HAR/body redaction pressure
long-horizon research navigation
real peer-runtime comparison failure modes
```
