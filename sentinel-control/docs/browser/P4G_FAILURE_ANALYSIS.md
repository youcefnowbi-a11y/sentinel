# P4G Failure Analysis

Date: 2026-04-30
Status: Complete

## Primary Failure

```text
peer_runtime_not_executed
```

This is not a Sentinel Browser failure. It is a lab-safety and reproducibility
failure: the peer runtime has not yet been approved for execution.

## Why This Matters

Without real peer execution, we cannot measure:

```text
OpenClaw raw task success
OpenClaw latency p50/p95
OpenClaw step count p50/p95
OpenClaw site compatibility
OpenClaw failure categories
OpenClaw artifact leakage
OpenClaw authority violation rate
```

## What Still Favors OpenClaw-Style Runtime

OpenClaw-style browser remains plausibly stronger in raw runtime breadth because
of:

```text
large Playwright/CDP action surface
sessions, tabs, profiles
download/upload ergonomics
storage/cookie handling
JS/network diagnostic routes
debug trace routes
large extension surface
```

## What Still Favors Sentinel

Sentinel remains stronger on governed execution:

```text
MissionAuthority
ContextPack
ToolIntentCompiler
receipts
redaction contracts
FinalGate
trace certification
raw-vs-governance benchmark split
```

## Required Fix

Create an approved containerized peer-runtime execution gate in Agent Lab. Until
then, P4G must remain inconclusive.
