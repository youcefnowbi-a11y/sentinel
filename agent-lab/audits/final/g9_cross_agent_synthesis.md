# G9 Cross-Agent Forensic Synthesis

Date: 2026-04-26
Mode: source-only cross-agent synthesis
Scope: OpenClaw, Hermes Agent, OpenJarvis, JARVIS
Decision: compare, extract, rank, and constrain. Do not build yet.

## Guardrails

This document is not a Sentinel runtime build plan.

- No vendor runtime was executed.
- No dependency install was performed.
- No skills, plugins, browsers, sidecars, shells, desktop tools, channels, OAuth flows, or accounts were run.
- No vendor code is approved for Sentinel.
- All mechanisms are rewrite knowledge only.
- Any claim below is either source-backed from the final forensic reports or explicitly marked as a synthesis inference.

Primary evidence files:

- `agent-lab/audits/final/openclaw_final_forensic_report.md`
- `agent-lab/audits/final/hermes_final_forensic_report.md`
- `agent-lab/audits/final/openjarvis_final_forensic_report.md`
- `agent-lab/audits/final/jarvis_final_forensic_report.md`

## 1. NEXUS Verdict

The four agents are not competitors to copy. They are four organs of the future Sentinel organism:

| Vendor | What it really represents | Most important lesson | Sentinel translation |
|---|---|---|---|
| OpenClaw | Multi-surface execution runtime behind a gateway | Runtime power becomes dangerous when plugins, channels, browser, shell, filesystem, and approvals sit too close together | Build a permissioned action kernel, not a vendor bridge |
| Hermes Agent | Persistent memory, skills, hooks, and delegation | A stateless assistant becomes useful when it remembers and delegates, but memory/skills can become hidden policy | Build memory and skills as non-authoritative context |
| OpenJarvis | Budget-aware local/cloud routing and skill import | Intelligence cost, latency, energy, model fit, and trace learning are architecture, not billing afterthoughts | Build a CostRouter and skill quarantine pipeline |
| JARVIS | Daemon plus permissioned sidecar plus desktop awareness | Machine operation is the highest-value and highest-risk agent surface | Treat sidecar/browser/desktop as future products, not helper utilities |

The strict synthesis:

Sentinel must not be "an agent with tools." Sentinel must be an operating control layer where agents can only act through evidence, declared capabilities, risk scoring, simulation, approval, budget caps, and trace.

The creative synthesis:

The winning product is not a clone of OpenClaw, Hermes, OpenJarvis, or JARVIS. It is the thing they all fail to become: a controlled business operator that can eventually touch the world, but only after it proves what it knows, what it plans, what it will change, why it is allowed, what it will cost, and who approved it.

## 2. Evidence Classification

| Class | Meaning | Allowed Use In G9 |
|---|---|---|
| Verified source-only | Confirmed from local vendor source or final report citations | Safe to use for architecture decisions |
| Derived synthesis | Pattern inferred across multiple verified findings | Safe as design direction, not as runtime fact |
| Runtime-unverified | Would require running vendor systems | Must not be used as proof of live behavior |
| Product decision | Sentinel-specific choice based on risk and product strategy | Safe as roadmap constraint, not vendor claim |

Runtime-unverified items remain explicitly unverified for all four vendors. This is intentional. The lab did not run real browsers, sidecars, shells, channels, accounts, OAuth, or vendor daemons.

## 3. Cross-Agent Role Assignment

### 3.1 OpenClaw: Execution Runtime Specimen

Source-backed evidence:

- Final report: `agent-lab/audits/final/openclaw_final_forensic_report.md`.
- Key areas: agent loop, prompt system, skills, plugin system, gateway/control plane, shell/process execution, browser control, channels/messaging, memory, model routing, sub-agents, security helpers.
- Report sections: `openclaw_final_forensic_report.md:111-595` for architecture and algorithms.
- Scanner result: 83 scanned items, 52 blocked, 29 needs review, 2 draft-only, per the final report's B2.5 consolidation.

