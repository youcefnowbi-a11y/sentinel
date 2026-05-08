# Hermes Final Forensic Report

Date: 2026-04-26
Vendor specimen: Hermes Agent
Lab mode: source-only forensic reverse phase
Source path: `agent-lab/vendors/hermes-agent/source`
Source commit: `35c57cc46b88710a98c4d43107b87b4ab828e3eb`

## Guardrails

This report is a forensic artifact, not an integration plan.

- No Hermes runtime was executed.
- No dependency install was performed.
- No skills, plugins, memory providers, shell hooks, gateways, OAuth flows, channels, or background services were run.
- No real accounts, credentials, browser profile, messages, or external services were connected.
- No vendor code is approved for Sentinel.
- All useful mechanisms below are classified as rewrite knowledge only.

## 1. Executive Summary

Hermes Agent is a Python agent runtime centered on persistent memory, prompt-context assembly, reusable skills, tool hooks, subagent delegation, context compression, model fallback, gateway sessions, and optional integrations. It is not primarily a GTM/business-decision product. It is a personal autonomous-agent operating layer that tries to make an agent better over time by remembering durable facts, loading procedural skills, invoking tools, delegating work, compressing long sessions, and optionally reaching external accounts and services.

The real superpower is learning-shaped operation: Hermes can preserve memory across sessions, turn skills into prompt-accessible procedures, run background memory/skill reviews, load external memory providers, and spawn isolated subagents. That makes it powerful because users do not have to restate context and workflows. It is also dangerous because memory, skills, project instruction files, plugin hooks, and context providers can become hidden behavior-shaping layers close to real execution.

Hermes should not be integrated into Sentinel. Sentinel should learn the mechanism classes and rewrite them under proof-first policy:

- TAKE: durable memory as context, compact skill index, source-context prompt scanner, subagent budget concepts, hook points for observability, context compression thresholds, provider capability checks.
- REWRITE: memory schema, skill system, plugin loader, tool dispatcher, shell hook model, delegation budgets, approval gate, context compiler, Google/external-account skills, learning review loop.
- AVOID: autonomous skill execution, runtime dependency install, OAuth/account setup from a skill, memory-as-policy, fail-open policy hooks, subagent auto-approve, shell hooks with user credential authority, unscanned user/project plugins, direct Gmail send/modify in v1.

Final vendor verdict:

- Best superpower: memory plus skill plus delegation turns a stateless chat agent into a persistent operator.
- Biggest weakness: too many prompt-shaping and execution-shaping layers can influence behavior before a Sentinel-grade evidence/firewall model exists.
- Biggest security risk: untrusted context, memory, skills, hooks, or plugins can push the agent toward shell/process, external account, messaging, or durable behavior changes.
- Most valuable Sentinel rewrite: `SentinelMemory + SentinelSkillSpec + FirewallDispatchPipeline`, where memory informs but never authorizes, skills declare capabilities but never execute directly, and every action is simulated, approved, and traced.
- Overall usefulness score: 8/10 as a lab specimen.
- Rewrite readiness score: 7/10. The architecture is source-visible enough to rewrite core ideas, but runtime behavior remains unverified because this phase intentionally avoided running Hermes.

## 2. Source Inventory

| Field | Finding |
|---|---|
| Repo URL | `https://github.com/nousresearch/hermes-agent` from local remote metadata |
| Commit | `35c57cc46b88710a98c4d43107b87b4ab828e3eb` |
| Clone path | `agent-lab/vendors/hermes-agent/source` |
| Clone size | `2,585 files / 67,523,148 bytes` from `audits/vendor_clone_checks.md` |
| Runtime | Python package, `>=3.11`, with CLI, gateway, plugins, skills, memory providers, optional web/RL/messaging extras |
| Package manager | setuptools via `pyproject.toml` |
| Package name/version | `hermes-agent`, version `0.11.0` at `pyproject.toml:5-7` |
| Description | "Self-improving AI agent - creates skills from experience, improves them during use, and runs anywhere" at `pyproject.toml:8` |
| Core deps | OpenAI, Anthropic, dotenv, httpx, requests, rich, tenacity, pydantic, prompt_toolkit, exa, firecrawl, parallel-web, fal-client, edge-tts, PyJWT crypto at `pyproject.toml:13-37` |
| Optional deps | modal, daytona, messaging, cron, Slack, Matrix, CLI, voice, pty, MCP, Home Assistant, SMS, ACP, Mistral, Bedrock, Google, web, RL, YC benchmark at `pyproject.toml:39-126` |
| Console entrypoints | `hermes`, `hermes-agent`, `hermes-acp` at `pyproject.toml:128-131` |
| Test config | pytest excludes integration tests and uses xdist at `pyproject.toml:142-147` |
| Primary agent loop | `run_agent.py`, class `AIAgent` at `run_agent.py:810-816` and initialization at `run_agent.py:833-896` |
| Tool dispatcher | `model_tools.py:498-634` |
| Prompt/context compiler | `agent/prompt_builder.py` |
| Memory system | `tools/memory_tool.py`, `agent/memory_manager.py`, `agent/memory_provider.py`, `plugins/memory/*` |
| Skill system | `agent/prompt_builder.py`, `agent/skill_commands.py`, `tools/skills_tool.py`, `skills/**/SKILL.md` |
| Bundled skills observed | `74` `SKILL.md` files under `skills/` in this source checkout |
| Plugin systems | General plugins in `hermes_cli/plugins.py`, memory providers in `plugins/memory/__init__.py`, dashboard plugins in `hermes_cli/web_server.py`, shell hooks in `agent/shell_hooks.py` |
| Generated/minified code | No full runtime build inspected or executed; source contains many reference docs and plugin/dashboard assets, but runtime generated artifacts were not validated |
| Dynamic loading | `importlib.util.spec_from_file_location` in plugin, memory-provider, dashboard-plugin, and context-engine paths |
| Install-time behavior | Not run. Source shows skill setup scripts and optional extras that can install dependencies if invoked, e.g. Google Workspace setup at `skills/productivity/google-workspace/scripts/setup.py:95-120` |

## 3. Consolidated Prior Lab Evidence

### G1 Static Audit

G1 established that Hermes is the strongest memory/learning/skill specimen in the lab. Existing source-only artifacts were:

- `audits/hermes_static_audit.md`
- `audits/hermes_algorithm_map.md`
- `audits/hermes_prompt_map.md`
- `audits/hermes_memory_map.md`
- `audits/hermes_skill_map.md`
- `audits/hermes_failure_modes.md`
- `audits/hermes_learning_map.md`
- `sentinel_integration_notes/hermes_to_sentinel.md`

This final report consolidates those into one vendor verdict and adds deeper source checks for plugin loaders, shell hooks, approvals, delegation caps, subprocess surfaces, memory-provider scoring, and skill inventory.

### No Runtime Evidence

