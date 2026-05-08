# P3Y Lock Verdict

Date: 2026-04-29
Status: P3Y implemented, audited, and accepted

## Verdict

P3Y is accepted.

Final audit result: passed in `P3Y_FINAL_AUDIT.md`.

Browser V2 now has a bounded LLM cortex contract:

```text
Browser evidence / P3X cortex signals
-> ContextPack
-> bounded LLM draft
-> ToolIntentCompiler
-> ToolRegistry / MissionAuthority
-> module execution only after existing gates
```

## Accepted Implementation

- `ContextPack` contract and validator.
- ContextPack assembly from mission authority and browser trace evidence.
- LLM planner/verifier stubs with no provider dependency.
- `ToolIntentCompiler` layered above `ToolCallProtocol`.
- Provenance binding for browser stable refs.
- Rejection of fabricated refs, stale refs, prompt-injection refs, and non-delegated browser powers.
- FinalGate P3Y check for validated packs and compiled intents.
- P3Y eval tests.

## Lock Conditions

P3Y remains accepted only while:

1. LLM output remains draft intent.
2. ContextPack control fields come from mission authority / brain code.
3. Browser-derived fields remain evidence-only.
4. Runtime refs are minted by Sentinel, never by the LLM.
5. Compiled tool intents require ContextPack id/hash binding.
6. Compiled tool intents require MissionAuthority and available-intent checks.
7. Prompt-injection sources cannot drive action-bearing refs.
8. Browser 2.5/V3 powers remain deferred until explicit authority phases.

## Next Gate

Only after P3Y stays green:

```text
P4A Browser V2.5
-> hybrid perception / CDP-native structure / public stateless pool
```

Browser V3 powers remain separate authority classes.
