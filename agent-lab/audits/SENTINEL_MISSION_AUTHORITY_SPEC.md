# Sentinel Mission Authority Specification

Status: G12 architecture and implementation spec
Runtime status: safe local mission authority only
Date: 2026-04-26

## 0. Doctrine

Sentinel does not ask permission for every action.

Sentinel asks permission for the mission, acts autonomously inside the mission, and escalates only at the boundary.

Core rule:

```text
Permission once for the mission.
Autonomy inside the mission.
Escalation only at the boundary.
```

## 1. What This Replaces

This spec supersedes the idea that Power Mode is the primary authority primitive.

Power Mode remains a future authority level, but the primary primitive is:

```text
MissionAuthorityEnvelope
```

Rejected models:

- permission per action as default behavior;
- global Full Access button;
- tool-only permission as the main contract;
- model-depth selection confused with autonomy level.

Accepted model:

- mission-scoped autonomous execution.

## 2. Authority Levels

### Safe

Purpose:

- local, reversible, draft-only missions.

Allowed:

- GTM pack generation;
- local project folder creation;
- markdown/JSON export;
- outreach drafts without sending;
- watchlist creation;
- research questions;
- trace writing.

### Operator

Purpose:

- serious missions with bounded internal work and light escalation.

Allowed:

- everything in Safe;
- durable memory writes after policy check;
- sensitive exports with preview;
- later internal system updates after connector-specific evals.

### Power

Purpose:

- future high-authority mission execution.

Allowed now:

- spec only.

Future examples:

- browser automation inside a sandbox;
- scoped outbound messages to approved recipients;
- scoped sidecar or app automation;
- controlled workspace mutations.

### Autonomous

Purpose:

- future recurring missions with narrow scope and strict caps.

Rule:

- the more durable the autonomy, the narrower the scope must be.

## 3. MissionAuthorityEnvelope

Required fields:

```json
{
  "id": "mission_...",
  "user_id": "user_...",
  "mission_title": "...",
  "mission_objective": "...",
  "success_criteria": [],
  "expected_artifacts": [],
  "mode": "safe|operator|power|autonomous",
  "effort_level": "quick|standard|deep",
  "allowed_systems": [],
  "allowed_tools": [],
  "allowed_actions": [],
  "forbidden_actions": [],
  "allowed_paths": [],
  "allowed_domains": [],
  "allowed_accounts": [],
  "allowed_data_types": [],
  "max_duration_minutes": 0,
  "max_actions": 0,
  "max_cost_usd": 0.0,
  "max_recipients": 0,
  "risk_appetite_score": 0,
  "escalation_triggers": [],
  "rollback_preference": "none|checkpoint|compensating_action",
  "trace_level": "standard|full",
  "emergency_stop_enabled": true,
  "created_at": "...",
  "expires_at": "...",
  "revoked_at": null
}
```

Invariants:

- no mission can disable trace;
- no mission can disable emergency stop;
- no mission can grant unknown tools;
- no mission can grant black-zone actions in v1;
- no mission can write outside approved paths;
- no mission can treat memory as authority;
- no mission can bypass evidence gates for business decisions.

## 4. MissionState

```json
{
  "mission_id": "mission_...",
  "status": "planned|running|paused|escalated|completed|failed|stopped|revoked",
  "current_step": "...",
  "action_count": 0,
  "cost_used": 0.0,
  "started_at": null,
  "updated_at": "...",
  "ended_at": null
}
```

Rules:

- expired missions block all future actions;
- stopped missions block queued actions;
- revoked missions invalidate the authority envelope;
- paused missions finish only the current safe step, then stop queue processing.

## 5. MissionAction

```json
{
  "id": "act_...",
  "mission_id": "mission_...",
  "action_type": "...",
  "tool": "...",
  "intent": "...",
  "target": "...",
  "input": {},
  "expected_output": "...",
  "reversibility": "read_only|draft|local_write_reversible|state_mutating_recoverable|irreversible",
  "externality": "internal_local|internal_connected_system|external_private|external_public",
  "sensitivity": "public|internal|personal|secret|financial|identity",
  "estimated_cost": 0.0,
  "confidence": "high|medium|low|unknown",
  "risk_score": 0,
  "route": "auto_execute|log_and_continue|escalate|block",
  "evidence_refs": [],
  "trace_id": null
}
```

## 6. EscalationRequest

```json
{
  "id": "esc_...",
  "mission_id": "mission_...",
  "action_id": "act_...",
  "reason": "...",
  "user_question": "...",
  "action_preview": {},
  "impact_summary": "...",
  "options": ["approve_once", "allow_for_this_mission", "deny", "take_over"],
  "created_at": "...",
  "resolved_at": null
}
```

Escalation must answer:

- why am I asking now?
- what exactly will happen?
- what is the impact?
- what do you want to do?

`allow_for_this_mission` may update mission authority only inside existing mode and system invariants.

It cannot grant:

- shell;
- desktop control;
- credential access;
- real browser submit;
- payment;
- dependency install;
- production mutation;
- unknown scopes.

## 7. MissionTraceEvent

```json
{
  "mission_id": "mission_...",
  "event_type": "mission_created|mission_started|mission_paused|mission_resumed|mission_stopped|mission_revoked|mission_completed|action_planned|action_routed|action_executed|action_escalated|action_blocked|user_approved_once|user_allowed_for_mission|user_denied|user_takeover|budget_warning|budget_exceeded|rollback_available|rollback_executed",
  "actor": "user|sentinel|reviewer|policy",
  "action_id": null,
  "summary": "...",
  "target": "...",
  "result": "...",
  "impact": "...",
  "reversible": true,
  "cost": 0.0,
  "timestamp": "..."
}
```

Trace language should be operational, not fear-based.

## 8. Safe Mission Types v0

Allowed v0 mission examples:

- create GTM launch pack for idea X;
- prepare first-customer outreach drafts;
- research competitors and create watchlist;
- build validation folder and 7-day roadmap;
- import CueIdea report and generate evidence-backed GTM pack.

Allowed auto-execute v0 actions:

- create_project_folder;
- create_markdown_file;
- export_json;
- generate_gtm_pack;
- generate_landing_copy;
- generate_outreach_drafts_without_sending;
- create_watchlist;
- generate_research_questions;
- write_trace.

Write boundary:

```text
sentinel-control/data/generated_projects
```

## 9. Black-Zone Actions v0

Blocked regardless of user mode:

- shell execution;
- desktop control;
- real browser submit;
- real email/channel send;
- payment/spend;
- dependency install;
- credential access;
- production code mutation;
- vendor runtime integration;
- policy mutation by memory or prompt;
- path traversal outside allowed project roots.

## 10. Implementation Rule

G12 implementation must make Sentinel feel more autonomous, not more bureaucratic.

The first product proof:

```text
User delegates GTM mission.
Sentinel creates the folder, evidence pack, GTM pack, landing copy, outreach drafts, watchlist, roadmap, and trace without micro-approval.
Sentinel escalates only if the next action crosses the mission boundary.
```
