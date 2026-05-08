# P4B Browser V3 Authority Class Plan

Date: 2026-04-29
Status: P4B-0 through P4B-8 locked; P4B-9/P4C review completed

## Direct Rule

P4B is not one feature. It is a sequence of separate authority classes.

Every class must include:

- request model;
- MissionAuthority field;
- ToolRegistry manifest;
- execution adapter;
- receipt;
- EventBus accepted/rejected events;
- FinalGate checks;
- negative tests;
- EvalBench mission;
- rollback or quarantine behavior when applicable.

No P4B class may bypass P3Y ContextPack, ToolIntentCompiler, ToolRegistry,
MissionAuthority, EventBus, receipts, or FinalGate.

## P4B Sequence

| Phase | Authority class | Purpose | Required P4A proof | Status |
| --- | --- | --- | --- | --- |
| P4B.0 | V3 authority kernel | Shared authority grant, request, receipt, and FinalGate contract. | P3Y compiler and P4A proof surfaces. | Done |
| P4B.1 | `browser_form_submit` | Submit public forms on granted domains. | UIObservation refs, form field map, dry-run plan, verifier postcondition. | Done |
| P4B.2 | `browser_download_quarantine` | Download into quarantine only. | URL policy proof, MIME/size proof, quarantine receipt. | Done |
| P4B.3 | `browser_upload_authorized` | Upload only certified Sentinel artifacts. | Artifact receipt, upload target UIObservation, verifier receipt. | Done |
| P4B.4 | `browser_private_session` | Per-mission private browser session boundary. | Session isolation proof, destroy proof, domain scope. | Done |
| P4B.5 | `browser_login_authority` | Login to granted accounts using vault indirection. | Private session proof, account id authority, no credential logs. | Done |
| P4B.6 | `browser_cookie_storage_contracts` | Explicit cookie/storage contracts. | Storage scope proof, expiration, no cross-mission reuse. | Done |
| P4B.7 | `browser_js_evaluate_sandboxed` | Whitelisted script-hash execution only. | Script hash allowlist, offline/no-network proof, result hash. | Done |
| P4B.8 | `browser_har_body_capture` | Bounded HAR/body capture for diagnostics. | Domain/MIME/byte limits, redaction proof, trace hash. | Done |
| P4B.9 / P4C | Browser V3 supremacy review | Integrated logic/code/algorithm/math/failure/comparison review. | P4B-0 through P4B-8 lock verdicts. | Done |

## P4B.1 Form Submit

Status: implemented and locked in `P4B_FORM_SUBMIT_LOCK_VERDICT.md`.

Required:

- `allowed_actions` includes `browser_form_submit`;
- allowed domains are explicit;
- certified dry-run plan exists;
- form fields are mapped to runtime refs;
- values are redacted in receipts where needed;
- post-submit verifier captures before/action/after;
- same-origin or explicitly granted redirect only.

Reject:

- no dry-run plan;
- form target outside allowed domains;
- payment or credential form unless separate authority exists;
- missing post-action snapshot;
- forged submission receipt.

## P4B.2 Download Quarantine

Status: implemented and locked in `P4B_DOWNLOAD_QUARANTINE_LOCK_VERDICT.md`.

Required:

- `allowed_actions` includes `browser_download_quarantine`;
- max bytes and MIME allowlist exist;
- file lands in quarantine path only;
- SHA-256 and MIME proof recorded;
- promotion is a separate future action.

Reject:

- direct promotion;
- path outside quarantine;
- MIME or size outside authority;
- missing hash.

## P4B.3 Upload Authorized

Status: implemented and locked in `P4B_UPLOAD_AUTHORIZED_LOCK_VERDICT.md`.

Required:

- `allowed_actions` includes `browser_upload_authorized`;
- source artifact id is explicitly granted;
- source artifact has a valid Sentinel receipt;
- upload target is bound to UIObservation ref;
- post-action verifier checks result.

Reject:

- arbitrary disk path;
- artifact not in capture ledger;
- target outside allowed domains;
- missing upload receipt.

## P4B.4 Private Session

Status: implemented and locked in `P4B_PRIVATE_SESSION_LOCK_VERDICT.md`.

Required:

- `allowed_actions` includes `browser_private_session`;
- profile is per mission only;
- allowed domains are explicit;
- created/destroyed events are recorded;
- cookies/storage are scoped and not exposed to LLM context.

Reject:

- profile reuse across missions;
- storage on non-granted domains;
- missing destroy proof.

## P4B.5 Login Authority

Status: implemented and locked in `P4B_LOGIN_AUTHORITY_LOCK_VERDICT.md`.

Required:

- private session authority exists;
- `allowed_actions` includes `browser_login_authority`;
- account id is granted by mission authority;
- credential source is vault indirection only;
- credentials never appear in prompts, events, docs, or receipts.

Reject:

- credential in payload;
- login to non-granted account;
- login without session proof.

## P4B.6 Cookie/Storage Contracts

Status: implemented and locked in `P4B_COOKIE_STORAGE_LOCK_VERDICT.md`.

Required:

- explicit storage scope;
- expiration and revocation model;
- no cross-mission reuse unless a future authority class grants it;
- redacted storage summaries only.

Reject:

- silent persistence;
- unscoped cookies;
- storage export to ContextPack.

## P4B.7 Sandboxed JS Evaluate

Status: implemented and locked in `P4B_JS_EVALUATE_SANDBOXED_LOCK_VERDICT.md`.

Required:

- script hash is pre-approved;
- no network calls from script;
- result size is bounded;
- timeout enforced;
- result hash recorded.

Reject:

- non-whitelisted script;
- network activity during script execution;
- oversized result without truncation proof.

## P4B.8 HAR/Body Capture

Status: implemented and locked in `P4B_HAR_BODY_CAPTURE_LOCK_VERDICT.md`.

Required:

- explicit domain scope;
- MIME and byte limits;
- redaction plan;
- body capture hash and retention metadata;
- final artifact proof.

Reject:

- credential-bearing body without redaction;
- unbounded capture;
- cross-domain capture without authority.

## P4B.9 / P4C Supremacy Review

Status: completed in `P4C_BROWSER_V3_SUPREMACY_REVIEW.md` and
`P4C_BROWSER_V3_LOCK_VERDICT.md`.

Decision:

- Browser V3 authority architecture is locked;
- P4C hardened `ToolIntentCompiler` against raw credential, cookie/storage, and
  HAR/body payload fields in LLM draft intents;
- external raw-browser supremacy is not declared until real backend hardening
  and multi-run EvalBench pass.

## P4B Acceptance Before Each Next Class

Each class must pass:

- targeted positive tests;
- forged receipt/event negative tests;
- authority-missing negative tests;
- stale-ref negative tests where refs are used;
- full core tests;
- compileall;
- vendor-trace scan;
- execution-boundary scan;
- class-specific lock verdict.

## Final P4B Rule

No class unlocks the next one by implication. Each power is granted, implemented,
tested, and locked independently.