Core power:

- OpenClaw demonstrates how an agent runtime can connect many execution surfaces through a gateway: plugins, skills, browser, channels, shell, filesystem, model routing, memory, and approval UI.

Core danger:

- The same gateway concentrates blast radius. If plugin or channel input reaches execution, the agent can move from text to real-world mutation.

Sentinel rewrite:

- `SentinelActionKernel`: every tool/channel/browser/plugin call becomes an `AgentAction` with evidence refs, risk level, dry-run, approval status, executor policy, and trace record.

Do not copy:

- Runtime bridge, host install path, unscanned marketplace/plugin loading, always-allow approval semantics, shell-as-general-tool, browser form submission, real outbound channels.

### 3.2 Hermes Agent: Memory and Learning Specimen

Source-backed evidence:

- Final report: `agent-lab/audits/final/hermes_final_forensic_report.md`.
- Key areas: `run_agent.py`, `agent/prompt_builder.py`, `tools/memory_tool.py`, `agent/memory_manager.py`, `agent/memory_provider.py`, `model_tools.py`, plugins, skills, shell hooks, delegation.
- Report sections: `hermes_final_forensic_report.md:89-694` for architecture and algorithms.

Core power:

- Hermes shows how memory, skill prompt indexes, tool hooks, context compression, background learning review, provider fallback, and delegated subagents turn chat into a persistent operator.

Core danger:

- Memory, skills, hooks, plugins, and context providers can become hidden behavior-shaping layers. They can influence future tool use without being visible to the user.

Sentinel rewrite:

- `SentinelMemory + SentinelSkillSpec`: memory can inform but never authorize; skills declare capabilities but never execute directly; hooks observe and enforce policy but cannot silently mutate permission.

Do not copy:

- Autonomous skill execution, runtime dependency install, OAuth setup inside a skill, memory-as-policy, fail-open policy hooks, subagent auto-approval, direct Gmail send/modify in v1.

### 3.3 OpenJarvis: Cost and Routing Specimen

Source-backed evidence:

- Final report: `agent-lab/audits/final/openjarvis_final_forensic_report.md`.
- Key areas: hardware detection, model recommendation, query complexity scoring, heuristic routing, learned routing, loop guard, capability policy, skill import, memory retrieval, cost/savings math, telemetry, benchmarks, sandbox, shell/code/browser/HTTP tools, scanners, audit logging.
- Report sections: `openjarvis_final_forensic_report.md:85-672` for architecture and algorithms.

Core power:

- OpenJarvis treats model selection, local/cloud choice, latency, hardware fit, energy, cost, telemetry, and learned routing as first-class control signals.

Core danger:

- The same system also contains optional high-impact surfaces: shell, code execution, browser, HTTP, channels, skill imports, learned config mutation, and bridge execution. Routing intelligence without hard policy becomes an accelerator for unsafe action.

Sentinel rewrite:

- `SentinelCostRouter`: route by task risk, evidence depth, budget, latency, model capability, context sensitivity, and confidence. Budget is a firewall dimension, not a billing UI.

Do not copy:

- Runtime skill sync, open-by-default capability policy, host shell/code execution, direct WhatsApp send, browser submission, Claude Code bridge execution, auto-written learned configs.

### 3.4 JARVIS: Sidecar and Desktop Awareness Specimen

Source-backed evidence:

- Final report: `agent-lab/audits/final/jarvis_final_forensic_report.md`.
- Key areas: daemon bootstrap, agent loop/tool registry, authority/approval/deferred execution/audit, sidecar enrollment/RPC, terminal/filesystem/clipboard/screenshot/admin handlers, browser CDP, desktop UI, observers, awareness/OCR/struggle scoring, workflows, prompts, vault.
- Report sections: `jarvis_final_forensic_report.md:80-588` for architecture and algorithms.

Core power:

- JARVIS turns an agent into a machine operator. Sidecars can expose terminal, filesystem, browser, desktop, clipboard, screenshot, system info, awareness, workflow triggers, and approval/audit lifecycles.

