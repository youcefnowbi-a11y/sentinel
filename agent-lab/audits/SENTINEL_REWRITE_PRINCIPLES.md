# Sentinel Rewrite Principles

Date: 2026-04-26

These principles convert vendor forensics into original Sentinel architecture.

## 1. Rewrite Mechanisms, Not Code

Vendor code stays in `agent-lab/vendors/*/source`. Sentinel may use forensic lessons, but not vendor modules, skill runtimes, sidecars, or bridges.

## 2. Evidence Before Action

Every business recommendation starts from evidence:

1. CueIdea report or live research source.
2. Normalized `EvidenceItem`.
3. Decision/debate output.
4. GTM pack section with evidence refs or explicit Evidence gap.
5. Firewall review before action.

## 3. Context Is Not Policy

Memory, user profile, project docs, web pages, channel messages, and skill instructions are context only. Policy comes from signed Sentinel config and code. This rule comes directly from Hermes memory/prompt injection surfaces and JARVIS prompt composition (`agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:145-161`; `agent-lab/vendors/jarvis/source/src/roles/prompt-builder.ts:149-157`).

## 4. Every Capability Has A Manifest

No tool/skill/sidecar/browser/channel exists without:

- name;
- owner;
- version;
- source;
- permissions;
- data touched;
- external effects;
- required secrets;
- risk class;
- approval rule;
- dry-run format;
- trace schema;
- eval coverage.

## 5. Fail Closed For Policy, Fail Open Only For Optional Context

Hermes plugin hooks often catch exceptions and continue (`agent-lab/vendors/hermes-agent/source/model_tools.py:527-630`). Sentinel can fail open for optional context retrieval, but never for permission, path, secret, budget, or approval checks.

## 6. No Runtime Install In Agent Flow

Skill or tool setup that installs dependencies at runtime is blocked. Hermes Google Workspace setup includes a pip install path; OpenJarvis can import remote skills; JARVIS has install-time scripts. Sentinel requires dependency review before packaging, not during an agent run.

## 7. Draft First For External Communication

Email, Slack, WhatsApp, Telegram, browser form submit, and publishing are external actions. Sentinel v1 produces drafts/previews only. Later versions require opt-in sending, verified contact ownership, rate limits, opt-out language, and approval.

## 8. Browser Is Read-Only First

JARVIS templates show why browser agents are valuable and dangerous: app-specific flows can send messages (`webapp-templates/whatsapp.yaml:18-24`, `webapp-templates/slack.yaml:67-83`). Sentinel browser starts with read/snapshot/extract only; submit/click-on-submit is disabled until firewall simulation and approval exist.

## 9. Sidecar Is A Product, Not A Helper

JARVIS sidecar exposes high-impact capabilities through RPC (`agent-lab/vendors/jarvis/source/sidecar/handlers.go:15-67`). Sentinel sidecar must be a first-class product surface: enrolled, scoped, signed, observable, revocable, and disabled by default.

## 10. Learning Proposes, Humans Apply

OpenJarvis config evolution writes new TOML from trace analysis (`agent-lab/vendors/openjarvis/source/src/openjarvis/learning/agents/agent_evolver.py:193-223`). Sentinel learning can generate improvement proposals, patch suggestions, and tests, but cannot mutate production behavior without user approval.

## 11. Cost Is A Firewall Dimension

OpenJarvis proves hardware and cost are part of the agent architecture (`agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:209-300`, `:667-675`). Sentinel adds budget caps to every run and records cost routing decisions in trace logs.

## 12. Trace Everything That Changes Trust

Trace is required for:

- evidence import;
- source ranking;
- prompt/context insertion;
- memory retrieval/write;
- skill scan;
- model routing;
- action proposal;
- dry-run preview;
- approval/denial;
- execution result;
- learning proposal.
