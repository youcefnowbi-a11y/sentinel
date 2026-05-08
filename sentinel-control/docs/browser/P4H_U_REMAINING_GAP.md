# P4H-U Remaining Gap

Date: 2026-04-30
Status: Open

## What P4H-U Proves

```text
12 representative Browser Fluency groups execute against live local pages
30 runs per mission
360 total iterations
Wilson intervals are reported
no artifact leakage observed
no authority violation observed
download quarantine preserves byte-level hash
redaction prevents raw cookie/HAR-style values from entering reports
```

## What P4H-U Does Not Prove

```text
all 72 Browser Fluency missions execute live
actual Chromium/Playwright rendering of every visual case
real OCR over noisy images and PDFs
open-web compatibility
external account/session compatibility
OpenClaw real-runtime comparison
browser supremacy on public benchmarks
```

## Next Hardening

P4H-V should expand live/self-hosted coverage from 12 representative missions
to the full 72-mission catalog.

Required additions:

```text
local fixture pages for all remaining mission ids
30-run scorecard for all 72 missions
per-mission Wilson intervals
secret scan after every report write
visual/OCR fixture expansion
SPA, redirect, stale ref, and conflict-resolution live fixtures
cross-class long workflow
```

P4G-R2 remains blocked until Docker or Podman is available.
