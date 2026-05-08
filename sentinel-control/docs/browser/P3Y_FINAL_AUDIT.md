# P3Y Final Audit

Date: 2026-04-29
Status: Passed

## Verdict

P3Y is locked after final audit.

This audit added no live LLM provider, no Browser 2.5/V3 capability, and no new
browser execution surface. It only verified that the LLM bridge remains a
bounded reasoning and intent-drafting layer.

## Audit Scope

- `ContextPack`
- `ContextPackValidator`
- `ContextPackAssembler`
- `ToolIntentCompiler`
- `BrowserPlannerRole`
- `BrowserVerifierRole`
- P3Y events
- `CoreFinalGate` P3Y checks
- `ToolCallProtocol` integration

## Audit Matrix

| Check | Result | Evidence |
| --- | --- | --- |
| ContextPack cannot lie about mission id/objective. | Pass | Mission goal mismatch rejected. |
| ContextPack cannot expand `MissionAuthorityEnvelope`. | Pass | Added test for extra `browser_download_quarantine` intent outside authority. |
| Verified hypothesis without citation is rejected. | Pass | Existing and audit tests reject unsupported verified hypotheses. |
| Citation without stable runtime ref is rejected. | Pass | Added test for citation targeting missing stable ref. |
| Fabricated ref is rejected. | Pass | Compiler rejects unknown runtime ref. |
| Stale page/snapshot hash is rejected. | Pass | Compiler rejects stale snapshot binding. |
| Prompt-injected source cannot produce action-bearing ref. | Pass | Compiler rejects ref whose source has high prompt-injection risk. |
| Raw LLM tool-call bypass is rejected. | Pass | Compiler rejects raw tool call without ContextPack id/hash binding. |
| Browser 2.5/V3 power is rejected when not delegated. | Pass | Compiler rejects submit/download/login/script token classes. |
| Compiler reuses existing `ToolCallProtocol`. | Pass | Audit test verifies `tool_call_canonicalized` precedes compiled intent. |
| Planner role output is draft only. | Pass | Planner emits `llm_reasoning_drafted` only. |
| Verifier role cannot certify without receipt/evidence. | Pass | Verifier rejects missing evidence refs. |
| FinalGate rejects forged P3Y event. | Pass | FinalGate rejects validated pack without assembly and compiled intent without validated pack. |

## Final Accepted Chain

```text
MissionAuthorityEnvelope
-> ContextPackAssembler
-> ContextPackValidator
-> BrowserPlannerRole draft
-> ToolIntentCompiler
-> ToolCallProtocol
-> provenance / authority / registry checks
-> existing browser contracts
-> receipts / FinalGate
```

## Commands

```text
pytest tests/test_agent_llm_context_pack.py tests/test_agent_llm_tool_intent_compiler.py -q
pytest tests -q
python -m compileall sentinel
product vendor-trace scan
P3Y execution-boundary scan
doctrine wording scan
```

Current result: pass.

## Lock Conditions

P3Y remains locked only while:

1. LLM output is draft-only.
2. LLM output cannot bypass `ToolIntentCompiler`.
3. `ToolIntentCompiler` keeps using `ToolCallProtocol`.
4. ContextPack validation precedes compiled intent.
5. Browser refs come from Sentinel runtime evidence.
6. Prompt-injection sources remain evidence-only.
7. Browser 2.5/V3 powers remain explicit authority-class work.

## Next Phase

P4A can begin after this audit:

```text
Browser V2.5 power upgrade
-> CDP-native structure
-> DOMSnapshot/layout
-> hybrid perception
-> public stateless pool
-> multi-tab operator
-> advanced interactions
```

P4A must still enter through authority contracts, receipts, events, tests, and
FinalGate checks.
