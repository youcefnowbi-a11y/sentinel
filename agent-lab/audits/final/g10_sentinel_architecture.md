# G10 Sentinel Super Agent Architecture

Date: 2026-04-26
Mode: architecture/specification only
Status: no runtime implementation authorized

## 0. G10 Boundary

G10 converts G9 into Sentinel architecture. It does not implement runtime power.

Blocked in G10:

- vendor runtime bridges;
- shell execution;
- browser submit;
- real email/channel send;
- sidecar runtime;
- desktop automation;
- runtime skill install;
- production code auto-mutation;
- memory-as-policy;
- unscanned skill import.

Allowed in G10:

- architecture specs;
- schemas;
- state machines;
- policy contracts;
- fake-only eval roadmap;
- safe implementation order;
- strict acceptance criteria for future work.

## 1. NEXUS Final Architecture Verdict

Sentinel is a proof-backed business operator and AgentOps firewall.

It has two product faces:

1. Sentinel GTM Operator:
   - turns CueIdea evidence and independent research into a validated GTM pack;
   - generates ICP, positioning, competitor gaps, outreach drafts, landing copy, interviews, roadmap, and watchlist;
   - never pretends weak evidence is strong.

2. Sentinel Control:
   - governs every agent action through manifest, risk score, simulation, approval, trace, and budget;
   - turns future browser, sidecar, channel, workflow, and skill power into permissioned capability rather than raw autonomy.

The core loop:

```text
see -> verify -> research -> debate -> decide -> plan -> simulate -> approve -> execute_safe -> trace -> learn
```

The four vendor lessons become four Sentinel organs:

| Vendor Lesson | Sentinel Organ | G10 Decision |
|---|---|---|
| OpenClaw gateway/runtime | Action Kernel + Skill Scanner | Build scanner and action contracts before runtime power |
| Hermes memory/skills/delegation | Memory + SkillSpec + Debate Agents | Memory informs, skills propose, subagents reason |
| OpenJarvis cost/local-cloud routing | CostRouter | Budget is a firewall dimension |
| JARVIS sidecar/desktop awareness | PermissionedSidecar + ScreenContextSanitizer | Future product track, disabled until fake benchmarks pass |

## 2. Operating Constitution

These laws are implementation constraints, not suggestions.

1. Evidence before decision.
   - Every recommendation cites evidence or declares an evidence gap.

2. Policy before tool.
   - No executor exists without a policy entry, dry-run schema, trace schema, and eval.

3. Simulation before approval.
   - The user approves a preview, not a vague intent.

4. Approval before impact.
   - Medium, high, and critical actions require explicit approval.

5. Trace before trust.
   - Every trust-changing event writes a trace record.

6. Memory is context, never authority.
   - Memory cannot grant permission, override policy, install tools, or pass evidence gates without source references.

7. Skills are supply chain.
   - Every skill has manifest, scan, risk class, fake eval, and version hash before use.

8. Cost is safety.
   - Budget exhaustion stops the run or downgrades output, never creates fake certainty.

9. External communication is draft-first.
   - No v1 email/channel/browser send.

10. Learning proposes; humans apply.
    - No automatic policy, prompt, code, tool, or production mutation.

## 3. System Map

```text
User / CueIdea Report / Research Input
        |
        v
Perception Gateway
        |
        v
Evidence Ledger <---- Memory Context Compiler
        |
        v
Research Enrichment
        |
        v
Debate Engine
        |
        v
Decision Planner
        |
        v
Action Kernel
        |
        v
Firewall
  | risk scorer
  | policy engine
  | dry-run simulator
  | approval gate
  | budget gate
        |
        v
Safe Executors v1
  | generated project files
  | markdown docs
  | JSON exports
  | outreach drafts
  | watchlists
        |
        v
Trace Ledger
        |
        v
Learning Proposals
```

Future disabled tracks:

```text
BrowserSandbox -> read-only first -> submit disabled
ChannelAdapters -> inbound untrusted -> outbound draft-only
PermissionedSidecar -> fake-only benchmark first -> no host control now
WorkflowEngine -> proposals only -> no autonomous execution now
```

## 4. Core Data Contracts

