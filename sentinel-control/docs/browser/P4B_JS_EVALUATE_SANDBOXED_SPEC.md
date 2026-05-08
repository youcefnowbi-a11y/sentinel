# P4B-7 Sandboxed JS Evaluate Spec

Date: 2026-04-29
Status: implemented and validated

## Authority Class

```text
browser_js_evaluate_sandboxed
```

This class allows JavaScript evaluation only when the script SHA-256 is explicitly
granted. It is not arbitrary JS: network calls are rejected, result size is
bounded, timeout is explicit, and output becomes an artifact.

## Required Chain

- mission grants `browser_js_evaluate_sandboxed`;
- V3 grant lists allowed script hashes;
- page URL is inside authority;
- ContextPack exposes sandboxed JS intent;
- ToolIntentCompiler compiles the draft intent;
- executor computes script SHA-256 and checks the allowlist;
- backend returns bounded result with no network calls;
- FinalGate verifies hash allowlist flag, no-network flag, result size, and
  result artifact hash.

## Runtime Contract

Implemented in:

```text
sentinel/agent/browser/v3_advanced_authorities.py
```

The receipt binds page URL hash, script hash, result hash, result artifact,
max-result bound, timeout result, and trace refs.

## Rejections

Rejected cases include missing authority, script hash outside allowlist, page URL
outside authority, network calls during evaluation, oversized result, and result
artifact capture failure.
