# P4D-H Browser V3 Cognitive Mapping

Date: 2026-04-29
Status: Complete

## Purpose

P4D found that Browser V3 could execute and certify high-impact classes, while
Browser-Cortex still mainly understood V2/P3H events.

P4D-H adds explicit V3 cognitive mapping.

## Code Changes

`sentinel/agent/browser/cortex.py` now maps these V3 event families:

| Event family | Cognitive source kind |
| --- | --- |
| `BROWSER_FORM_SUBMIT_*` | `browser_v3_form_submit` |
| `BROWSER_DOWNLOAD_*` | `browser_v3_download_quarantine` |
| `BROWSER_UPLOAD_AUTHORIZED_*` | `browser_v3_upload_authorized` |
| `BROWSER_PRIVATE_SESSION_*` | `browser_v3_private_session` |
| `BROWSER_LOGIN_AUTHORITY_*` | `browser_v3_login_authority` |
| `BROWSER_COOKIE_STORAGE_CONTRACT_*` | `browser_v3_cookie_storage` |
| `BROWSER_JS_EVALUATE_SANDBOXED_*` | `browser_v3_js_sandbox` |
| `BROWSER_HAR_BODY_*` | `browser_v3_har_body` |
| `BROWSER_VERIFICATION_COMPLETED` | `browser_verification` |
| `BROWSER_LOOP_DETECTED` | `browser_loop_detected` |

## Mission Meaning

| V3 signal | Meaning in the brain |
| --- | --- |
| form submit executed | mission progress signal after proof chain, not evidence truth by itself |
| download quarantined | artifact available in quarantine, not promoted trust |
| upload authorized | outbound artifact side effect completed |
| private session opened/closed | scoped runtime state, not evidence authority |
| login success | authenticated state exists; no credential evidence |
| cookie/storage summary | tainted redacted session metadata |
| JS network rejection | protection and repair signal |
| HAR/body capture | sensitive diagnostic evidence through redacted artifact only |

## Test Coverage

Added tests for:

- V3 event mapping into Browser-Cortex source kinds;
- form submit as progress signal;
- download quarantine as non-promoted evidence;
- cookie/storage as tainted redacted metadata;
- HAR/body as redacted diagnostic evidence;
- sandboxed JS network rejection as repair/security signal;
- login event not creating ContextPack credential evidence.

## Verdict

Browser V3 is now more than executable. It is cognitively visible to the brain.

This does not make browser content authority. It makes browser effects legible
to the mission reasoning layer.
