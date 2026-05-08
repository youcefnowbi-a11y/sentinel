# P4G-R OpenClaw Container Results

Date: 2026-05-01
Status: Not executed after Docker recheck

## Result Files

```text
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_r_openclaw_container_results.jsonl
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_r_container_summary.json
agent-lab/benchmarks/browser_peer_campaign/reports/p4g_r_container_report.md
```

## Summary

```text
task_count = 13
run_count = 0
execution_status = blocked_no_approved_runtime_command
failure_category = peer_runtime_command_not_approved
container_runtime = docker
container_runtime_version = Docker version 29.4.1, build 055a478
blocked_reason = container runtime found, but no approved real peer command is defined for this machine
```

## Scientific Meaning

These are non-execution rows. They prove that P4G-R preserved the container
boundary after Docker became available, but they do not provide OpenClaw raw
runtime metrics.
