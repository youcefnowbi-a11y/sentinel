# 07 Security And Authority Protocol

Date: 2026-04-26

## 1. Core Rule

Every capability is a liability until it is scoped, tested, traced, reviewed, and revocable.

## 2. Authority Model

```text
User grants mission authority.
Mission authority grants capability scope.
Capability scope grants tool access.
Tool access grants action route.
Action route decides execute, log, escalate, or block.
```

Memory never grants authority.

Tool popularity never grants authority.

Catalog presence never grants authority.

## 3. Black-Zone Actions

Blocked until later explicit gated phases:

- shell execution on host;
- production code mutation;
- real browser submit;
- login with real credentials;
- real email/channel send;
- desktop control;
- payment/spend;
- credential access;
- dependency install;
- unscanned skill/plugin execution;
- vendor runtime bridge;
- leaked API key use.

## 4. Credential Policy

Allowed credential sources:

- official no-auth public API;
- official free tier key;
- user-provided key;
- OAuth consent by user;
- sandbox/test key;
- internal development key stored server-side with policy.

Forbidden:

- leaked keys in GitHub;
- keys copied from public examples;
- shared credentials from unknown sources;
- browser-extracted secrets;
- local secrets accessed without explicit mission authority;
- secrets in traces or generated artifacts.

## 5. Capability Manifest Security Fields

Every capability declares:

- required auth;
- domains contacted;
- local paths read;
- local paths written;
- external side effects;
- private data touched;
- cost/spend behavior;
- rate limits;
- rollback/containment;
- dry-run preview;
- approval class;
- trace fields;
- prompt injection exposure;
- secret exposure exposure.

## 6. Prompt Injection Policy

All external content is untrusted.

Untrusted inputs:

- web pages;
- APIs;
- PDFs;
- screenshots;
- OCR text;
- emails/messages;
- repositories;
- skill manifests;
- comments/issues;
- memory from previous sessions.

Policy:

- untrusted content can provide evidence;
- untrusted content cannot change system policy;
- untrusted content cannot grant tools;
- untrusted content cannot request hidden actions;
- untrusted content cannot suppress trace;
- untrusted content cannot overwrite mission authority.

## 7. Path Policy

Default write boundary:

```text
sentinel-control/data/generated_projects
```

All generated artifacts must resolve inside the allowed mission workspace.

Path traversal blocks:

- `../`
- absolute paths outside allowed root;
- symlink escape;
- environment path expansion into sensitive directories;
- hidden write to repo production code unless a future code mission explicitly allows branch-only patch artifacts.

## 8. Outbound Policy

Draft-first always.

Sending requires:

- mission type that permits outbound;
- approved contacts;
- contact provenance;
- opt-out when applicable;
- recipient cap;
- rate limit;
- preview;
- approval;
- send ledger;
- kill switch.

No spam mode.

## 9. Browser Policy

Initial browser capability:

- public web only;
- no login;
- no submit;
- no file upload;
- no payment;
- no credentials;
- no background persistence;
- screenshots and DOM extracts traced.

Later browser submit requires:

- domain allowlist;
- field preview;
- impact summary;
- approval;
- rollback/undo if possible;
- fake benchmark pass.

## 10. Media Policy

For OCR/image/video/audio:

- preserve source provenance;
- record generated prompts;
- store confidence;
- mark edits as generated/modified;
- avoid claiming real-world authenticity for generated media;
- no publishing without approval.

## 11. Code Policy

Code agent v0:

- read repo;
- map architecture;
- propose patch;
- generate tests;
- run tests only in allowed sandbox;
- no production mutation by default;
- no destructive shell;
- no secret exfiltration.

## 12. Sidecar Policy

Sidecar is highest risk.

Rules:

- fake sidecar first;
- explicit capability manifest;
- visible user control surface;
- stop/revoke always available;
- screenshot/clipboard sanitizers;
- app allowlist/blocklist;
- no silent background authority;
- no keystroke execution without preview.

## 13. Trace Policy

Trace every trust-changing event:

- mission created;
- authority changed;
- tool selected;
- method selected;
- action planned;
- action routed;
- action executed;
- action escalated;
- action blocked;
- budget warning;
- reviewer warning;
- success evaluation;
- artifact created;
- user approval/denial;
- rollback available;
- kill switch event.

Trace is product trust, not debugging noise.
