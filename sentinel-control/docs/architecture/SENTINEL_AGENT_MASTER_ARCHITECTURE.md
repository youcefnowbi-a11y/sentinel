# Sentinel Agent Master Architecture

Date: 2026-04-26
Status: pre-implementation architecture lock
Scope: Sentinel Control / Sentinel GTM Operator / Mission Authority Kernel

## 0. Architecture Verdict

Sentinel is not a chat assistant and not a raw autonomous runtime.

Sentinel is a mission operating system for proof-backed business agents.

Core doctrine:

```text
Permission once for the mission.
Autonomy inside the mission.
Escalation only at the boundary.
```

The user does not approve every micro-action. The user delegates a bounded mission. Sentinel works aggressively inside that mandate and escalates when an action crosses the mission boundary, becomes external, irreversible, sensitive, costly, ambiguous, or forbidden.

## 1. Product Shape

### Public wedge

Sentinel GTM Operator:

- accepts an idea, CueIdea report, or market signal;
- validates and normalizes evidence;
- enriches research;
- debates the decision;
- creates a First Customer / GTM Pack;
- executes safe local work automatically under mission authority;
- produces a mission timeline and trace.

### Platform moat

Sentinel Control:

- mission authority;
- action routing;
- firewall policy;
- skill scanning;
- trace ledger;
- cost routing;
- memory without authority;
- future browser/channel/sidecar power through scoped mission authority.

## 2. Existing Code Baseline

Current `sentinel-control` already contains useful primitives:

```text
services/sentinel-core/sentinel/shared/models.py
services/sentinel-core/sentinel/shared/enums.py
services/sentinel-core/sentinel/cueidea_bridge/
services/sentinel-core/sentinel/decision/research_enrichment.py
services/sentinel-core/sentinel/decision/debate/
services/sentinel-core/sentinel/execution/gtm_pack.py
services/sentinel-core/sentinel/execution/gtm_quality.py
services/sentinel-core/sentinel/execution/action_runner.py
services/sentinel-core/sentinel/execution/file_executor.py
services/sentinel-core/sentinel/execution/email_draft_executor.py
services/sentinel-core/sentinel/firewall/
services/sentinel-core/sentinel/learning/trace_ledger.py
```

Current gap:

- the system has run/action/firewall concepts, but not mission authority;
- the current firewall is action-first;
- the next kernel must wrap actions inside mission-scoped authority.

## 3. Target Runtime Flow

```text
Mission request
  -> Mission Gateway
  -> MissionAuthorityEnvelope
  -> Mission Planner
  -> CueIdea / Evidence Import
  -> Evidence Verifier
  -> Research Enrichment
  -> Debate / Decision
  -> Mission Plan DAG
  -> Autonomy Engine
       -> scope check
       -> deterministic classifiers
       -> budget check
       -> kill switch check
       -> route: auto / log / escalate / block
  -> Safe Mission Executors
  -> Mission Trace Timeline
  -> GTM Pack / Assets
  -> Mission Completion Report
```

The important shift:

```text
Old: Action -> Firewall -> Approval -> Execution
New: Mission -> Authority -> Plan -> Action -> Route -> Execute/Escalate/Block -> Trace
```

## 4. Core Packages To Add

Create a new mission package:

```text
services/sentinel-core/sentinel/mission/
├── __init__.py
├── authority.py
├── scope_checker.py
├── classifiers.py
├── risk.py
├── budget.py
├── kill_switch.py
├── trace_timeline.py
├── escalation.py
├── planner.py
├── runner.py
└── safe_executors.py
```

Responsibilities:

| File | Responsibility |
|---|---|
| `authority.py` | create and validate `MissionAuthorityEnvelope` |
| `scope_checker.py` | verify tool/action/path/domain/account/data scope |
| `classifiers.py` | deterministic v0 classifiers for reversibility, externality, sensitivity, confidence |
| `risk.py` | mission-aware risk scoring and route selection |
| `budget.py` | max cost, budget warning, max actions |
| `kill_switch.py` | pause, stop, revoke mission authority |
| `trace_timeline.py` | mission trace events, operational timeline |
| `escalation.py` | build escalation payloads and handle user decisions |
| `planner.py` | turn a GTM mission into ordered safe mission actions |
| `runner.py` | execute mission loop end to end |
| `safe_executors.py` | map mission actions to safe existing executors |

