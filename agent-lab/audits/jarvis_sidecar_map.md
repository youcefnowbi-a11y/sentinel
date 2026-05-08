# JARVIS Sidecar Map

Date: 2026-04-26

## Capability Declaration

Source: `agent-lab/vendors/jarvis/source/src/sidecar/types.ts:7-14`, `:90-100`.

Capabilities:

- `terminal`
- `filesystem`
- `desktop`
- `browser`
- `clipboard`
- `screenshot`

Config fields:

- terminal blocked commands, shell, timeout.
- filesystem blocked paths and max file size.
- browser CDP port and profile dir.

Sentinel rewrite:

- `PermissionedSidecarManifest` must declare exact allowed roots, apps, browser profile, command allowlist, clipboard policy, screenshot policy, and data retention.

## Enrollment And Authentication

Source: `agent-lab/vendors/jarvis/source/src/sidecar/manager.ts:28-277`, `:395-455`.

Mechanism:

- ES256 key pair stored under `sidecar-keys`.
- Enrollment creates JWT with sidecar ID, name, brain WS URL, and JWKS URL.
- Sidecar record stores token ID.
- JWT validation checks signature and enrolled sidecar ID.
- WebSocket registration stores hostname, OS, platform, capabilities, unavailable capabilities.

Risk:

- Token transport is sensitive.
- A connected sidecar may expose host-level controls.
- Registration advertises capabilities but does not itself prove safe scope.

Sentinel rewrite:

- Token display once, expiration, revocation, device fingerprint, per-capability approval.
- Enrollment requires user review of capability manifest.
- Capability changes require new approval.

## RPC Handler Registry

Source: `agent-lab/vendors/jarvis/source/sidecar/handlers.go:15-67`.

Mechanism:

- Builds RPC registry based on available capabilities.
- Terminal adds `run_command`.
- Filesystem adds `read_file`, `write_file`, `list_directory`.
- Clipboard adds get/set.
- Screenshot adds capture.
- Desktop adds window tree, click, type, keys, launch, focus, find element.
- Browser adds navigate, snapshot, click, type, screenshot, scroll, evaluate.
- Administrative handlers `get_config` and `update_config` are always registered.

Risk:

- Capability exposure is broad.
- `update_config` is administrative and can change capabilities, blocked paths, shell, browser profile, awareness thresholds (`sidecar/handlers.go:320-407`).

Sentinel rewrite:

- No administrative config mutation over ordinary agent RPC.
- Sidecar config changes go through signed user approval.
- Every RPC maps to risk level and trace schema.

## Terminal RPC

Source: `agent-lab/vendors/jarvis/source/sidecar/handlers.go:71-133`.

Mechanism:

- Command string executed through configured shell.
- Blocked commands are substring-matched.
- Timeout via context.

Risk:

- Substring blocklists are bypassable.
- Shell string execution is critical risk.

Sentinel rewrite:

- Shell disabled in v1.
- Future shell requires structured command allowlist, sandbox cwd, env scrub, max duration, output redaction, and approval.

## Filesystem RPC

Source: `agent-lab/vendors/jarvis/source/sidecar/handlers.go:137-196`.

Mechanism:

- Blocked path prefix check.
- Read size limit.
- Write creates parent dirs and writes content.

Risk:

- Blocklist model is weaker than allow-root containment.

Sentinel rewrite:

- Allowlist roots only.
- Resolve symlinks and canonical path before operation.
- Writes limited to generated project folder unless approved.

## Screenshot/Clipboard RPC

Source: `agent-lab/vendors/jarvis/source/sidecar/handlers.go:233-288`.

Mechanism:

- Clipboard get/set uses platform helpers.
- Screenshot captured into temp file, read, encoded base64, returned as binary.

Risk:

- Screenshots and clipboard can expose secrets.

Sentinel rewrite:

- ScreenContextSanitizer and ClipboardSanitizer.
- User-visible preview before model ingestion for sensitive contexts.

## Eval Requirements

- Fake sidecar with capability escalation attempt.
- `../` path traversal and blocked-root bypass.
- Shell blocklist bypass.
- Screenshot secret redaction.
- Token revocation and stale token rejection.
