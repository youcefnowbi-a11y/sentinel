# P4G Real Peer Runtime Runner

Date: 2026-04-30
Status: Runner channel created; real peer execution blocked by policy

## Runner

```text
agent-lab/benchmarks/browser_peer_campaign/p4g_neutral_runner.py
```

This runner is lab-only. It does not live in Sentinel product code and does not
import OpenClaw into `sentinel-control/services/sentinel-core/sentinel`.

## Current Peer Runtime State

OpenClaw source exists locally:

```text
agent-lab/vendors/openclaw/source
```

But the local vendor policy says:

```text
run decision = clone only
dependency install = blocked on host
runtime execution = blocked
```

Source documents:

```text
agent-lab/audits/vendor_clone_checks.md
agent-lab/audits/openclaw_dependency_audit.md
agent-lab/vendors/openclaw/README.md
```

## Why Execution Is Blocked

The dependency audit flags:

```text
install-time code execution
native dependencies
browser/CDP runtime packages
shell/process packages
channels and messaging integrations
credential-heavy configuration surface
plugin and skill execution surfaces
```

Therefore P4G records the peer runtime as:

```text
execution_status = blocked_not_executed
failure_category = peer_runtime_not_executed
```

## Required Before Real Run

Before executing OpenClaw real runtime:

```text
1. approve container-only dependency install;
2. pin source commit;
3. use fake env only;
4. disable real channels/accounts;
5. isolate browser profiles;
6. export only neutral JSONL results;
7. keep all runtime artifacts inside agent-lab;
8. run no vendor code inside Sentinel product modules.
```
