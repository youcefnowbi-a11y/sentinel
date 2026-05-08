# P4C-S Browser V3 Measured Supremacy Gate

Date: 2026-04-29
Status: Implemented

## Goal

P4C-S measures Browser V3 as a runtime capability surface.

It does not add browser powers. It measures the powers already delegated by
P4B/P4C:

- public evidence plus limited interaction;
- form submit;
- download quarantine;
- upload authorized;
- private session plus login plus cookie/storage summary;
- sandboxed JS no-network denial;
- HAR/body redaction;
- cross-class private/login/cookie/HAR flow;
- denial cases for stale refs, prompt-injected refs, cross-origin result, and
  credential leak attempts.

## Implementation

The gate is implemented by:

```text
sentinel.agent.browser.v3_measured_supremacy.BrowserV3MeasuredSupremacyGate
```

It runs through `SentinelEvalBench`, not through a separate benchmark path.

Each mission group becomes an `EvalCase`. The runtime executes actual Browser V3
executors and then reports:

- `run_count`;
- `accepted_rate`;
- `success_rate`;
- CI95 half widths;
- unstable iterations;
- trace quality;
- proof completeness;
- side-effect containment.

## Measured Local Result

The targeted P4C-S test ran:

```text
9 mission groups
2 runs per group
accepted_rate = 1.0
success_rate = 1.0
unstable_iterations = []
```

This is enough to lock local measured Browser V3 readiness.

## Boundary

This is not an external open-web benchmark.

The verdict is:

```text
Browser V3 is locally measured as ready for next organ work.
External browser-supremacy claims still require a broader open-web benchmark.
```
