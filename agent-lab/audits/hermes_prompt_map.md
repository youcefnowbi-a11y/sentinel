# Hermes Prompt Map

Date: 2026-04-26

## Prompt Assembly Sources

| Prompt surface | Source | Purpose | Risk | Sentinel rewrite |
| --- | --- | --- | --- | --- |
| Project context files | `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:1045-1085` | Load `.hermes.md`, `HERMES.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, and SOUL.md into prompt | Local files can contain hostile instructions | Trust-labeled project context; never policy |
| Context scanner | `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:32-75` | Block known injection patterns before prompt injection | Pattern-only scanner | Multi-layer context quarantine |
| Memory guidance | `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:145-161` | Tells agent how to write durable memory | Memory entries can become quasi-instructions | Enforce memory schema and no imperative policy |
| Session search guidance | `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:164-168` | Encourages retrieval of past context | Past context may be stale | Require freshness and provenance labels |
| Skill maintenance guidance | `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:170-177` | Encourages saving and patching skills | Self-modifying procedural behavior | Improvements require proposal and approval |
| Tool-use enforcement | `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:179-190` | Pushes agent to take tool actions instead of promising | Can increase unsafe execution pressure | Sentinel separates plan/proposal from execution |
| Skill index prompt | `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:621-708` | Summarizes available skills | Untrusted skill metadata can influence behavior | Only scanned skill summaries enter prompt |
| Skill command payload | `agent-lab/vendors/hermes-agent/source/agent/skill_commands.py:112-212` | Builds skill activation message with content, config, paths, supporting files | Skill can point to scripts and runtime actions | Skill becomes structured manifest plus safe docs |

## Priority Model Observed

Hermes relies on system prompt assembly to steer behavior. The project context block says loaded project context files "should be followed" (`agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:1084`). This is powerful for local agent productivity but risky when the files are untrusted or malicious.

Sentinel rewrite:

- Prompt compiler must tag each block:
  - `trusted_policy`
  - `trusted_product_spec`
  - `user_context`
  - `external_evidence`
  - `untrusted_vendor_or_web`
  - `memory_context`
- Only `trusted_policy` can influence permissions.

## Prompt Injection Surfaces

| Surface | Why it matters | Required Sentinel eval |
| --- | --- | --- |
| Project instruction files | Automatically discovered and loaded | Malicious `AGENTS.md` fixture |
| Skill markdown | Indexed and invoked through prompt | Malicious skill instruction fixture |
| Memory | Injected every turn or retrieved | Memory-as-policy fixture |
| Provider memory blocks | External provider output can be merged | External memory injection fixture |
| Tool result transform hooks | Tool output can be transformed before model sees it | Raw-vs-transformed trace eval |

## Sentinel Prompt Compiler Requirements

1. Every prompt block records source path/URL, trust level, scanner result, and content hash.
2. Untrusted blocks are wrapped with explicit "data only" delimiters.
3. Evidence blocks must reference `EvidenceItem.id`.
4. Skill instructions must not contain imperative permission changes.
5. Memory blocks cannot include "always", "never", "ignore", "system", or hidden directives without review.
6. Prompt compiler emits a `PromptTraceRecord` before model call.
