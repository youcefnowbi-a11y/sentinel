# G12B Implementation Audit

Date: 2026-04-26

## Verdict

G12B is now a mission platform kernel, not only a GTM file generator.

The first implementation pass proved a safe local GTM mission. The audit gate found real GTM coupling in the generic runner and corrected it with a registry-based mission architecture:

```text
MissionAuthorityEnvelope
-> MissionRegistry
-> mission-specific planner / reviewer / success evaluator / artifact schema
-> generic MissionRunner
-> AutonomyEngine
-> SafeMissionExecutors
-> MissionTraceTimeline
```

GTM remains the first commercial mission type, but it is no longer the whole kernel.

## Files Created Or Changed

Generic kernel:

- `sentinel/shared/enums.py`
  - Added `MissionType`, `MissionMode`, `MissionStatus`, `MissionActionRoute`, deterministic classifier enums, escalation options, and mission timeline events.
- `sentinel/mission/models.py`
  - Added `MissionAuthorityEnvelope`, `MissionState`, `MissionAction`, `EscalationRequest`, `MissionTraceEvent`, `MissionPlan`, `MissionPlanStep`, `MissionArtifact`, `MissionArtifactSchema`, `RollbackMetadata`, `ReviewResult`, and `MissionRunResult`.
- `sentinel/mission/protocols.py`
  - Added protocol contracts for planners, executors, reviewers, and success evaluators.
- `sentinel/mission/registry.py`
  - Added `MissionRegistry`, `MissionDefinition`, and default mission registration.
- `sentinel/mission/runner.py`
  - Refactored from GTM-specific runner to generic mission runner.
- `sentinel/mission/trace_timeline.py`
  - Writes `mission_timeline.json`.
- `sentinel/mission/artifacts.py`
  - Writes `mission_artifacts.json` and `artifact_manifest.json`.
- `sentinel/mission/autonomy.py`
  - Routes proposed mission actions.
- `sentinel/mission/risk.py`
  - Scores scope, externality, reversibility, sensitivity, cost, and uncertainty.
- `sentinel/mission/scope_checker.py`
  - Enforces mission scope, allowed tools/actions, path boundaries, and black-zone actions.
- `sentinel/mission/safe_executors.py`
  - Executes safe local actions only under `data/generated_projects`.
- `sentinel/mission/reviewer.py`
  - Generic ReviewerLite with mission artifact schema support.
- `sentinel/mission/success.py`
  - Generic success evaluator with mission artifact schema support.
- `sentinel/mission/budget.py`
  - Enforces budget and action count.
- `sentinel/mission/kill_switch.py`
  - Pause, stop, and revoke.
- `sentinel/mission/escalation.py`
  - Creates mission-boundary escalation requests.

Mission types:

- `sentinel/missions/gtm/`
  - First real mission type.
  - Own planner, reviewer, success evaluator, and artifact schema.
- `sentinel/missions/research_summary/`
  - Minimal non-GTM mission type used to prove kernel extensibility.

Tests:

- `tests/test_mission_kernel.py`
- `tests/test_mission_reviewer.py`
- `tests/test_mission_success.py`

## Classes And Responsibilities

| Component | Responsibility |
| --- | --- |
| `MissionAuthorityEnvelope` | Defines delegated mission authority: objective, scope, allowed tools/actions, paths, budgets, mode, expiry, revocation. |
| `MissionRegistry` | Maps mission type to planner, executor, reviewer, success evaluator, and artifact schema. |
| `MissionRunner` | Generic mission lifecycle: create timeline, execute plan DAG, route actions, write indexes, review, evaluate success. |
| `AutonomyEngine` | Decides action route through `RiskRouter`. |
| `RiskRouter` | Produces `auto_execute`, `log_and_continue`, `escalate`, or `block`. |
| `MissionScopeChecker` | Enforces allowed mission scope and black-zone bans. |
| `SafeMissionExecutors` | Executes only local safe actions; no shell/browser/email send/desktop/payment/credentials. |
| `MissionTraceTimeline` | Records operational timeline and writes `mission_timeline.json`. |
| `MissionArtifactIndex` | Records generated artifacts and rollback metadata. |
| `ReviewerLite` | Checks missing artifacts, missing evidence refs/gaps, generic content, and unresolved escalation. |
| `MissionSuccessEvaluator` | Checks required files, evidence/gap presence, draft-only safety, review status, and critical escalation status. |
| `MissionBudgetController` | Enforces `max_cost_usd`, 80 percent warnings, and `max_actions`. |
| `EscalationGateway` | Produces user-facing boundary escalation payloads and prevents black-zone scope grants. |
| `MissionKillSwitch` | Pauses, stops, or revokes mission authority. |

