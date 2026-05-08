# Browser LLM ContextPack Spec

Date: 2026-04-29
Status: P3Y-A implemented

## Contract

`ContextPack` is the typed LLM handoff contract. It is assembled from mission
authority, brain state, browser evidence summaries, citations, stable refs,
source quality flags, prompt-injection flags, diagnostics, budget, and available
action intents.

The pack is compact by design. Raw HTML, raw page text, PDFs, screenshots, and
large artifacts stay outside the LLM context and are referenced through proof
ids, hashes, stable refs, and trace refs.

## Required Planes

| Plane | Fields | Trust Rule |
| --- | --- | --- |
| Control | mission goal, authority boundary, action intents, budget | Brain-authored. |
| Reasoning | current state, verified hypotheses, summaries | Brain-validated before use. |
| Proof | citations, stable refs, digests, trace refs | Rehydratable proof layer. |
| Evidence | source quality, prompt flags, diagnostics | Browser-derived and tainted until validated. |

## Validation Rules

- `context_pack_id` must use the `cpk_` prefix.
- `mission_id` and `mission_goal` must match the active mission authority.
- `available_action_intents` must be a subset of allowed mission actions.
- A verified hypothesis must reference at least one citation.
- A full-support citation must include an excerpt and digest.
- Every citation stable ref must exist in `browser_stable_refs`.
- Every summary source must have a source-quality record.
- High prompt-injection sources cannot support verified hypotheses.
- The pack hash must match canonical pack content.

## Events

- `context_pack_assembled`
- `context_pack_validated`
- `context_pack_rejected`
- `context_pack_rehydrated` reserved for proof pulls
