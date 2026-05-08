# JARVIS Failure Modes

Date: 2026-04-26

| Failure | Source evidence | Trigger | Impact | Sentinel prevention | Eval |
| --- | --- | --- | --- | --- | --- |
| Overbroad authority level | `roles/authority.ts:14-45` | Level 5 grants execute/browser/control app | Host/browser state changes | Payload-sensitive risk policy | Authority downgrade eval |
| Temporary grant escalation | `authority/engine.ts:74-83` | Parent grants action category | Bypass normal checks | Scoped grant TTL and critical-action exception | Grant escalation eval |
| Approval missing evidence | `authority/approval.ts:31-196` | Approval request stores args/reason but not evidence/risk/dry-run schema | User approves blind action | Dry-run/evidence/risk required | Approval preview eval |
| Shell execution | `src/actions/terminal/executor.ts:16-67`; `sidecar/handlers.go:71-133` | Shell command string runs | Host compromise | Shell disabled in v1 | Shell block eval |
| Filesystem blocklist bypass | `sidecar/handlers.go:137-196` | Path not in blocked prefix | Secret read/write | Allow-root containment | Path traversal eval |
| Browser submit/send | `webapp-templates/whatsapp.yaml:18-24`, `:88-93`; `webapp-templates/slack.yaml:67-83` | Browser/desktop flow sends message | External communication | Draft-only and approval | Fake send eval |
| Screenshot secret leak | `src/actions/tools/desktop.ts:478-516`; `sidecar/handlers.go:266-288` | Desktop screenshot is sent to AI | Secret exposure | Screen sanitizer | Secret screenshot eval |
| Clipboard leak | `sidecar/handlers.go:233-264` | Clipboard read returns sensitive text | Secret exposure | Clipboard sanitizer and approval | Clipboard secret eval |
| Sidecar token compromise | `src/sidecar/manager.ts:228-277`, `:395-455` | Enrollment token leaked or stale | Remote host control | Expiring token, revocation, device fingerprint | Token replay eval |
| Sidecar config mutation | `sidecar/handlers.go:320-407` | `update_config` changes capabilities/blocked paths/shell/profile | Permission escalation | Config updates require signed user approval | Config mutation eval |
| Prompt-level webapp safety | `webapp-templates/slack.yaml:67-83` | Prompt says banned tools/confirm target, but model may ignore | External send/data leak | Tool policy enforces, not prompt only | Template injection eval |

## Sentinel Rewrite Priorities

1. ApprovalGate with dry-run/evidence/risk.
2. PermissionedSidecarManifest.
3. ScreenContextSanitizer.
4. Browser read-only sandbox.
5. Action taxonomy for desktop/browser/channel.
