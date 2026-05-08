# P4B Browser V3 Authority Kernel

Date: 2026-04-29
Status: implemented and validated

## Purpose

P4B introduces Browser V3 as explicit authority classes. The kernel exists so
new browser powers enter Sentinel as governed contracts, not raw tool buttons.

## Kernel Models

Implemented:

- `BrowserV3AuthorityClass`
- `BrowserV3AuthorityGrant`
- `BrowserV3RequestModel`
- `BrowserV3Receipt`

Mission authority now includes:

```text
MissionAuthorityEnvelope.browser_v3_authority_grants
```

Each grant declares:

- authority class;
- allowed domains;
- max uses;
- cross-origin policy;
- ContextPack requirement;
- ToolIntentCompiler requirement;
- certified-plan requirement;
- pre/post snapshot requirement;
- blocked flow types.

## Kernel Rule

```text
MissionAuthorityEnvelope
-> browser_v3_authority_grant
-> ToolRegistry policy
-> ContextPack action intent
-> ToolIntentCompiler
-> executor
-> receipt
-> FinalGate
```

No V3 class may skip the chain.

## Current Implemented Classes

Implemented Browser V3 classes:

```text
browser_form_submit
browser_download_quarantine
browser_upload_authorized
browser_private_session
browser_login_authority
browser_cookie_storage_contract
browser_js_evaluate_sandboxed
browser_har_body_capture
```

`browser_form_submit` is locked in `P4B_FORM_SUBMIT_LOCK_VERDICT.md`.
`browser_download_quarantine` is locked in
`P4B_DOWNLOAD_QUARANTINE_LOCK_VERDICT.md`.
`browser_upload_authorized` is locked in
`P4B_UPLOAD_AUTHORIZED_LOCK_VERDICT.md`.
P4B-4 through P4B-8 are locked in their dedicated lock verdicts.

No future Browser V3 power is implied by these locks. Any new class still needs
its own grant, compiler rule, receipt, events, FinalGate check, and tests.
