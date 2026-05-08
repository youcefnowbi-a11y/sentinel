# Sentinel Super Agent Genome

Date: 2026-04-26
Status: initial genome from OpenClaw B2/B3 plus source-only G1-G3 forensic pass.

This file is the design DNA Sentinel should rewrite from first principles. It is not a vendor integration list.

## Core Loop

`see -> verify -> reason -> debate -> plan -> simulate -> approve -> execute -> trace -> learn`

| Gene | Source lesson | Sentinel rewrite |
| --- | --- | --- |
| Evidence-first perception | CueIdea/Sentinel S1 showed reports must normalize into evidence before decisions. | CueIdea evidence is seed context; independent research can enrich but must produce `EvidenceItem` rows. |
| Tool-call loop budget | Hermes `AIAgent.__init__` has `max_iterations`, shared `IterationBudget`, and subagent inheritance (`agent-lab/vendors/hermes-agent/source/run_agent.py:844-946`). | Sentinel uses per-run and per-subagent budgets enforced by Firewall and Trace Ledger. |
| Context/prompt hygiene | Hermes scans project context files for injection patterns before prompt injection (`agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:32-75`). | Sentinel scans every imported prompt/context/evidence text as untrusted input before model context insertion. |
| Authority gate | JARVIS centralizes action approval in `AuthorityEngine.checkAuthority` (`agent-lab/vendors/jarvis/source/src/authority/engine.ts:61-175`). | Sentinel keeps risk levels independent of agent role level: high-impact actions require explicit approval even for high authority. |
| Cost/router awareness | OpenJarvis maps hardware to engine/model tiers and learning metrics include accuracy/latency/cost/efficiency (`agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:209-300`, `:667-675`). | Sentinel CostRouter chooses model by quality target, budget, risk, evidence depth, and expected action value. |
| Permissioned sidecar | JARVIS sidecars declare terminal/filesystem/desktop/browser/clipboard/screenshot capabilities (`agent-lab/vendors/jarvis/source/src/sidecar/types.ts:7-14`). | Sentinel sidecars must be opt-in, capability-scoped, sandbox-profiled, and blocked from silent desktop/browser control in v1. |

## Memory Genome

| Gene | Source lesson | Sentinel rewrite |
| --- | --- | --- |
| Durable preferences | Hermes stores `MEMORY.md`/`USER.md` and injects a frozen snapshot per session (`agent-lab/vendors/hermes-agent/source/run_agent.py:1596-1617`; `agent-lab/vendors/hermes-agent/source/tools/memory_tool.py:105-124`). | Store facts, preferences, and outcomes; never store imperatives as policy. |
| External memory provider plugins | Hermes permits one external memory provider via config and injects provider tool schemas (`agent-lab/vendors/hermes-agent/source/run_agent.py:1621-1704`; `agent-lab/vendors/hermes-agent/source/agent/memory_manager.py:84-145`). | Memory providers require manifest, data boundary, secret filter, prompt-injection scan, and trace of every retrieval/write. |
| Knowledge graph retrieval | JARVIS retrieves entities/facts/relationships by terms, caps profiles, and injects formatted knowledge (`agent-lab/vendors/jarvis/source/src/vault/retrieval.ts:47-149`). | Use structured retrieval with source IDs and confidence; no memory-as-evidence unless provenance is explicit. |

## Skill Genome

| Gene | Source lesson | Sentinel rewrite |
| --- | --- | --- |
| Skill prompt index | Hermes builds a compact skill index with in-process and disk snapshot caches (`agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:621-708`). | Sentinel SkillIndex is generated only from scanned manifests and declares risk class, tools, permissions, tests, and owner. |
| Skill import sources | OpenJarvis can install/sync skills from Hermes/OpenClaw/GitHub and optionally include scripts (`agent-lab/vendors/openjarvis/source/src/openjarvis/cli/skill_cmd.py:162-245`, `:258-349`). | Sentinel blocks unscanned imports; scripts are disabled until static scan, sandbox test, policy mapping, and approval pass. |
| Tool dispatcher hooks | Hermes tool calls pass pre/post/transform plugin hooks (`agent-lab/vendors/hermes-agent/source/model_tools.py:498-630`). | Sentinel tool execution must be mediated by Firewall hooks that fail closed for policy, secrets, and path violations. |

## Runtime Genome

| Gene | Source lesson | Sentinel rewrite |
| --- | --- | --- |
| Browser templates | JARVIS webapp templates encode app-specific browser/desktop instructions and sending flows (`agent-lab/vendors/jarvis/source/webapp-templates/whatsapp.yaml:18-24`; `agent-lab/vendors/jarvis/source/webapp-templates/slack.yaml:67-83`). | Sentinel browser starts read-only; submit/send/publish require dry-run preview and approval. |
| Terminal execution | JARVIS terminal executor spawns shell with user command and timeout (`agent-lab/vendors/jarvis/source/src/actions/terminal/executor.ts:16-67`). | Sentinel v1 blocks shell; future shell requires command AST policy, allowlist, sandbox cwd, secrets redaction, and approval. |
| Sidecar RPC | JARVIS sidecar maps capabilities to RPC handlers including command, filesystem, clipboard, screenshot, desktop, and browser (`agent-lab/vendors/jarvis/source/sidecar/handlers.go:15-67`). | Sentinel sidecar RPC requires signed manifest, least privilege, per-call risk score, audit, and revocation. |

## North Star

Sentinel becomes a proof-backed business operator with agentic runtime powers gated by evidence, policy, simulation, approval, trace, and learning controls.
