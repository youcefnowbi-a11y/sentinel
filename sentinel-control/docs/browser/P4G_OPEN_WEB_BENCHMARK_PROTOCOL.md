# P4G External/Open-Web Browser Benchmark Protocol

Date: 2026-04-30
Status: Complete with inconclusive peer execution

## Goal

P4G attempts the next step after P4F: a real external/open-web comparison
between Sentinel Browser V3 and an OpenClaw-style peer runtime.

The gate keeps the P4F rules:

```text
same task corpus
same timeout
same run_count
same scoring
same success criteria
raw task success separated from governed/provable quality
no vendor runtime imported into Sentinel product code
```

## Implemented Lab Harness

```text
agent-lab/benchmarks/browser_peer_campaign/p4g_neutral_runner.py
```

The harness writes neutral JSONL results:

```text
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_sentinel_results.jsonl
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_openclaw_real_results.jsonl
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_comparison_summary.json
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_neutral_campaign_report.md
```

## Execution Result

Sentinel executed the 13 P4G groups with 30 runs per group.

The real peer runtime was not executed because Agent Lab vendor policy still
marks OpenClaw as source-clone-only and runtime-blocked.

## Verdict Rule

Because the real peer runtime was not executed, P4G cannot produce a supremacy
claim. The only valid decision is:

```text
D) external campaign inconclusive
```
