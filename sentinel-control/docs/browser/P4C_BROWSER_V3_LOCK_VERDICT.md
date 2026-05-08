# P4C Browser V3 Lock Verdict

Date: 2026-04-29
Status: Locked after P4C-S measured local corpus

## Final Decision

Browser V3 authority architecture is locked.

Browser V3 local live-adapter proof is locked.

Browser V3 measured local corpus is locked.

External raw-browser supremacy is not declared yet.

## What Is Locked

- P4B-0 authority kernel;
- P4B-1 form submit;
- P4B-2 download quarantine;
- P4B-3 upload authorized;
- P4B-4 private session;
- P4B-5 login authority;
- P4B-6 cookie/storage contracts;
- P4B-7 sandboxed JS evaluate;
- P4B-8 HAR/body capture;
- ToolIntentCompiler V3 boundaries;
- ContextPack V3 exposure rules;
- CoreFinalGate V3 class contracts.

## What P4C Fixed

P4C hardened `ToolIntentCompiler` so LLM draft intents cannot carry raw
credential, cookie/storage, or HAR/body values into V3 classes even when a grant
exists.

## P4C-H Tranche 1

P4C-H tranche 1 is now recorded in `P4C_H_LOCK_VERDICT.md`.

It added:

- backend reality validation for private session and login;
- sensitive marker validation for cookie/storage and HAR/body backend results;
- EvalBench multi-run metrics with accepted/success rates, CI95 half width, and
  unstable iteration reporting.

## P4C-H Tranche 2

P4C-H tranche 2 is now recorded in `P4C_H2_LOCK_VERDICT.md`.

It added:

- `BrowserV3FixtureBackendBench`;
- fixture profile open/close lifecycle proof;
- fixture JS network marker rejection;
- fixture cookie/storage and HAR/body adversarial leak rejection;
- Browser V3 EvalBench multi-run proof.

## P4C-H Tranche 3

P4C-H tranche 3 is now recorded in `P4C_H3_LOCK_VERDICT.md`.

It added:

- Playwright-backed local live adapter harness;
- live private-session profile create/close/destroy proof;
- vault-style account-id login harness with exception-path redaction;
- live cookie/storage redaction summary;
- JS runtime no-network observation;
- HAR/body live redaction artifact proof;
- 10-run Browser V3 live harness EvalBench proof.

## P4C-S

P4C-S is now recorded in `P4C_S_LOCK_VERDICT.md`.

It added:

- nine Browser V3 measured mission groups;
- repeated EvalBench runs;
- local measured scorecard;
- peer-browser comparison update using observed local results;
- explicit boundary against external open-web victory claims.

## What Remains Before External Supremacy Claims

No external browser-supremacy claim should be made until a public target corpus
is measured:

1. live public target suite;
2. repeated direct peer-browser missions;
3. external fault injection and adversarial pages;
4. measured scorecard with observed external results.

## Verdict Phrase

Browser V3 is now a governed authority-class browser with local live-adapter
and measured local corpus proof. It is ready for the next organ decision, not
for unmeasured external victory claims.
