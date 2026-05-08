# Hermes Algorithm Map

Date: 2026-04-26
Mode: source-only.

## A1. Iteration Budget

Source: `agent-lab/vendors/hermes-agent/source/run_agent.py:214-253`, `:844-946`, `:9552-9576`.

Function/class:

- `IterationBudget`.
- `AIAgent.__init__`.

Inputs:

- `max_iterations`, default 90.
- Optional inherited `iteration_budget`.

Mechanism:

```text
budget.max_total = max_iterations
for each LLM iteration:
  if budget.remaining <= 0:
    exit or give grace summary call
  else:
    budget.consume()
```

Assumption:

- Iteration count is a proxy for runaway agent behavior.
- Parent and child budgets can be independent; comments note subagents can exceed parent cap in aggregate (`run_agent.py:217-222`).

Failure risk:

- Budget controls LLM loop turns, not necessarily external side-effect severity.

Sentinel rewrite:

- Enforce both iteration budget and action-risk budget.
- A subagent cannot increase total external-action authority.
- Trace `budget_initial`, `budget_used`, `budget_remaining`, and `budget_exhausted_reason`.

Eval:

- Agent loop stops at budget.
- Subagent cannot bypass parent risk/budget.

## A2. Prompt Cache Routing

Source: `agent-lab/vendors/hermes-agent/source/run_agent.py:2638-2708`.

Function/class:

- `AIAgent._anthropic_prompt_cache_policy`.

Inputs:

- provider, base URL, API mode, model.

Pseudocode:

```text
if native Anthropic: cache = true, native layout
elif OpenRouter and model contains "claude": cache = true, envelope layout
elif anthropic wire and model contains "claude": cache = true, native layout
elif provider in {opencode, opencode-zen, opencode-go, alibaba} and model contains "qwen":
  cache = true, envelope layout
else:
  cache = false
```

Assumption:

- Provider/model names reliably indicate cache support.

Failure risk:

- Drift in provider behavior can cause false cache assumptions and cost spikes.

Sentinel rewrite:

- CostRouter stores provider capability evidence and live cache-hit telemetry.
- Cache assumptions are advisory; hard budget cap remains authoritative.

Eval:

- Cache-miss simulation must stop before run budget exceeds cap.

## A3. Context Threat Scanner

Source: `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:32-75`.

Function/class:

- `_scan_context_content`.

Inputs:

- Context file content.
- Filename.

Mechanism:

- Detects invisible unicode characters.
- Regex-detects patterns: ignore prior instructions, hidden comments, system prompt override, exfil commands, secret reads.
- If findings exist, returns a blocked placeholder instead of content.

Failure risk:

- Regex-only scanner can miss paraphrases, encoded payloads, or multi-file attacks.

Sentinel rewrite:

- Combine static patterns, heuristic classifiers, provenance labels, and context quarantine.

Eval:

- Prompt injection corpus with invisible unicode, HTML hidden text, command exfil, and paraphrases.

## A4. Skill Prompt Cache

Source: `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:621-708`.

Function/class:

- `build_skills_system_prompt`.

Inputs:

- Local skills dir.
- External dirs.
- Available tools/toolsets.
- Platform hint.
- Disabled skill names.

Mechanism:

```text
cache_key = skills_dir + external_dirs + tools + toolsets + platform + disabled
if in-process LRU hit: return prompt
elif disk snapshot valid: build prompt from snapshot
else: scan filesystem and write snapshot
```

Failure risk:

- A stale or poisoned skill snapshot can bias future prompt assembly.

Sentinel rewrite:

- Skill index is generated from signed scanner output.
- Snapshot includes hash of every skill file, scanner version, and policy version.

Eval:

- Stale snapshot cannot preserve a deleted/blocked skill.

## A5. Tool Dispatch Hooks

Source: `agent-lab/vendors/hermes-agent/source/model_tools.py:498-630`.

Function/class:

- Tool dispatcher main call path.

Inputs:

- Function name.
- Function args.
- task/session/tool IDs.

Mechanism:

- Coerces arguments.
- Blocks agent-loop-only tools from registry dispatch.
- Calls `get_pre_tool_call_block_message`.
- Measures dispatch duration with `time.monotonic`.
- Calls post-tool hook.
- Allows `transform_tool_result` hook to replace result string.

Failure risk:

- Exceptions around hooks are mostly swallowed.
- Transform hook can alter output after execution.

Sentinel rewrite:

- Hook chain is typed and policy hooks fail closed.
- Result transforms cannot hide raw executor output; both raw and transformed outputs are traced.

Eval:

- Plugin hook failure cannot permit a blocked action.

## A6. Skill Command Expansion

Source: `agent-lab/vendors/hermes-agent/source/agent/skill_commands.py:125-202`.

Function/class:

- `_build_skill_message`.

Inputs:

- Loaded skill content.
- Skill directory.
- Config values.
- Linked files.

Mechanism:

- Optional template substitution.
- Optional inline-shell expansion when config enables it.
- Injects absolute skill directory.
- Tells the agent to load supporting files or run scripts by absolute path.

Failure risk:

- Skill prompt can become a launcher for scripts and terminal commands.

Sentinel rewrite:

- Skill content can never instruct execution directly.
- Execution is represented as declared `AgentAction` objects and scored by Firewall.

Eval:

- Skill prompt containing "run scripts/foo" cannot execute without action proposal and approval.