## 5. Core Data Contracts

Mission models should live in `sentinel/shared/models.py` first, unless the file becomes too large. If it does, move them into `sentinel/mission/models.py` and re-export from `sentinel/shared`.

### MissionAuthorityEnvelope

Purpose:

- the authority contract for a mission;
- replaces global Full Access and permission-per-action as the main primitive.

Fields:

```python
class MissionAuthorityEnvelope:
    id: str
    user_id: str
    mission_title: str
    mission_objective: str
    success_criteria: list[str]
    expected_artifacts: list[str]
    mode: MissionMode                 # safe | operator | power | autonomous
    effort_level: EffortLevel         # quick | standard | deep
    allowed_systems: list[str]
    allowed_tools: list[str]
    allowed_actions: list[str]
    forbidden_actions: list[str]
    allowed_paths: list[str]
    allowed_domains: list[str]
    allowed_accounts: list[str]
    allowed_data_types: list[str]
    max_duration_minutes: int
    max_actions: int
    max_cost_usd: float
    max_recipients: int
    risk_appetite_score: int
    escalation_triggers: list[str]
    rollback_preference: RollbackPreference
    trace_level: TraceLevel
    emergency_stop_enabled: bool
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
```

Invariants:

- cannot disable trace;
- cannot disable emergency stop;
- cannot grant unknown tools;
- cannot grant black-zone actions in v0;
- cannot write outside allowed roots;
- cannot use memory as authority;
- cannot bypass evidence gates.

### MissionState

Purpose:

- runtime state of one mission.

Fields:

```python
class MissionState:
    mission_id: str
    status: MissionStatus             # planned | running | paused | escalated | completed | failed | stopped | revoked
    current_step: str | None
    action_count: int
    cost_used: float
    started_at: datetime | None
    updated_at: datetime
    ended_at: datetime | None
```

### MissionAction

Purpose:

- mission-scoped action candidate;
- a richer version of `AgentAction`, carrying mission route metadata.

Fields:

```python
class MissionAction:
    id: str
    mission_id: str
    action_type: str
    tool: str
    intent: str
    target: str
    input: dict[str, Any]
    expected_output: str
    reversibility: Reversibility
    externality: Externality
    sensitivity: Sensitivity
    estimated_cost: float
    confidence: Confidence
    risk_score: int
    route: MissionRoute               # auto_execute | log_and_continue | escalate | block
    evidence_refs: list[str]
    trace_id: str | None
```

### EscalationRequest

Purpose:

- compact user-facing decision request at mission boundary.

Fields:

```python
class EscalationRequest:
    id: str
    mission_id: str
    action_id: str
    reason: str
    user_question: str
    action_preview: dict[str, Any]
    impact_summary: str
    options: list[EscalationOption]    # approve_once | allow_for_this_mission | deny | take_over
    created_at: datetime
    resolved_at: datetime | None
```

### MissionTraceEvent

Purpose:

- operational timeline event, separate from raw debug logs.

Fields:

```python
class MissionTraceEvent:
    id: str
    mission_id: str
    event_type: MissionTraceEventType
    actor: MissionActor                # user | sentinel | reviewer | policy
    action_id: str | None
    summary: str
    target: str | None
    result: str | None
    impact: str | None
    reversible: bool
    cost: float
    timestamp: datetime
```

## 6. Enums To Add

Add to `sentinel/shared/enums.py`:

