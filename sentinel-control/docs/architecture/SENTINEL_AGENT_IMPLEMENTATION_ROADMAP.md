# Sentinel Agent Implementation Roadmap

Date: 2026-04-26
Status: pre-code roadmap
Scope: from Mission Authority Kernel v0 to future runtime power

## 0. Rule For This Roadmap

Do not start by building browser, shell, desktop, sidecar, or email send.

Start by building the kernel that will control those powers later.

The proof of G12B is simple:

```text
User delegates a GTM mission.
Sentinel executes all safe local work automatically.
No micro-approval.
No real risky runtime.
Everything traced.
```

## 1. Phase G12A - Architecture Lock

Status: current document set.

Goal:

- create a complete implementation map before writing agent code.

Deliverables:

- `docs/architecture/SENTINEL_AGENT_MASTER_ARCHITECTURE.md`
- `docs/architecture/SENTINEL_AGENT_IMPLEMENTATION_ROADMAP.md`
- Agent Lab G12 specs remain as research/source-of-truth inputs.

Acceptance:

- code map exists;
- model map exists;
- security protocol exists;
- skill protocol exists;
- mission lifecycle exists;
- test plan exists;
- no runtime power is enabled.

## 2. Phase G12B - Mission Authority Kernel v0

Goal:

- implement mission-level authority in `sentinel-core`.

Files to create:

```text
services/sentinel-core/sentinel/mission/__init__.py
services/sentinel-core/sentinel/mission/authority.py
services/sentinel-core/sentinel/mission/scope_checker.py
services/sentinel-core/sentinel/mission/classifiers.py
services/sentinel-core/sentinel/mission/risk.py
services/sentinel-core/sentinel/mission/budget.py
services/sentinel-core/sentinel/mission/kill_switch.py
services/sentinel-core/sentinel/mission/trace_timeline.py
services/sentinel-core/sentinel/mission/escalation.py
services/sentinel-core/sentinel/mission/planner.py
services/sentinel-core/sentinel/mission/runner.py
services/sentinel-core/sentinel/mission/safe_executors.py
```

Files to update:

```text
services/sentinel-core/sentinel/shared/enums.py
services/sentinel-core/sentinel/shared/models.py
services/sentinel-core/sentinel/learning/trace_ledger.py
services/sentinel-core/sentinel/execution/action_runner.py
```

Tests:

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

Implementation order:

1. Add enums.
2. Add mission models.
3. Add MissionTraceTimeline.
4. Add MissionBudgetController.
5. Add MissionKillSwitch.
6. Add classifiers.
7. Add ScopeChecker.
8. Add AutonomyEngine.
9. Add EscalationGateway.
10. Add SafeMissionExecutors.
11. Add MissionPlanner.
12. Add MissionRunner.
13. Add e2e safe GTM mission test.

Acceptance:

- safe GTM mission runs end-to-end without micro-approval;
- folder and markdown files are created under generated projects only;
- outreach drafts are created but not sent;
- watchlist is created;
- trace timeline exists;
- mission reaches completed status;
- black-zone actions block even in Power mode;
- every route writes trace.

## 3. Phase G13 - Mission UI

Goal:

- make mission authority visible and usable.

Pages:

```text
apps/web/app/dashboard/missions/page.tsx
apps/web/app/dashboard/missions/new/page.tsx
apps/web/app/dashboard/missions/[missionId]/page.tsx
apps/web/app/dashboard/missions/[missionId]/timeline/page.tsx
apps/web/app/dashboard/missions/[missionId]/escalations/page.tsx
```

Components:

```text
MissionModeCards
MissionEffortSelector
MissionScopeBuilder
AuthorityPreview
MissionControlHeader
MissionTimeline
EscalationCard
BudgetMeter
StopRevokeControls
ArtifactList
```

UX requirements:

- mission first, not chat first;
- autonomy mode separate from effort level;
- show what Sentinel will do without asking;
- show what Sentinel will still ask for;
- show what Sentinel cannot do;
- stop/revoke always visible;
- timeline shows operational facts, not hidden reasoning.

Acceptance:

- user can create a local GTM mission from UI;
- user can view mission status and timeline;
- user can stop/revoke mission;
- escalation UI exists even if most v0 missions do not need it.

## 4. Phase G14 - Fake Power Harness

Goal:

- test future Power Mode authority without real risky execution.

Fake fixtures:

```text
fake_browser_submit.json
fake_email_send.json
fake_channel_send.json
fake_shell_command.json
fake_desktop_click.json
fake_payment.json
fake_dependency_install.json
fake_credential_access.json
fake_path_traversal.json
fake_memory_policy_override.json
```

Harness:

```text
packages/evals/datasets/mission_power_fake_cases.jsonl
services/sentinel-core/tests/test_fake_power_harness.py
```

Acceptance:

- in-scope fake low-risk actions can route green;
- out-of-scope fake actions escalate or block;
- black-zone fake actions block;
- `allow_for_this_mission` cannot grant black-zone;
- all fake cases write trace.

## 5. Phase G15 - Read-Only Browser Sandbox

Goal:

- collect public evidence through a controlled browser/read-only web layer.

Allowed:

- public page fetch;
- public extraction;
- citations;
- screenshots later if sanitized;
- no logged-in profile.

Blocked:

- submit;
- send;
- upload;
- login;
- password managers;
- arbitrary page JS;
- real account mutation.

Acceptance:

- browser research is evidence-only;
- DOM/text is untrusted;
- prompt injection fixtures are detected;
- extracted claims map to EvidenceItem;
- no form submission exists.

## 6. Phase G16 - Controlled Outbound Draft To Send

Goal:

- move from draft-only to tightly controlled send for approved contacts later.

Prerequisites:

- mission authority v0;
- compliance policy;
- opt-out policy;
- contact ownership proof;
- rate limits;
- DLP checks;
- fake channel send benchmarks;
- approval and trace UI.

Initial send scope:

- approved contacts only;
- approved domain/list only;
- single or small batch;
- no spam mode;
- no fake personalization.

Acceptance:

- all sends are tied to a mission;
- user can see recipients, message, source, opt-out, and evidence;
- send is traceable;
- rate limit exists;
- deny/revoke stops send queue.

## 7. Phase G17 - Sidecar Lab

Goal:

- study host/desktop authority without real host control.

Start with:

- fake sidecar RPC;
- sidecar manifest;
- scope model;
- protected app list;
- screen/context sanitizer fixtures;
- permission prompts;
- stop/revoke.

Blocked:

- real desktop click/type;
- clipboard read/write;
- screenshot capture;
- shell;
- OS-level app control;
- credentials.

Acceptance:

- sidecar authority can be modeled without real control;
- protected apps block;
- sanitizer requirements exist;
- all fake RPC actions trace.

## 8. Phase G18 - Skill Scanner Productization

Goal:

- turn Agent Lab scanner knowledge into Sentinel SkillScanner v0.

Inputs:

- `SentinelSkillManifest`;
- local skill files;
- plugin metadata;
- prompt/instruction blocks.

Outputs:

- deterministic JSON report;
- Markdown report generated from JSON;
- hash;
- risk classification;
- required policies;
- required evals;
- promotion blockers.

Acceptance:

- shell/install/secrets/external send/browser submit/desktop control are flagged;
- safe static docs are distinguished from tools;
- draft-only tools are distinguished from runtime executors;
- no skill can enter mission scope without scan result.

## 9. Phase G19 - Cost Router And Reviewer

Goal:

- make mission autonomy cost-aware and quality-reviewed.

Build:

- CostRouter Lite;
- reviewer agent contract;
- budget-per-mission;
- budget-per-subtask;
- quality review for GTM packs;
- evidence review before ready/build.

Acceptance:

- mission shows budget before launch;
- budget warning emits timeline event;
- budget exhaustion stops or escalates;
- reviewer can flag weak evidence or mission drift;
- GTM pack cannot mark ready with missing WTP.

## 10. Phase G20 - Private Staging

Goal:

- prepare hosted/private testers only after kernel and UI are reliable.

Requirements:

- `SENTINEL_REQUIRE_AUTH=true`;
- user-scoped missions;
- user-scoped runs;
- server-side service-role keys only;
- Supabase RLS review if used;
- trace retention policy;
- deletion/export controls.

Acceptance:

- no cross-user mission reads;
- no unauthenticated mutation routes;
- staging has auth and scoped storage;
- logs do not store secrets.

## 11. Build Dependencies

```text
Mission models
  -> Autonomy Engine
  -> SafeMissionExecutors
  -> MissionRunner
  -> Mission UI
  -> Fake Power Harness
  -> Browser/Channel/Sidecar tracks
```

Never reverse this order.

## 12. Definition Of Done For G12B

G12B is done only when:

- all mission models exist;
- safe GTM mission e2e test passes;
- local generated project folder is created;
- pack files are created;
- outreach drafts exist but are not sent;
- watchlist exists;
- mission trace timeline exists;
- stop/revoke behavior is tested;
- black-zone actions block in all modes;
- path traversal is blocked;
- no vendor code is copied;
- no risky runtime is enabled.

## 13. North Star

The next implementation should make Sentinel feel like an operator, not a permission form: give it a bounded GTM mission, and it should produce the complete local operating package while tracing every step and escalating only at the boundary.
