# P4H-V Full Live Self-Hosted Browser Fluency Runner

Date: 2026-04-30
Status: Complete

## Goal

P4H-V expands P4H-U from a 12-mission representative live slice to all 72
Browser Fluency missions.

This is still self-hosted local evidence. It does not execute open-web tasks,
real credentials, real peer runtimes, or user browser profiles.

## Runner

Implementation:

```text
agent-lab/benchmarks/browser_tasks/browser_fluency_live_runner.py
```

New scope:

```text
--scope full
```

Outputs:

```text
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_live_full_results.jsonl
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_live_full_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_live_full_scorecard.md
```

## Coverage

P4H-V covers all 12 mission groups and all 72 mission ids:

```text
life  = 6 missions
nav   = 6 missions
perc  = 6 missions
vis   = 6 missions
form  = 6 missions
state = 6 missions
file  = 6 missions
net   = 6 missions
tab   = 6 missions
res   = 6 missions
safe  = 6 missions
cog   = 6 missions
```

## Fixture Surfaces

The local HTTP harness now includes fixture paths for:

```text
page read/navigation
redirects and HTTP errors
SPA route marker
duplicate buttons and interactability flags
visual/OCR/chart/uncertainty markers
forms, autocomplete, credential/payment boundaries
cookie/storage redaction
download quarantine and denial
upload certified artifact and arbitrary upload denial
PDF text/OCR fixtures
HAR/body redaction
JS allowlist/no-network/arbitrary denial
multi-tab comparison and stale-tab repair
research conflict, hard-to-find path, recency, insufficient evidence
prompt injection, policy override, CAPTCHA, payment, stale ref denial
repair loop, loop detector, evidence chain, LLM draft boundary
```

## Boundary

P4H-V is stronger than P4H-T because it performs local HTTP runtime operations.
It is stronger than P4H-U because it covers the full 72-mission catalog.

It is still not:

```text
open-web benchmark proof
real Chromium visual-rendering proof for every case
real OCR model proof
real peer-runtime proof
external supremacy proof
```