```python
MissionMode = safe | operator | power | autonomous
EffortLevel = quick | standard | deep
MissionStatus = planned | running | paused | escalated | completed | failed | stopped | revoked
MissionRoute = auto_execute | log_and_continue | escalate | block
Reversibility = read_only | draft | local_write_reversible | state_mutating_recoverable | irreversible
Externality = internal_local | internal_connected_system | external_private | external_public
Sensitivity = public | internal | personal | secret | financial | identity
Confidence = high | medium | low | unknown
RollbackPreference = none | checkpoint | compensating_action
TraceLevel = standard | full
EscalationOption = approve_once | allow_for_this_mission | deny | take_over
MissionActor = user | sentinel | reviewer | policy
MissionTraceEventType = mission_created | mission_started | mission_paused | mission_resumed | mission_stopped | mission_revoked | mission_completed | action_planned | action_routed | action_executed | action_escalated | action_blocked | user_approved_once | user_allowed_for_mission | user_denied | user_takeover | budget_warning | budget_exceeded | rollback_available | rollback_executed
```

## 7. Autonomy Engine

### Inputs

```text
MissionAuthorityEnvelope
MissionState
MissionAction
```

### Output

```text
MissionRoute
```

### Route semantics

| Route | Meaning |
|---|---|
| `auto_execute` | in-scope, allowed, reversible, local, non-sensitive, within budget |
| `log_and_continue` | in-scope and recoverable, visible in mission timeline |
| `escalate` | needs user decision because boundary is high-impact or ambiguous |
| `block` | violates invariant, scope, forbidden action, expired/revoked authority, or black-zone runtime |

### Risk score v0

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

Routing:

```text
0-30   -> auto_execute
31-55  -> log_and_continue
56-80  -> escalate
81-100 -> block
```

Hard overrides:

- expired mission blocks;
- revoked mission blocks;
- stopped mission blocks;
- forbidden action blocks;
- unknown tool blocks or escalates depending on risk, but v0 should block unknown execution tools;
- path traversal blocks;
- black-zone runtime blocks.

Black-zone in v0:

- shell;
- desktop control;
- real browser submit;
- real email/channel send;
- payment/spend;
- dependency install;
- credential access;
- production code mutation;
- vendor runtime integration.

## 8. Mission Planner

The mission planner is not a general planner in v0. It is a deterministic planner for safe GTM missions.

Input:

- mission envelope;
- idea or CueIdea report;
- evidence items;
- research enrichment result;
- debate verdict;
- GTM pack generation result.

Output:

- ordered `MissionAction` list.

Safe GTM mission plan:

```text
1. create_project_folder
2. create_markdown_file: 00_VERDICT.md
3. create_markdown_file: 01_EVIDENCE.md
4. create_markdown_file: 02_ICP.md
5. create_markdown_file: 03_COMPETITOR_GAPS.md
6. create_markdown_file: 04_LANDING_PAGE_COPY.md
7. create_markdown_file: 05_OUTREACH_MESSAGES.md
8. create_markdown_file: 06_INTERVIEW_SCRIPT.md
9. create_markdown_file: 07_7_DAY_ROADMAP.md
10. create_markdown_file: 08_WATCHLIST.md
11. export_json: trace.json
12. mission_completed
```

All actions above should be green if:

- mission mode is `safe` or higher;
- tools/actions are allowed;
- target paths remain under generated projects;
- content does not contain secrets;
- outreach is draft-only.

## 9. Safe Mission Executors

Use existing safe execution modules where possible:

```text
execution/file_executor.py
execution/email_draft_executor.py
execution/gtm_pack.py
execution/action_runner.py
```

New `mission/safe_executors.py` should adapt `MissionAction` to safe existing executors.

Allowed auto actions:

- `create_project_folder`
- `create_markdown_file`
- `export_json`
- `generate_gtm_pack`
- `generate_landing_copy`
- `generate_outreach_drafts_without_sending`
- `create_watchlist`
- `generate_research_questions`
- `write_trace`

Implementation mapping:

