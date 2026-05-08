# P4G-R Container Policy

Date: 2026-04-30
Status: Complete

## Hard Rules

```text
no host dependency install
no host runtime execution
no user home mount
no SSH/token/browser profile mount
no real credentials
no real accounts
no channel/messaging/payment integrations
no vendor import into Sentinel product code
fake env only
neutral JSONL output only
```

## Required Runtime Shape

The approved run must use:

```text
throwaway container
pinned source commit
pinned lockfile
fake environment
explicit network policy
isolated output volume under agent-lab
read-only vendor source mount or copied source layer
no persistent browser profile
```

## Prohibited Fallbacks

If Docker/Podman is missing, P4G-R must not:

```text
run pnpm install on host
run npm install on host
run OpenClaw scripts on host
run Playwright/CDP peer browser on host
copy vendor runtime into Sentinel product code
```

## Current Machine Status

```text
docker = unavailable
podman = unavailable
decision = blocked_no_container_runtime
```
