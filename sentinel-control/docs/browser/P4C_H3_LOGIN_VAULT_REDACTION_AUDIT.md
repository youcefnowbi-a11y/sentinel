# P4C-H.3 Login Vault Redaction Audit

Date: 2026-04-29
Status: Completed

## Model

The live harness uses `account_id` as the public authority value. The secret
stays inside `BrowserV3LiveHarnessAccount` and is only used inside the adapter
boundary.

## Proof

- ContextPack/intent/event surfaces carry `account_id`, not raw credentials.
- The live harness fills a local Playwright login fixture.
- Post-login snapshot artifacts are captured through the existing executor.
- Backend exception strings are sanitized before EventBus emission.

## Tests

`test_p4c_h3_backend_exception_redacts_secret_like_strings` verifies that:

- `password=...` does not leak;
- bearer token text does not leak;
- sanitized error payloads contain `[REDACTED]`.

## Remaining Work

Add a vault provider contract separate from the harness before real account
flows are allowed.
