# Sentinel Sidecar Spec

Date: 2026-04-26
Status: future design only, no sidecar runtime authorized

## Principle

The sidecar is a product surface, not a helper process.

It can eventually touch a user's machine. Therefore it starts disabled, deny-by-default, scoped, signed, observable, revocable, and fake-benchmarked before any real host control.

## G10 Boundary

Blocked now:

- no sidecar implementation;
- no host connection;
- no terminal;
- no desktop control;
- no screenshot capture;
- no clipboard read/write;
- no browser profile;
- no RPC execution.

Allowed now:

- manifest spec;
- fake fixture design;
- policy matrix;
- sanitizer requirements;
- eval roadmap.

## Manifest

```json
{
  "sidecar_id": "sidecar_...",
  "device_name": "...",
  "owner_user_id": "...",
  "enrollment": {
    "status": "pending|approved|revoked|expired",
    "created_at": "...",
    "expires_at": "...",
    "public_key_fingerprint": "..."
  },
  "capabilities": [
    {
      "name": "screenshot",
      "enabled": false,
      "risk_level": "high",
      "scope": {},
      "approval_required": true,
      "eval_suite": "sidecar_screenshot_sanitizer"
    }
  ],
  "allowed_roots": [],
  "allowed_apps": [],
  "browser_profile": "sentinel-sandbox",
  "retention_policy": "none|redacted_only|short_lived",
  "policy_version": "..."
}
```

## Capability Matrix

| Capability | Default | Risk | Before Enable |
|---|---|---|---|
| system_info | disabled | medium | fake benchmark and privacy review |
| list_windows | disabled | medium | window-title redaction |
| screenshot | disabled | high | ScreenContextSanitizer |
| clipboard_read | disabled | high | sanitizer, opt-in, approval |
| clipboard_write | disabled | critical | preview and approval |
| filesystem_read | disabled | high | allow-root, sensitivity scan |
| filesystem_write | disabled | critical | allow-root, dry-run, approval |
| browser_read | disabled | high | sandbox profile |
| browser_submit | disabled | critical | future only |
| desktop_click_type | disabled | critical | future only |
| terminal | disabled | critical | future only |

## RPC Contract

Every future sidecar RPC must include:

```json
{
  "rpc_id": "rpc_...",
  "sidecar_id": "sidecar_...",
  "capability": "...",
  "method": "...",
  "args_hash": "...",
  "dry_run_id": "dry_...",
  "approval_id": null,
  "trace_id": "trace_...",
  "policy_version": "..."
}
```

## Sanitizer Requirements

Screen/clipboard/browser/desktop context must pass:

- secret detection;
- PII detection;
- app/window allowlist;
- crop/minimize if possible;
- redaction before model use;
- retention label;
- user-visible trace.

## Required Evals

- Capability escalation blocked.
- Stale token rejected.
- Revoked sidecar rejected.
- Path traversal blocked.
- Screenshot secret redacted.
- Clipboard secret redacted.
- Browser submit blocked.
- Terminal blocked.
- Admin config mutation blocked.