The lab deliberately did not run Hermes. Therefore all statements here are source-backed static conclusions. Behavioral claims that require live confirmation are listed under missing blocks.

## 4. Architecture Map

### 4.1 Agent Loop

Primary source paths:

- `run_agent.py:810-816` declares `AIAgent`.
- `run_agent.py:833-896` defines constructor arguments for provider/model/session/context/memory/fallback/checkpoint/persistence behavior.
- `run_agent.py:941-946` stores `max_iterations` and creates or inherits `IterationBudget`.
- `run_agent.py:9183` begins `run_conversation`.
- `run_agent.py:9552-9577` gates the live loop by `api_call_count < max_iterations`, `iteration_budget.remaining > 0`, and `_budget_grace_call`.

Inputs:

- User message, optional context files, model/provider/base URL/API key, enabled toolsets, session metadata, memory config, fallback chain, checkpoint config, gateway status callbacks.

Outputs:

- Assistant response, tool calls, tool results, session logs, memory syncs, optional traces/checkpoints.

Side effects:

- Model API calls, tool execution, session file writes, memory writes/syncs, checkpoint writes, provider fallback changes, subagent spawning when tool calls request it.

Control flow:

```text
construct AIAgent
load tools and valid tool names
load memory and context compressor
build or reuse system prompt
while iteration budget remains:
  call model
  parse assistant response/tool calls
  run dispatcher for tool calls
  append tool results
  compress/retry/fallback if needed
  exit on final response, interrupt, or budget exhaustion
```

Sentinel rewrite:

- Convert this implicit loop into explicit stages:

```text
see -> verify -> reason -> debate -> plan -> simulate -> approve -> execute -> trace -> learn
```

Hermes optimizes for capable operation. Sentinel must optimize for evidence-backed decisions and controlled action.

### 4.2 Iteration Budget

Primary source paths:

- `run_agent.py:214-253` defines `IterationBudget`.
- `run_agent.py:218-222` notes parent and subagent budgets are separate and aggregate subagent usage can exceed the parent cap.
- `run_agent.py:9552-9577` consumes budget in the loop.
- `run_agent.py:11545-11548` refunds budget on compression restart.
- `run_agent.py:11994-11999` refunds budget if the only tool called is `execute_code`.

Mechanism:

```text
parent max_iterations default = 90
subagent max_iterations default = delegation.max_iterations, documented as 50
for each model iteration:
  if grace call active:
    clear grace flag
  elif not budget.consume():
    exit as budget_exhausted
compression restart and execute_code-only calls may refund one iteration
```

Failure risk:

- Iteration count limits conversational/tool-loop length, not action severity.
- Child agents can multiply total API calls and cost.
- `execute_code` refund makes sense for programmatic calls but could hide loop pressure if code execution is abused.

Sentinel rewrite:

- Add two budgets: `reasoning_budget` and `risk_budget`.
- Subagents inherit lower or equal permission, budget, and spend caps.
- No tool call can be refunded out of the risk ledger.

Eval required:

- Subagent cannot exceed parent spend/risk budget.
- Repeated `execute_code` calls cannot avoid action-budget limits.

### 4.3 Prompt And Context Compiler

Primary source paths:

- `agent/prompt_builder.py:32-52` defines context threat patterns and invisible character detection.
- `agent/prompt_builder.py:55-73` blocks suspicious context content by returning a placeholder.
- `agent/prompt_builder.py:145-161` emits memory guidance.
- `agent/prompt_builder.py:170-177` emits skill-maintenance guidance.
- `agent/prompt_builder.py:179-190` emits tool-use enforcement guidance.
- `agent/prompt_builder.py:920-929` truncates context content to 20,000 chars with head/tail preservation.
- `agent/prompt_builder.py:932-1042` loads `SOUL.md`, `.hermes.md`, `HERMES.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, and Cursor rules.
- `agent/prompt_builder.py:1045-1085` chooses and builds context-file prompt blocks.
- `run_agent.py:4463-4470` shows system prompt layer ordering: identity, user/gateway prompt, persistent memory, skills, context files, date/time, platform hint.

Inputs:

- Local project files, user/gateway prompt, memory snapshots, skills index, date/time, platform context.

Outputs:

- One combined system prompt.

Side effects:

- Reads local files from current workspace and Hermes home.
- Blocks only pattern-matched suspicious context content.

Observed priority model:

- Project context files are prompt material. The G1 prompt map identified `agent/prompt_builder.py:1084` language saying loaded context files "should be followed."
- This is useful for local coding assistants but risky when files are untrusted, vendor-provided, or web-derived.

Sentinel rewrite:

- Every prompt block must carry:
  - `source`
  - `trust_level`
  - `content_hash`
  - `scanner_result`
  - `allowed_influence`
  - `evidence_refs` where relevant
- Only Sentinel-owned policy can affect permissions.
- Memory, skills, project files, web pages, and vendor docs are data, not authority.

### 4.4 Memory System

Primary source paths:

- `run_agent.py:1596-1617` enables built-in persistent memory and user profile snapshots, defaulting memory/user char limits to `2200` and `1375`.
- `tools/memory_tool.py:61-102` scans memory content for prompt-injection/exfiltration patterns and invisible characters.
- `tools/memory_tool.py:105-123` describes `MemoryStore` as bounded curated memory with frozen prompt snapshot plus live mutable disk entries.
- `tools/memory_tool.py:222-263` adds memory with scanning, locking, duplicate checks, limit checks, and disk persistence.
- `tools/memory_tool.py:276-323` replaces entries with scanning and budget checks.
- `tools/memory_tool.py:325-357` removes matching entries.
- `tools/memory_tool.py:359-367` formats the frozen load-time snapshot for the system prompt.
- `tools/memory_tool.py:463-501` exposes add/replace/remove memory tool actions.
- `agent/memory_manager.py:47-63` strips internal memory fences from provider output.
- `agent/memory_manager.py:66-81` wraps prefetched external memory with `<memory-context>` and a note that it is not new user input.
- `agent/memory_manager.py:84-94` supports built-in memory plus at most one external provider.
- `agent/memory_manager.py:342-370` mirrors built-in memory writes to external providers and fails open on provider errors.

Data model observed:

- Built-in memory is curated strings with character budgets.
- User profile is a separate target.
- External providers can add their own schemas and retrieval behavior.

Key safety feature:

- Mid-session writes persist to disk but do not affect the current frozen system prompt snapshot (`tools/memory_tool.py:359-367`). This reduces immediate prompt-injection feedback loops.

Key safety gap:

- Memory can still influence future sessions.
- The scanner is regex-based.
- External providers can return contextual text and tools that become part of future model behavior.

Sentinel rewrite:

```text
SentinelMemoryRecord:
  id
  type: fact | preference | project_context | outcome | rejected_suggestion
  scope
  source_run_id
  source_event_id
  confidence
  trust_level
  created_by
  expires_at
  content_hash
  policy_influence_allowed = false