| Mission action | Existing or new executor |
|---|---|
| `create_project_folder` | `FileExecutor.create_folder` |
| `create_markdown_file` | `FileExecutor.create_file` |
| `export_json` | new helper using path guard |
| `generate_gtm_pack` | `GtmPackGenerator` |
| `generate_landing_copy` | GTM pack section generator |
| `generate_outreach_drafts_without_sending` | `EmailDraftExecutor` / GTM pack section |
| `create_watchlist` | GTM pack section / new JSON export |
| `generate_research_questions` | `research_enrichment.py` output |
| `write_trace` | `MissionTraceTimeline` |

Write boundary:

```text
sentinel-control/data/generated_projects
```

No executor may write outside this root in v0.

## 10. Escalation Gateway

Escalation should not be scary or verbose. It must be operational.

Every escalation answers:

1. Why am I asking now?
2. What exactly will happen?
3. What is the impact?
4. What do you want to do?

Options:

- `approve_once`;
- `allow_for_this_mission`;
- `deny`;
- `take_over`.

Rules:

- `approve_once` applies only to the exact action preview/hash;
- `allow_for_this_mission` can expand mission authority only inside existing mode and safe invariants;
- it cannot grant black-zone actions;
- it cannot disable trace or stop/revoke controls;
- it must write `user_approved_once`, `user_allowed_for_mission`, `user_denied`, or `user_takeover` trace events.

## 11. Mission Trace Timeline

Mission timeline is the user-facing reconstruction layer.

It is not raw chain-of-thought and not a panic audit log.

It records:

- what Sentinel planned;
- what Sentinel routed;
- what Sentinel executed;
- what Sentinel blocked;
- what Sentinel escalated;
- what user approved or denied;
- what artifacts were created;
- what evidence was used;
- what cost was consumed.

Trace events:

```text
mission_created
mission_started
mission_paused
mission_resumed
mission_stopped
mission_revoked
mission_completed
action_planned
action_routed
action_executed
action_escalated
action_blocked
user_approved_once
user_allowed_for_mission
user_denied
user_takeover
budget_warning
budget_exceeded
rollback_available
rollback_executed
```

Integration with existing trace:

- `TraceLedger` remains the lower-level run trace;
- `MissionTraceTimeline` writes mission-level operational events;
- where useful, mission trace events can also be mirrored as `TraceRecord` rows.

## 12. Budget Controller

Budget must be enforced before runtime expands.

Rules:

- track `cost_used` in `MissionState`;
- estimate each action cost before routing;
- emit `budget_warning` at 80 percent;
- escalate or block when projected cost exceeds limit;
- block at 100 percent unless success criteria already met;
- max_actions is enforced independently from cost.

Effort levels:

- `quick`: short mission, low token budget, minimal debate depth;
- `standard`: default depth;
- `deep`: requires budget preview and explicit mission budget.

Important:

- effort level is not authority level;
- Power Mode does not mean higher model cost;
- Deep effort does not grant more execution authority.

## 13. Kill Switch

Functions:

- pause;
- stop;
- revoke.

Semantics:

| Control | Behavior |
|---|---|
| pause | finish current safe step, then stop queued actions |
| stop | stop queued work immediately and mark mission stopped |
| revoke | invalidate authority envelope and block all future actions |

Rules:

- kill switch cannot be disabled;
- every mission must expose stop/revoke controls;
- all kill switch operations write mission trace events.

## 14. Memory Protocol

Memory is context, never authority.

Allowed memory types:

- user preference;
- project fact;
- run summary;
- evidence outcome;
- approved niche;
- rejected output;
- workflow hint;
- eval failure.

Forbidden memory content:

- API keys;
- passwords;
- tokens;
- approval grants;
- policy overrides;
- hidden prompt instructions;
- executable procedures;
- unverified evidence promoted to fact.

Rules:

- memory cannot pass an evidence gate without source evidence;
- memory cannot update mission authority;
- memory cannot approve actions;
- memory cannot disable firewall, trace, or kill switch.

## 15. Skill Protocol

Skills are supply chain, not trusted code.

In v0, skills are mostly internal, static capability descriptors. No runtime skill install.

