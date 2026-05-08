# Sentinel Autonomy Engine Specification

Status: G12 architecture and implementation spec
Runtime status: deterministic v0 only
Date: 2026-04-26

## 0. Purpose

The Autonomy Engine decides whether a proposed mission action should run automatically, continue with logging, escalate to the user, or block.

It is mission-aware. It does not evaluate actions in isolation.

```text
MissionAuthorityEnvelope + MissionState + MissionAction -> route
```

## 1. Routing Outputs

```text
auto_execute
log_and_continue
escalate
block
```

Meaning:

- `auto_execute`: in-scope, allowed, reversible, local, non-sensitive, within budget.
- `log_and_continue`: in-scope and allowed, but should be visible in timeline.
- `escalate`: needs user decision because boundary is unclear or impact is high.
- `block`: violates invariant, mission scope, forbidden action, expired authority, or black-zone runtime.

## 2. Deterministic Classifiers v0

Do not train neural classifiers in G12.

G12 creates deterministic rule-based classifiers and trace data for later model training.

### ReversibilityClassifier

Classes:

- read_only;
- draft;
- local_write_reversible;
- state_mutating_recoverable;
- irreversible.

### ExternalityClassifier

Classes:

- internal_local;
- internal_connected_system;
- external_private;
- external_public.

### SensitivityClassifier

Classes:

- public;
- internal;
- personal;
- secret;
- financial;
- identity.

### ConfidenceClassifier

Classes:

- high;
- medium;
- low;
- unknown.

## 3. Risk Score v0

```text
risk_score =
  25 * out_of_scope
+ 20 * forbidden_or_unknown_tool
+ 15 * externality
+ 15 * irreversibility
+ 10 * sensitivity
+ 10 * cost_pressure
+  5 * low_confidence
```

Inputs are normalized to 0 or 1 in v0, except confidence where `high = 0`, `medium = 0.5`, and `low|unknown = 1`.

Routing:

```text
0-30   -> auto_execute
31-55  -> log_and_continue
56-80  -> escalate
81-100 -> block
```

## 4. Hard Overrides

Block immediately if:

- mission is expired;
- mission is revoked;
- mission is stopped;
- action matches forbidden_actions;
- action uses unknown tool;
- action asks for unknown action type;
- target path leaves allowed paths;
- action requires black-zone runtime.

Black-zone runtime in G12:

- shell;
- desktop control;
- browser submit;
- real external send;
- payment;
- dependency install;
- credential access;
- production mutation;
- vendor runtime integration.

## 5. Scope Checks

An action is in scope only if all required dimensions pass:

- system is allowed;
- tool is allowed;
- action type is allowed;
- target path/domain/account is allowed;
- data type is allowed;
- cost is within budget;
- action count is within max_actions;
- mission is active;
- action is compatible with mode.

## 6. Mission Budget Controller

Inputs:

- max_cost_usd;
- current cost_used;
- estimated action cost;
- effort_level;
- remaining mission steps.

Rules:

- if estimated action exceeds remaining budget, escalate or block;
- if mission reaches 80 percent budget, emit budget_warning;
- if mission reaches 100 percent budget, block new actions;
- deep effort requires budget preview;
- budget exhaustion cannot mark mission completed successfully unless success criteria were already met.

## 7. Mission Kill Switch

Functions:

- pause mission;
- stop mission;
- revoke mission authority.

Rules:

- pause finishes current safe step and stops queue;
- stop interrupts queue immediately when safe to do so;
- revoke invalidates MissionAuthorityEnvelope and blocks all future actions.

Trace events:

- mission_paused;
- mission_stopped;
- mission_revoked.

## 8. Reviewer Agent Role

G12 should make room for a reviewer even if implementation starts simple.

Reviewer checks:

- evidence references;
- mission drift;
- cost drift;
- quality of generated artifacts;
- policy boundary violations;
- repeated failures;
- escalation triggers.

Reviewer does not need to approve every action. It can review:

- before mission start;
- after a batch;
- before final package;
- when an escalation trigger fires.

## 9. Pseudocode

```python
def route_action(envelope, state, action):
    if state.status in {"stopped", "revoked"}:
        return block("mission_not_active")

    if now() > envelope.expires_at:
        return block("mission_expired")

    if action.action_type in envelope.forbidden_actions:
        return block("forbidden_action")

    if action.tool not in envelope.allowed_tools:
        return escalate("tool_not_in_mission_scope")

    if action.action_type not in envelope.allowed_actions:
        return escalate("action_not_in_mission_scope")

    if is_black_zone(action):
        return block("black_zone_runtime_disabled")

    if exceeds_budget(envelope, state, action):
        return escalate("budget_limit_reached")

    risk = score_action(envelope, state, action)

    if risk <= 30:
        return auto_execute(risk)
    if risk <= 55:
        return log_and_continue(risk)
    if risk <= 80:
        return escalate("risk_threshold_exceeded", risk)
    return block("risk_too_high", risk)
```

## 10. Required Tests

- in-scope reversible action auto-executes;
- out-of-scope action escalates;
- forbidden action blocks;
- mission expired blocks;
- revoked mission blocks;
- stopped mission blocks;
- budget exceeded escalates or blocks;
- max_actions exceeded escalates;
- local GTM file generation runs without approval;
- outreach draft generation does not send;
- external send escalates or blocks;
- shell action blocks even in Power mode;
- browser submit blocks even in Power mode;
- credential access blocks;
- `allow_for_this_mission` cannot grant unknown or black-zone scope;
- every auto action writes trace;
- every escalation writes trace;
- every block writes trace;
- path traversal outside generated_projects blocks;
- mission kill switch stops queued actions.