Core danger:

- This is host-level authority. If prompt injection, memory poisoning, weak approval, token leakage, or sidecar misconfiguration reaches these surfaces, the impact is the user's machine and accounts.

Sentinel rewrite:

- `SentinelPermissionedSidecar + ScreenContextSanitizer + FirewallDeferredExecutor`: sidecar is deny-by-default, scoped, signed, observable, revocable, and every host action needs preview, approval, and trace.

Do not copy:

- Default all-capability sidecar config, raw shell handlers, path blocklists, arbitrary browser evaluate, browser submit/send, desktop keystroke execution, prompt-only tool bans, heartbeat execution, real-message app templates.

## 4. Comparative Scoreboard

| Vendor | Usefulness as lab specimen | Rewrite readiness | Runtime risk if integrated | Product relevance now | Product relevance later | Verdict |
|---|---:|---:|---:|---:|---:|---|
| OpenClaw | 8/10 | 6/10 | Critical | High for scanner/action kernel | High for gateway/channel patterns | Study deeply; never bridge now |
| Hermes | 8/10 | 7/10 | High | High for memory/skills/debate | High for learning/subagents | Rewrite memory and skills under policy |
| OpenJarvis | 8/10 | 7/10 | High to Critical | Medium-high for CostRouter | High for local/cloud/runtime efficiency | Build cost routing before runtime power |
| JARVIS | 9/10 | 7/10 | Critical | Medium for approval model | Very high for sidecar/desktop | Sidecar later, firewall first |

Ranking by immediate Sentinel value:

1. OpenClaw scanner/action-kernel lessons.
2. Hermes memory/skill/delegation lessons.
3. OpenJarvis cost/router/budget lessons.
4. JARVIS approval/sidecar lessons.

Ranking by danger if copied:

1. JARVIS sidecar/desktop/browser/clipboard/screenshot.
2. OpenClaw plugin/channel/browser/shell runtime.
3. OpenJarvis skill import plus execution/bridge surfaces.
4. Hermes memory/skill/plugin/hook mutation.

Ranking by future moat:

1. JARVIS-like PermissionedSidecar under Sentinel policy.
2. OpenClaw-like SkillScanner and ActionKernel.
3. OpenJarvis-like CostRouter and benchmark telemetry.
4. Hermes-like Memory/SkillSpec/delegation with non-authoritative memory.

## 5. Cross-Agent Anatomy

| Agent Body Part | OpenClaw | Hermes | OpenJarvis | JARVIS | Sentinel Genome |
|---|---|---|---|---|---|
| See | Browser, channels, external content | Context providers, memory files | Search, tools, telemetry | Screen, clipboard, windows, browser, sidecar events | Perception is untrusted evidence |
| Remember | Memory and hybrid search | Durable memory and skill index | Memory backends and retrieval | Vault, observations, goals | Memory is context, never policy |
| Reason | Agent loop and prompts | Agent loop, compression, provider fallback | Query complexity and routing | Role prompts, awareness analysis | Reasoning must cite evidence and risk |
| Delegate | Sub-agents | Subagents with budgets | Tool/agent scoring | Role-based subagents | Delegation proposes, not executes |
| Route | Model fallback/cost | Provider fallback/cache | Hardware/local/cloud/cost router | Sidecar target routing | Router includes budget and permission |
| Execute | Plugins, shell, browser, channels | Tools, hooks, skills | Shell/code/browser/sandbox/channels | Sidecar, desktop, browser, workflows | Execution only after firewall approval |
| Approve | Approval UI pattern | Approval/hardline concepts | Capability policy and scanner | Approval/deferred execution/audit | Approval is evidence-rich and traceable |
| Learn | Memory/routing | Learning review and skills | Trace-driven config learning | Goals/workflows/awareness suggestions | Learning proposes patches; humans apply |

## 6. Superpower Extraction Matrix

