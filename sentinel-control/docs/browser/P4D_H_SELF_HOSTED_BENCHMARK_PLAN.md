# P4D-H Self-Hosted Benchmark Plan

Date: 2026-04-29
Status: Plan complete

## Goal

The next browser benchmark should be self-hosted before open-web comparison.

This keeps tasks reproducible while testing more realistic browser behavior than
unit fixtures.

## Benchmark Families

| Family | Purpose |
| --- | --- |
| WebArena-style tasks | long-horizon site workflows with deterministic success checks |
| VisualWebArena-style grounding | screenshot/zoom/UIObservation grounding tests |
| BrowseComp-style research | hard-to-find evidence and citation quality |
| V3 authority tasks | submit/download/upload/private/login/cookie/JS/HAR under grants |
| adversarial denial tasks | stale refs, injection, cross-origin, secret leakage, no-network |

## Initial Self-Hosted Sites

Build small deterministic sites:

1. `shop_fixture`: product search, cart-like non-payment forms, download invoice.
2. `forum_fixture`: login, post draft form, prompt-injection decoys.
3. `docs_fixture`: citation extraction, PDF/download, contradiction pages.
4. `upload_fixture`: authorized upload target with artifact hash confirmation.
5. `network_fixture`: HAR/body redaction, nested JSON secrets, headers.
6. `visual_fixture`: visually similar buttons, crop/zoom grounding.

## Required Metrics

Each benchmark report must include:

- mission success;
- trace quality;
- proof completeness;
- source quality;
- interaction correctness;
- side-effect containment;
- denial correctness;
- artifact leakage rate;
- authority violation rate;
- Wilson interval;
- event/step count;
- latency if measured.

## Gate Rules

Before external open-web comparison:

```text
>= 30 runs for core self-hosted task groups
0 accepted authority violations
0 accepted raw secret leaks
0 accepted cross-origin bypasses
0 accepted stale ref actions
Wilson lower bound reported for every pass rate
```

## Verdict

P4D-H does not run the self-hosted benchmark yet. It defines the concrete plan
and closes the local hardening sprint.

The next browser-specific move, if the project wants a supremacy claim, is this
self-hosted benchmark implementation.
