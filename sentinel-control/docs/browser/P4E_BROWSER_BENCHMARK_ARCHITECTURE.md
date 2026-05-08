# P4E Browser Benchmark Architecture

Date: 2026-04-30
Status: Complete

## Purpose

P4E turns the Browser V3 proof from local authority fixtures into a
self-hosted benchmark corpus.

This is not a new browser power. It is a measurement layer for existing Browser
V3 contracts.

## Architecture

```text
BrowserSelfHostedBenchmarkGate
-> SentinelEvalBench
-> BrowserSelfHostedBenchmarkRuntime
-> existing Browser V3 measured runtime or self-hosted fixture runtime
-> EvalCaseResult
-> BrowserSelfHostedBenchmarkScore
-> BrowserSelfHostedBenchmarkReport
```

## Task Families

| Family | Purpose |
| --- | --- |
| `web_arena_style` | deterministic form, search/navigation, and multi-page workflows |
| `visual_grounding` | UIObservation-based disambiguation and grounding |
| `research_browsing` | citation, source quality, and browser-cortex interpretation |
| `v3_authority` | download, upload, login, cookie/storage, HAR, and cross-class flows |
| `adversarial_denial` | JS no-network rejection and authority denial cases |

## Implementation

Code:

```text
sentinel/agent/browser/self_hosted_benchmark.py
```

Exports:

```text
BrowserSelfHostedBenchmarkGate
BrowserSelfHostedBenchmarkRuntime
BrowserSelfHostedTaskGroup
BrowserSelfHostedBenchmarkScore
BrowserSelfHostedBenchmarkReport
BrowserPeerRunnerProtocol
```

## Scientific Rules

- each critical group must support `run_count >= 30`;
- pass rates use Wilson score intervals;
- latency p50/p95 is captured from EvalBench runtime duration;
- step count p50/p95 is derived from trace event counts;
- artifact leakage and authority violation are separate metrics;
- peer comparison must stay in the lab and must not import vendor runtime into
  product code.

## Verdict

P4E adds a reproducible self-hosted benchmark layer. It does not claim external
open-web supremacy.
