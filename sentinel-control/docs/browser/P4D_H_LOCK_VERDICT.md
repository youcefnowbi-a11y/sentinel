# P4D-H Lock Verdict

Date: 2026-04-29
Status: Locked

## Final Decision

P4D-H is locked.

Browser V3 is now:

```text
architecturally governed
locally proven
statistically better reported
cognitively mapped into Browser-Cortex
adversarially hardened for JS/HAR/cookie redaction
locally scored at 10 runs per mission group
```

## What Changed

Code:

- EvalBench now uses Wilson score intervals and reports lower/upper bounds.
- EvalBench now reports event-count step proxies.
- Browser-Cortex now maps Browser V3 event families explicitly.
- Browser V3 measured scores carry Wilson bounds and event-count metrics.
- Fixture measured mode now works without the live harness.
- Live HAR redaction now hashes query parameter names, not only values.
- Redaction detection now covers token/API-key/access-token style keys.

Tests:

- small-n perfect-rate Wilson interval test;
- V3 cognitive mapping tests;
- ContextPack no credential evidence from login event;
- JS adversarial network corpus;
- cookie/storage and HAR/body adversarial redaction corpus;
- local 10-run Browser V3 measured scorecard.

Docs:

- `P4D_H_EVALBENCH_STATS_HARDENING.md`;
- `P4D_H_BROWSER_V3_COGNITIVE_MAPPING.md`;
- `P4D_H_ADVERSARIAL_CORPUS.md`;
- `P4D_H_LOCAL_10RUN_SCORECARD.md`;
- `P4D_H_SELF_HOSTED_BENCHMARK_PLAN.md`;
- `P4D_H_LOCK_VERDICT.md`.

## Current Sentinel vs OpenClaw Browser Verdict

Sentinel is stronger on governance:

```text
MissionAuthority
ContextPack
ToolIntentCompiler
receipts
FinalGate
redaction/quarantine
forgery rejection
```

OpenClaw-style browser is still stronger on proven raw runtime breadth:

```text
long-lived browser runtime
session/page target ergonomics
broad action routes
role ref cache
debug/trace routes
upload/download/dialog/response body maturity
more mature Playwright/CDP runtime surface
```

So the honest comparison is:

```text
Sentinel = stronger governed browser operating system.
OpenClaw = stronger proven raw browser automation runtime.
```

Sentinel can surpass OpenClaw only after self-hosted and external benchmark
campaigns prove comparable raw runtime breadth under Sentinel governance.

## Remaining Boundary

No external browser supremacy is claimed.

P4D-H supports this claim:

```text
Browser V3 is locally hardened and benchmark-ready.
```

It does not support this claim yet:

```text
Browser V3 beats OpenClaw on the open web.
```

## Next Decision

For browser supremacy:

```text
run self-hosted benchmark implementation
-> run external/open-web peer campaign
```

For product sequencing:

```text
the browser can be treated as locally hardened,
but any claim of superiority must wait for external benchmark proof.
```
