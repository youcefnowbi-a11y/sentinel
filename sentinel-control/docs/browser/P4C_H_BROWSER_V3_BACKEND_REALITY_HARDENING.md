# P4C-H Browser V3 Backend Reality Hardening

Date: 2026-04-29
Status: Contract-level hardening completed

## Goal

P4C-H does not add browser powers. It makes Browser V3 harder to fake by
checking backend output before accepted V3 events are emitted.

## Hardening Added

### Private Session

The private-session executor now rejects backend results when:

- backend `operation` does not match the request operation;
- session/profile ids are missing;
- storage state hash is not SHA-256 shaped;
- backend enables storage without request/grant alignment;
- backend reports domains outside the grant;
- close result does not match requested session/profile;
- close result lacks destroy/profile-destroy proof.

### Login Authority

The login executor now rejects backend results when:

- backend before-snapshot hash does not match the certified plan snapshot;
- after-page final URL does not match backend final URL;
- backend post-login payload contains sensitive markers such as credential or
  authorization material.

### Cookie/Storage Contracts

The cookie/storage executor now rejects backend results when:

- storage state hash is not SHA-256 shaped;
- a redacted summary still contains sensitive markers such as `Set-Cookie` or
  raw cookie APIs.

### HAR/Body Capture

The HAR/body executor now rejects backend results when:

- supplied body hash is malformed;
- redacted entries still contain sensitive markers such as `Authorization`,
  bearer tokens, or `Set-Cookie`.

## Tests Added

- private-session backend mismatch rejection;
- cookie/storage redaction marker rejection;
- HAR/body sensitive marker rejection.

## Verdict

P4C-H closes the most important contract-level backend-reality gap. It still does
not prove real Playwright/private-profile behavior. That requires the next
fixture-backed adapter tranche.
