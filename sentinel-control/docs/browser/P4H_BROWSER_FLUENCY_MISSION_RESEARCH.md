# P4H Browser Fluency Mission Research

Date: 2026-04-30
Status: Draft locked for corpus construction

## Purpose

P4H shifts the question from:

```text
Can Sentinel compare itself to OpenClaw right now?
```

to:

```text
Can Sentinel behave like a fluent browser operator across the real surfaces a
browser agent must handle?
```

This means testing browser fluency directly:

```text
open / close
navigate any allowed URL
handle redirects and failures
see page structure
see screenshots and images
OCR visual text
understand cookies / storage / sessions
use tabs
fill forms
submit only under authority
download / upload under authority
inspect PDFs and images
capture HAR/body safely
repair failures
resist prompt injection
produce citations and proof
```

## Research Signals Used

The mission corpus is influenced by:

| Source | Useful lesson for Sentinel |
| --- | --- |
| WebArena | Self-hosted realistic web environments and long-horizon tasks are necessary. |
| VisualWebArena | Visual grounding is a first-class capability, not a fallback after text. |
| BrowserGym | A reusable benchmark environment should unify task definitions, agent wrappers, and analysis. |
| OSWorld | Browser tasks must eventually connect to real computer-use workflows. |
| Mind2Web | Generalist web agents need cross-site action grounding, not only fixed fixtures. |
| ST-WebAgentBench | Safety/trustworthiness needs its own tasks, not only success tasks. |
| BrowseComp | Research browsing must test persistent, hard-to-find information retrieval with citations. |

## Design Decision

P4H does not add browser powers.

It creates the test list that tells us which powers matter and what the agent
must prove before the Browser can be called fluent.

## Corpus Philosophy

Each mission must answer four questions:

```text
1. Did the browser complete the user-visible task?
2. Did it preserve Sentinel authority boundaries?
3. Did it produce proof that the brain and LLM can consume?
4. Did it recover or stop correctly when the page fought back?
```

## Fluency Axes

```text
navigation fluency
page perception fluency
visual / OCR fluency
state and session fluency
interaction fluency
file artifact fluency
network diagnostic fluency
research and citation fluency
safety denial fluency
repair and loop fluency
cognitive integration fluency
```
