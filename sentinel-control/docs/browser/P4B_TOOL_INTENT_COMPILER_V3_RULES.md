# P4B ToolIntentCompiler V3 Rules

Date: 2026-04-29
Status: implemented for all P4B authority classes

## Compiler Rule

`ToolIntentCompiler` treats LLM output as draft intent. For Browser V3 it now
allows `browser_form_submit`, `browser_download_quarantine`, and
`browser_upload_authorized`, `browser_private_session`,
`browser_login_authority`, `browser_cookie_storage_contract`,
`browser_js_evaluate_sandboxed`, and `browser_har_body_capture` only when a
matching `BrowserV3AuthorityGrant` exists in the mission envelope.

## Accepted For P4B-1

The compiler may accept:

```text
tool_id = browser_public_form_submit
action = browser_form_submit
side effect = browser_submit
```

only when:

- ContextPack id/hash match;
- mission authority grants tool and action;
- ContextPack lists the action intent;
- V3 authority grant exists;
- runtime refs exist;
- page/snapshot hashes match;
- refs are not from high prompt-injection sources.

The compiler may accept:

```text
tool_id = browser_download_quarantine
action = browser_download_quarantine
side effects = network_read + browser_read + filesystem_write + local_draft_write
```

only when:

- ContextPack id/hash match;
- mission authority grants tool and action;
- ContextPack lists the action intent;
- V3 authority grant exists;
- source refs, when supplied, exist and are fresh;
- refs are not from high prompt-injection sources;
- the draft intent does not request promotion, upload, private session, login,
  cookie/storage, JS evaluate, payment, or credential access.

The compiler may accept:

```text
tool_id = browser_upload_authorized
action = browser_upload_authorized
side effects = network_write + browser_read + filesystem_read
```

only when:

- ContextPack id/hash match;
- mission authority grants tool and action;
- ContextPack lists the action intent;
- V3 authority grant exists;
- source artifact id is declared by the draft intent;
- upload target ref exists and is fresh;
- refs are not from high prompt-injection sources;
- the draft intent does not request arbitrary disk paths, private session,
  login, cookie/storage, JS evaluate, payment, or credential access.

## Still Rejected

The compiler still rejects:

- missing ContextPack id/hash;
- raw submit calls without contract binding;
- fabricated refs;
- stale refs;
- refs from prompt-injection source;
- upload without `browser_upload_authorized` authority;
- login/private/session/storage/cookie/script powers;
- download outside quarantine authority;
- Browser V3 classes not currently implemented.
- raw credential values, raw cookie/storage values, unbounded HAR/body capture,
  arbitrary JS, or script execution without hash authority.

## FinalGate Binding

Every executed Browser V3 event must reference a compiled intent event. Forged
V3 events without compiled intent trace are rejected.
