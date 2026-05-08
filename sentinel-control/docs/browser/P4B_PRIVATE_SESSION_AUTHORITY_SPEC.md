# P4B-4 Private Session Authority Spec

Date: 2026-04-29
Status: implemented and validated

## Authority Class

```text
browser_private_session
```

This class creates a per-mission private browser session boundary with explicit
open and close proof. It does not grant login, cookie export, storage export,
upload, download promotion, arbitrary JavaScript, payment, or credential flow.

## Required Chain

- mission grants `browser_private_session`;
- V3 authority grant exists with `session_scope=per_mission`;
- ContextPack exposes the action intent;
- ToolIntentCompiler compiles the draft intent;
- session open emits `BROWSER_PRIVATE_SESSION_STARTED`;
- session close emits `BROWSER_PRIVATE_SESSION_CLOSED`;
- close proves `destroyed=true` and `profile_destroyed=true`;
- FinalGate rejects any opened session without a later close.

## Runtime Contract

Implemented in:

```text
sentinel/agent/browser/v3_advanced_authorities.py
```

The receipt binds session id, profile id, storage state hash, allowed domains,
scope, create/destroy flags, receipt artifact, and trace refs.

## Rejections

Rejected cases include missing authority, non-`per_mission` scope, domain outside
authority, storage enabled without grant, close without session/profile ids, and
backend failure to destroy the profile.
