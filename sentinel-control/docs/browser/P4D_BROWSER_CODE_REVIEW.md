# P4D Browser Code Review

Date: 2026-04-29
Status: Complete

## Scope

This review covers the code paths that turn Browser V3 from contracts into
runtime behavior:

- `sentinel/agent/browser/v3_authority.py`;
- `sentinel/agent/browser/form_submit.py`;
- `sentinel/agent/browser/download_quarantine.py`;
- `sentinel/agent/browser/upload_authorized.py`;
- `sentinel/agent/browser/v3_advanced_authorities.py`;
- `sentinel/agent/browser/v3_live_adapter_harness.py`;
- `sentinel/agent/browser/v3_measured_supremacy.py`;
- `sentinel/agent/llm/context_pack.py`;
- `sentinel/agent/llm/tool_intent_compiler.py`;
- `sentinel/agent/llm/interface.py`;
- `sentinel/agent/browser/cortex.py`;
- `sentinel/agent/final_gate.py`;
- Browser V3 tests.

## Findings

### Finding 1: V3 authority classes are correctly separated

`BrowserV3AuthorityClass` defines the expected V3 class set. The grant model
also carries domains, accounts, script hashes, byte/record limits, storage
flags, redaction requirement, and blocked flow types.

This is the right design. It prevents a single broad browser permission from
implicitly granting login, storage, JS, upload, or HAR powers.

Residual risk: grants are still permissive when `allowed_domains` is empty.
That is acceptable for test fixtures but should be avoided in production
mission envelopes.

### Finding 2: Executors emit proof-rich events

Form submit, download quarantine, upload authorized, private session, login,
cookie/storage, JS, and HAR/body paths all emit class-specific accepted or
rejected events. Receipts are artifact-bound for the sensitive classes.

The code checks common V3 fields:

```text
authority_grant_id
context_pack_id
compiled_intent_trace_id
receipt/artifact hash
plan/ref/snapshot bindings where applicable
```

Residual risk: the class-specific code repeats similar validation patterns.
That is tolerable while the contracts are still evolving, but a table-driven V3
contract registry would reduce drift later.

### Finding 3: ToolIntentCompiler blocks obvious LLM bypasses

`ToolIntentCompiler` verifies ContextPack hash/id, mission allowed tools,
allowed actions, forbidden actions, available action intents, V3 grant presence,
runtime refs, stale hashes, prompt-injection boundaries, and sensitive V3 raw
payload markers.

This is one of the strongest parts of the implementation.

Residual risk: the non-delegated token scanner is intentionally conservative
but lexical. It should remain a guardrail, not the only semantic policy layer.

### Finding 4: FinalGate has broad V3 coverage

`CoreFinalGate` contains V3 contracts for:

- form submit;
- download quarantine;
- upload authorized;
- private session;
- login authority;
- cookie/storage contracts;
- sandboxed JS;
- HAR/body capture.

It checks class identity, compiled intent binding, receipts, artifact order,
hashes, redaction, no-network status, session close order, and quarantine
rules.

Residual risk: FinalGate is becoming large. Future hardening should split V3
contract data into a registry or helper module while keeping the final decision
centralized.

### Finding 5: Live adapter harness is real but fixture-bound

`BrowserV3LiveAdapterHarness` launches Chromium through Playwright, creates
temporary profile directories, exercises account-id login through a vault-style
stub, records network attempts during JS execution, and captures redacted HAR
metadata.

This is a real local live-adapter proof.

It is not an open-web proof. It routes fixture pages and aborts unknown network
requests. That is the correct harness boundary, but it must not be described as
external browser supremacy.

### Finding 6: EvalBench measurement is useful but statistically weak

`BrowserV3MeasuredSupremacyGate` covers nine mission groups and produces
accepted/success rates. The targeted test currently uses two iterations per
group and can report zero CI half-width when all runs pass.

This is useful as CI regression coverage.

It is not enough for a scientific benchmark claim.

## Code Hardening Items

| ID | Item | Severity | Recommendation |
| --- | --- | --- | --- |
| P4D-CODE-1 | Small-n CI can report zero uncertainty at 100% success. | High | Replace with Wilson interval or conservative lower/upper bound. |
| P4D-CODE-2 | V3-specific events are not fully mapped in BrowserEvidenceInterpreter. | High | Add explicit V3 cognitive event classes and tests. |
| P4D-CODE-3 | FinalGate V3 logic is correct but large. | Medium | Add V3 contract helper/registry after behavior stabilizes. |
| P4D-CODE-4 | Redaction tests are good but corpus is narrow. | Medium | Add nested JSON, form data, headers, query params, base64-like secrets. |
| P4D-CODE-5 | JS no-network tests need a larger adversarial corpus. | Medium | Add fetch/XHR/WebSocket/sendBeacon/import/image/script cases. |
| P4D-CODE-6 | P4C-S measured gate lives in browser package. | Low | Mirror long-term benchmark runners under dedicated eval namespace. |

## Code Verdict

The code is coherent and governed. It is good enough to remain locked as Browser
V3 architecture.

It is not enough to declare final browser supremacy. P4D hardening is required.
