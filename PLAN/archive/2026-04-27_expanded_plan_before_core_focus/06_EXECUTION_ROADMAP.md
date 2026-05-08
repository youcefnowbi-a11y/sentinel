# 06 Execution Roadmap

Date: 2026-04-26

## Roadmap Doctrine

Do not finish a reduced agent and then rewrite it radically.

Build capability tracks under the correct architecture from the start.

## Phase P0: Plan Gate

Status: current.

Deliverables:

- `PLAN/` folder;
- current state audit;
- super agent architecture;
- capability matrix;
- tool intelligence design;
- work method library;
- agent family map;
- security protocol;
- research backlog;
- plan gate.

Exit criteria:

- user accepts that implementation can resume;
- next phase is chosen explicitly;
- no hidden assumption that GTM is the full product.

## Phase P1A: Agent Core Runtime Skeleton

Goal:

Create the actual Sentinel agent loop before adding more tools.

Why:

The previous roadmap correctly identified the need for capabilities, but a tool registry without an agent runtime is only a catalog. The agent must first know how to:

- initialize from a mission;
- build context;
- orient around the problem;
- select methods;
- express needed capabilities;
- select or report missing tools;
- create a plan through the mission registry;
- coordinate workers;
- route actions through mission authority;
- review artifacts;
- evaluate success;
- propose learning.

Deliverables:

- `sentinel/agent/identity.py`
- `sentinel/agent/models.py`
- `sentinel/agent/event_bus.py`
- `sentinel/agent/state.py`
- `sentinel/agent/context_builder.py`
- `sentinel/agent/cognitive_cycle.py`
- `sentinel/agent/method_selector.py`
- `sentinel/agent/tool_selector.py`
- `sentinel/agent/planner_bridge.py`
- `sentinel/agent/worker_coordinator.py`
- `sentinel/agent/supervisor.py`
- `sentinel/agent/review_loop.py`
- `sentinel/agent/learning_loop.py`
- `sentinel/agent/runtime.py`

Tests:

- agent initializes from mission envelope;
- agent builds context;
- agent selects methods;
- agent reports needed capabilities;
- agent creates mission plan through registry;
- agent routes actions through Mission OS;
- agent completes safe GTM mission through runtime;
- agent reports missing tools without hallucination;
- agent cannot let memory or tool output expand authority.

No live browser/email/shell/sidecar.

## Phase P1B: Capability Manifest And Tool Registry

Goal:

Create the first platform layer for future powers.

Deliverables:

- `sentinel/capabilities/`
- `CapabilityManifest`
- `ToolRegistry`
- `ToolRiskClass`
- `ToolAuthType`
- `ToolSideEffect`
- `CapabilityPolicy`
- static test catalog fixtures;
- registry UI stub or JSON export;
- tests proving unknown tools cannot execute.

No live browser/email/shell/sidecar.

## Phase P1C: Tool Selection Through Agent Runtime

Goal:

Connect `ToolSelector` to the new `ToolRegistry` so tools are selected by the agent runtime, not by mission-specific shortcuts.

Deliverables:

- tool selection decision trace;
- missing capability report;
- blocked tool report;
- safe fake tool routed through mission authority;
- tests that unknown tools do not enter worker execution.

## Phase P2: API Cartographer And Fake Tool Bench

Goal:

Make Sentinel able to discover and classify tools without executing risky calls.

Deliverables:

- importer for public API catalog fixture;
- normalized API candidate model;
- fake ToolBench;
- deterministic tool score;
- mission-to-tool compiler v0;
- tests for auth, cost, freshness, risk, replacement tools.

Allowed:

- no-auth metadata import;
- static catalog fixtures.

Forbidden:

- leaked keys;
- paid calls;
- user account APIs;
- external mutation.

## Phase P3: Work Method Registry

Goal:

Make the agent choose how to think before choosing tools.

Deliverables:

- method registry;
- evidence ladder implementation;
- contradiction mining v0;
- premortem v0;
- ROI tree v0;
- method trace events;
- reviewer checks for missing contradiction pass.

## Phase P4: Launch Agent Upgrade

Goal:

Upgrade GTM into Launch Agent.

Deliverables:

- brand narrative module;
- brand kit artifact schema;
- visual direction artifact;
- image prompt assets;
- landing asset plan;
- pitch deck outline;
- launch social asset plan;
- reviewer checks for brand/asset completeness.

No real image generation yet unless routed through approved image capability.

## Phase P5: Vision/OCR Pack

Goal:

Give Sentinel eyes.

Deliverables:

- OCR capability manifest;
- image text extraction;
- screenshot artifact schema;
- PDF text extraction;
- vision result confidence;
- evidence mapping from OCR;
- tests with fixture images/PDFs.

Risk controls:

- local files only at first;
- no private screen capture;
- trace source file and extracted text confidence.

## Phase P6: Image Creation Pack

Goal:

Generate and edit visual launch assets safely.

Deliverables:

- image generation manifest;
- image edit manifest;
- brand style constraints;
- prompt trace;
- asset provenance;
- reviewer for brand consistency;
- generated media artifact index.

Risk controls:

- no impersonation;
- no unapproved public posting;
- no hidden copyrighted-source claims;
- user preview.

## Phase P7: Read-Only Browser Sandbox

Goal:

Give Sentinel public web vision.

Deliverables:

- browser sandbox profile;
- no login;
- no submit;
- no form write;
- source extractor;
- citation ledger;
- prompt injection detector;
- screenshot capture;
- browser trace.

## Phase P8: Deep Research Agent

Goal:

Turn browser/data/API tools into structured verification.

Deliverables:

- source ranker;
- competitor mapper;
- pricing extractor;
- review/community signal extractor;
- contradiction miner integration;
- evidence verifier;
- research report artifact.

## Phase P9: Code Intelligence Agent

Goal:

Give Sentinel code understanding without production mutation.

Deliverables:

- repo map;
- function/class extraction;
- dependency scan;
- architecture report;
- test plan generator;
- patch proposal only;
- diff artifact;
- no auto-apply unless explicit approval.

## Phase P10: Controlled Outbound

Goal:

Move from drafts to controlled sending.

Deliverables:

- contact provenance model;
- campaign authority envelope;
- approval preview;
- opt-out policy;
- rate limiter;
- send ledger;
- reputation kill switch.

## Phase P11: Video/Audio Media Pack

Goal:

Create and transform richer media.

Deliverables:

- transcription;
- frame extraction;
- subtitle generation;
- video summary;
- video storyboard;
- video generation/editing manifest;
- media reviewer.

## Phase P12: Cost Router And Reviewer Loop

Goal:

Separate effort level from authority and improve output quality.

Deliverables:

- model/provider routing;
- task complexity scoring;
- budget-aware effort selection;
- reviewer/fix loop;
- quality/cost trace;
- downgrade path when budget is low.

## Phase P13: Memory And Learning

Goal:

Make Sentinel persistent without memory becoming authority.

Deliverables:

- project memory;
- preference memory;
- outcome memory;
- memory trust score;
- memory poisoning guard;
- learning proposal generator;
- no automatic policy/code mutation.

## Phase P14: Skill Scanner Productization

Goal:

Turn agent skill risk into a product capability.

Deliverables:

- skill manifest scanner;
- dependency scan;
- dynamic loading scan;
- network/filesystem/shell scan;
- prompt injection scan;
- canonical JSON/Markdown output;
- hash and reproducibility;
- UI risk review.

## Phase P15: Fake Sidecar Lab

Goal:

Prepare desktop power without touching host authority.

Deliverables:

- fake sidecar RPC;
- sidecar manifest;
- screenshot sanitizer fixture;
- clipboard sanitizer fixture;
- protected app policy;
- stop/revoke controls;
- no real desktop execution.

## Phase P16: Permissioned Sidecar

Goal:

Only after fake sidecar passes.

Deliverables:

- signed sidecar manifest;
- per-app permissions;
- screen context sanitizer;
- clipboard policy;
- visible control surface;
- revocation;
- full audit.

## Phase P17: Autonomous Recurring Missions

Goal:

Allow recurring bounded missions.

Deliverables:

- schedule authority envelope;
- recurrence limits;
- budget caps;
- escalation summaries;
- weekly mission review;
- drift detector.

## Phase P18: Super Agent Integration

Goal:

Integrate agents into a coherent mission operating system.

Deliverables:

- Launch Agent;
- Research Agent;
- Brand Agent;
- Media Agent;
- Code Agent;
- Sales Agent;
- Tool Scout Agent;
- Sidecar Agent;
- cross-agent mission orchestration;
- unified trace and artifact UI.

## 72-Hour Next Move After Plan Gate

If this PLAN is accepted:

1. Freeze implementation branch state with a short audit note.
2. Implement P1A Agent Core Runtime Skeleton.
3. Then implement P1B Capability Manifest and Tool Registry.
