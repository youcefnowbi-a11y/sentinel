# P4A Browser V2.5 Architecture

Status: locked

P4A upgrades Browser V2 from a public operator to an advanced public perception and grounding organ. It does not open Browser V3 authority classes.

## Scope

P4A adds:

- CDP-native accessibility tree normalization.
- DOMSnapshot and layout normalization.
- Unified `BrowserUIObservation` records.
- Visual crop/zoom observation metadata with OCR stub only.
- Public/stateless browser pool accounting.
- Public multi-tab strategy orchestration.
- Post-action verifier and loop detector.
- FinalGate checks for forged V2.5 observations and operator events.

## Execution Boundary

P4A remains public/stateless:

- `stateless_public = true`
- `cookies_enabled = false`
- `storage_enabled = false`
- `js_enabled = false`
- `downloads_enabled = false`

The following are still non-delegated until Browser V3 authority classes exist:

- login
- private sessions
- cookies or storage
- form submit, post, send, publish
- upload or download execution
- arbitrary JavaScript evaluate
- credentials or payment
- remote browser node

## Architecture

```text
Rendered Snapshot / Runtime Payload
-> CDP AX adapter
-> DOMSnapshot adapter
-> Visual observation builder
-> UIObservation builder
-> Verifier / loop detector
-> EventBus
-> FinalGate
```

LLM-derived browser intents still pass through:

```text
ContextPack
-> ToolIntentCompiler
-> ToolRegistry / authority route
-> browser contract
-> receipt / observation proof
-> FinalGate
```

## Lock Criteria

P4A is locked only when:

- targeted P4A tests pass;
- full core tests pass;
- compileall passes;
- vendor-trace scan is clean;
- execution-boundary scan is clean;
- no Browser V3 power appears in P4A runtime;
- `P4A_LOCK_VERDICT.md` records the result.
