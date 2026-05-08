# P4F OpenClaw Lab Runner Plan

Date: 2026-04-30
Status: Complete

## Purpose

This document defines how an OpenClaw-style runtime can be evaluated without
copying or importing vendor code into Sentinel product modules.

## Lab Boundary

Allowed location:

```text
agent-lab/
```

Forbidden location:

```text
sentinel-control/services/sentinel-core/sentinel/
```

The lab runner may launch a peer browser runtime as an external process or
adapter, but Sentinel product code must see only a neutral result file:

```text
task_id
run_id
binary_success
events_seen
artifacts_seen
latency_ms
step_count
failure_category
```

## Why OpenClaw-Style Browser Is Still Strong

Prior forensic research identified the peer-browser strength as runtime breadth:

```text
large action surface
Playwright / CDP execution maturity
sessions, tabs, profiles
download / upload
storage / cookies
JS / network diagnostics
snapshots / refs / debug traces
large extension surface
```

Sentinel is stronger on governance and proof, but a peer runtime can still be
stronger on raw site compatibility, speed, and ergonomic browser primitives.

## Lab Runner Contract

The lab runner must:

```text
1. consume the P4F shared task corpus;
2. use the same run_count and timeout;
3. write neutral JSONL results;
4. never write credentials, raw cookies, raw storage, or raw HAR secrets;
5. record screenshots/artifacts only inside the lab output directory;
6. never import peer runtime code into Sentinel product modules.
```

## Next Execution Step

P4F currently locks the protocol and profiled baseline. The next hard proof is a
real lab runner that executes the same corpus with a real peer runtime and feeds
the neutral result schema back into the P4F report.
