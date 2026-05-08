# P4B-5 Login Authority Spec

Date: 2026-04-29
Status: implemented and validated

## Authority Class

```text
browser_login_authority
```

This class allows login only to mission-granted account ids inside a certified
private session. Credentials are never included in ContextPack, tool intent,
events, receipts, artifacts, or docs.

## Required Chain

- mission grants `browser_login_authority`;
- V3 login grant lists the allowed account id;
- private session start event exists before login;
- ContextPack exposes login intent;
- ToolIntentCompiler compiles the draft intent;
- certified interaction plan and login ref exist;
- backend confirms login success;
- post-login snapshot artifact is captured;
- FinalGate rejects credential-bearing payloads.

## Runtime Contract

Implemented in:

```text
sentinel/agent/browser/v3_advanced_authorities.py
```

The receipt binds account id, private session trace, login URL hash, final URL
hash, plan hash, post-login snapshot artifact, and trace refs.

## Rejections

Rejected cases include missing authority, account outside grant, login URL
outside authority, missing private session trace, invalid plan/ref, backend
failure, cross-origin result without grant, missing post-login snapshot, and any
credential-bearing payload.
