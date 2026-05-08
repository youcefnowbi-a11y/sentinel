# Hermes Agent Static Forensic Audit

Date: 2026-04-26
Mode: source-only, no install, no runtime.

## Source Inventory

| Field | Value |
| --- | --- |
| Repository | `https://github.com/nousresearch/hermes-agent` |
| Local source | `agent-lab/vendors/hermes-agent/source` |
| Commit | `35c57cc46b88710a98c4d43107b87b4ab828e3eb` |
| Clone size | 2,585 files / 67,523,148 bytes |
| Runtime | Python >= 3.11 package with gateway, plugins, skills, CLI, optional web/RL/messaging extras |
| Dependency manager | `pyproject.toml` with setuptools |
| Entrypoints | `hermes = hermes_cli.main:main`, `hermes-agent = run_agent:main`, `hermes-acp = acp_adapter.entry:main` (`agent-lab/vendors/hermes-agent/source/pyproject.toml`) |
| Install/runtime status | Not installed, not run |

## Entrypoints And Packages

- `run_agent.py` contains the primary `AIAgent` class, iteration budget, memory setup, tool calling, prompt caching, fallback/retry behavior, and delegation dispatch (`agent-lab/vendors/hermes-agent/source/run_agent.py:844-946`, `:1596-1704`, `:2638-2708`).
- `model_tools.py` is the tool dispatcher and hook surface (`agent-lab/vendors/hermes-agent/source/model_tools.py:498-630`).
- `agent/prompt_builder.py` builds system prompt components, context-file insertion, skill index, and prompt-injection checks (`agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:32-75`, `:621-708`, `:1045-1085`).
- `agent/memory_manager.py` orchestrates built-in and external memory providers, with only one external provider at a time (`agent-lab/vendors/hermes-agent/source/agent/memory_manager.py:84-145`).
- `tools/memory_tool.py` is the built-in durable memory store and includes threat pattern checks (`agent-lab/vendors/hermes-agent/source/tools/memory_tool.py:73-124`).
- `tools/delegate_tool.py` contains subagent delegation safety defaults and auto-approve/auto-deny behavior (`agent-lab/vendors/hermes-agent/source/tools/delegate_tool.py:55-107`).

## High-Risk Optional Surfaces

- Messaging extras include Telegram, Discord, Slack, Matrix, SMS, and other channel packages in `pyproject.toml`.
- Google Workspace skill setup declares Gmail send/modify, Calendar, Drive, Contacts, Sheets, and Docs scopes (`agent-lab/vendors/hermes-agent/source/skills/productivity/google-workspace/scripts/setup.py:45-56`).
- Google Workspace setup can install dependencies via `subprocess.check_call([sys.executable, "-m", "pip", "install", ...])` (`agent-lab/vendors/hermes-agent/source/skills/productivity/google-workspace/scripts/setup.py:95-120`).
- Skill commands can expand inline shell snippets when enabled by config (`agent-lab/vendors/hermes-agent/source/agent/skill_commands.py:125-133`).
- Skill messages instruct the agent to run bundled scripts by absolute path with terminal tools (`agent-lab/vendors/hermes-agent/source/agent/skill_commands.py:137-202`).

## Core Architecture

| Subsystem | Purpose | Source paths | Inputs | Outputs | Side effects | Sentinel rewrite |
| --- | --- | --- | --- | --- | --- | --- |
| Agent loop | Convert user task into LLM/tool loop | `run_agent.py` | user message, model config, tools, memory, platform context | assistant response, tool calls, traces | API calls, tool execution, memory/tool state | Sentinel agent loop with explicit evidence/debate/firewall states |
| Memory | Persist facts/profile and inject context | `tools/memory_tool.py`, `agent/memory_manager.py`, `plugins/memory/*` | memory writes, provider config, session metadata | system prompt blocks, provider tool schemas | disk writes, external provider calls | Sentinel memory is context only, never policy |
| Skills | Index and load procedural abilities | `agent/prompt_builder.py`, `agent/skill_commands.py`, `tools/skills_tool.py` | skill files, config, platform | prompt skill index, skill messages | possible script references, config injection | Scanned manifests with risk class and tests |
| Tool dispatcher | Route model tool calls | `model_tools.py` | tool name/args, task/session IDs | JSON result string | plugin hooks, registry dispatch | Firewall-owned dispatcher, fail-closed for policy |
| Delegation | Spawn subagents | `tools/delegate_tool.py`, `run_agent.py` | delegate task call, config | child agent result | background thread workers | Sentinel subagents need separate budgets and trace roots |
| Context prompt | Load project instructions | `agent/prompt_builder.py` | cwd, context files, SOUL.md | prompt block | reads local files | Trust-labeled context scanner |

## Lab Notes

Commands run:

- `git rev-parse HEAD`, `remote get-url origin`, `status --short`.
- File inventory and targeted `rg`/`Get-Content` reads.

Commands intentionally not run:

- `pip install`, `uv sync`, `hermes`, `hermes-agent`, `python run_agent.py`, `hermes-acp`.
- Skill setup scripts, OAuth flows, messaging bridges, gateway/web server, RL/web/cron extras.

Unresolved questions:

- Exact runtime ordering of all agent loop transitions requires deeper line-by-line trace through `run_agent.py`.
- Complete bundled skill inventory should be scanned with the Agent Forensics Protocol before any Sentinel SkillSpec is finalized.

Next experiment:

- Build a Hermes fixture scanner that extracts memory providers, skill setup scripts, tool hooks, and delegation config into a machine-readable map.
