# Hermes Skill Map

Date: 2026-04-26

## Skill Indexing

Source: `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:621-708`.

Mechanism:

- Scans local skills and external skill directories.
- Builds a compact skill index for the system prompt.
- Caches in-process and to disk snapshot.
- Filters by platform, disabled list, available tools/toolsets, and skill conditions.

Risk:

- Skill metadata enters prompt context.
- External directories are included in index.
- Snapshot can hide drift unless hashed and invalidated strictly.

Sentinel rewrite:

- `SkillIndex` is derived from `SkillScanReport`.
- Every skill has `risk_level`, `required_tools`, `required_secrets`, `external_effects`, `tests`, and `policy_id`.

## Skill Invocation Message

Source: `agent-lab/vendors/hermes-agent/source/agent/skill_commands.py:112-212`.

Mechanism:

- Loads skill payload.
- Applies template substitution.
- Optionally expands inline shell.
- Injects absolute skill directory.
- Lists supporting files and says they can be loaded or scripts can be run directly by absolute path.

Risk:

- A skill can become an execution instruction source.

Sentinel rewrite:

- Skill instructions are docs only.
- Any script/file/browser/email action must be converted into an `AgentAction`, dry-run, and approval request.

## Google Workspace Skill

Source: `agent-lab/vendors/hermes-agent/source/skills/productivity/google-workspace/scripts/setup.py:45-120`.

Mechanism:

- Scopes include Gmail read/send/modify, Calendar, Drive read, Contacts read, Sheets, and Docs read.
- Stores token/client-secret/pending auth JSON under Hermes home.
- Can install dependencies via pip if missing.

Risk:

- OAuth scopes include external-send and account data access.
- Runtime dependency installation is a supply-chain risk.
- Token storage and refresh behavior need independent security review.

Sentinel rewrite:

- No Google Workspace runtime in v1.
- Future Google integration is draft-only first.
- OAuth scopes must be least privilege and feature-specific.
- No runtime pip/npm install from an agent action.

## Delegation Skill Surface

Source: `agent-lab/vendors/hermes-agent/source/tools/delegate_tool.py:55-107`, `agent-lab/vendors/hermes-agent/source/run_agent.py:4706-4737`.

Mechanism:

- Subagents run in worker threads.
- Dangerous command approval defaults to auto-deny unless `delegation.subagent_auto_approve=true`.
- Recursive delegation is excluded from subagent tools.
- Excess `delegate_task` calls are capped by max concurrent children.

Risk:

- Opt-in auto-approve creates a high-risk mode.
- Subagents can multiply cost and tool calls.

Sentinel rewrite:

- Delegation is a first-class trace tree.
- Subagents inherit lower or equal permissions.
- Subagent work cannot execute external side effects without parent/user approval.

## Classification

| Mechanism | Classification | Reason |
| --- | --- | --- |
| Static skill markdown | `needs_review` | Prompt injection risk even without scripts |
| Skill scripts | `blocked` | Execution path until scanner/sandbox exist |
| Google Workspace setup | `blocked` | OAuth, pip install, Gmail send/modify scopes |
| Skill index cache | `needs_review` | Prompt-surface caching |
| Delegation | `needs_review` | Cost/tool amplification |

## Eval Requirements

- Skill with inline shell is blocked.
- Skill with OAuth scope is blocked until integration manifest exists.
- Skill with supporting scripts cannot run by prompt instruction.
- Subagent cannot request shell/email/browser-send without approval.