## Test Coverage

Current mission tests prove:

- Safe GTM mission completes without micro-approval.
- Research summary mission completes through the same generic runner.
- Mission registry rejects unknown mission types.
- Generic runner does not contain GTM artifact filenames.
- DAG dependencies are represented.
- In-scope reversible local actions auto-execute.
- Out-of-scope actions escalate.
- Shell, browser submit, credentials, and payment block even in Power mode.
- Email send escalates or blocks.
- Path traversal outside the mission project folder blocks.
- Expired and revoked missions block.
- Budget and max action boundaries escalate.
- `allow_for_this_mission` cannot grant black-zone actions.
- Every auto/escalate/block route writes trace events.
- ReviewerLite catches missing artifacts and missing evidence references.
- MissionSuccessEvaluator prevents completion if required files are missing or outreach is marked sent.

## What Is Generic

Generic platform primitives:

- Mission authority envelope.
- Mission status lifecycle.
- Plan DAG model.
- Mission registry.
- Planner/reviewer/success/executor protocols.
- Artifact schema model.
- Risk routing.
- Scope checking.
- Path enforcement.
- Budget enforcement.
- Kill switch.
- Escalation payloads.
- Trace timeline.
- Artifact index.
- Rollback metadata.
- Safe local execution boundary.

These can support future Research, Sales, Coding, Browser, Ops, and Self-Improvement agents without changing the runner.

## What Is GTM-Specific

GTM-specific logic now lives under `sentinel/missions/gtm/`:

- GTM artifact names: `00_VERDICT.md`, `05_OUTREACH_MESSAGES.md`, etc.
- GTM plan steps: pack, landing copy, outreach drafts, watchlist, roadmap.
- GTM artifact schema.
- GTM review and success criteria.

The compatibility wrapper `sentinel/mission/planner.py` still exposes `create_gtm_plan()` for earlier G12B tests/imports, but generic execution now uses the registry.

## What Is Still Hardcoded

Known hardcoded v0 areas:

- `SafeMissionExecutors` still contains local templates for GTM outputs.
- `MissionScopeChecker.BLACK_ZONE_ACTIONS` is static.
- Risk scoring is deterministic and rule-based.
- Artifact index uses local JSON files only.
- Rollback is metadata-only, not destructive rollback.
- No persistent DB mission registry exists yet.
- No UI-facing mission registry API exists yet.
- No plugin/skill scanner integration exists yet.

These are acceptable for G12B but must be upgraded before real browser/channel/desktop powers.

## Extensibility Check

| Requirement | Status |
| --- | --- |
| Multiple `MissionType` values | Present: `gtm`, `research_summary`. |
| Mission planner registry | Present via `MissionRegistry`. |
| Mission reviewer registry | Present via `MissionDefinition.reviewer`. |
| Mission success evaluator registry | Present via `MissionDefinition.success_evaluator`. |
| Mission artifact schemas | Present via `MissionArtifactSchema`. |
| Mission executor registry | Present via `MissionDefinition.executor`. |
| Future Research Agent | Supported by mission type pattern; minimal proof exists. |
| Future Sales Agent | Supported, but requires outbound drafts/send gates. |
| Future Coding Agent | Supported structurally, but production mutation remains black-zone. |
| Future Browser Agent | Supported structurally, but submit/login remains black-zone. |
| Future Self-Improvement Agent | Supported structurally, but only proposal/patch/test flow allowed. |

## What Must Be Refactored Before Adding New Agent Powers

Before browser, channel send, desktop, coding, or self-improvement powers:

1. Split executors by capability.
   - Current `SafeMissionExecutors` is good for local file artifacts, not future browser/channel/desktop tools.
2. Add tool manifests.
   - Every tool needs capability declarations, inputs, outputs, side effects, and required policies.
3. Add SkillScanner.
   - No unscanned skill can become a mission executor.
4. Add policy-backed black-zone rules.
   - Static constants should become versioned policy documents and tests.
5. Add trace persistence.
   - JSON timeline is enough for v0; later requires DB-backed trace ledger.
6. Add cost router.
   - Deterministic budget exists, but model/provider routing is not implemented.
7. Add reviewer/fix loop.
   - ReviewerLite currently checks only completion quality, not iterative repair.
8. Add mission UI registry.
   - UI should display mission type, allowed capabilities, impossible actions, and escalation triggers.

## Final Platform Gate Verdict

G12B passes the platform audit after refactor.

Sentinel is not yet a full super agent. It is now a mission operating kernel with one real commercial mission type and one proof mission type. The next layers can add tool surface area without rewriting the core mission lifecycle.
