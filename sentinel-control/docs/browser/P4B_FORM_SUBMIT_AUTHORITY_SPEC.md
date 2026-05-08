# P4B Form Submit Authority Spec

Date: 2026-04-29
Status: implemented and validated

## Authority Class

```text
browser_form_submit
```

This class allows a governed public form submit/post/send/publish action when
all proof requirements are met.

## Required Chain

Execution requires:

- `MissionAuthorityEnvelope.allowed_tools` includes `browser_public_form_submit`;
- `MissionAuthorityEnvelope.allowed_actions` includes `browser_form_submit`;
- `browser_v3_authority_grants` includes a `browser_form_submit` grant;
- ToolRegistry manifest is approved;
- ContextPack contains `browser_form_submit` as available action intent;
- ToolIntentCompiler compiles the LLM draft intent;
- refs are runtime-minted and hash-bound;
- certified dry-run plan exists;
- pre-submit snapshot trace exists;
- post-submit snapshot artifact is captured;
- FinalGate certifies the before/action/after chain.

## Runtime Contract

Implemented code:

```text
sentinel/agent/browser/v3_authority.py
sentinel/agent/browser/form_submit.py
```

Events:

```text
BROWSER_FORM_SUBMIT_EXECUTED
BROWSER_FORM_SUBMIT_REJECTED
```

Receipt:

```text
BrowserFormSubmitReceipt
```

The receipt binds:

- authority class;
- authority grant id;
- ContextPack id;
- compiled intent trace id;
- plan id/hash;
- before snapshot trace id;
- before/after snapshot hashes;
- form ref id;
- submit ref id;
- submit kind;
- expected effect;
- final URL before/after;
- same-origin or cross-origin authorization;
- post-submit snapshot artifact;
- network ledger hash.

## Rejections

The executor rejects:

- missing V3 authority grant;
- URL outside grant domains;
- blocked flow types such as payment, credential, login, upload, download;
- stale snapshot/page;
- refs absent from certified plan;
- missing pre-submit snapshot trace;
- missing post-submit snapshot;
- cross-origin result without grant;
- missing compiled intent trace;
- invalid plan hash.

## Boundary

P4B-1 does not implement private sessions, login, cookies/storage,
upload/download execution, arbitrary JavaScript, credentials, payment, or remote
browser nodes.