### 4.1 EvidenceItem

```json
{
  "id": "ev_...",
  "run_id": "run_...",
  "source": "cueidea|research|user|generated",
  "source_ref": "...",
  "url": null,
  "quote": null,
  "summary": "...",
  "evidence_type": "pain|wtp|competitor_gap|competitor_complaint|trend|pricing|community_signal|direct_proof|adjacent_proof",
  "proof_class": "direct|adjacent|weak|unknown",
  "confidence": 0.0,
  "freshness_score": 0.0,
  "relevance_score": 0.0,
  "sensitivity": "public|user_private|secret_suspected",
  "created_at": "..."
}
```

Invariant:

- `wtp` requires explicit paid intent, pricing, budget, purchase, or willingness-to-pay signal. Absence of WTP is not WTP.

### 4.2 DecisionPlan

```json
{
  "id": "plan_...",
  "run_id": "run_...",
  "goal": "...",
  "mode": "evidence_backed|sandbox_hypothesis",
  "verdict": "build|pivot|niche_down|kill|research_more|needs_revision",
  "confidence": 0.0,
  "risk_score": 0.0,
  "evidence_refs": [],
  "evidence_gaps": [],
  "reasoning_summary": "...",
  "proposed_actions": []
}
```

Invariant:

- `build` or `ready` cannot occur when WTP is missing or evidence is mostly adjacent.

### 4.3 AgentAction

```json
{
  "id": "act_...",
  "run_id": "run_...",
  "tool": "create_file",
  "intent": "...",
  "input": {},
  "expected_output": "...",
  "risk_level": "low|medium|high|critical",
  "requires_approval": true,
  "v1_allowed": false,
  "evidence_refs": [],
  "dry_run_id": null,
  "policy_version": "..."
}
```

Invariant:

- Unknown action is blocked.
- Every action is stored before execution.

### 4.4 DryRun

```json
{
  "id": "dry_...",
  "action_id": "act_...",
  "risk_level": "medium",
  "why_needed": "...",
  "evidence_used": [],
  "resource_scope": {},
  "preview": {},
  "blocked_reasons": [],
  "requires_approval": true,
  "expires_at": "..."
}
```

Invariant:

- Approval is tied to a dry-run hash. If preview changes, approval expires.

### 4.5 TraceRecord

```json
{
  "id": "trace_...",
  "run_id": "run_...",
  "event_type": "evidence_import|research|debate|decision|action_proposed|dry_run|approval|execution|cost_route|memory_read|memory_write|eval",
  "payload": {},
  "policy_version": "...",
  "cost_usd": 0.0,
  "created_at": "..."
}
```

Invariant:

- Any trust-changing event emits a trace.

## 5. Module Specifications

### 5.1 Perception Gateway

Purpose:

- Accept ideas, CueIdea reports, user constraints, uploaded docs, and later read-only browser research.

Outputs:

- `ContextBundle` with source labels and sensitivity labels.

Rules:

- User text is trusted for intent, not for policy.
- External text is untrusted.
- Scraped/browser/channel/screen text is untrusted.
- No direct action can be emitted by perception.

### 5.2 Evidence Ledger

Purpose:

- Normalize all market proof into queryable, citeable evidence rows.

Core jobs:

- CueIdea import.
- Direct vs adjacent separation.
- WTP preservation.
- Competitor gap extraction.
- Evidence gap visibility.

Failure to avoid:

- Treating "people complain" as "people will pay."

### 5.3 Research Enrichment

Purpose:

- Convert evidence into business context.

Outputs:

- competitors;
- alternatives;
- ICP segments;
- communities;
- objections;
- buying triggers;
- pricing hints;
- evidence gaps;
- recommended research questions.

Rules:

- If no specific community exists, output `unknown`, not "founders."
- If no competitor gap exists, output `Evidence gap`.

### 5.4 Debate Engine

Agents:

- SIGNAL: market timing, trend, competitor movement.
- AXIOM: evidence quality, scoring, invalidation, expected value.
- CIPHER: feasibility, execution constraints, technical risks.
- NOVA: positioning, offer, GTM creative.
- FORGE: transformation, wedge, category design.
- SKEPTIC: attacks assumptions and weak evidence.
- NEXUS: final verdict.

