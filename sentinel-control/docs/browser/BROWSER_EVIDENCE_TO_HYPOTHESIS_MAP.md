# Browser Evidence To Hypothesis Map

Date: 2026-04-29
Status: P3X accepted

## Core Rule

Browser evidence can update a hypothesis only through an explicit trace-bound
contract:

```text
Browser event
-> source confidence score
-> linked hypothesis
-> BrowserHypothesisUpdate
-> evidence chain
```

## Linkage

A browser source is linked to a hypothesis when at least one is true:

- hypothesis `evidence_refs` contains browser evidence item id;
- hypothesis `evidence_refs` contains browser trace id, receipt id, artifact id,
  or URL;
- deterministic keyword overlap exists between hypothesis statement and browser
  title/URL/source identifiers.

## Update Rules

| Browser Signal | Effect | Delta |
| --- | --- | ---: |
| source score >= 0.72 | `confirm` | `+0.15` |
| source score <= 0.35 | `needs_alternative_evidence` | `-0.12` |
| medium score | `weaken` | `-0.05` |
| prompt flags present | max confidence source score `0.45` | bounded |
| rejected browser output | repair signal | no direct promotion |

## Invariant

Browser evidence cannot directly set a hypothesis to `verified`. It can only
create a browser-derived update. Hypothesis promotion remains a cortex decision
that must preserve existing evidence-chain and verification rules.

## Example

```text
Hypothesis: competitor pricing is visible publicly
Browser event: rendered pricing page, receipt, title, citations, high score
Update: confirm, +0.15 confidence, evidence refs preserved
```

## Prompt-Injected Pages

Prompt-injection-like browser content is not an instruction. It is evidence with
limited confidence and a cross-check recommendation.
