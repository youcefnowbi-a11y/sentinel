# Brain Authority And Policy

Date: 2026-04-28
Status: Core Brain Lock documentation

## Mission Authority

`MissionAuthorityEnvelope` is the delegation contract. It defines:

- mission id and user id;
- mission type, title, objective, success criteria;
- mode;
- allowed systems, tools, actions, paths, domains, accounts, and data types;
- forbidden actions;
- max duration, max actions, max cost, max recipients;
- risk appetite;
- escalation triggers;
- rollback preference;
- trace level;
- emergency stop;
- expiration and revocation.

No context source can expand this envelope during a run.

## Memory Boundary

Memory can inform context. It cannot:

- add allowed tools;
- add allowed actions;
- add allowed paths;
- approve an action;
- change risk posture;
- disable trace;
- disable stop/revoke;
- mark evidence as verified without source evidence.

This rule also applies to web pages, uploaded documents, vendor prompts, skill
files, and model output.

## Tool Policy

Tool selection is a classification step, not execution.

Statuses:

- `eligible_for_safe_worker`;
- `eligible_for_dry_run`;
- `candidate`;
- `blocked`;
- `unavailable`.

Only policy-eligible tools can be passed to planning or the controlled worker
execution lane.
Candidate, blocked, and unavailable tools must remain non-executable.

## Execution Posture

`ExecutionPosturePolicy` decides how aggressively the brain can push inside
already granted authority.

Modes:

- SAFE: cautious, no direct tool-call budget, no repair cycles.
- OPERATOR: balanced, small direct budget, one repair cycle.
- POWER: more aggressive for local reversible work, larger direct budget and
  repair allowance.
- AUTONOMOUS-like modes: still no new powers; stricter duration/recurrence
  discipline must apply when implemented.

Posture never grants:

- tools;
- actions;
- paths;
- systems;
- domains;
- credentials;
- network access;
- account access.

POWER means "push harder inside the mandate", not "bypass the mandate".

## RiskRouter

`RiskRouter` lives in `sentinel/mission/risk.py`. It routes a
`MissionAction` under:

- `MissionAuthorityEnvelope`;
- `MissionState`;
- optional `MissionExecutionPosture`;
- budget controller;
- scope checker.

Routes:

- `auto_execute`;
- `log_and_continue`;
- `escalate`;
- `block`.

Hard block or escalation conditions include:

- mission identity mismatch;
- revoked, stopped, failed, completed, or escalated mission;
- expired mission;
- forbidden or black-zone action;
- outside authority;
- budget boundary;
- posture mismatch;
- non-local or non-recoverable action.

## Risk Score

Risk score currently increases for:

- out-of-scope action;
- external action;
- irreversible action;
- sensitive data;
- high relative cost;
- low or unknown confidence.

The score is bounded at 100. Posture thresholds decide route only after hard
authority checks pass.

## Black-Zone

The brain must not enable these powers in the current certified core:

- shell/process execution;
- browser submit or logged-in browser automation;
- network/API mutation;
- email/channel send;
- credentials or password manager access;
- payment/spend;
- desktop/sidecar control;
- arbitrary eval/exec;
- dependency install;
- production mutation;
- path escape outside allowed roots.

Future modules may model these as fake eval cases or capability contracts, but
they remain non-executable until separately approved.