```

Memory may help reasoning. It cannot change policy, approval rules, risk class, or evidence-backed/sandbox mode.

### 4.5 External Memory Providers

Primary source paths:

- `run_agent.py:1621-1682` loads configured external memory provider with session/user/chat metadata.
- `run_agent.py:1684-1705` appends provider tool schemas to the active tool list.
- `agent/memory_provider.py:42-217` defines memory provider interface and hooks.
- `plugins/memory/__init__.py:40-63` discovers user-installed memory providers by scanning for `register_memory_provider` or `MemoryProvider`.
- `plugins/memory/__init__.py:66-97` scans bundled providers first, then user-installed `$HERMES_HOME/plugins/<name>`.
- `plugins/memory/__init__.py:188-273` loads provider modules via `importlib.util.spec_from_file_location`, preloads submodules, executes module code, and calls `register(ctx)`.
- `plugins/memory/__init__.py:322-376` loads CLI commands for the active memory plugin only.

Provider examples:

- `plugins/memory/mem0/__init__.py:247-270` queues background search prefetch with `rerank` and `top_k=5`.
- `plugins/memory/mem0/__init__.py:323-340` exposes `mem0_search`, caps `top_k` at `50`, and returns `memory` plus `score`.
- `plugins/memory/openviking/__init__.py:375-409` queues background search with `top_k=5`.
- `plugins/memory/openviking/__init__.py:531-566` sorts returned memories/resources/skills by score descending.
- `plugins/memory/retaindb/__init__.py:542-555` spawns multiple background prefetch threads for context, dialectic, and agent model.

Mechanism:

```text
memory.provider config selects exactly one external provider
provider loader imports provider module dynamically
provider system prompt block may be added
provider prefetch may run in background
provider tool schemas may expand active tools
provider sync_turn/on_memory_write hooks receive conversation events
```

Failure risk:

- User-installed memory provider import executes code.
- Provider output is untrusted context but may still bias the model.
- Provider search scores are vendor/provider-defined.
- Provider hooks fail open in `MemoryManager`.

Sentinel rewrite:

- External memory providers require signed or local scanner output.
- Retrieval result must be structured:

```text
MemoryHit:
  provider
  uri
  text
  score
  score_type
  source_timestamp
  trust_level
  used_in_prompt
```

- Provider failures must not silently drop policy checks.
- Provider output cannot create or modify memory without an audited write event.

### 4.6 Skill System

Primary source paths:

- `agent/prompt_builder.py:621-638` describes compact skill index, in-process LRU cache, disk snapshot `.skills_prompt_snapshot.json`, external dirs read-only, and local precedence.
- `agent/prompt_builder.py:645-667` uses in-process LRU cache.
- `agent/prompt_builder.py:669-742` reads disk snapshot or scans filesystem.
- `agent/prompt_builder.py:744-793` scans external skill directories with local precedence.
- `agent/prompt_builder.py:795-838` builds the mandatory skills prompt telling the agent to load matching skills with `skill_view` and update them with `skill_manage` if wrong/outdated/incomplete.
- `agent/prompt_builder.py:840-845` limits the skill prompt LRU cache to 8.
- `agent/skill_commands.py:73-109` injects skill-declared config values from `config.yaml`.
- `agent/skill_commands.py:123-133` supports template substitution and optional inline-shell expansion when `skills_cfg["inline_shell"]` is enabled.
- `agent/skill_commands.py:135-146` appends skill directory and tells the agent to resolve relative paths and run scripts with terminal using absolute paths.
- `agent/skill_commands.py:173-202` lists supporting files and says scripts may be run by absolute path.

Skill inventory:

- This source checkout contains `74` `SKILL.md` files under `skills/`.
- High-surface examples include Apple/iMessage, autonomous-agent skills, email/Himalaya, GitHub, MCP, Google Workspace, Linear, Notion, Spotify, red-teaming/godmode, smart-home/OpenHue, MLOps/training/inference, and software-development subagent skills.

Mechanism:

```text
scan skills dirs
filter by disabled/platform/tool conditions
compile compact skill prompt
on slash/skill invocation:
  load skill content
  inject config
  optionally expand inline shell
  expose skill directory/supporting files/scripts to agent
```

Failure risk:

- Skill text is prompt authority adjacent.
- Skill scripts create an execution pathway.
- Inline shell expansion is a direct dynamic behavior surface.
- Disk snapshots can preserve stale or poisoned skill metadata.
- Skill maintenance guidance encourages patching skills during use.

Sentinel rewrite:

```text
SentinelSkillManifest:
  id
  name
  version
  source_path
  content_hash
  required_tools
  required_secrets
  declared_side_effects
  risk_level
  allowed_actions
  tests
  scanner_report_id
  policy_id
  approval_required
```

Skills are documentation and action templates. They cannot execute directly. Script execution becomes an `AgentAction` proposal and must pass firewall review.

### 4.7 Google Workspace Skill

Primary source paths:

- `skills/productivity/google-workspace/scripts/setup.py:41-43` stores `google_token.json`, `google_client_secret.json`, and `google_oauth_pending.json` under Hermes home.
- `skills/productivity/google-workspace/scripts/setup.py:45-54` declares scopes including Gmail read/send/modify, Calendar, Drive readonly, Contacts readonly, Sheets, and Docs readonly.
- `skills/productivity/google-workspace/scripts/setup.py:95-120` installs Google API packages with `subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet"] + REQUIRED_PACKAGES)` if imports are missing.
- `skills/productivity/google-workspace/scripts/setup.py:133-184` reads, refreshes, and rewrites token files.
- `skills/productivity/google-workspace/scripts/setup.py:187-206` validates and stores a Google OAuth client secret.

Failure risk:

- Gmail send/modify is a high-impact external action.
- Calendar/Drive/Contacts/Sheets/Docs scopes access private account data.
- Runtime dependency installation is a supply-chain and reproducibility risk.
- Token/client-secret persistence needs independent storage, encryption, scope, and deletion review.

Sentinel rewrite:

- No Google Workspace integration in v1.
- Future version must be draft-first and least-privilege:
  - Gmail draft creation before send.
  - Per-scope capability manifest.
  - Human approval for every external send/modify.
  - No runtime package install by an agent.
  - Token storage server-side with explicit user revocation and audit trail.

### 4.8 Tool Dispatcher And Hooks

Primary source paths:

