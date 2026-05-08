# P4C-H.2 Browser V3 Fixture Backend Bench

Date: 2026-04-29
Status: Completed

## Goal

P4C-H.2 adds a fixture-backed Browser V3 backend bench. It does not add browser
powers. It gives V3 executors a deterministic backend that performs real local
profile lifecycle work and adversarial redaction checks.

## Implemented Bench

`BrowserV3FixtureBackendBench` provides backend callables for:

- private session;
- login authority;
- cookie/storage contracts;
- sandboxed JS evaluate;
- HAR/body capture.

## Reality Properties

### Private Session

The bench creates an actual profile directory under the fixture root, writes a
storage-state fixture, returns its SHA-256, and removes the profile directory on
close.

Proof:

```text
open -> profile path exists
close -> profile path no longer exists
```

### Login Authority

The bench returns a before snapshot bound to the certified interaction plan
snapshot hash and a post-login rendered page with same-origin URL.

### Cookie/Storage

The bench emits redacted summaries by default and can intentionally leak
`Set-Cookie` markers for adversarial rejection tests.

### Sandboxed JS

The bench does not execute arbitrary JS. It detects network-capable script
markers such as `fetch`, `XMLHttpRequest`, `sendBeacon`, `WebSocket`, and
dynamic `import`, then returns network-call evidence for executor rejection.

### HAR/Body

The bench emits bounded redacted HAR/body fixtures and can intentionally include
an `Authorization` header for adversarial rejection tests.

## Tests

`tests/test_agent_browser_v3_fixture_bench.py` verifies:

- profile lifecycle exists/open and destroyed/close;
- private-session FinalGate accepts the fixture lifecycle;
- sandboxed JS fixture accepts no-network script and rejects network marker;
- cookie/storage fixture leak is rejected;
- HAR/body fixture leak is rejected.

## Verdict

P4C-H.2 gives Browser V3 a concrete backend-reality fixture layer. This is still
not live browser automation proof, but it is stronger than injected return
objects because the profile lifecycle and adversarial fixture paths are tested.