Rules:

- At least one skeptical challenge per run.
- No build verdict without WTP.
- No ready status without specific ICP and competitor alternative/gap.
- Every recommendation cites evidence refs or declares gap.

### 5.5 Action Kernel

Purpose:

- Turn decisions into proposed actions, never direct execution.

Allowed v1 actions:

- `create_project_folder`;
- `create_markdown_file`;
- `export_json`;
- `prepare_email_draft`;
- `create_watchlist`.

Blocked v1 actions:

- `send_email`;
- `browser_submit_form`;
- `run_shell_command`;
- `modify_code`;
- `desktop_click`;
- `desktop_type`;
- `sidecar_rpc`;
- `spend_money`;
- `publish_content`;
- `install_dependency`.

### 5.6 Firewall

Submodules:

- PolicyEngine.
- RiskScorer.
- BudgetGate.
- DryRunSimulator.
- ApprovalGate.
- ExecutionGuard.
- TraceEmitter.

Risk levels:

- low: local non-sensitive generation inside allowed directory.
- medium: draft communication, memory write, watchlist update, data export.
- high: external account, browser action, sensitive data access, outbound communication.
- critical: shell, code mutation, desktop control, sidecar, payment, delete, install, credential use.

Invariant:

- High/critical actions cannot execute in v1.

### 5.7 Safe Executors v1

Allowed write boundary:

- `sentinel-control/data/generated_projects` only, unless a future policy expands it.

Executors:

- FileExecutor.
- GtmPackExporter.
- EmailDraftExecutor.
- WatchlistExporter.
- TraceExporter.

Rules:

- No network side effects.
- No browser side effects.
- No shell.
- No code modification.
- No production mutation.

### 5.8 Learning Layer

Inputs:

- user feedback;
- approved/rejected outputs;
- pack quality scores;
- run outcomes;
- eval failures;
- evidence gaps.

Outputs:

- `ImprovementProposal`.

Forbidden:

- modifying code;
- modifying prompts;
- modifying policies;
- installing tools;
- enabling skills;
- changing budget caps.

## 6. G10 Build Order

G10 does not build code, but it defines implementation order.

### Track A: Product Core

1. CueIdea import contract.
2. Evidence Ledger.
3. Research Enrichment.
4. Debate Engine.
5. GTM Pack Generator.
6. GTM Quality Evaluator.

### Track B: Control Core

1. Trace Ledger.
2. Action Kernel.
3. Firewall PolicyEngine.
4. RiskScorer.
5. DryRunSimulator.
6. ApprovalGate.
7. SafeExecutors.

### Track C: AgentOps Moat

1. SkillScanner.
2. CostRouter Lite.
3. Memory v0.
4. Trace Viewer.
5. Approval Inbox.
6. Plugin Risk Review UI.

### Track D: Future Runtime Power

Only after fake benchmarks and product quality are strong:

1. Read-only browser sandbox.
2. Inbound channels as untrusted input.
3. Workflow proposals.
4. Permissioned sidecar fake runtime.
5. Desktop awareness with sanitizer.

## 7. G10 Acceptance Criteria

G10 is complete when these docs exist:

- `SENTINEL_SUPER_AGENT_BLUEPRINT.md`
- `SENTINEL_AGENT_LOOP_SPEC.md`
- `SENTINEL_MEMORY_SPEC.md`
- `SENTINEL_SKILL_SPEC.md`
- `SENTINEL_COST_ROUTER_SPEC.md`
- `SENTINEL_SIDECAR_SPEC.md`
- `SENTINEL_BROWSER_SPEC.md`
- `SENTINEL_CHANNEL_SPEC.md`
- `SENTINEL_EVAL_ROADMAP.md`
- `audits/final/g10_sentinel_architecture.md`

No acceptance criterion allows dangerous execution.

## 8. Final G10 Verdict

Sentinel's superpower is controlled agency.

The agent can become powerful only if every power is represented as a declared, scoped, budgeted, simulated, approved, traced capability.

The architecture is intentionally slower than a raw agent runtime. That is the product advantage: the user gets business action without blind autonomy.
