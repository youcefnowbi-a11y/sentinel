# P4G-R Containerized Peer Runtime Run

Date: 2026-05-01
Status: Rechecked with Docker; blocked by missing approved peer command

## Goal

P4G-R attempts to execute the real OpenClaw-style peer runtime inside a
disposable isolated container and export only neutral JSONL results.

## Implemented Runner

```text
agent-lab/benchmarks/browser_peer_campaign/p4g_r_container_runner.py
```

The runner records:

```text
source commit
package hash
dependency lockfile hash
Dockerfile hash
container runtime availability
host dependency install status
product vendor import status
per-task neutral peer result rows
```

## Execution Result

```text
peer_real_runtime_executed = false
container_runtime = docker
container_runtime_version = Docker version 29.4.1, build 055a478
execution_status = blocked_no_approved_runtime_command
failure_category = peer_runtime_command_not_approved
host_dependency_install = false
product_vendor_runtime_imported = false
```

## Source Pinning

```text
source_commit = a2288c2b09e621f89a915960398f58e200b3b69d
package_json_sha256 = 9ffd60e01a31dd9d5b40568bdbaadc0128eab18eac3e2de8f45ae915132603ac
lockfile_sha256 = bd223e18e5eed01cacca34ed211e23dfc9211aa441057223a08548196629e591
dockerfile_sha256 = e2df3230c1093e0751bdc02a754348259a5b84e532d5fa25529bf2e9728a2001
```

## Interpretation

P4G-R is not a failed Sentinel Browser test. It is a blocked peer-runtime
execution gate. Docker is now exposed, so the old environment block is gone.
The remaining block is the lack of an approved real peer runtime command or
adapter that emits only the neutral P4G JSONL schema.
