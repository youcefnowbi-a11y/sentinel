# P4E OpenClaw-Style Peer Runner Protocol

Date: 2026-04-30
Status: Complete

## Purpose

P4E defines how Sentinel can compare against an OpenClaw-style browser runtime
without importing vendor runtime into product code.

## Protocol Rules

```text
same task corpus
same timeout
same scoring
same run_count
same success criteria
same side-effect observation
lab-only peer runner
no vendor runtime import into Sentinel product code
```

## Required Metrics

- mission success score;
- trace quality;
- proof completeness;
- source quality;
- interaction correctness;
- side-effect containment;
- denial correctness;
- artifact leakage rate;
- authority violation rate;
- latency p50/p95;
- step count p50/p95;
- Wilson interval;
- unstable iterations.

## Expected Comparison Shape

Sentinel can win governance and proof while losing raw runtime speed or site
compatibility. The peer report must keep those axes separate.

## Verdict

P4E creates the peer comparison protocol. It does not run or import OpenClaw.
