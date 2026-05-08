# JARVIS To Sentinel Rewrite Notes

Date: 2026-04-26
Rule: rewrite, do not integrate.

## What Sentinel Should Learn

- A central authority engine is necessary.
- Approval requests must be persisted and queryable.
- Sidecars need enrollment, revocation, capabilities, and audit.
- Desktop/browser awareness is powerful only after sanitization and user confirmation.
- App-specific web templates can make browser agents practical, but sending/submitting must be hard-gated.

## What Sentinel Must Not Copy

- JARVIS daemon.
- Bun CLI.
- Go sidecar.
- Browser or desktop tools.
- Webapp templates as executable instructions.
- Authority level model as-is.

## Sentinel PermissionedSidecar Blueprint

Inputs:

- Sidecar identity.
- Signed capability manifest.
- User-approved scopes.
- Allowed roots/apps/browser profile.
- Denied paths/apps/URLs.
- Data retention.
- Audit policy.

Allowed v0:

- None in production.
- Fake sidecar fixtures in Agent Lab only.

Future read-only phase:

- `list_windows` with titles redacted if needed.
- sanitized screenshot/OCR after user approval.
- read-only browser snapshot in isolated profile.

Blocked until later:

- terminal;
- filesystem write;
- clipboard write;
- desktop click/type/keys;
- browser submit;
- external message send.

## ScreenContextSanitizer Requirements

- Detect secrets/API keys/password fields.
- Detect personal contacts/messages.
- Crop to target app/window.
- Blur sensitive regions.
- Keep original out of model context unless user explicitly approves.
- Trace sanitized vs raw handling without storing raw secrets.

## Desktop Action Risk Classes

| Action | Risk | Rule |
| --- | --- | --- |
| list windows | medium | user opt-in; redact titles if sensitive |
| screenshot | high | sanitizer and approval |
| focus window | high | approval |
| click/type/keys | critical | disabled until sandbox/approval |
| launch app | critical | disabled until policy |
| clipboard read | high | sanitizer and approval |
| clipboard write | critical | approval and preview |
| terminal | critical | disabled v1 |

## Required Evals

- Fake sidecar capability mismatch.
- Fake token replay.
- Fake screenshot with secrets.
- Fake clipboard secret.
- Fake desktop click on destructive button.
- Fake browser submit.
- Fake Slack/WhatsApp send.