| Primitive | Best Vendor Evidence | Mechanism | Why It Matters | Failure Mode | Sentinel Rewrite | Priority |
|---|---|---|---|---|---|---|
| Gateway action kernel | OpenClaw, `openclaw_final_forensic_report.md:286-323` | Centralizes runtime/tool/channel routing | Makes agents operational | Centralized blast radius | `SentinelActionKernel` with action object, policy, preview, approval | Now |
| Skill scanner | OpenClaw, scanner consolidation in final report | Static classification of plugin/skill risk | Turns agentic risk into product feature | False negatives, stale reports | Deterministic scanner with canonical JSON/Markdown/hash | Now |
| Approval queue | JARVIS, `jarvis_final_forensic_report.md:155-205` | Pending/approved/denied/executed lifecycle | Creates human control point | Approval lacks proof/risk preview | `ApprovalGate` with dry-run, evidence, risk, approval actor | Now |
| Trace ledger | JARVIS audit, OpenClaw scanner, OpenJarvis telemetry | Log action/decision/tool/cost | Reconstructs why an agent acted | Incomplete trace | Trace everything that changes trust | Now |
| Persistent memory | Hermes, `hermes_final_forensic_report.md:223-333` | Memory providers and retrieval | User does not repeat context | Memory poisoning | Typed memory with source/trust/freshness/sensitivity | Now |
| Skill manifest | Hermes/OpenJarvis/OpenClaw | Skills as reusable procedures | Reuse workflows | Supply chain and prompt injection | Manifest + scan + sandbox test + policy mapping | Now |
| Cost router | OpenJarvis, `openjarvis_final_forensic_report.md:115-245` | Hardware/model/query/cost routing | Prevents spend and latency blowups | Wrong routing, weak model | Budget-aware router with trace and caps | Next |
| Query complexity scoring | OpenJarvis | Task complexity as explainable signal | Routes depth and model | Can be gamed or wrong | Explainable depth selector + eval | Next |
| Context compression | Hermes | Compress long sessions | Keeps long tasks alive | Lost constraints | Evidence-preserving compression | Next |
| Sidecar manifest | JARVIS, `jarvis_final_forensic_report.md:205-285` | Device declares capabilities | Allows remote/local machine control | Capability overreach | Deny-by-default signed sidecar manifest | Later |
| Screen awareness | JARVIS | OCR, window, clipboard, struggle detection | Agent can help from user context | Privacy leakage and prompt injection | ScreenContextSanitizer and opt-in app scopes | Later |
| Browser operator | OpenClaw/JARVIS | CDP and app templates | Operates web apps | Form submit/external send | Read-only browser first; submit later with approval | Later |
| Workflow triggers | JARVIS/OpenJarvis | Cron/webhook/poll/screen triggers | Automates repeated tasks | Trigger-to-action abuse | WorkflowFirewall with static and runtime policy | Later |
| Learning from traces | Hermes/OpenJarvis/JARVIS | Reviews, config evolution, suggestions | Improves over time | Unsafe self-modification | ImprovementProposal only, manual application | Later |

## 7. Failure Convergence Index

These failures repeat across vendors. Repetition is the signal.

