# Browser LLM Eval Missions

Date: 2026-04-29
Status: P3Y-D initial evals implemented

## Implemented P3Y Tests

| Eval | Coverage |
| --- | --- |
| `P3Y-CONTEXT-VALID` | Valid ContextPack validates and emits trace. |
| `P3Y-CONTEXT-NO-CITATION` | Verified hypothesis without citation is rejected. |
| `P3Y-CONTEXT-INJECTION` | Prompt-injection source cannot support verified hypothesis. |
| `P3Y-CONTEXT-MISSION` | Mission goal mismatch is rejected. |
| `P3Y-CONTEXT-AUTHORITY` | ContextPack cannot expand mission authority or add undelegated action intents. |
| `P3Y-CONTEXT-REF` | Citation without stable runtime ref is rejected. |
| `P3Y-CONTEXT-RAW` | Raw browser text does not enter ContextPack summaries. |
| `P3Y-COMPILER-VALID` | Bound ref + validated pack compiles into canonical intent. |
| `P3Y-COMPILER-PROTOCOL` | Existing `ToolCallProtocol` event precedes compiled intent. |
| `P3Y-COMPILER-FABRICATED-REF` | Fabricated runtime ref is rejected. |
| `P3Y-COMPILER-STALE-REF` | Stale snapshot/page binding is rejected. |
| `P3Y-COMPILER-POWER-BOUNDARY` | Non-delegated browser powers are rejected. |
| `P3Y-COMPILER-PACK-BINDING` | Missing ContextPack binding is rejected. |
| `P3Y-COMPILER-RAW-BYPASS` | Raw LLM tool call without ContextPack id/hash is rejected. |
| `P3Y-COMPILER-INJECTION-REF` | Ref from prompt-injection source is rejected. |
| `P3Y-LLM-STUBS` | Planner/verifier produce drafts only, no execution. |
| `P3Y-VERIFIER-EVIDENCE` | Verifier cannot accept without receipt evidence refs. |
| `P3Y-FINALGATE-FORGED` | Compiled intent without validated pack is rejected. |
| `P3Y-FINALGATE-FORGED-VALIDATION` | Validated pack without assembly is rejected. |

## Next EvalBench Expansion

P3Y does not yet run a live LLM provider or multi-run browser benchmark. The
next EvalBench tranche should add:

- mission success score;
- trace score;
- source quality score;
- interaction correctness;
- fail-to-pass / pass-to-pass;
- multi-run stability;
- cost and latency;
- side-effect rate.
