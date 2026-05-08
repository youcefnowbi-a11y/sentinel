# P4H-W Lock Verdict

Date: 2026-04-30
Status: Locked

## Verdict

P4H-W is accepted as a controlled local browser-engine visual/OCR harness.

```text
Browser visual evidence path = pass
OCR as fallback only = pass
runtime ref binding = pass
crop/zoom artifact binding = pass
post-action visual verifier event = pass
FinalGate V2.5 check = pass
30-run scorecard = pass
```

## What Was Proven

```text
real Playwright-rendered screenshot is captured
element screenshot crop is captured as artifact
crop/zoom observation is hash-bound
visual observation includes page/snapshot/viewport metadata
visual candidate binds to runtime accessibility ref
OCR fallback cannot create action authority
post-action visual verifier emits FinalGate-valid proof
BF-VIS-001..006 pass 30 runs each
```

## What Was Not Proven

```text
open-web visual robustness
real OCR model accuracy
complex charts beyond the fixture
dynamic visual pages with JS enabled
CAPTCHA or anti-bot handling
peer/OpenClaw visual superiority
```

## Decision

Browser P4H-W is locked as a local visual perception slice.

Next recommended gate:

```text
P4H-X - Visual hardening with broader self-hosted visual corpus
```

P4H-X should expand the visual corpus before any final browser completion claim.
