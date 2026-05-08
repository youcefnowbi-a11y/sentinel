# P4H-V Failure Analysis

Date: 2026-04-30
Status: Complete

## Final Failure State

```text
total_iterations = 2160
failed_iterations = 0
unstable_iterations = []
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
```

## Development Regression Checks

P4H-V preserved the P4H-U fix for byte-exact download quarantine. The full
scorecard includes:

```text
download_quarantine = 30/30 pass
download_denial = 30/30 pass
upload_artifact = 30/30 pass
arbitrary_upload_denial = 30/30 pass
```

## Remaining Failure Classes Outside This Gate

```text
browser-engine rendering differences
real OCR confidence drift
real website SPA timing
third-party authentication behaviors
external network instability
large real HAR redaction pressure
complex open-web research routes
peer runtime comparison failures
```

These are outside P4H-V because P4H-V is a self-hosted local fixture benchmark.