- `model_tools.py:498-519` defines dispatcher entry.
- `model_tools.py:520-525` coerces arguments and blocks agent-loop tools from registry dispatch.
- `model_tools.py:527-545` invokes `pre_tool_call` plugin hook, which may block.
- `model_tools.py:562-569` resets read-loop tracker for non-read/search tools.
- `model_tools.py:571-594` measures tool dispatch duration and dispatches registry tools.
- `model_tools.py:596-609` invokes `post_tool_call`.
- `model_tools.py:611-634` invokes `transform_tool_result`, which may replace the result string.
- `hermes_cli/plugins.py:60-70` defines hook names including `pre_tool_call`, `post_tool_call`, `transform_terminal_output`, `transform_tool_result`, API hooks, session hooks, and memory hooks.
- `hermes_cli/plugins.py:1071-1105` treats first valid `pre_tool_call` block directive as blocking.

Mechanism:

```text
model tool call
coerce args
pre_tool_call hooks can block
dispatch built-in or plugin-registered tool
post_tool_call hooks observe result
transform_tool_result hooks may replace result before model sees it
return final string
```

Power:

- Hooks are a clean extensibility point for policy, observability, logging, transforms, and tool instrumentation.

Failure risk:

- Hook exceptions are generally logged and ignored.
- Transform hooks can alter output after execution.
- Policy hooks and observer hooks share a flexible untyped channel.
- User/project plugins can register tools and hooks.

Sentinel rewrite:

- Split hooks into typed stages:
  - `policy_precheck`: fail closed.
  - `observer_pre`: fail open but cannot authorize.
  - `executor`: returns raw output.
  - `observer_post`: fail open but cannot hide output.
  - `presentation_transform`: optional, raw output remains trace-visible.

Trace requirement:

- Store raw args, policy result, executor raw output hash, transform output hash, hook failures, and final model-visible result.

### 4.9 General Plugin System

Primary source paths:

- `hermes_cli/plugins.py:1-31` states plugins are loaded from bundled, user, project, and pip entry-point sources.
- `hermes_cli/plugins.py:10-17` notes user/project plugins can override earlier sources on name collision.
- `hermes_cli/plugins.py:196-230` lets plugins register tools into the global registry.
- `hermes_cli/plugins.py:523-646` discovers bundled, user, project, and entry-point plugins; project plugins require `HERMES_ENABLE_PROJECT_PLUGINS`; built-in backends auto-load; standalone/user plugins require `plugins.enabled`.
- `hermes_cli/plugins.py:842-929` imports plugin module dynamically and calls `register(ctx)`.
- `hermes_cli/web_server.py:2947-3020` discovers dashboard plugin manifests from user, bundled, and optionally project plugin dirs.
- `hermes_cli/web_server.py:3052-3068` serves plugin assets and blocks path traversal with `resolve().is_relative_to()`.
- `hermes_cli/web_server.py:3090-3124` imports plugin API route files dynamically and mounts their routers.

Failure risk:

- Dynamic plugin import executes arbitrary plugin code.
- User/project plugins can override bundled names.
- Dashboard plugin APIs can add server routes.
- Backend and dashboard plugin lifecycles are broad.

Sentinel rewrite:

- Plugin installation/import is not an agent action in v1.
- Future Sentinel plugin system must require:
  - manifest scan;
  - explicit capabilities;
  - hash pinning;
  - sandbox execution;
  - no name-collision override by default;
  - no backend route mounting without administrator review.

### 4.10 Shell Hooks

Primary source paths:

- `agent/shell_hooks.py:150-215` registers configured shell hooks onto the plugin manager.
- `agent/shell_hooks.py:158-162` says `accept_hooks=True`, `HERMES_ACCEPT_HOOKS=1`, or `hooks_auto_accept: true` can skip TTY consent.
- `agent/shell_hooks.py:363-417` runs the hook command with `subprocess.run`, `shell=False`, stdin JSON, captured output, and timeout.
- `agent/shell_hooks.py:420-459` builds the callback and parses stdout even for non-zero exits.
- `agent/shell_hooks.py:630-664` approves unseen event/command pairs, with no prompt if auto-accepted or no TTY.
- `agent/shell_hooks.py:667-683` records allowlist entries with script mtime at approval.
- `agent/shell_hooks.py:689-695` states revoking an allowlist entry does not unregister live callbacks in the current process.
- `agent/shell_hooks.py:741-757` combines accept-hooks sources.

Power:

- Shell hooks make it possible to connect external policy, logging, or transformation scripts without modifying Hermes core.

Failure risk:

- Hook commands run with full user credentials.
- Auto-accept can register hooks without interactive review.
- Live callbacks persist until restart even after revocation.
- Hook stdout can become a blocking or transform directive.

Sentinel rewrite:

- No shell hooks in v1.
- Future hooks run in a restricted worker with a manifest, signed hash, read-only input, no ambient secrets, and fail-closed policy stage.

### 4.11 Terminal, Code Execution, And Approvals

Primary source paths:

- `tools/approval.py:57-99` defines sensitive paths and a hardline blocklist for catastrophic host commands.
- `tools/approval.py:698-781` checks dangerous commands, hardline block, YOLO/session bypass, cron behavior, gateway approval-required response, and CLI approval.
- `tools/approval.py:828-1101` combines Tirith and dangerous-command findings into one approval decision, supports `approvals.mode=smart`, gateway queue approvals, timeout, one/session/always persistence.
- `tools/terminal_tool.py:1612-1648` runs pre-exec security checks before terminal execution unless `force=True`.
- `tools/terminal_tool.py:1674-1712` starts tracked background processes.
- `tools/environments/local.py:110-138` filters Hermes-managed provider secrets from subprocess environment and can isolate HOME.
- `tools/environments/local.py:337-365` runs local commands via bash subprocess with environment and cwd.
- `tools/code_execution_tool.py:1020-1070` creates a child Python subprocess with scrubbed env, `PYTHONPATH`, optional HOME isolation, selected cwd, stdout/stderr pipes, and timeout loop.
- `tools/code_execution_tool.py:1375-1415` picks Python interpreter, preferring active venv/conda in project mode.
- `tools/code_execution_tool.py:1418-1435` resolves working directory, using `TERMINAL_CWD` or `os.getcwd()` in project mode.

Power:

- Hermes has a full local execution surface with approvals, background processes, local/docker/singularity/modal/daytona/ssh environments, and code execution mode choices.

Failure risk:

- Approvals can be bypassed by YOLO/session/mode off for non-hardline dangerous commands.
- Non-interactive non-gateway runs can allow commands except certain cron denial cases.
- Container backends skip the dangerous-command layer in approval checks.
- `force=True` bypasses pre-exec checks.
- Project-mode code execution uses project cwd and active venv, which increases capability and risk.

Sentinel rewrite:

- Sentinel v1 keeps shell and arbitrary code execution disabled.
- Later execution must be action-specific, not a generic shell:

```text
create_file
create_markdown
prepare_email_draft
export_json
```

- If shell is ever added, it must require:
  - no ambient secrets;
  - isolated workspace;
  - command allowlist;
  - dry-run preview;
  - user approval;
  - immutable trace;
  - no `force` bypass in agent-controlled flows.

### 4.12 Delegation And Subagents

Primary source paths:

