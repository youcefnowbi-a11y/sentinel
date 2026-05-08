# P4B-8 HAR Body Capture Spec

Date: 2026-04-29
Status: implemented and validated

## Authority Class

```text
browser_har_body_capture
```

This class captures bounded HAR/body diagnostics as redacted artifacts. It does
not allow unbounded capture, raw secret-bearing bodies, credential extraction, or
cross-domain capture outside mission authority.

## Required Chain

- mission grants `browser_har_body_capture`;
- source URL is inside authority;
- ContextPack exposes HAR/body capture intent;
- ToolIntentCompiler compiles the draft intent;
- backend returns redacted entries, MIME metadata, total bytes, and truncation
  proof;
- artifact capture stores the diagnostic payload;
- FinalGate verifies record/byte bounds, redaction flag, body hash, and artifact
  hash.

## Runtime Contract

Implemented in:

```text
sentinel/agent/browser/v3_advanced_authorities.py
```

The receipt binds source URL hash, body capture hash, record/byte limits,
redaction status, truncation status, HAR artifact, and trace refs.

## Rejections

Rejected cases include missing authority, URL outside authority, record or byte
limit exceeded, MIME outside allowlist, redaction missing, and artifact capture
failure.
