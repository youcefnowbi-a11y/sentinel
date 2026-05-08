# Browser Source Confidence Model

Date: 2026-04-29
Status: P3X accepted

## Formula

Browser source confidence is computed deterministically:

```text
score =
  0.30 * source_quality
+ 0.20 * citation_validity
+ 0.20 * extraction_confidence
+ 0.15 * freshness
+ 0.15 * contradiction_status
- prompt_injection_penalty
```

All terms are clamped to `[0, 1]`.

## Terms

| Term | Meaning |
| --- | --- |
| `source_quality` | Penalizes thin, empty, truncated, missing-title, or prompt-flagged content. |
| `citation_validity` | Rewards offset-bound snippets or citation counts. |
| `extraction_confidence` | Depends on extraction/render/interaction type. |
| `freshness` | Accepted live browser events are stronger than rejected events. |
| `contradiction_status` | Penalizes network failures and page errors. |
| `prompt_injection_penalty` | Caps instruction-like browser text as evidence-only. |

## Thresholds

| Score | Cortex Meaning |
| ---: | --- |
| `>= 0.72` | Strong enough to support a linked hypothesis. |
| `0.36 - 0.71` | Useful but not decisive. |
| `<= 0.35` | Weak/noisy; seek alternative evidence or repair. |

## Prompt Flag Rule

If prompt flags are present, the source score is capped at `0.45`.

This prevents a page from using instruction-like content to create confidence or
authority. The page may still be summarized as evidence.