| Failure | Vendors | Root Cause | Sentinel Rule |
|---|---|---|---|
| Prompt injection | All | Untrusted context enters prompts near tools | Context is data, never authority |
| Memory poisoning | Hermes, JARVIS, OpenJarvis | Past state shapes future behavior invisibly | Memory is typed, trusted, sourced, and non-policy |
| Malicious skill/plugin | OpenClaw, Hermes, OpenJarvis | Reusable instructions/code can alter behavior | Every skill has manifest, scan, sandbox, eval |
| Shell abuse | OpenClaw, OpenJarvis, JARVIS, Hermes hooks | Raw host command execution | Shell blocked in v1 |
| Filesystem escape | OpenClaw, OpenJarvis, JARVIS | Broad read/write paths | Workspace allowlists and canonical path proof |
| Browser submit | OpenClaw, JARVIS, OpenJarvis | Browser tools can click/type/submit | Browser read-only first; submit high-risk |
| External send | All | Channels, browser apps, email/API integrations | Draft-first, approval, compliance, opt-out |
| Credential leakage | All | Env vars, browser profiles, screen, clipboard, OAuth | Secret scanner, redaction, no real accounts in lab |
| Sidecar overreach | JARVIS, partially OpenClaw runtime sidecars | Machine control exposed through RPC | Sidecar is product surface, not helper |
| Runtime install | OpenClaw, Hermes, OpenJarvis, JARVIS scripts | Agent/runtime setup can execute dependency code | No runtime install in agent flow |
| Dynamic loading | OpenClaw, Hermes, OpenJarvis | Plugins/skills/hooks loaded at runtime | Loader must be manifest-locked and scanned |
| Cost explosion | OpenJarvis, Hermes, JARVIS awareness | Long prompts, repeated calls, cloud vision | CostRouter and hard budget caps |
| Unsafe self-improvement | Hermes, OpenJarvis, JARVIS workflows | Agent learns/mutates behavior from traces | Learning proposes, humans apply |
| Policy fragmentation | JARVIS, OpenClaw, Hermes | Prompt rules, roles, config, hooks disagree | One firewall source of truth |
| Trace gaps | All | Logs exist but not full evidence/action chain | Trace every trust-changing event |

## 8. Strict Design Rulings

### Ruling 1: Execution Is Not The Product Until The Firewall Is The Product

Contested pattern:

- OpenClaw and JARVIS prove users want agents that act.
- All four reports prove action without proof and policy creates unacceptable blast radius.

G9 ruling:

- Sentinel v1 execution remains local safe file/draft generation only.
- Browser submit, email send, shell, desktop, sidecar, channel outbound, and code mutation remain blocked.

Design consequence:

- Every future executor must first exist as a scanner rule, fake benchmark, dry-run schema, approval policy, and trace schema.

### Ruling 2: Memory Must Never Become Authority

Contested pattern:

- Hermes proves memory is essential.
- Hermes/JARVIS/OpenJarvis prove memory can poison future behavior.

G9 ruling:

- Sentinel Memory stores facts, preferences, project context, outcomes, and user feedback.
- Sentinel Memory cannot set policy, grant permission, install tools, override evidence, or approve actions.

Design consequence:

- Any memory injected into a prompt must carry source, trust level, freshness, sensitivity, and "not policy" marking.

### Ruling 3: Cost Is A Safety Boundary

Contested pattern:

- OpenJarvis treats cost as routing.
- Other agents treat cost as incidental or partial.

G9 ruling:

- Sentinel budget is a firewall dimension. A run can be blocked for budget risk just like it can be blocked for permission risk.

Design consequence:

- Every run has budget cap, model route decision, expected token/API spend, fallback behavior, and trace record.

### Ruling 4: Sidecar Is A Separate Product Track

Contested pattern:

- JARVIS makes sidecar obvious and powerful.
- JARVIS also shows sidecar is the most dangerous surface.

G9 ruling:

- Sentinel sidecar is not part of GTM Operator v1.
- It becomes a later AgentOps Firewall product surface after fake benchmarks, manifest policy, screen sanitizer, and approval UI are mature.

Design consequence:

- G10 can specify sidecar, but implementation must remain later.

### Ruling 5: Browser Automation Begins As Evidence Collection

Contested pattern:

- OpenClaw/JARVIS browser tools unlock web apps.
- Browser tools can send, submit, purchase, publish, and leak.

G9 ruling:

- Sentinel browser begins as read-only source collection and screenshot/DOM extraction.
- Write actions are separate high/critical actions.

Design consequence:

- No `browser_submit_form`, no "press enter to send", no app-template send flows in v1.

### Ruling 6: Skills Are Supply Chain, Not Convenience

Contested pattern:

- OpenClaw/Hermes/OpenJarvis show skills make agents powerful.
- The same skill systems create prompt, dependency, network, binary, secret, and execution risk.

