# P4D Browser Brain/LLM Integration Review

Date: 2026-04-29
Status: Complete

## Doctrine

Browser content is evidence, not authority.

LLM output is draft intent, not execution.

The brain owns:

```text
mission authority
ContextPack construction
tool-intent compilation
risk routing
repair decisions
FinalGate acceptance
```

The browser owns:

```text
observation
bounded interaction
V3 authority-class execution
receipts
runtime artifacts
```

## What Works

### ContextPack

`ContextPackValidator` rejects mission mismatch, mission-goal mismatch,
authority expansion, forbidden action intents, citations without stable refs,
verified hypotheses without citations, prompt-injection source usage, and hash
mismatches.

This is the right LLM boundary.

### ToolIntentCompiler

`ToolIntentCompiler` rejects:

- raw tool calls without ContextPack binding;
- actions outside mission authority;
- actions not available in ContextPack;
- missing V3 grants;
- fabricated refs;
- stale page/snapshot hashes;
- prompt-injection refs;
- raw credential/cookie/storage/HAR payload attempts.

This keeps the LLM in a proposal role.

### LLM role stubs

`BrowserPlannerRole` drafts intent JSON only. `BrowserVerifierRole` produces a
grounding verdict only and cannot certify without receipt/evidence refs.

This is correct. No live LLM provider is required for P4D.

## Critical Gap

`BrowserEvidenceInterpreter` currently accepts the core Browser V2/P3H event
families:

```text
BROWSER_EVIDENCE_COLLECTED
BROWSER_SNAPSHOT_CAPTURED
BROWSER_INTERACTION_PLAN_CREATED
BROWSER_INTERACTION_EXECUTED
```

It also handles selected rejection events.

It does not yet explicitly model V3 event classes such as:

```text
BROWSER_FORM_SUBMIT_EXECUTED
BROWSER_DOWNLOAD_QUARANTINED
BROWSER_UPLOAD_AUTHORIZED_EXECUTED
BROWSER_PRIVATE_SESSION_STARTED/CLOSED
BROWSER_LOGIN_AUTHORITY_EXECUTED
BROWSER_COOKIE_STORAGE_CONTRACT_APPLIED
BROWSER_JS_EVALUATE_SANDBOXED_EXECUTED/REJECTED
BROWSER_HAR_BODY_CAPTURED
```

That means Browser V3 can be certified by FinalGate without being deeply
understood by the cognitive scoring layer.

This is not a security failure, because FinalGate and ToolIntentCompiler still
guard execution. It is an intelligence gap: the brain needs richer V3 semantics
for hypothesis, repair, and effort decisions.

## Required Integration Hardening

P4D requires adding explicit cognitive handling for V3 outputs:

| V3 signal | Brain meaning |
| --- | --- |
| form submit success | action progress, not evidence truth by itself |
| download quarantine | artifact available in quarantine, not promoted trust |
| upload authorized | outbound artifact side effect completed |
| private session opened | scoped runtime state exists, must close |
| login success | authenticated state exists; no credential evidence exposed |
| cookie/storage summary | tainted session metadata, redacted only |
| JS no-network rejection | repair/security success signal |
| HAR/body capture | sensitive diagnostic evidence, redacted and bounded |

## Tests Needed

Add mission-level tests where:

1. V3 form submit changes mission progress only after FinalGate passes.
2. Download quarantine creates evidence but not a trusted promoted artifact.
3. Login success does not create credential evidence in ContextPack.
4. Cookie/storage summaries cannot become user-visible raw facts.
5. JS network rejection triggers repair/security success.
6. HAR/body capture updates evidence quality only through redacted artifacts.
7. V3 rejection events raise repair pressure.
8. LLM drafted V3 intents are still compiler-only drafts.

## Verdict

P3Y correctly prevents LLM takeover.

P4D finds that V3 execution is more mature than V3 cognition. The next hardening
must connect V3 event semantics to Browser-Cortex and mission-level reasoning
without weakening the authority boundary.
