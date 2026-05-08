# P4C-H Browser V3 Hardening Verdict

Date: 2026-04-29
Status: Tranches 1-3 locked

## Final Decision

P4C-H tranches 1, 2, and 3 are locked.

Together they harden Browser V3 at the contract/backend-result boundary, fixture
backend boundary, and local live-adapter boundary.

## What Is Locked

- private-session backend reality validation;
- login backend reality validation;
- cookie/storage redaction marker validation;
- HAR/body redaction marker validation;
- EvalBench multi-run metric summary;
- targeted tests for backend mismatch and redaction leaks.

## Still Not Declared

External browser supremacy is still not declared.

## P4C-H.2

P4C-H.2 is now recorded in `P4C_H2_LOCK_VERDICT.md`.

It adds:

- fixture-backed profile lifecycle;
- fixture-backed JS no-network marker detection;
- fixture-backed cookie/storage and HAR/body adversarial redaction checks;
- Browser V3 EvalBench multi-run case.

## P4C-H.3

P4C-H.3 is now recorded in `P4C_H3_LOCK_VERDICT.md`.

It adds:

- Playwright-backed local live adapter harness;
- private-session profile create/close/destroy proof;
- vault-style account-id login harness;
- login exception-path redaction;
- cookie/storage live redaction summary;
- JS runtime no-network observation;
- HAR/body live redaction artifact proof;
- Browser V3 live EvalBench case with 10 iterations.

## P4C-S

P4C-S is now recorded in `P4C_S_LOCK_VERDICT.md`.

It adds measured local corpus proof through nine EvalBench mission groups.

## Remaining Work

The remaining work is external benchmark proof, not a new power:

1. expand from local fixtures to live public target corpus;
2. run direct peer-browser missions with measured pass rates;
3. decide whether any external-only Browser V3 hardening is needed.

## Next Move

P4C-S is locked. Next decision can move to the next organ or to an external
open-web benchmark, depending on project priority.