- `tools/delegate_tool.py:40-49` blocks child tools: `delegate_task`, `clarify`, `memory`, `send_message`, and `execute_code`.
- `tools/delegate_tool.py:55-107` sets subagent approval callback; default auto-deny, opt-in `delegation.subagent_auto_approve=true` returns once approval.
- `tools/delegate_tool.py:325-360` reads `delegation.max_concurrent_children`, default 3, no hard ceiling beyond floor 1; warns above 10 because cost multiplies linearly.
- `tools/delegate_tool.py:363-387` reads child timeout, default 600 seconds and floor 30 seconds.
- `tools/delegate_tool.py:390-426` reads `delegation.max_spawn_depth`, default flat depth 1, clamped to 1..3.
- `tools/delegate_tool.py:637-645` strips delegation, clarify, memory, and code execution toolsets.
- `tools/delegate_tool.py:835-923` builds child agents, including credential/model overrides and inherited/intersected toolsets.
- `tools/delegate_tool.py:1396-1414` installs the approval callback in a worker thread.
- `tools/delegate_tool.py:1955-1990` runs single child directly or batch children concurrently with `ThreadPoolExecutor(max_workers=max_children)`.
- `tools/delegate_tool.py:2300-2325` describes delegate task schema, batch parallelism, default max concurrent children 3, nested delegation for orchestrator role with depth config.
- `run_agent.py:4706-4734` caps multiple `delegate_task` tool calls to `max_concurrent_children`.

Mechanism:

```text
delegate_task call
resolve role/depth/batch
intersect and strip child tools
construct child AIAgent
run child in thread with approval callback
collect result(s)
notify memory manager of delegation result
```

Power:

- Parallel subagents allow independent exploration and task splitting.

Failure risk:

- Cost and tool calls multiply with each child.
- Auto-approve mode is dangerous for batch/cron workflows.
- Child model/credential overrides may drift from parent safety assumptions.
- Tool stripping is important but not sufficient as the available inherited tools may still include network/files/external services.

Sentinel rewrite:

- Subagents are plan-only by default.
- Each child gets:
  - parent run id;
  - child run id;
  - bounded objective;
  - lower/equal permissions;
  - no external action permission unless parent plan has approved action;
  - separate cost cap;
  - trace subtree.

Eval required:

- Child cannot regain blocked tools.
- Child cannot auto-approve external action.
- Child cannot exceed parent budget.

### 4.13 Context Compression And Cost/Model Routing

Primary source paths:

- `run_agent.py:1446-1469` builds provider fallback chain.
- `run_agent.py:1728-1741` defaults API retries to 3, compression threshold to `0.50`, target ratio to `0.20`, and protect-last to `20`.
- `run_agent.py:1847-1883` selects context engine from config, context engine plugin, general plugin, or built-in compressor.
- `run_agent.py:1907-1918` creates built-in `ContextCompressor`.
- `run_agent.py:2404-2524` verifies auxiliary compression context length; enforces minimum context length and auto-lowers threshold if aux model context is below the main compression threshold.
- `run_agent.py:2638-2710` implements Anthropic prompt-cache policy.
- `run_agent.py:6984-7000` updates context compressor limits for fallback model.

Mechanisms:

```text
compression threshold = context_length * 0.50 by default
summary target ratio = 0.20 by default
protect first 3 and last 20 messages by default
if auxiliary context < threshold:
  threshold_tokens = auxiliary_context
  threshold_percent = threshold_tokens / main_context
```

Prompt cache policy:

```text
native Anthropic -> cache true, native layout
OpenRouter Claude -> cache true, envelope layout
Anthropic wire + Claude -> cache true, native layout
Qwen/Alibaba family -> cache true, envelope layout
else -> cache false
```

Failure risk:

- Provider naming heuristics can drift.
- Compression can drop or summarize context that includes evidence or approvals.
- Fallback model changes context limits and behavior.
- Cost tracking exists but hard budget enforcement is not the central product boundary.

Sentinel rewrite:

- CostRouter must be explicit:

```text
budget_per_run
max_provider_cost
max_tokens
fallback_allowed
cache_assumption
actual_usage
stop_before_over_budget
```

- Compression must preserve evidence ids, approval decisions, policy blocks, and trace references.

## 5. Algorithm And Math Audit

| Mechanism | Source | Formula/pseudocode | Inputs | Assumptions | Failure risk | Sentinel rewrite |
|---|---|---|---|---|---|---|
| Iteration budget | `run_agent.py:214-253`, `:9552-9577` | consume one iteration unless grace/refund path | `max_iterations`, inherited budget | iteration count approximates runaway risk | side effects can be severe before budget exhausts | separate reasoning/action/risk budgets |
| Subagent concurrency | `tools/delegate_tool.py:325-360`, `:1955-1990` | `max(1, int(config))`, default 3, warn >10 | config/env, batch size | user can tune parallelism | cost multiplies linearly | hard per-run cost cap, child budget ledger |
| Subagent timeout | `tools/delegate_tool.py:363-387` | `max(30, child_timeout_seconds)`, default 600 | config/env | timeout bounds stuck tasks | long enough for high cost/action loops | per-child wall time plus action cap |
| Spawn depth | `tools/delegate_tool.py:390-426` | clamp requested depth to 1..3 | config | shallow default prevents recursion | orchestrator mode can re-enable nested delegation | child permissions monotonic decreasing |
| Context compression | `run_agent.py:1728-1741`, `:2404-2524` | threshold 0.50, target ratio 0.20, protect last 20; auto-lower threshold to aux context | model context, aux model context | summarization preserves important state | evidence/approval details may be compressed away | preserve trace ids and policy events losslessly |
| Prompt cache policy | `run_agent.py:2638-2710` | provider/model name branches for cache support | provider/base_url/model | naming predicts cache capability | cache miss cost spike | measured cache-hit telemetry and budget stop |
| Memory char budget | `run_agent.py:1596-1617`, `tools/memory_tool.py:116-120` | memory max 2200, user max 1375 by default | config | concise memory reduces prompt bloat | text budget not semantic safety | typed memory records plus policy scanner |
| Context injection scanner | `agent/prompt_builder.py:32-73` | regex and invisible-char findings cause blocked placeholder | local context content | known strings catch attacks | paraphrase/encoding/multi-file bypass | hybrid scanner plus trust labels |
| Skill prompt cache | `agent/prompt_builder.py:621-845` | LRU cache max 8 plus disk snapshot | skills dirs, tools, platform | snapshot improves speed | stale/poisoned skill index | scanner-hash snapshot, policy version pin |
| External memory search | `plugins/memory/mem0/__init__.py:247-270`, `:323-340`; `plugins/memory/openviking/__init__.py:531-566` | top_k 5 prefetch, top_k <=50 tool, sort score desc | provider response scores | provider scoring is meaningful | opaque or poisoned scores | normalized `MemoryHit` with score provenance |
| Approval hardline | `tools/approval.py:57-99`, `:828-853` | hardline block before YOLO/mode off | shell command/env type | tiny catastrophic list is enough | recoverable destructive commands may pass with approval/off | Sentinel blocks high-impact classes unless explicit policy |
| Smart approval | `tools/approval.py:921-945` | aux LLM returns approve/deny/escalate | command and combined risk desc | LLM can judge risk | model misclassification | deterministic policy first, LLM advisory only |
| Hook dispatch | `model_tools.py:527-634` | pre hook block, dispatch, post hook, transform result | tool name/args/result | plugin hooks are trustworthy enough | fail-open and output mutation | typed fail-closed policy stage and raw trace |