Future `SentinelSkillManifest`:

```json
{
  "name": "...",
  "version": "...",
  "owner": "...",
  "description": "...",
  "allowed_actions": [],
  "required_tools": [],
  "input_schema": {},
  "output_schema": {},
  "data_access": [],
  "filesystem_access": [],
  "network_access": [],
  "external_effects": [],
  "secrets_required": [],
  "risk_level": "low|medium|high|critical",
  "dry_run_schema": {},
  "trace_schema": {},
  "eval_suite": [],
  "hash": "sha256..."
}
```

Skill lifecycle:

```text
proposed
-> manifest written
-> static scanned
-> risk classified
-> fake evaluated
-> policy mapped
-> approved for mission scope
-> monitored in trace
```

Skill classifications:

- safe_static_doc;
- draft_only_tool;
- needs_review;
- blocked.

Blocked skill traits in v0:

- shell/process;
- dependency install;
- dynamic loader;
- external send;
- browser submit;
- desktop control;
- credential access;
- broad filesystem access;
- obfuscation/eval/base64 suspicious payload;
- policy mutation;
- prompt instructions that claim authority.

## 16. Security Protocol

### System invariants

These are not user preferences. They are hard rules.

- no shell execution in v0;
- no desktop control in v0;
- no real browser submit in v0;
- no real email/channel send in v0;
- no payment/spend in v0;
- no dependency install in v0;
- no credential access in v0;
- no production code mutation in v0;
- no vendor runtime integration in v0;
- no path traversal outside generated projects;
- no trace disable;
- no kill switch disable;
- no memory-as-policy;
- no unscanned skill execution.

### Data boundaries

Data classes:

- public;
- internal;
- personal;
- secret;
- financial;
- identity.

Default handling:

- public: usable if mission scope allows it;
- internal: trace minimally;
- personal: escalate if external or persistent;
- secret: block storage and execution;
- financial: escalate or block;
- identity: escalate or block.

### Prompt injection handling

Untrusted inputs:

- web pages;
- Reddit posts;
- CueIdea imported text;
- user-uploaded documents from unknown origin;
- future inbound channels;
- future browser DOM;
- future sidecar/screen text.

Rule:

- untrusted content can become evidence only after normalization;
- untrusted content cannot become instructions;
- untrusted content cannot modify mission authority;
- untrusted content cannot grant tools.

## 17. Evidence Protocol

CueIdea is the evidence engine seed, not absolute truth.

Evidence flow:

```text
CueIdea report
-> normalized EvidenceItem
-> direct/adjacent/weak separation
-> WTP preservation
-> competitor gap extraction
-> research enrichment
-> debate
-> decision
-> GTM pack references
```

Rules:

- no WTP means no ready/build verdict;
- adjacent proof cannot masquerade as direct proof;
- noisy evidence is downgraded, not hidden;
- every major pack section cites evidence or says Evidence gap;
- local direct runs without evidence are Sandbox / hypothesis mode.

## 18. GTM Mission Protocol

First production mission type:

```text
Create First Customer / GTM Pack
```

Inputs:

- idea;
- optional CueIdea report;
- optional niche;
- mission mode;
- effort level;
- budget;
- output path.

Outputs:

```text
00_VERDICT.md
01_EVIDENCE.md
02_ICP.md
03_COMPETITOR_GAPS.md
04_LANDING_PAGE_COPY.md
05_OUTREACH_MESSAGES.md
06_INTERVIEW_SCRIPT.md
07_7_DAY_ROADMAP.md
08_WATCHLIST.md
trace.json
mission_timeline.json
```

Success criteria:

- generated folder exists;
- every pack section has evidence refs or Evidence gap;
- outreach is draft-only;
- watchlist exists;
- mission trace exists;
- mission status is completed;
- no micro-approval required for safe local actions.

## 19. UI Architecture

Add mission surfaces after kernel exists:

