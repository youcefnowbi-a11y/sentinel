# P4C Browser V3 Failure Modes

Date: 2026-04-29
Status: Completed

## Failure Register

| Failure mode | Current control | P4C verdict |
| --- | --- | --- |
| Missing authority grant | ToolIntentCompiler rejection | Covered |
| Action not in ContextPack | ToolIntentCompiler rejection | Covered |
| Fabricated/stale ref | provenance checks | Covered where refs apply |
| Raw LLM submit/tool call | ToolCallProtocol + compiler | Covered |
| Private session left open | FinalGate close proof check | Covered |
| Credential leaked in login payload | FinalGate + P4C compiler filter | Covered |
| Raw cookie/storage value exposed | FinalGate + P4C compiler filter | Covered |
| JS script hash not granted | executor/FinalGate checks | Covered by contract |
| JS network call not blocked | FinalGate checks payload proof | Needs adversarial backend test |
| HAR/body capture unredacted | FinalGate + P4C compiler filter | Covered by contract |
| HAR/body exceeds bounds | FinalGate max record/byte checks | Covered |
| Upload arbitrary disk path | upload source artifact proof | Covered |
| Download auto-promotion | quarantine receipt requires `promoted=false` | Covered |
| Cross-class implicit grant | independent authority classes | Covered |

## Highest Residual Failures

1. Real backend does not destroy private profile even though injected result says
   destroyed.
2. JS backend reports no-network without instrumentation that observes network.
3. HAR redactor misses secrets in unusual encodings or nested payloads.
4. Login adapter leaks a credential string through an exception path.
5. EvalBench passes targeted tests but misses multi-step cross-class flows.

## Required Hardening Queue

- real profile lifecycle fixture for private sessions;
- credential redaction audit across exception messages;
- no-network instrumentation around sandboxed JS;
- adversarial HAR/body redaction fixtures;
- multi-run EvalBench missions for cross-class browser flows.