## 6. Prompt And Skill Instruction Audit

| Surface | Source | Purpose | Risk | Sentinel rewrite |
|---|---|---|---|---|
| Identity prompt | `run_agent.py:4472-4482`, `agent/prompt_builder.py:932-957` | Load `SOUL.md` or default identity | Local identity can shape behavior too strongly | Signed Sentinel identity only |
| Project context files | `agent/prompt_builder.py:960-1085` | Load project guidance into prompt | Prompt injection from repo files | Context trust scanner, data-only tags |
| Memory guidance | `agent/prompt_builder.py:145-161` | Encourage durable memory writes | Imperative memory may become future instruction | Typed memory schema and imperative blocker |
| Skill maintenance guidance | `agent/prompt_builder.py:170-177` | Encourage save/patch skill after difficult tasks | Self-improving procedural mutation | Improvement proposals only, user approval |
| Tool-use enforcement | `agent/prompt_builder.py:179-190` | Force immediate tool use | Can pressure unsafe execution | Sentinel separates planning from execution |
| Skill index | `agent/prompt_builder.py:795-838` | Tell agent to load matching skills | Skill metadata becomes behavior router | Index from scanner output only |
| Skill activation message | `agent/skill_commands.py:112-202` | Load skill content, config, paths, scripts | Skill may instruct shell/script execution | Skill is docs; action proposal required |
| External memory context | `agent/memory_manager.py:66-81` | Inject prefetched memory | Untrusted stale/provider context | `MemoryHit` provenance and freshness |
| Hook result transform | `model_tools.py:611-634` | Transform model-visible tool result | Can hide raw executor behavior | Raw output always traced and user-visible on demand |

Prompt injection surfaces:

- Project instruction files.
- Skill markdown.
- Skill config value injection.
- External memory provider context.
- Built-in memory entries.
- Tool result transforms.
- Dashboard/backend plugin APIs.
- Shell hook stdout.

Sentinel requirements:

1. Prompt compiler emits `PromptTraceRecord` before every model call.
2. Each prompt block has source, trust, scanner result, and allowed influence.
3. Evidence blocks use `EvidenceItem.id`.
4. Memory blocks cannot include policy/permission instructions.
5. Skills cannot directly request execution.
6. Result transforms cannot erase raw executor output from trace.

## 7. Runtime Side-Effect Map

| Side effect | Source path | Trigger | Existing mitigation | Risk | Sentinel mitigation | Eval required |
|---|---|---|---|---|---|---|
| Filesystem read | `agent/prompt_builder.py:932-1085` | Prompt context loading | regex scanner/truncation | local hostile instructions | trust labels and quarantined context | malicious `AGENTS.md` fixture |
| Filesystem write | `tools/memory_tool.py:195-198`, `:222-357` | Memory add/replace/remove | scanning, locks, limits | persistent poisoned memory | typed memory, no policy, hash trace | memory-as-policy eval |
| External memory network | `plugins/memory/*` providers | provider prefetch/search/sync | provider-specific | private data / opaque retrieval | provider manifest, provenance, network policy | memory provider fake API eval |
| Dynamic provider import | `plugins/memory/__init__.py:188-273` | configured memory.provider | only one active provider | arbitrary code import | no unscanned provider load | malicious provider fixture |
| Dynamic plugin import | `hermes_cli/plugins.py:842-929` | enabled plugin | opt-in for standalone | arbitrary code import/tool hooks | scanner + manifest + sandbox | malicious plugin eval |
| Dashboard plugin API | `hermes_cli/web_server.py:3090-3124` | plugin declares API router | exception logging | server route injection | admin review and route manifest | dashboard API fixture |
| Shell hook subprocess | `agent/shell_hooks.py:363-459` | configured hook fires | allowlist/TTY/auto-accept | full user credential execution | disabled v1; sandboxed later | shell hook deny eval |
| Terminal command | `tools/terminal_tool.py:1612-1712` | terminal tool call | approval checks unless force | shell abuse | disabled v1 | shell blocked eval |
| Code execution | `tools/code_execution_tool.py:1020-1070` | execute_code tool | env scrub, timeout | project cwd/venv execution | disabled v1 | code exec blocked eval |
| OAuth/account access | `skills/productivity/google-workspace/scripts/setup.py:41-56` | skill setup | OAuth flow | external send/data access | future least-privilege draft-only | OAuth scope gate eval |
| Runtime package install | `skills/productivity/google-workspace/scripts/setup.py:95-120` | missing deps | pip install command | supply-chain | no runtime install | install blocked eval |
| Subagent spawn | `tools/delegate_tool.py:1955-1990` | delegate_task | tool stripping and timeout | cost/tool multiplication | trace tree and inherited permissions | subagent cap eval |
| Background review | `run_agent.py:3220-3295` | memory/skill review thread | max_iterations=8, quiet fork | durable mutation | proposal-only learning | self-improvement no-mutation eval |

## 8. Security And Failure Autopsy

