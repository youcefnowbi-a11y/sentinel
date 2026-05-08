# P4D Browser Benchmark Research

Date: 2026-04-29
Status: Complete

## Purpose

P4D benchmark research defines how Sentinel should evaluate browser strength
without collapsing multiple skills into one misleading score.

Browser agents require at least five benchmark families:

```text
web task execution
visual grounding
computer-use workflows
hard browsing/research
open-web head-to-head failure analysis
```

## Primary Sources Reviewed

- WebArena: https://arxiv.org/abs/2307.13854
- VisualWebArena: https://aclanthology.org/2024.acl-long.50/
- OSWorld: https://arxiv.org/abs/2404.07972
- BrowseComp: https://openai.com/index/browsecomp/
- BrowserArena: https://arxiv.org/abs/2510.02418

## Benchmark Roles

### WebArena

WebArena is the closest reference for reproducible web task execution. It uses
functional websites across domains such as commerce, forums, collaborative
development, and content management. Its reported baseline gap between agents
and humans shows that end-to-end browser tasks are still difficult.

Sentinel use:

```text
self-hosted task execution
long-horizon browser workflows
functional correctness
trace/proof evaluation
```

### VisualWebArena

VisualWebArena extends web tasks to visual grounding. It tests whether an agent
can use image and text signals to act on realistic websites.

Sentinel use:

```text
CDP AX + DOMSnapshot + screenshot/zoom verification
visual fallback evaluation
UIObservation grounding score
```

### OSWorld

OSWorld is broader than browser-only evaluation. It includes real computer
tasks across applications and operating systems.

Sentinel use:

```text
future desktop/browser combined evaluation
GUI grounding stress tests
cross-application workflow readiness
```

For the current Browser track, OSWorld is informative but not the primary pass
gate.

### BrowseComp

BrowseComp measures persistent hard-to-find web research. It is less about
clicking forms and more about strategic search, source interpretation, and
verification.

Sentinel use:

```text
browser as research organ
source confidence
evidence chain quality
multi-source contradiction handling
LLM reasoning with citations
```

### BrowserArena

BrowserArena focuses on live open-web navigation with head-to-head comparison
and step-level human feedback. It is useful because open-web agents fail in
ways self-hosted tests often miss.

Sentinel use:

```text
future peer comparison
failure mode discovery
human-judged trace quality
open-web robustness
```

## Benchmark Stack Recommendation

Sentinel should not jump directly from local fixtures to open-web claims.

The recommended sequence is:

```text
Tier 0: unit and contract tests
Tier 1: local fixture EvalBench
Tier 2: local live-adapter EvalBench with >=10 runs
Tier 3: self-hosted WebArena-style tasks
Tier 4: visual grounding tasks
Tier 5: hard browsing/research tasks
Tier 6: open-web head-to-head/human-feedback campaign
```

## Metrics Required

The benchmark must report:

- mission success score;
- binary success;
- trace quality;
- source/proof quality;
- interaction correctness;
- side-effect containment;
- denial correctness;
- artifact leakage rate;
- authority violation rate;
- latency;
- step count;
- cost when LLM is live;
- multi-run stability;
- confidence intervals with a small-n-safe method.

## Benchmark Verdict

P4C-S is a local regression gate, not a final benchmark.

P4D recommends a real Sentinel Browser EvalBench before any external supremacy
claim.
