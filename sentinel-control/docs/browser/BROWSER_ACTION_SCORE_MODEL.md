# Browser Action Score Model

Date: 2026-04-29
Status: P3X accepted

## Purpose

The browser action score model turns browser output into action
recommendations. These are recommendations to the cortex, not direct tool
execution.

## Recommendation Types

| Recommendation | Meaning |
| --- | --- |
| `use_as_evidence` | Source confidence is high enough for evidence-chain reasoning. |
| `seek_alternative_source` | Source is weak, rejected, noisy, or confidence-limited. |
| `create_interaction_plan` | Browser should prepare a plan before action, not execute raw interaction. |
| `treat_interaction_as_progress` | Limited interaction has before/after proof and can count as progress evidence. |
| `do_not_use_for_authority` | Source can support reasoning but cannot grant action authority. |

## Action Impact

Browser action recommendations carry an impact score in `[0, 1]`. Current V2
recommendations are bounded:

- evidence use: medium impact;
- alternative source search: medium impact;
- limited interaction progress: high but still public and plan-bound;
- authority use: always rejected as a browser-derived action.

## Cortex Boundary

The action score model does not execute anything. It only prepares signals for
`ActionEvaluator`, `EffortRouter`, and future LLM ContextPack consumers.
