# P4B-6 Cookie Storage Contract Spec

Date: 2026-04-29
Status: implemented and validated

## Authority Class

```text
browser_cookie_storage_contract
```

This class exposes only redacted cookie/storage summaries or scoped clearing
inside a private session. It does not allow raw cookie export, raw storage export,
credential extraction, or cross-mission persistence.

## Required Chain

- mission grants `browser_cookie_storage_contract`;
- private session start trace exists;
- target domain is inside authority;
- ContextPack exposes storage contract intent;
- ToolIntentCompiler compiles the draft intent;
- backend returns redacted summary and storage hash;
- FinalGate requires `redaction_applied=true` and `raw_value_exposed=false`.

## Runtime Contract

Implemented in:

```text
sentinel/agent/browser/v3_advanced_authorities.py
```

The receipt binds operation, session/profile ids, private-session trace, target
domain, counts, storage hash, redaction flags, summary artifact, and trace refs.

## Rejections

Rejected cases include missing authority, missing private session trace, domain
outside authority, invalid operation, redaction missing, raw value exposure, and
summary artifact capture failure.
