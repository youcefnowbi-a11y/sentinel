# Sentinel Power Mode Specification

Status: G11 product and architecture spec, superseded by G12 Mission Authority as the primary primitive
Runtime status: disabled
Date: 2026-04-26

## 0. Boundary

This document defines future Power Mode semantics. It does not enable:

- shell execution;
- desktop control;
- browser submit;
- real email or channel send;
- sidecar runtime;
- payment or spend;
- dependency install;
- production code mutation;
- credential access;
- vendor runtime integration.

Power Mode is a future authority level. Current Sentinel remains safe local execution only.

G12 correction:

- Power Mode is not the primary authority primitive.
- The primary primitive is `MissionAuthorityEnvelope`.
- Power Mode is one mode inside a mission-scoped authority envelope.
- Sentinel should ask permission for the mission, not for every action and not through a global Full Access toggle.

## 1. Purpose

Sentinel must be aggressive where actions are reversible and controlled where actions affect the outside world.

Power Mode exists to make high-impact future capabilities possible without turning them into unbounded autonomy.

It must always be attached to a mission objective, success criteria, allowed systems, allowed actions, forbidden actions, duration, cost limits, escalation triggers, and stop/revoke controls.

Core principle:

```text
Default safe. Powerful when scoped. Autonomous only when trusted by explicit policy.
```

## 2. Modes

### 2.1 Safe Mode

Default mode.

Allowed behavior:

- generate GTM packs;
- create local project folders inside approved roots;
- create markdown files;
- export JSON;
- create watchlists;
- generate landing copy;
- generate outreach drafts without sending;
- run research and evidence analysis;
- write trace records.

UX:

- minimal friction;
- automatic execution for green-zone actions after policy check;
- no scary approval screens for safe local generation.

### 2.2 Operator Mode

Controlled impact mode.

Allowed behavior:

- medium-risk actions with preview;
- user-approved real contact drafts;
- durable memory writes after policy validation;
- sensitive export previews;
- later read-only browser research if the browser sandbox passes evals.

UX:

- quick preview;
- approve once for a clearly bounded action;
- no hidden background authority.

### 2.3 Power Mode

Future advanced mode.

Purpose:

- unlock high-impact scopes after explicit opt-in, capability evals, policy gates, trace guarantees, and revocation controls.

Possible future scopes:

- browser_control;
- email_send;
- external_messages;
- filesystem_write;
- filesystem_read;
- desktop_context;
- desktop_control;
- app_automation;
- shell_commands;
- sidecar_rpc;
- publish_content;
- spend_money;
- install_dependency;
- code_mutation.

Rule:

- Power Mode is never global. It grants authority through scoped envelopes.

### 2.4 Autonomous Mode

Later mode only.

Purpose:

- pre-approved recurring playbooks with strict caps, scoped resources, trace, kill switch, and outcome review.

Not allowed:

- generic unlimited autonomy;
- silent account mutation;
- memory-created authority;
- autonomous shell or desktop power without a dedicated future review.

## 3. Authority Envelope

Every Power Mode grant must create an authority envelope.

Required fields:

```json
{
  "id": "auth_...",
  "user_id": "...",
  "run_id": "...",
  "mode": "operator|power|autonomous",
  "scopes": [],
  "allowed_resources": {},
  "denied_resources": {},
  "allowed_paths": [],
  "allowed_domains": [],
  "allowed_accounts": [],
  "max_actions": 0,
  "max_cost_usd": 0.0,
  "max_recipients": 0,
  "duration_minutes": 0,
  "dry_run_preference": "always|first_time|policy_based",
  "approval_threshold": "low|medium|high|critical",
  "trace_level": "standard|full",
  "emergency_stop_enabled": true,
  "created_at": "...",
  "expires_at": "...",
  "revoked_at": null
}
```

Invariants:

- No envelope can disable trace.
- No envelope can disable emergency stop.
- No envelope can grant unknown scopes.
- No envelope can grant authority through memory.
- No envelope can permit actions outside its resource scope.
- No envelope can survive expiration or revocation.

## 4. Tempo Router

Power Mode uses the G12 mission-aware tempo router.

```text
green  -> in-scope and reversible -> execute after policy check
amber  -> in-scope and recoverable -> log, preview, or light approval
red    -> in-scope but external, irreversible, sensitive, costly, or low confidence -> escalate
black  -> forbidden, out of mission scope, or unavailable until capability evals pass -> block
```

Green:

- local, reversible, non-sensitive, no external mutation.

Amber:

- durable memory;
- sensitive local export;
- draft linked to real contacts;
- future read-only browser research.

Red:

- external send;
- browser action in authenticated context;
- account mutation;
- publish;
- external API mutation;
- filesystem write outside generated-project roots.

Black:

- shell commands;
- desktop control;
- payment;
- dependency install;
- production code mutation;
- credential access;
- sidecar RPC before signed sidecar and fake benchmarks.

## 5. UI Contract

Activation copy must communicate capability, not fear.

The UI must show the mission mandate:

- mission objective;
- success criteria;
- exact scopes being granted;
- allowed resources;
- denied resources;
- duration;
- max actions;
- max cost;
- approval behavior;
- trace behavior;
- emergency stop;
- revocation control.

The UI must not use:

- one-click global Full Access;
- vague "I accept responsibility for everything" consent;
- hidden capability expansion;
- silent credential access;
- disabled logs;
- non-revocable sessions.

## 6. Trace Requirements

Power Mode creates additional trace events:

- authority_envelope_created;
- authority_scope_checked;
- authority_denied;
- authority_used;
- authority_expired;
- authority_revoked;
- emergency_stop_triggered;
- power_mode_action_previewed;
- power_mode_action_executed;
- power_mode_action_blocked.

Every high-impact action trace must include:

- envelope id;
- scope used;
- resource touched;
- dry-run hash;
- policy version;
- cost estimate;
- user approval reference if required;
- result;
- rollback status when applicable.

## 7. Eval Gates

No Power Mode scope can move from spec to real runtime until it has:

- fake fixture dataset;
- scanner rule coverage;
- policy mapping;
- dry-run schema;
- approval or authority-envelope schema;
- trace completeness tests;
- out-of-scope denial tests;
- prompt-injection tests;
- memory-poisoning tests;
- emergency-stop tests;
- budget-cap tests where relevant.

Scope-specific gates:

- browser_control requires browser sandbox evals and no form submit by default;
- email_send requires contact ownership, opt-out policy, rate limits, and reputation safeguards;
- external_messages require channel-specific compliance and no bulk spam mode;
- filesystem_write requires path sandboxing and traversal tests;
- shell_commands require a future isolated command sandbox and remain black-zone now;
- desktop_control requires signed sidecar, screen sanitizer, and explicit user-visible control;
- spend_money requires hard caps, merchant preview, receipt trace, and separate user confirmation.

## 8. Roadmap Placement

Current:

- Safe Mode only;
- Operator Mode for previews and draft approvals;
- no real high-impact runtime.

Next:

- implement Mission Authority Kernel with green-zone auto-execution;
- implement MissionAuthorityEnvelope data model;
- implement fake-only Power Mode harness.

Later:

- read-only browser sandbox;
- inbound channels as untrusted sources;
- scoped external send after compliance gates;
- permissioned sidecar after fake benchmarks;
- autonomous playbooks after repeated approval/outcome data.

## 9. Final Rule

Power Mode is not "no rules."

Power Mode is:

```text
explicit authority
+ scoped resources
+ bounded time
+ action caps
+ cost caps
+ dry-run semantics
+ trace
+ revocation
+ emergency stop
```

That is how Sentinel becomes powerful without becoming blind.
