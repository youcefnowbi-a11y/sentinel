# P4D Browser Grand Review

Date: 2026-04-29
Status: Review gate complete

## Purpose

P4D is a hard review gate after P4C-S. It does not add browser powers and it
does not start the next organ.

The goal is to decide whether the current Browser V3 work is:

```text
implemented
governed
locally measured
scientifically proven
ready for external peer benchmark
```

Those are different claims. P4D keeps them separate.

## Direct Verdict

Browser V3 is not "finished" in the scientific sense yet.

The current state is:

```text
Browser V3 authority architecture = strong
Browser V3 local fixture/live proof = strong
Browser V3 local measured corpus = useful smoke/regression gate
Browser V3 external benchmark supremacy = not proven
```

The correct decision is:

```text
Browser architecture remains locked.
Browser scientific hardening is required before any supremacy claim.
External benchmark campaign remains a separate gate.
```

## Reviewed Surface

P4D reviewed these Sentinel-native browser areas:

- Browser V3 authority kernel: `v3_authority.py`;
- V3 class executors: `form_submit.py`, `download_quarantine.py`,
  `upload_authorized.py`, `v3_advanced_authorities.py`;
- runtime routing: `controlled_runner.py`;
- live harness and local measured gate: `v3_live_adapter_harness.py`,
  `v3_measured_supremacy.py`;
- LLM boundary: `context_pack.py`, `tool_intent_compiler.py`,
  `interface.py`;
- Brain/Cortex: `cortex.py`, `runtime.py`, `world_model.py`,
  `effort_router.py`, `repair_loop.py`;
- certification: `final_gate.py`;
- tests and P4C-S docs.

## What Is Strong

The V3 browser is no longer a raw browser surface. Each high-impact capability
enters through an explicit authority class:

- `browser_form_submit`;
- `browser_download_quarantine`;
- `browser_upload_authorized`;
- `browser_private_session`;
- `browser_login_authority`;
- `browser_cookie_storage_contract`;
- `browser_js_evaluate_sandboxed`;
- `browser_har_body_capture`.

Each class has a grant/request/receipt/event/FinalGate shape. The LLM cannot
directly execute a browser action: the ContextPack and ToolIntentCompiler remain
in the path.

## What Is Not Strong Enough Yet

P4C-S uses a local measured corpus, but the targeted test records only two runs
per mission group. That is good for regression, not for a statistical browser
supremacy claim.

The EvalBench confidence interval currently uses a normal binomial half-width.
When the observed rate is `1.0`, the half-width becomes `0.0`, even with only a
small number of runs. That can mislead a reader into thinking there is no
uncertainty. P4D marks this as a hardening item.

The Brain/Cortex interpreter currently consumes core Browser V2/P3H event types
well, but V3-specific events need explicit cognitive mapping. Private session,
login, cookie/storage, JS, and HAR/body outputs must not be treated as new
authority or as ordinary evidence without sensitivity class.

## Hardening Queue

P4D creates this required queue:

1. Replace normal-approximation CI for small-n browser gate reports with Wilson
   or a conservative rule-of-three style bound.
2. Expand P4C-S from smoke runs to at least 10 local runs per mission group.
3. Add adversarial redaction suites for cookie/storage and HAR/body capture.
4. Add adversarial JS no-network corpus covering fetch, XHR, WebSocket,
   sendBeacon, image/script loading, and dynamic import attempts.
5. Add mission-level Brain/LLM tests where V3 outputs alter hypothesis,
   repair, effort, or action choice through explicit evidence chains.
6. Move or mirror long-term benchmark harnesses under a dedicated EvalBench
   package so product runtime does not become benchmark-heavy.
7. Run a self-hosted WebArena-style corpus before any open-web peer claim.

## Final Decision

P4D decision is `B + C`:

```text
B) Browser V3 needs scientific hardening.
C) External/open-web benchmark campaign is required before supremacy claim.
```

Browser V3 remains powerful and governed, but it is not declared fully finished.