G9 ruling:

- Sentinel skill import is blocked unless scanner, manifest, sandbox tests, permission policy, dry-run, approval, and trace exist.

Design consequence:

- `SentinelSkillScanner` becomes a product differentiator, not a developer utility.

### Ruling 7: Learning Produces Proposals, Not Mutations

Contested pattern:

- Hermes/OpenJarvis/JARVIS show learning loops and suggestions.
- Runtime self-mutation is too dangerous.

G9 ruling:

- Sentinel learning can produce evidence-backed improvement proposals and patch suggestions.
- It cannot change production behavior, tools, prompts, policies, or code automatically.

Design consequence:

- Every learning output is an `ImprovementProposal` with risk, tests, and manual approval.

## 9. Sentinel Super Agent Genome

This is a genome, not an implementation plan. G10 may convert it into specs.

### Gene 01: Evidence Authority

Purpose:

- The agent cannot claim strategic certainty without evidence.

Inputs:

- CueIdea reports, independent research sources, user-provided materials, generated evidence items.

Rules:

- Every claim maps to evidence or an explicit evidence gap.
- WTP evidence gates build/ready verdicts.
- Direct proof and adjacent proof remain separate.

Derived from:

- Sentinel product context plus vendor failure: all vendor agents can act without business proof.

### Gene 02: Capability Manifest

Purpose:

- No capability exists without a declaration.

Required fields:

- name, version, owner, source, input schema, output schema, data touched, external effects, secrets required, network domains, filesystem roots, risk class, dry-run schema, approval rule, trace schema, eval suite.

Derived from:

- OpenClaw skills/plugins, OpenJarvis skill import, JARVIS sidecar capabilities, Hermes skills.

### Gene 03: Firewall Kernel

Purpose:

- Convert every possible execution into a governed action.

Required pipeline:

- propose -> classify -> score risk -> simulate -> preview -> approve/deny -> execute -> trace -> learn.

Derived from:

- OpenClaw gateway/approvals, JARVIS authority/approval/deferred execution, OpenJarvis capability policy, Hermes tool hooks.

### Gene 04: Memory Without Authority

Purpose:

- Preserve user/project continuity without hidden behavior mutation.

Allowed memory:

- facts, preferences, project context, decisions, outcomes, feedback.

Forbidden memory:

- policy overrides, permission grants, hidden instructions, secrets, executable procedures, "always do X" directives without user-visible preference object.

Derived from:

- Hermes memory and skill index; JARVIS vault/awareness.

### Gene 05: Cost-Aware Reasoning

Purpose:

- Spend intelligence only where it changes decision quality.

Routing dimensions:

- risk, evidence gap, task depth, confidence, latency, budget, model capability, privacy level, expected output value.

Derived from:

- OpenJarvis cost/model routing and Hermes provider fallback.

### Gene 06: Skill Quarantine

Purpose:

- Let Sentinel learn from skills without trusting them.

Pipeline:

- import source -> hash -> parse manifest -> static scan -> dependency scan -> prompt injection scan -> fake runtime eval -> policy mapping -> user approval -> draft-only first run.

Derived from:

- OpenClaw plugin ecosystem, Hermes skill prompt index, OpenJarvis skill import.

### Gene 07: Read-Only Browser First

Purpose:

- Use the browser as an evidence collector before using it as an actuator.

Allowed first:

- navigate to public page, read/snapshot/extract, capture citations, rank sources.

Blocked first:

- submit, send, post, publish, purchase, upload, delete, install, account changes.

Derived from:

- OpenClaw and JARVIS browser/tool/template risks.

### Gene 08: Permissioned Sidecar Later

Purpose:

- Real machine control becomes possible only after sidecar security is a product.

Minimum sidecar requirements:

- deny-by-default, capability manifest, user enrollment, token expiry, revocation, scoped filesystem roots, no raw shell, screen redaction, clipboard opt-in, visible action preview, trace viewer.

Derived from:

- JARVIS sidecar and desktop awareness.

