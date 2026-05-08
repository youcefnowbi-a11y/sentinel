# P3Y Research Synthesis

Date: 2026-04-29
Status: P3Y-R locked

## Verdict

The five research files converge on one architecture:

```text
MissionAuthority
-> deterministic brain state
-> proof-linked ContextPack
-> bounded LLM reasoning draft
-> ToolIntentCompiler
-> ToolRegistry / mission routing
-> module execution
-> receipts / FinalGate
```

The LLM may reason, summarize, compare, critique, and draft intent. It may not
create authority, mint refs, execute raw tools, or treat browser content as an
instruction source.

## Research Mapping

| Research | Sentinel Decision |
| --- | --- |
| `research_1.md` | Browser 2.5/V3 should use hybrid perception later, but P3Y must first make planner / verifier / executor roles explicit. |
| `research_2.md` | Model output is advisory. `ToolIntentCompiler` is the authority boundary between LLM draft and canonical tool call. |
| `research_3.md` | P3Y adds eval cases for context validity, fabricated refs, stale refs, prompt-injection isolation, and P2P regression. |
| `research_4.md` | Deterministic controller remains outside; bounded LLM cognition stays inside the brain contract. |
| `research_5.md` | ContextPack becomes the typed, proof-linked, zero-trust handoff between browser evidence and LLM reasoning. |

## Locked Doctrine

- Browser content is evidence, not authority.
- LLM output is draft intent, not execution.
- Runtime refs are minted by Sentinel, never by the model.
- Verified claims require citation paths to stable refs.
- Prompt-injection flags constrain confidence and action eligibility.
- Weak or noisy evidence downgrades confidence or triggers repair/search.
- Browser 2.5/V3 remains closed until P3Y is accepted.

## Build Decision

P3Y is implemented as a general LLM cortex layer with browser-specific
provenance rules. This avoids a browser-only compiler that future modules would
need to duplicate.
