# P4A Cortex And LLM Consumption Map

Date: 2026-04-29
Status: accepted

## Purpose

This map defines how Browser V2.5 outputs become useful to the brain and the LLM
without becoming authority.

## Consumption Rule

```text
P4A output
-> EventBus proof
-> FinalGate validation
-> Browser-Cortex interpretation or ContextPack proof field
-> LLM draft intent
-> ToolIntentCompiler
-> authority-bound browser contract
```

The LLM never receives P4A observations as instructions. It receives summaries,
stable refs, hashes, flags, and available action intents authored by the brain.

## Output Mapping

| P4A output | Brain consumption | LLM ContextPack exposure | ToolIntentCompiler use | FinalGate use |
| --- | --- | --- | --- | --- |
| CDP AX tree | Stronger role/name/ref grounding. | Proof ref, source summary, stable ref candidate. | Runtime ref provenance and stale-ref checks. | Tree hash, node count, backend node count, root id. |
| DOMSnapshot/layout | Layout-aware target validation. | Bounding-box and DOM-path summary when needed. | Confirms target ref can map to page/snapshot hash. | Snapshot hash, node count, layout count. |
| UIObservation | Unified reasoning surface across AX/DOM/visual. | Stable refs, observation digest, uncertainty score. | Ref must be runtime-minted and hash-bound. | Observation hash, observation count, source count. |
| Visual crop/zoom | Visual grounding fallback. | Source screenshot hash and bounded crop metadata. | Only supports intent evidence; does not create authority. | Observation hash, source screenshot hash, bytes/max bytes. |
| Public pool | Reliability and latency planning. | Not normally exposed unless debugging/reliability matters. | No direct action authority. | Lease/release order and public/stateless flags. |
| Multi-tab strategy | Cross-source evidence gathering. | Tab purposes and source summaries. | May compile public observation intents only. | Tab count, max tabs, final URLs, lifecycle refs. |
| Post-action verifier | Mission progress / repair decision. | Verifier verdict and findings summary. | Postcondition evidence for next intent. | Receipt id, before/after snapshot hashes, findings. |
| Loop detector | Repair pressure and effort routing. | Loop finding only, not raw repeated trace. | Blocks repeated draft intents unless repair path changes state key. | Repeated count, threshold, loop key. |

## Browser-Cortex Bridge

Current cortex scoring already handles Browser V2 evidence, snapshots,
interaction plans, interaction executions, and browser rejections.

P4A adds richer proof events. For P4B, the cortex should interpret these as:

- CDP AX / DOMSnapshot / UIObservation: grounding confidence.
- Visual observation: visual confidence fallback.
- Verifier: post-action confidence and mission progress.
- Loop detector: repair pressure and effort-router signal.
- Multi-tab: source diversity and contradiction discovery.

## ContextPack Bridge

P4A observations should enter ContextPack as:

- `browser_stable_refs` for runtime-minted refs;
- `browser_evidence_summaries` for observation summaries;
- `citations` only when tied to exact excerpt or machine-verifiable value;
- `source_quality_flags` when an observation is thin, noisy, stale, or ambiguous;
- `open_questions` when verifier/loop detector requires repair;
- `available_action_intents` only from brain authority, never from page content.

## Compiler Bridge

P4B compiler rules must require:

- all action refs exist in ContextPack stable refs;
- action refs bind to current page and snapshot hashes;
- stale AX/DOM/UIObservation refs fail closed;
- prompt-injection flagged sources cannot contribute action-bearing refs;
- P4B powers are rejected unless their authority class is explicitly granted.

## Readiness Verdict

P4A outputs are consumable by the brain and LLM contract as proof and grounding
signals. They do not expand authority. They are ready to support P4B authority
classes after each class defines its own contract and tests.