### Gene 09: Learning As Proposal

Purpose:

- Improve safely without autonomous mutation.

Output:

- problem observed, evidence, proposal, affected files/policies/prompts, risk, tests, rollback plan, user approval status.

Derived from:

- Hermes learning review, OpenJarvis config evolution, JARVIS workflow auto-suggest.

### Gene 10: Trace As Product Memory

Purpose:

- Sentinel should know why it did something and prove it.

Trace must cover:

- input, evidence, model route, prompt/context blocks, memory used, decision, risk score, dry-run, approval, action, output, cost, errors, user feedback.

Derived from:

- OpenClaw scanner reports, JARVIS audit trail, OpenJarvis telemetry, Hermes hook metrics.

## 10. G10 Architecture Constraints

G10 may design architecture, but it must obey these constraints:

1. Do not implement vendor runtime bridges.
2. Do not add shell execution.
3. Do not add browser submit or account automation.
4. Do not add real email/channel send.
5. Do not add sidecar runtime.
6. Do not add desktop automation.
7. Do not auto-modify production code.
8. Do not make memory authoritative.
9. Do not import unscanned skills.
10. Do not let cost routing mutate policy.

G10 should produce specs, not dangerous runtime power:

- `SENTINEL_SUPER_AGENT_BLUEPRINT.md`
- `SENTINEL_AGENT_LOOP_SPEC.md`
- `SENTINEL_MEMORY_SPEC.md`
- `SENTINEL_SKILL_SPEC.md`
- `SENTINEL_COST_ROUTER_SPEC.md`
- `SENTINEL_SIDECAR_SPEC.md`
- `SENTINEL_BROWSER_SPEC.md`
- `SENTINEL_CHANNEL_SPEC.md`
- `SENTINEL_EVAL_ROADMAP.md`

## 11. What Sentinel Should Build First

This is still not a code build command. It is the priority order G10 should encode.

### Now

- CueIdea-backed evidence import and GTM pack quality.
- Trace Ledger completeness.
- AgentOps Firewall v0.
- SkillScanner v0 using OpenClaw lessons.
- SafeActionKernel for local files and drafts only.
- CostRouter Lite for model/run budget caps.
- Memory v0 with trust labels and no authority.

### Next

- Research upgrade with source ranking, WTP extraction, competitor gaps, evidence gaps.
- Debate engine with skeptical challenge and build gates.
- Gated skill manifest and fake benchmark framework.
- Approval inbox with dry-run previews.
- Trace viewer.

### Later

- Read-only browser research sandbox.
- Channel inbound adapters as untrusted input.
- PermissionedSidecar design and fake-only sidecar benchmarks.
- Workflow proposals, not workflow execution.
- Local/cloud routing with telemetry.

### Avoid Until Explicitly Approved

- Vendor bridges.
- Real channel sending.
- Browser submit.
- Shell/code execution.
- Desktop control.
- Runtime skill install.
- Sidecar host control.
- Production self-mutation.

## 12. Final Cross-Agent Verdict

OpenClaw teaches Sentinel how agents become powerful execution runtimes.

Hermes teaches Sentinel how agents become persistent and skillful.

OpenJarvis teaches Sentinel how agents become economically intelligent.

JARVIS teaches Sentinel how agents become machine operators.

The synthesis is strict:

- OpenClaw without Sentinel becomes too much runtime power.
- Hermes without Sentinel becomes hidden memory/prompt authority.
- OpenJarvis without Sentinel becomes cost-efficient access to unsafe tools.
- JARVIS without Sentinel becomes host-level control with insufficient proof boundaries.

The Sentinel answer:

- Power must be decomposed into declared capabilities.
- Capabilities must be scored before use.
- Risk must be simulated before action.
- Users must approve high-impact steps.
- Every step must be traced.
- Learning must propose, not mutate.
- Evidence must drive business decisions.

North star:

Sentinel becomes the agent control layer that turns raw autonomous power into proof-backed, budget-aware, permissioned business operation.
