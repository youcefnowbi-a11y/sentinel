# 01 Super Agent Master Architecture

Date: 2026-04-26
Status: target architecture, no direct runtime authorization

## 1. Product Identity

Sentinel is not:

- a chatbot;
- a raw desktop agent;
- an OpenClaw clone;
- a JARVIS clone;
- a plugin marketplace;
- a GTM document generator only.

Sentinel is:

```text
Mission OS + Agent Foundry + Tool Intelligence + Capability Governance
```

Its first market wedge remains launch/GTM, because that creates visible business value. But the architecture must support much more than GTM.

## 2. Core Loop

```text
mission intake
-> authority envelope
-> context and evidence builder
-> mission-to-method compiler
-> mission-to-tool compiler
-> plan DAG
-> worker execution
-> reviewer loop
-> boundary router
-> safe execution / escalation / block
-> trace timeline
-> success evaluator
-> learning proposal
```

Short form:

```text
Think -> See -> Verify -> Plan -> Create -> Act -> Review -> Launch -> Learn
```

## 3. Layered System

```text
Sentinel Super Agent
|
|-- 01 Mission OS
|   |-- MissionAuthorityEnvelope
|   |-- MissionRegistry
|   |-- MissionRunner
|   |-- MissionPlanDAG
|   |-- AutonomyEngine
|   |-- ScopeChecker
|   |-- RiskRouter
|   |-- BudgetController
|   |-- EscalationGateway
|   |-- KillSwitch
|   |-- TraceTimeline
|
|-- 02 Agent Foundry
|   |-- mission type registry
|   |-- planner registry
|   |-- reviewer registry
|   |-- success evaluator registry
|   |-- artifact schema registry
|   |-- executor registry
|
|-- 03 Capability Matrix
|   |-- thinking
|   |-- research
|   |-- browser
|   |-- vision/OCR
|   |-- media/image/video/audio
|   |-- code intelligence
|   |-- brand/launch
|   |-- outbound channels
|   |-- sidecar/desktop
|   |-- data/API tools
|
|-- 04 Tool Intelligence Layer
|   |-- ToolRegistry
|   |-- CapabilityManifest
|   |-- APICartographer
|   |-- ToolBench
|   |-- ToolGraph
|   |-- MissionToToolCompiler
|   |-- SkillScanner
|
|-- 05 Work Method Library
|   |-- OODA
|   |-- red team / blue team
|   |-- Bayesian update
|   |-- premortem
|   |-- contradiction mining
|   |-- causal map
|   |-- ROI tree
|   |-- evidence ladder
|   |-- opportunity arbitrage
|
|-- 06 Evidence and Knowledge
|   |-- CueIdea bridge
|   |-- evidence ledger
|   |-- source ranker
|   |-- contradiction miner
|   |-- verifier
|   |-- world model notes
|
|-- 07 Creation and Launch Studio
|   |-- copy generation
|   |-- brand kit generation
|   |-- image generation/editing
|   |-- video generation/editing
|   |-- landing assets
|   |-- deck/export generation
|
|-- 08 Memory and Learning
|   |-- mission memory
|   |-- project memory
|   |-- preference memory
|   |-- outcome memory
|   |-- no memory-as-authority
|   |-- improvement proposals
|
|-- 09 Security and Governance
|   |-- policies
|   |-- safe outreach
|   |-- secret filtering
|   |-- path boundaries
|   |-- network/domain boundaries
|   |-- prompt injection detection
|   |-- rollback/containment
```

## 4. Mission Authority

The user delegates a mission, not micro-actions.

Every mission has:

- objective;
- success criteria;
- mode;
- allowed systems;
- allowed tools;
- allowed actions;
- forbidden actions;
- allowed paths;
- allowed domains;
- allowed accounts;
- max duration;
- max actions;
- max cost;
- risk appetite;
- escalation triggers;
- rollback preference;
- trace level;
- emergency stop.

The agent acts inside the envelope. It escalates only at the boundary.

## 5. Capability Surface Principle

Every superpower is a capability pack.

A capability pack must contain:

- capability manifest;
- inputs/outputs;
- side effects;
- risk classes;
- policy mapping;
- fake benchmark;
- executor boundary;
- review rule;
- trace schema;
- rollback/containment rule;
- UI preview.

Examples:

- `browser_readonly`
- `browser_submit_controlled`
- `ocr_image_text`
- `image_generate`
- `image_edit`
- `video_generate`
- `video_edit`
- `repo_read`
- `patch_proposal`
- `email_draft`
- `email_send_controlled`
- `sidecar_screenshot`
- `sidecar_clipboard_read`
- `desktop_action_controlled`

## 6. Knowledge Substrate

The user is correct: a strong agent must understand the world deeply enough to choose methods, not just call tools.

Sentinel needs a world-model substrate:

| Domain | Why It Matters |
| --- | --- |
| Internet architecture | URLs, DNS, HTTP, APIs, auth, scraping limits, rate limits, browser state |
| Computer architecture | filesystems, processes, memory, OS permissions, shells, sandboxing |
| Electronics/hardware | sensors, devices, buses, cameras, audio, local compute, energy/latency tradeoffs |
| LLM architecture | context, tokens, hallucination, tool calls, routing, evals, prompt injection |
| Media systems | image/video/audio formats, OCR, compression, metadata, editing pipelines |
| Business systems | GTM, sales, pricing, markets, evidence, buyer psychology |
| Security systems | secrets, supply chain, permissions, identity, escalation, audit |

This does not mean stuffing encyclopedia content into prompts. It means encoding operating methods, tool schemas, and reviewer checks that reflect how these systems actually work.

## 7. Vendor Lessons Integrated

| Vendor | Keep As Lesson | Rewrite As Sentinel |
| --- | --- | --- |
| OpenClaw | Many execution surfaces can be coordinated through a runtime gateway | Capability registry plus mission router, not vendor bridge |
| Hermes | Memory, delegation, and skills make an agent persistent | Memory as context, delegation as plan nodes, skills as scanned manifests |
| OpenJarvis | Routing should optimize cost, latency, local/cloud fit | CostRouter with budget, quality, sensitivity, and fallback |
| JARVIS | Sidecar/desktop gives high user value | PermissionedSidecar with sanitizer, explicit scope, trace, and revocation |

## 8. Final Shape

The final Sentinel should feel like:

```text
A business/creative/technical operator that can accept a mission,
build its own safe toolchain,
use methods instead of vibes,
create real launch assets,
inspect code and media,
research across sources,
and act only inside an auditable mandate.
```