| Failure mode | How it can happen in Hermes | Source paths | Existing protection | Gap | Sentinel prevention | Test fixture |
|---|---|---|---|---|---|---|
| Prompt injection | Project context or skills enter prompt | `agent/prompt_builder.py:32-73`, `:932-1085`, `:795-838` | regex scanner | pattern bypass and trusted phrasing | trust-labeled prompt compiler | malicious context + paraphrase |
| Tool injection | Skill or memory asks for tool use | `agent/skill_commands.py:135-202`, `agent/prompt_builder.py:179-190` | tool dispatcher checks later | prompt pressure still exists | action proposals only | skill asks to run shell |
| Malicious skill | Skill markdown/scripts direct execution | `skills/**/SKILL.md`, `agent/skill_commands.py:173-202` | disabled list, skill tools | no full static risk scanner | SkillScanner required | malicious skill manifest |
| Credential leakage | Terminal/code/subprocess/env/plugins can access credentials | `tools/environments/local.py:110-138`, `tools/code_execution_tool.py:1020-1070`, `hermes_cli/plugins.py:842-929` | env scrub for known provider vars | ambient files/tokens remain possible | no ambient secrets, scoped vault | secret exfil fixture |
| Filesystem escape | Terminal or project-mode code can operate in cwd | `tools/terminal_tool.py`, `tools/code_execution_tool.py:1418-1435` | command approvals | generic filesystem power remains | generated-projects-only v1 | path traversal fixture |
| Shell abuse | Terminal/shell hooks/background processes | `tools/approval.py`, `tools/terminal_tool.py`, `agent/shell_hooks.py` | hardline blocks and approvals | YOLO/off/force/noninteractive gaps | shell disabled v1 | destructive command fixture |
| Unauthorized external action | Google Workspace/Gmail/send_message/channel tools | `skills/productivity/google-workspace/scripts/setup.py:45-56`, `tools/delegate_tool.py:40-49` | child blocks send_message | adult agent can still use integrations if configured | outbound draft-only and approval | fake Gmail send |
| Memory poisoning | Durable memory stores instructions | `tools/memory_tool.py:222-367`, `agent/memory_manager.py:342-370` | threat regex and frozen snapshot | future-session impact | no imperative memory, no policy | memory override |
| Fake evidence | Memory/provider/search can return stale/false context | `plugins/memory/*`, `agent/memory_manager.py:66-81` | source wrapper text | no evidence ledger requirement | EvidenceItem with source/trust | fake memory evidence |
| Hallucinated decision | Agent can decide from memory/skills without proof | `run_agent.py` prompt loop | none product-specific | not evidence-gated | DecisionPlan requires evidence refs | no-evidence build verdict |
| Cost explosion | Delegation, retries, fallback, compression, external providers | `tools/delegate_tool.py:325-426`, `run_agent.py:1728-1741`, `:1446-1469` | iteration limits/warnings | no hard product budget by risk | CostRouter budget cap | parallel child cost eval |
| Unsafe self-improvement | Background review may save memory/skills | `run_agent.py:3097-3155`, `:3220-3295`; `agent/prompt_builder.py:170-177` | quiet max_iterations=8 | durable behavior may change | proposal-only learning | skill patch proposal eval |
| Privilege escalation | User/project plugin override or shell hook registration | `hermes_cli/plugins.py:10-17`, `:568-642`; `agent/shell_hooks.py:150-215` | opt-in/env gates | local config/env can elevate | admin-reviewed manifests | project plugin escalation |
| Persistence abuse | Memory, sessions, tokens, shell-hook allowlist | `run_agent.py:1520-1535`, `tools/memory_tool.py`, `agent/shell_hooks.py:667-695`, Google setup token files | local files | revocation may require restart; tokens persist | explicit retention/delete trace | persistence cleanup eval |
| Vendor lock-in | Provider-specific memory/tool APIs | `plugins/memory/*`, `pyproject.toml` extras | abstraction interfaces | behavior/score semantics vary | normalized provider contract | provider swap eval |
| User trust collapse | Hidden memory/skills/hooks affect action | multiple layers | logs/prints | user may not see why action happened | trace ledger with prompt/action refs | explain-decision eval |

## 9. Superpower Extraction

### Superpower 1: Persistent Memory

Source paths:

- `run_agent.py:1596-1705`
- `tools/memory_tool.py:105-123`, `:222-367`
- `agent/memory_manager.py:66-94`, `:342-370`

Mechanism:

- Built-in memory/user files plus optional external provider, prompt injection, provider tools, prefetch, sync, and write mirroring.

Why users care:

- The agent remembers preferences, facts, project context, and repeated patterns across sessions.

What makes it powerful:

- Memory reduces repeated explanation and enables personalization.

What makes it risky:

- Memory can become hidden instruction, stale evidence, or poisoned context.

Sentinel rewrite:

- Typed memory records with trust, provenance, expiry, and no policy authority.

Firewall implication:

- Memory writes are medium risk; high/critical if they contain credentials, policy language, external identity, or compliance-relevant claims.

Trace requirement:

- `memory.read`, `memory.write.proposed`, `memory.write.approved`, `memory.injected_into_prompt`.

Eval requirement:

- Memory cannot turn sandbox/hypothesis into evidence-backed mode.

Priority:

- Now, but only typed and constrained.

### Superpower 2: Compact Skill Index

Source paths:

- `agent/prompt_builder.py:621-845`
- `agent/skill_commands.py:73-202`
- `skills/**/SKILL.md`

Mechanism:

- Scan skills, compile compact prompt index, load skill on demand, expose config/supporting files/scripts.

Why users care:

- The agent gains procedural competence without bloating every prompt with full manuals.

What makes it powerful:

- Skills are reusable operational memory.

What makes it risky:

- Skill docs can instruct execution, load scripts, or smuggle policy.

Sentinel rewrite:

- Skills become scanned manifests and templates, not direct instructions.

Firewall implication:

- Skill activation is medium risk by default; high/critical if scripts, network, shell, secrets, browser, messaging, install, or OAuth are declared/found.

Trace requirement:

- `skill.scan`, `skill.index.compile`, `skill.view`, `skill.action.proposed`.

Eval requirement:

- Skill with `pip install`, OAuth scope, shell command, or external send is blocked.

Priority:

- Later for general skills; now only internal GTM templates.

### Superpower 3: Delegated Subagents

Source paths:

- `tools/delegate_tool.py:40-49`, `:55-107`, `:325-426`, `:637-645`, `:835-923`, `:1396-1414`, `:1955-1990`, `:2300-2325`
- `run_agent.py:4706-4734`

Mechanism:

- Spawn child agents in worker threads, strip specific tools, cap depth/concurrency, enforce timeout, inherit/intersect toolsets.

Why users care:

- Parallel exploration and specialized subtasks.

What makes it powerful:

- Work can be split without losing main session context.

What makes it risky:

- Cost and action authority multiply. Auto-approve mode is dangerous.

Sentinel rewrite:

- Subagents are traceable children with inherited lower permissions and explicit budget caps.

Firewall implication:

- Delegation is medium risk; high if child has external tools or write actions.

Trace requirement:

- `subagent.spawn.proposed`, `subagent.spawn.approved`, `subagent.result`, `subagent.cost`.

Eval requirement:

- Child cannot regain blocked tools or exceed parent caps.

Priority:

- Later for research/debate; not execution first.

### Superpower 4: Hookable Tool Pipeline

Source paths:

- `model_tools.py:498-634`
- `hermes_cli/plugins.py:60-70`, `:1071-1105`

Mechanism:

- Pre-tool hooks can block, post hooks can observe, transform hooks can change result.

Why users care:

- Extensible policy, logging, and integrations.

What makes it powerful:

- Cross-cutting behavior can be added without changing every tool.

What makes it risky:

- Fail-open hooks and result transforms can hide or alter reality.

Sentinel rewrite:

- Typed firewall-owned dispatch stages with raw output trace.

Firewall implication:

- Policy hook failure blocks execution. Observer hook failure only logs.

Trace requirement:

