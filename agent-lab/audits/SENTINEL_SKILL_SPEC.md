# Sentinel Skill Spec

Date: 2026-04-26
Status: G10 architecture spec

## Principle

Skills are supply chain.

A skill is never trusted because it is useful. It is trusted only after manifest declaration, scan, classification, fake eval, policy mapping, and approval.

## Skill Manifest

```json
{
  "id": "skill_...",
  "name": "...",
  "version": "...",
  "source": {
    "type": "local|github|vendor|generated",
    "url": null,
    "commit": null,
    "path": "..."
  },
  "owner": "sentinel|user|vendor",
  "description": "...",
  "instructions_path": "SKILL.md",
  "required_tools": [],
  "required_secrets": [],
  "filesystem": {
    "read_roots": [],
    "write_roots": []
  },
  "network": {
    "domains": [],
    "methods": []
  },
  "external_effects": [],
  "install_commands": [],
  "runtime_commands": [],
  "risk_level": "low|medium|high|critical",
  "approval_required": true,
  "dry_run_schema": {},
  "trace_schema": {},
  "tests": [],
  "scanner_report_id": "scan_..."
}
```

## Classification

| Class | Meaning | Runtime Status |
|---|---|---|
| `safe_static_doc` | docs, examples, templates only | may inform prompts |
| `draft_only_tool` | generates local drafts/assets only | may propose safe actions |
| `needs_review` | reads web/API/files or uses untrusted context | cannot run until reviewed |
| `blocked` | shell, install, browser submit, external send, secrets, broad filesystem, code mutation | blocked |

## Promotion Flow

```text
source candidate
-> hash source
-> parse manifest
-> static scan
-> dependency scan
-> prompt injection scan
-> permission extraction
-> risk classification
-> fake eval
-> user review
-> SkillIndexCompiler
```

## Scanner Findings

Scanner must detect:

- shell/process calls;
- runtime install commands;
- dynamic imports/loaders;
- network/API calls;
- browser submit/click/type flows;
- external message/send/publish flows;
- env secret references;
- filesystem reads/writes;
- code mutation;
- prompt injection text;
- hidden/unicode instructions;
- obfuscation/base64/eval;
- vendor runtime coupling.

## Runtime Rules

- Skill text cannot execute.
- Skill can only propose structured `AgentAction`.
- Executor can only run after Firewall approval.
- A skill cannot change policy, memory authority, budget caps, or approval state.
- Skill index version is traced on every run.

## Required Evals

- Malicious prompt-only skill blocked.
- Runtime install skill blocked.
- External send skill becomes draft-only or blocked.
- Missing manifest field blocks promotion.
- Skill cannot change policy.
- Skill cannot request shell in v1.
- Skill scanner report is deterministic and hashable.
