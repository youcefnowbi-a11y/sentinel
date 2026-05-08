# P4B-5 Login Authority Lock Verdict

Date: 2026-04-29
Status: locked

## Implemented

- Browser login authority request/result/receipt models.
- EventBus executed/rejected events.
- ToolRegistry manifest for `browser_login_authority`.
- ToolIntentCompiler grant rules.
- CapabilityPolicy authorization for `credential_access` only with login grant.
- Controlled runner branch with injected backend.
- FinalGate login contract and credential leak rejection.
- Tests for certified login and forged credential payload rejection.

## Verdict

P4B-5 is locked. Sentinel can perform login only through account-id authority,
private-session proof, compiled intent, certified plan, post-login snapshot, and
FinalGate credential-redaction checks.