- `tool.precheck`, `tool.exec.raw`, `tool.transform`, `tool.final`.

Eval requirement:

- Hook crash cannot allow blocked action.

Priority:

- Now as internal firewall design, not plugin openness.

### Superpower 5: Context Compression And Provider Fallback

Source paths:

- `run_agent.py:1446-1469`, `:1728-1918`, `:2404-2524`, `:2638-2710`, `:6984-7000`

Mechanism:

- Compress long conversations, validate aux model context, update context limits on fallback, and use provider-specific cache policy.

Why users care:

- Long-running work survives context pressure and provider failures.

What makes it powerful:

- It keeps agent sessions alive over complex workflows.

What makes it risky:

- Compression can erase evidence/approval state; fallback can change cost and behavior.

Sentinel rewrite:

- Evidence and approval state are trace-ledger records, not only prompt text. Compression cannot delete the ledger.

Firewall implication:

- Compression summaries cannot substitute for source evidence.

Trace requirement:

- `context.compress.started`, `context.compress.summary`, `model.fallback`, `cost.usage`.

Eval requirement:

- Compressed run still cites original evidence and approval records.

Priority:

- Later, after trace ledger is stable.

### Superpower 6: Background Learning Review

Source paths:

- `run_agent.py:3097-3155`
- `run_agent.py:3220-3295`
- `agent/prompt_builder.py:170-177`

Mechanism:

- Background quiet forked agent reviews conversation to save memory/skills, with `max_iterations=8`.

Why users care:

- Agent improves after work without explicit user maintenance.

What makes it powerful:

- Converts repeated failure/workflows into reusable behavior.

What makes it risky:

- Durable memory/skills can mutate behavior without a product-grade approval boundary.

Sentinel rewrite:

- Self-improvement writes proposal documents only:

```text
observed_problem
evidence
proposed_change
risk
tests_needed
user_approval_required
```

Firewall implication:

- Any production mutation is critical risk.

Trace requirement:

- `learning.observation`, `learning.proposal`, `learning.approval`, `learning.patch_applied`.

Eval requirement:

- Background review cannot change code, policies, or skills without approval.

Priority:

- Later. For v1, feedback capture only.

## 10. TAKE / REWRITE / AVOID

### TAKE

- Durable memory as product value, but only as typed context.
- Skill indexes as compact procedural discovery.
- Context threat scanning before prompt insertion.
- Subagent concurrency/depth/timeout as budgeting primitives.
- Hook points for observability and policy, if typed and traced.
- Context compression thresholds and aux-model feasibility checks.
- Provider abstraction boundaries for future memory/research/cost providers.

### REWRITE

- `MemoryStore` into `SentinelMemoryStore`.
- External memory providers into `MemoryProviderManifest` plus normalized `MemoryHit`.
- Skill system into `SentinelSkillManifest` and scanner-derived index.
- Tool dispatcher into `FirewallDispatchPipeline`.
- Delegation into `SubagentPlan` with inherited permissions and trace tree.
- Prompt builder into `PromptCompiler` with trust labels and content hashes.
- Background learning into proposal-only `LearningReview`.
- Google/external-account skills into least-privilege, draft-first, approval-only integrations.
- Shell hooks into disabled-by-default, sandboxed, manifest-verified hook workers later.

### AVOID

- Running Hermes runtime inside Sentinel.
- Copying Hermes skills.
- Loading Hermes plugins or memory providers in Sentinel.
- Runtime `pip install` from agent-controlled flows.
- Gmail send/modify or external message send in v1.
- Memory entries that contain policy or permission language.
- Skill instructions that can run scripts directly.
- Fail-open policy hooks.
- Subagent auto-approve.
- Shell hooks with full user credential authority.
- User/project plugin override of bundled capabilities without review.

## 11. Missing Blocks And Unknowns

The following were not audited or verified in this pass:

- Full line-by-line runtime trace of all branches in `run_agent.py`.
- Live behavior of `AIAgent.run_conversation`.
- Complete provider-by-provider security audit for every `plugins/memory/*` provider.
- Full bundled skill scanner report for all 74 skills.
- Full terminal/code execution backend comparison across local/docker/singularity/modal/daytona/ssh.
- Gateway/channel live behavior, including Telegram/Discord/Slack/Matrix/SMS integrations.
- Browser tool implementation and live browser profile behavior.
- ACP/Copilot/Claude/OAuth credential flows beyond static references.
- Dashboard frontend plugin JavaScript behavior.
- Token storage encryption/permissions on disk.
- Real test suite results.

Commands intentionally not run:

- `pip install`, `uv sync`, `hermes`, `hermes-agent`, `python run_agent.py`, `hermes-acp`.
- Skill setup scripts.
- OAuth flows.
- Messaging/channel bridges.
- Gateway/web server.
- Shell hooks.
- Memory provider connections.
- Browser or desktop automation.

Next experiment before Sentinel build:

- Create a Hermes static scanner similar to OpenClaw B2.5:
  - enumerate `SKILL.md` files;
  - detect setup scripts, OAuth scopes, pip/npm installs, shell commands, account tokens, send/modify actions, browser/desktop hints;
  - enumerate plugin manifests, memory providers, dashboard APIs, shell hook examples;
  - produce deterministic JSON/Markdown with hash and consistency tests.

## 12. Final Vendor Verdict

Best superpower:

- Persistent memory plus reusable skills plus delegation. This is the strongest pattern for turning an agent from a one-off responder into an operator that accumulates context and technique.

Biggest weakness:

- Hermes blends many behavior-shaping layers: identity files, project context, memory, skills, providers, plugins, shell hooks, and tool transforms. This makes the runtime powerful but hard to audit from the user perspective unless every layer is traced and permission-scoped.

Biggest security risk:

- Durable and dynamic behavior surfaces can approach execution: memory can shape future prompts, skills can reference scripts, hooks can run subprocesses, plugins can register tools/routes, Google setup can request send/modify scopes, and terminal/code tools can reach the host.

Most valuable Sentinel rewrite:

- A first-principles `Sentinel Operating Kernel`:

```text
PromptCompiler with trust labels
+ SentinelMemory typed context
+ SkillScanner/SkillManifest
+ FirewallDispatchPipeline
+ SubagentPlan trace tree
+ LearningProposal only
```

What not to copy:

- The runtime, skill library, plugin loader, memory provider modules, Google Workspace implementation, shell hooks, terminal/code execution surfaces, or any vendor bridge.

Usefulness score:

- `8/10` as a memory/learning/skills/delegation specimen.

Rewrite readiness score:

- `7/10` for Sentinel v1 design. Enough source detail exists to design original Sentinel memory/skills/delegation safely, but a machine-readable Hermes scanner is still needed before any runtime-power comparison is final.

North star for Sentinel from Hermes:

- Remember what helps, forget what endangers, propose improvements instead of mutating behavior, and never let memory or skill text become permission.