```text
apps/web/app/dashboard/missions/page.tsx
apps/web/app/dashboard/missions/new/page.tsx
apps/web/app/dashboard/missions/[missionId]/page.tsx
apps/web/app/dashboard/missions/[missionId]/timeline/page.tsx
apps/web/app/dashboard/missions/[missionId]/escalations/page.tsx
```

Core UI components:

- Mission creation flow;
- Authority Preview;
- Mission Control;
- Timeline;
- Escalation card;
- Stop/Revoke controls;
- Budget meter;
- Artifact viewer.

UX language:

- use mission, mandate, scope, actions, limits, timeline, stop, revoke;
- avoid danger-heavy language for safe actions;
- avoid "Full Access" as a global concept.

## 20. API Architecture

Future API routes:

```text
POST /api/missions
GET  /api/missions
GET  /api/missions/{id}
POST /api/missions/{id}/start
POST /api/missions/{id}/pause
POST /api/missions/{id}/stop
POST /api/missions/{id}/revoke
GET  /api/missions/{id}/timeline
GET  /api/missions/{id}/escalations
POST /api/missions/{id}/escalations/{id}/resolve
GET  /api/missions/{id}/artifacts
```

Auth:

- local dev can use `local_user`;
- hosted must require auth;
- every mission query and mutation is user-scoped.

## 21. Storage Architecture

Start with existing repository/in-memory patterns if needed.

Future DB tables:

```text
missions
mission_states
mission_actions
mission_trace_events
mission_escalations
mission_artifacts
mission_budgets
mission_authority_versions
```

Relationship:

- one mission has one active state;
- one mission has many actions;
- one mission has many trace events;
- one mission has many escalations;
- one mission can reference an `agent_run`;
- generated assets remain in `generated_assets` and are linked to mission artifacts.

## 22. Test Architecture

Minimum test files:

```text
services/sentinel-core/tests/test_mission_models.py
services/sentinel-core/tests/test_autonomy_engine.py
services/sentinel-core/tests/test_mission_budget.py
services/sentinel-core/tests/test_mission_kill_switch.py
services/sentinel-core/tests/test_mission_trace_timeline.py
services/sentinel-core/tests/test_escalation_gateway.py
services/sentinel-core/tests/test_safe_mission_executors.py
services/sentinel-core/tests/test_safe_gtm_mission_e2e.py
```

Required tests:

- in-scope reversible action auto-executes;
- out-of-scope action escalates;
- forbidden action blocks;
- expired mission blocks;
- revoked mission blocks;
- stopped mission blocks;
- budget warning at 80 percent;
- budget exceeded escalates or blocks;
- max actions exceeded escalates;
- local GTM mission runs without micro-approval;
- outreach drafts are created but not sent;
- shell blocks even in Power mode;
- browser submit blocks even in Power mode;
- credential access blocks;
- path traversal blocks;
- `allow_for_this_mission` cannot grant black-zone action;
- every auto action writes trace;
- every escalation writes trace;
- every block writes trace;
- mission kill switch stops queued actions.

## 23. Build Order Summary

```text
1. Mission models and enums
2. MissionTraceTimeline
3. MissionBudgetController
4. MissionKillSwitch
5. Deterministic classifiers
6. ScopeChecker
7. AutonomyEngine
8. EscalationGateway
9. SafeMissionExecutors
10. MissionPlanner for GTM
11. MissionRunner end-to-end
12. Tests and eval datasets
13. Mission UI
14. Fake Power harness
15. Future runtime tracks
```

## 24. Non-Negotiable Acceptance

Before any browser, email send, shell, sidecar, or desktop power, Sentinel must prove:

- mission authority works;
- safe local GTM mission completes;
- trace timeline reconstructs the mission;
- black-zone actions are impossible;
- boundary escalation works;
- user can stop/revoke mission authority;
- no vendor code is copied.

## 25. North Star

Sentinel becomes the mission operating system for AI business agents: users delegate bounded outcomes, Sentinel works aggressively inside the mandate, and every boundary crossing is routed, traced, and controlled.
