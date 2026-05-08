# P4F Peer Browser Benchmark Protocol

Date: 2026-04-30
Status: Complete

## Purpose

P4F compares Sentinel Browser V3 against a peer browser runtime on the same
task corpus, same scoring rules, same timeout class, and same run count.

This gate does not add browser powers and does not import a peer runtime into
Sentinel product code.

## Implemented Artifact

```text
sentinel-control/services/sentinel-core/sentinel/agent/browser/peer_benchmark.py
```

The implementation creates a neutral benchmark campaign:

```text
BrowserPeerBenchmarkCampaign
BrowserPeerRuntimeProfile
BrowserPeerBenchmarkReport
BrowserPeerTaskComparison
BrowserPeerBenchmarkVerdict
```

## Boundary

Current P4F execution mode:

```text
comparison_mode = profiled_lab_baseline
real_peer_runtime_executed = false
product_vendor_runtime_imported = false
```

That means this gate proves the comparison protocol and produces a measured
Sentinel-vs-peer-profile scorecard. It does not claim that a real external peer
runtime was executed.

## Required Fairness Rules

```text
same_task_corpus = true
same_timeout = true
same_scoring = true
same_run_count = true
peer_runner_stays_lab_only = true
product_vendor_runtime_imported = false
```

## Comparison Dimensions

P4F separates two dimensions:

```text
raw browser task completion
governed / provable execution quality
```

This matters because a peer runtime may complete a task quickly while lacking
Sentinel-grade authority, receipt, redaction, and FinalGate proof.

## Verdict Rule

Sentinel can claim browser supremacy only after a real lab or external peer run.

With a profiled baseline, the only acceptable lock verdict is:

```text
external_open_web_campaign_required
```
