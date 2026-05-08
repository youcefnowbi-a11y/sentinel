# OpenJarvis Final Forensic Report

Date: 2026-04-26
Vendor specimen: OpenJarvis
Lab mode: source-only forensic reverse phase
Source path: `agent-lab/vendors/openjarvis/source`
Source commit: `484d0f090b127a9b8a00f02d64c35428cb7be706`

## Guardrails

This report is a forensic artifact, not an integration plan.

- No OpenJarvis runtime was executed.
- No dependency install was performed.
- No skills, plugins, channels, browser tools, shell tools, code tools, model hosts, sandboxes, dashboards, or background services were run.
- No real accounts, credentials, browser profiles, WhatsApp auth state, Claude Code runner, Docker containers, local models, or cloud providers were connected.
- No vendor code is approved for Sentinel.
- All useful mechanisms below are classified as rewrite knowledge only.

## 1. Executive Summary

OpenJarvis is a Python agent runtime that tries to make local-first agent operation practical. Its strongest axis is not one single agent loop. It is the combination of hardware-aware model selection, local/cloud routing, query complexity scoring, trace-driven routing learning, benchmark telemetry, memory retrieval backends, skill import from other ecosystems, and optional execution surfaces such as browser, shell, code interpreter, Docker sandbox, WhatsApp, Claude Code, and server/dashboard layers.

The real superpower is budget-aware agency: OpenJarvis treats hardware, model size, token budget, latency, cloud price, energy, and tool/runtime capability as first-class concerns. That is valuable to Sentinel because Sentinel will eventually need a CostRouter that can decide whether a task should use local inference, a cheap cloud model, a stronger model, or no model at all because the run budget is exhausted.

The real danger is that the same system contains many optional high-impact surfaces. Source inspection found shell execution, Python code execution, persistent REPL state, browser form interaction, HTTP requests, file read/write, Git commit, Docker subprocesses, Node bridges, WhatsApp outbound messaging, Claude Code subprocess execution, GitHub/Hermes/OpenClaw skill import, dynamic prompt overrides, learned config mutation, and open-by-default capability policy unless configured otherwise. These are not defects by themselves, but they are not acceptable as direct Sentinel runtime powers.

OpenJarvis should not be integrated into Sentinel. Sentinel should learn the mechanism classes and rewrite them under proof-first controls:

- TAKE: hardware/model catalog vocabulary, deterministic query complexity scoring, budget-aware model routing, telemetry-derived cost/latency/energy metrics, benchmark stats, trace-backed optimization, skill provenance metadata, mount allowlist idea, security scanners, Merkle-style audit log.
- REWRITE: CostRouter, capability policy, skill importer, model/router learning, browser tools, shell/code tools, memory injection, prompt override system, channel bridge, sandbox runner, savings calculator, security scanners, audit pipeline.
- AVOID: runtime `npm install` from agent surfaces, host shell execution, unscanned external skill sync, open-by-default capabilities, direct WhatsApp send, browser typing/clicking/submission in v1, Claude Code bridge execution, auto-written learned configs, memory-as-policy, unrestricted filesystem access.

Final vendor verdict:

- Best superpower: cost-aware local/cloud routing with hardware, query complexity, benchmark, and telemetry signals.
- Biggest weakness: local-first ambition is mixed with many optional execution powers that become unsafe if enabled before a Sentinel-grade firewall.
- Biggest security risk: imported skills, prompt overrides, channels, browser tools, shell/code tools, and learned config writes can alter behavior or trigger external side effects if policy is fail-open.
- Most valuable Sentinel rewrite: `SentinelCostRouter + SentinelCapabilityKernel + SentinelSkillScanner`, where every model/tool/channel decision has budget, permission, evidence, dry-run, approval, and trace records.
- Overall usefulness score: 8/10 as a lab specimen.
- Rewrite readiness score: 7/10. The routing, cost, memory, skill, and security mechanisms are source-visible enough to rewrite, but runtime behavior remains unverified because this phase intentionally avoided running OpenJarvis.

## 2. Source Inventory

| Field | Finding |
|---|---|
| Repo URL | `https://github.com/open-jarvis/OpenJarvis` from local remote metadata |
| Commit | `484d0f090b127a9b8a00f02d64c35428cb7be706` |
| Clone path | `agent-lab/vendors/openjarvis/source` |
| Current local file count | `1,741` files / `19,378,602` bytes measured in this checkout; prior `audits/vendor_clone_checks.md:72` recorded `1,774` files / `30,714,956` bytes at the same commit, likely reflecting clone/check timing and blobless checkout behavior |
| Runtime | Python package, optional Rust bridge, optional Tauri/server/dashboard/channel/browser/sandbox extras |
| Package manager | `pyproject.toml` with Hatchling; `uv.lock` present |
| Project name/version | `OpenJarvis`, version `0.1.1` at `pyproject.toml:6-7` |
| Description | Modular AI assistant backend with composable intelligence primitives at `pyproject.toml:8` |
| Python version | `>=3.10` at `pyproject.toml:10` |
| Core deps | click, datasets, ddgs, httpx, openai, python-telegram-bot, rich, tomli, tomlkit at `pyproject.toml:26-35` |
| Optional inference deps | MLX, vLLM, cloud, Google, LiteLLM, Gemma at `pyproject.toml:48-58` |
| Optional tool/memory deps | search, FAISS, ColBERT, PDF, BM25 at `pyproject.toml:59-73` |
| Optional browser/sandbox/dashboard deps | Playwright, wasmtime, Docker, Textual at `pyproject.toml:108-115` |
| Console entrypoint | `jarvis = openjarvis.cli:main` at `pyproject.toml:135` |
| Bundled Node bridges | `claude_code_runner` and `whatsapp_baileys_bridge` force-included at `pyproject.toml:141-142` |
| Major source dirs | `src/openjarvis/agents`, `bench`, `channels`, `cli`, `core`, `engine`, `learning`, `sandbox`, `security`, `skills`, `tools`, `server`, `telemetry`, `workflow` |
| Dynamic/runtime loading | prompt override loading from `OPENJARVIS_HOME`, optional import modules, skill loading, Node bridge runtime dirs, Rust bridge calls, dashboard/server reload paths |
| Install-time/runtime risk | Not run. Source shows host package install commands and subprocesses in CLI, Claude Code runner, WhatsApp bridge, skill source resolvers, sandbox runner, model host commands, and optional extras. |

## 3. Consolidated Prior Lab Evidence

### G2 Static Audit

The existing G2 artifacts established the first OpenJarvis split:

- `audits/openjarvis_static_audit.md`
- `audits/openjarvis_algorithm_map.md`
- `audits/openjarvis_cost_router_map.md`
- `audits/openjarvis_skill_import_map.md`
- `audits/openjarvis_failure_modes.md`
- `sentinel_integration_notes/openjarvis_to_sentinel.md`

Those artifacts correctly identified OpenJarvis as the strongest specimen for budget-aware agents and local/cloud routing, not as a runtime to integrate. This final report expands that first layer into a deeper source-path map.

### Vendor Clone Check

`audits/vendor_clone_checks.md:66-81` marks OpenJarvis clone-only. It explicitly says not to run `pip install`, `uv sync`, `jarvis`, skill import/sync/run, model pulls/downloads, channel login/start, dashboard/server start, Tauri/npm install, or any real account setup.

## 4. Architecture Map

### 4.1 Package and Runtime Surface

Purpose: expose a modular agent backend with optional local inference, cloud inference, tools, memory, channels, browser automation, security wrappers, evals, dashboard, sandbox, and learning.

Source paths:

- `pyproject.toml:26-35` for core dependencies.
- `pyproject.toml:48-115` for optional extras.
- `pyproject.toml:135` for CLI entrypoint.
- `pyproject.toml:141-142` for bundled Node bridges.
- `src/openjarvis/core/config.py` for configuration dataclasses.

Inputs:

- CLI commands, config TOML, environment variables, model/tool configs, skill sources, runtime flags, prompt overrides, local hardware.

Outputs:

- Agent responses, tool results, telemetry, memory rows, skill installs, local files, channel messages, benchmark records, server responses.

Side effects:

- Optional filesystem, subprocess, Docker, HTTP, browser, Node, model host, channel, cloud API, SQLite, memory and config writes.

Sentinel rewrite:

- Treat OpenJarvis as a capability taxonomy and cost/routing specimen only. Sentinel must not inherit its full optional runtime surface.

### 4.2 Hardware and Model Recommendation

Purpose: select a local engine and model based on hardware.

Source paths:

- `src/openjarvis/core/config.py:192` `detect_hardware`.
- `src/openjarvis/core/config.py:209` `recommend_engine`.
- `src/openjarvis/core/config.py:231` `_available_memory_gb`.
- `src/openjarvis/core/config.py:254` `recommend_model`.

Control flow:

1. Detect CPU, RAM, platform, GPU vendor/model/count/VRAM.
2. Choose engine by hardware:
   - no GPU -> `llamacpp`;
   - Apple GPU -> `mlx`;
   - NVIDIA datacenter keywords `A100/H100/H200/L40/A10/A30` -> `vllm`;
   - other NVIDIA -> `ollama`;
   - AMD datacenter keywords `MI300/MI325/MI350/MI355` -> `vllm`;
   - other AMD -> `lemonade`.
3. Compute available memory:
   - GPU VRAM path: `vram_gb * max(count, 1) * 0.9`;
   - RAM fallback: `(ram_gb - 4) * 0.8`;
   - unknown fallback: `0`.
4. Map memory tiers to model targets:
   - `<=8 GB` -> small 2B tier;
   - `<=16 GB` -> 4B tier;
   - `<=32 GB` -> 9B tier;
   - `<=64 GB` -> 27B tier;
   - else fallback 27B.
5. Scan model catalog for engine-compatible model and compute download estimate as `parameter_count_b * 0.5 * 1.1`.

Failure risks:

- Vendor-specific hardware heuristics may misclassify consumer/pro GPUs.
- Download size is approximate and ignores quantization, MoE active parameters, disk cache, and model packaging differences.
- Engine choice does not prove runtime is installed or safe.

Sentinel rewrite:

- Build `SentinelCostRouter` with explicit confidence, hardware detection trace, compatibility proof, budget cap, fallback, and manual override. Recommendation must not auto-download or auto-start engines.

### 4.3 Query Complexity and Heuristic Routing

Purpose: classify a query and select an appropriate model/token budget.

Source paths:

- `src/openjarvis/learning/routing/complexity.py:1-75` signal regexes and token tiers.
- `src/openjarvis/learning/routing/complexity.py:101` `score_complexity`.
- `src/openjarvis/learning/routing/complexity.py:208` `adjust_tokens_for_model`.
- `src/openjarvis/learning/routing/router.py:20` `build_routing_context`.
- `src/openjarvis/learning/routing/router.py:91` `HeuristicRouter`.
- `src/openjarvis/learning/routing/router.py:118` `HeuristicRouter.select_model`.

Algorithm:

`score = 0.20 * length_score + 0.25 * domain_score + 0.25 * reasoning_score + 0.15 * multi_part_score + 0.15 * creative_score`

Tier thresholds:

- `<0.15` -> `trivial`, 1024 tokens.
- `<0.30` -> `simple`, 2048 tokens.
- `<0.55` -> `moderate`, 4096 tokens.
- `<0.80` -> `complex`, 8192 tokens.
- else -> `very_complex`, 16384 tokens.

Thinking-model multiplier:

- If model name matches `qwen3.5|qwq|deepseek-r1|o1-|o3-|o4-`, token budget is multiplied by `2`.

Heuristic model selection rules:

1. Urgency `>0.8` -> smallest model.
2. Code signal -> model name containing `code` or `coder`, else largest.
3. Math signal -> largest.
4. Complexity `<0.20` -> smallest.
5. Complexity `>=0.55` or reasoning signal -> largest.
6. Default -> default model, fallback model, first available.

Failure risks:

- Regex-derived complexity is cheap and explainable but easy to game.
- Urgency can override correctness.
- Largest/smallest model by parameter count is not the same as best model for a task.

Sentinel rewrite:

- Keep deterministic scoring, but attach uncertainty and evaluation feedback. For business decisions, query complexity should influence depth and cost budget, not override evidence gates.

### 4.4 Learned Routing

Purpose: learn query-class to model mappings from traces.

Source paths:

- `src/openjarvis/learning/routing/learned_router.py:21` `LearnedRouterPolicy`.
- `src/openjarvis/learning/routing/learned_router.py:35` `min_samples = 5`.
- `src/openjarvis/learning/routing/learned_router.py:50` `select_model`.
- `src/openjarvis/learning/routing/learned_router.py:72` `update_from_traces`.
- `src/openjarvis/learning/routing/learned_router.py:139` `observe`.
- `src/openjarvis/learning/routing/learned_router.py:158` `update`.
- `src/openjarvis/learning/routing/learned_router.py:234` `_ModelScore.composite_score`.

Algorithm:

- Runtime selection uses learned model only if `query_class` exists and confidence count is at least `min_samples`.
- Batch update groups traces by `classify_query`.
- Per model score in `_ModelScore.composite_score` is `0.6 * success_rate + 0.4 * average_feedback`.
- Alternative update path computes each trace composite as `0.6 * outcome_score + 0.4 * feedback`.

Inputs:

- Trace query, model, outcome, feedback, latency fields.

Outputs:

- In-memory policy map and confidence counts.

Failure risks:

- Success and feedback can encode user bias or noisy labels.
- Model choice can become path dependent.
- It does not appear to require a policy review before the learned mapping changes runtime behavior.

Sentinel rewrite:

- Learned routing should be proposal-only in v1. It may recommend changes to budgets/model preference, but a trace record and human-approved policy version must gate promotion.

### 4.5 Agent Loop and Tool Dispatch

Purpose: implement tool-calling agent turns with loop limits and optional parallel tool execution.

Source paths:

- `src/openjarvis/agents/orchestrator.py:28` `OrchestratorAgent`.
- `src/openjarvis/agents/orchestrator.py:46` default max turns `10`.
- `src/openjarvis/agents/orchestrator.py:93` structured run.
- `src/openjarvis/agents/orchestrator.py:208` function-calling run.
- `src/openjarvis/agents/orchestrator.py:284-323` parallel/sequential tool execution.
- `src/openjarvis/tools/_stubs.py:26` `ToolSpec`.
- `src/openjarvis/tools/_stubs.py:88` `ToolExecutor`.
- `src/openjarvis/tools/_stubs.py:120` `ToolExecutor.execute`.

Control flow:

1. Build messages/system prompt.
2. Ask engine for response.
3. If no tool calls, return final answer.
4. Parse tool calls.
5. Check loop guard before execution.
6. Execute tools, optionally in a `ThreadPoolExecutor`.
7. Append tool observations.
8. Stop after `max_turns`.

Tool executor gates:

- Boundary guard for non-local tools.
- Capability policy check for `required_capabilities`.
- Taint check if `_taint` metadata exists.
- Confirmation callback for `requires_confirmation`.
- Per-tool timeout via a worker thread.
- Event emission for tool start/end/denial.

Failure risks:

- Capability policy is only as strict as the configured policy.
- Confirmation only exists for tools that declare `requires_confirmation`.
- Parallel tool calls can multiply side effects.
- Some high-impact tools are available as regular registered tools if enabled.

Sentinel rewrite:

- Sentinel action execution must be inverted: tools cannot self-declare safety. A central firewall must classify the action, generate dry-run, require evidence refs, require approval for medium/high/critical actions, and write trace before execution.

### 4.6 Loop Guard

Purpose: detect repeated tool calls, ping-pong loops, polling loops, and context overflow.

Source paths:

- `src/openjarvis/agents/loop_guard.py:14` `LoopGuardConfig`.
- `src/openjarvis/agents/loop_guard.py:18-21` thresholds.
- `src/openjarvis/agents/loop_guard.py:34` `LoopGuard`.
- `src/openjarvis/agents/loop_guard.py:71` `check_call`.
- `src/openjarvis/agents/loop_guard.py:148` `compress_context`.

Thresholds:

- `max_identical_calls = 3`.
- `ping_pong_window = 6`.
- `poll_tool_budget = 5`.
- `max_context_messages = 100`.

Algorithm:

- Hash `(tool_name, arguments)` with SHA-256 and block after repeated identical calls.
- Count per-tool usage and block when it exceeds polling budget.
- Maintain recent tool sequence and detect ping-pong.
- Compress context if message count exceeds threshold while preserving system/tool context structure.

Sentinel rewrite:

- Keep loop-guard class, but add trace records for each warning/block and expose the reason to the user in the approval board.

### 4.7 Capability Policy, Boundary Guard, and Security Scanners

Purpose: define tool permissions and scan inputs/outputs for secrets, PII, prompt injection, SSRF, and sensitive paths.

Source paths:

- `src/openjarvis/security/capabilities.py:16` `Capability`.
- `src/openjarvis/security/capabilities.py:48` `CapabilityPolicy`.
- `src/openjarvis/security/capabilities.py:55-63` open-by-default capability note and `default_deny`.
- `src/openjarvis/security/capabilities.py:94` `check`.
- `src/openjarvis/security/capabilities.py:171` `DEFAULT_TOOL_CAPABILITIES`.
- `src/openjarvis/security/boundary.py:27` `BoundaryGuard`.
- `src/openjarvis/security/boundary.py:74` `scan_outbound`.
- `src/openjarvis/security/boundary.py:108` `check_outbound`.
- `src/openjarvis/security/scanner.py:13` `SecretScanner`.
- `src/openjarvis/security/scanner.py:78` `PIIScanner`.
- `src/openjarvis/security/injection_scanner.py:21-96` prompt injection regex patterns.
- `src/openjarvis/security/ssrf.py:12-27` blocked metadata hosts and CIDRs.
- `src/openjarvis/security/file_policy.py:8-24` sensitive filename patterns.
- `src/openjarvis/security/guardrails.py:20` `GuardrailsEngine`.

Important implementation details:

- Capability policy defaults to grant if `default_deny=False`.
- Boundary guard modes include `redact`, `warn`, and `block`.
- Guardrails scan regular `generate` inputs/outputs before/after generation.
- Streaming paths emit tokens live and scan accumulated output post-hoc at `security/guardrails.py:219-290`.
- SSRF checks block cloud metadata hosts and private/link-local CIDRs.
- Secret and PII scanners are Rust-backed in this checkout.

Failure risks:

- Open-by-default policy is dangerous if a caller forgets to set `default_deny=True`.
- Post-hoc streaming scan can leak sensitive output before the scan result is known.
- Regex scanners are necessary but not sufficient for prompt injection or secret detection.

Sentinel rewrite:

- Sentinel policy must be deny-by-default. Streaming external outputs need pre-send chunk gating or safe buffering for sensitive contexts. Scanners feed the firewall; they do not replace approval and trace.

### 4.8 Skill Import, Loading, and Security

Purpose: import skills from Hermes, OpenClaw, GitHub, parse/translate them, and optionally include scripts.

Source paths:

- `src/openjarvis/cli/skill_cmd.py:141` `_parse_source_query`.
- `src/openjarvis/cli/skill_cmd.py:159` `_get_resolver`.
- `src/openjarvis/cli/skill_cmd.py:199` `install`.
- `src/openjarvis/cli/skill_cmd.py:270` `sync`.
- `src/openjarvis/skills/importer.py:31` copied subdirs: `references`, `assets`, `templates`.
- `src/openjarvis/skills/importer.py:47` `SkillImporter`.
- `src/openjarvis/skills/importer.py:62` `import_skill`.
- `src/openjarvis/skills/importer.py:115` overwrite uses `shutil.rmtree`.
- `src/openjarvis/skills/importer.py:130-135` scripts copied only with `with_scripts=True`.
- `src/openjarvis/skills/importer.py:177-192` `.source` provenance metadata.
- `src/openjarvis/skills/security.py:10` dangerous capabilities: `shell:execute`, `network:listen`, `filesystem:write`.
- `src/openjarvis/skills/loader.py:46` `load_skill`.
- `src/openjarvis/skills/loader.py:109-127` optional signature verification and injection scan.

Mechanism:

- CLI accepts source-qualified queries like `hermes:name`, `openclaw:name`, `github:name`.
- GitHub resolver requires `--url`.
- Importer writes translated `SKILL.md`, copies non-script asset dirs by default, copies `scripts/` only when explicitly requested, and writes `.source` metadata with source, commit, category, translated tools, missing tools, and scripts flag.
- Loader can verify signatures and scan step arguments, but both are optional parameters.

Failure risks:

- Skill source sync may clone or update third-party code.
- `with_scripts=True` imports executable material.
- Optional verification/scanning can be bypassed by callers.
- Capability declarations are data, not proof.

Sentinel rewrite:

- Skill import must become `SkillScanner -> Manifest -> Quarantine -> Static Report -> Dry-run Fixture -> Approval`. Scripts stay blocked in v1. External skill import is not a runtime feature until scanner evals pass.

### 4.9 Memory and Retrieval

Purpose: store, retrieve, index, and inject context from several memory backends.

Source paths:

- `src/openjarvis/tools/storage_tools.py:19` `MemoryStoreTool`.
- `src/openjarvis/tools/storage_tools.py:82` `MemoryRetrieveTool`.
- `src/openjarvis/tools/storage_tools.py:150` `MemorySearchTool`.
- `src/openjarvis/tools/storage_tools.py:224` `MemoryIndexTool`.
- `src/openjarvis/tools/storage/context.py:15` `ContextConfig`.
- `src/openjarvis/tools/storage/context.py:88-103` score filtering and token truncation.
- `src/openjarvis/tools/storage/faiss_backend.py:30` `FAISSMemory`.
- `src/openjarvis/tools/storage/faiss_backend.py:48` `IndexFlatIP`.
- `src/openjarvis/tools/storage/dense.py:625` dense retrieval.
- `src/openjarvis/tools/storage/hybrid.py:12` `reciprocal_rank_fusion`.
- `src/openjarvis/tools/storage/colbert_backend.py:114` `_maxsim`.
- `src/openjarvis/core/config.py:761` `StorageConfig`.

Algorithms:

- Context injection retrieves `top_k=5`, filters `score >= 0.1`, and truncates to `max_context_tokens=2048`.
- FAISS normalizes vectors and uses inner product, equivalent to cosine similarity for normalized vectors.
- Dense retrieval computes `scores = matrix_snapshot @ q_vec[0]`, then `argpartition` and descending sort.
- Hybrid retrieval uses Reciprocal Rank Fusion: `RRF_score(d) = sum(weight_i / (k + rank_i(d)))`, default `k=60`, over-fetches `top_k * 3`.
- ColBERT MaxSim normalizes query/doc token embeddings, computes similarity matrix, takes max per query token, and sums.

Failure risks:

- Retrieved context is injected as a system message in `build_context_message`, which can elevate untrusted memory into high-priority prompt context.
- Memory tools do not by themselves distinguish trusted facts, user preferences, policy, evidence, or untrusted documents.
- Indexing arbitrary paths can ingest sensitive or malicious content if not separately gated.

Sentinel rewrite:

- Memory must be typed: evidence, preference, project fact, outcome, trace summary. No memory can become policy. Untrusted memory must be injected as quoted evidence with source and confidence, never as authority.

### 4.10 Cost, Savings, Telemetry, and Benchmarks

Purpose: estimate cloud cost, local savings, FLOPs, MFU, latency, throughput, and energy.

Source paths:

- `src/openjarvis/engine/cloud.py:136` `estimate_cost`.
- `src/openjarvis/server/savings.py:17` token counting version.
- `src/openjarvis/server/savings.py:24` `CLOUD_PRICING`.
- `src/openjarvis/server/savings.py:87` `compute_savings`.
- `src/openjarvis/telemetry/flops.py:45` `estimate_flops`.
- `src/openjarvis/telemetry/flops.py:65` `estimate_flops_no_kv_cache`.
- `src/openjarvis/telemetry/flops.py:84` `compute_mfu`.
- `src/openjarvis/bench/_stats.py:9` percentile.
- `src/openjarvis/bench/_stats.py:20` `compute_stats`.
- `src/openjarvis/bench/latency.py:24` `LatencyBenchmark`.
- `src/openjarvis/bench/throughput.py:20` `ThroughputBenchmark`.
- `src/openjarvis/bench/energy.py:20` `EnergyBenchmark`.

Algorithms:

- Cloud cost: `input_cost = prompt_tokens / 1_000_000 * input_price`; `output_cost = completion_tokens / 1_000_000 * output_price`.
- Savings energy estimate: `flops = 2 * params * total_tokens_evaluated`.
- Provider energy: `wh_per_flop = energy_wh_per_1k_tokens / (1000 * flops_per_token)`; `energy_wh = flops * wh_per_flop`.
- Monthly projection: `(total_cost / session_duration_hours) * 720`.
- FLOPs with KV cache: `2 * params * total_tokens`.
- FLOPs without KV cache: `params * total_tokens * (total_tokens + 1)`.
- MFU: `(actual_tflops / (peak_tflops * num_gpus)) * 100`.
- Benchmark stats: mean, p50, p95 via linear interpolation, min, max, std.
- Throughput: `tokens / elapsed`.
- Energy per token: `energy_j / tokens`.

Failure risks:

- Pricing tables are hardcoded and drift over time.
- Cloud model parameter counts and energy constants are approximations.
- Local cost is treated as zero in savings, which ignores amortized hardware, power, ops, and maintenance.
- Budget checks in agent executor are post-tick, so a costly tick can occur before `budget_exceeded` is emitted.

Sentinel rewrite:

- CostRouter must have dated pricing tables, source metadata, pre-run budget reservation, post-run reconciliation, and trace records for every model/provider choice.

### 4.11 Learning and Agent Evolution

Purpose: analyze traces and write updated agent TOML configs.

Source paths:

- `src/openjarvis/learning/agents/agent_evolver.py:1-6` docstring says it writes updated TOML configs with versioning/rollback.
- `src/openjarvis/learning/agents/agent_evolver.py:52` `AgentConfigEvolver`.
- `src/openjarvis/learning/agents/agent_evolver.py:84` `analyze`.
- `src/openjarvis/learning/agents/agent_evolver.py:112` `_analyze_class`.
- `src/openjarvis/learning/agents/agent_evolver.py:171-179` max-turn recommendation.
- `src/openjarvis/learning/agents/agent_evolver.py:193` `write_config`.
- `src/openjarvis/learning/agents/agent_evolver.py:304` `_archive`.
- `src/openjarvis/learning/agents/agent_evolver.py:333` `_ToolScore.composite_score`.
- `src/openjarvis/learning/agents/agent_evolver.py:356` `_AgentScore.composite_score`.
- `src/openjarvis/core/config.py:657-695` learning defaults.

Algorithms:

- Tool score: `0.4 * success_rate + 0.4 * avg_feedback + 0.2 * min(log1p(count) / 10, 1)`.
- Agent score: `0.6 * success_rate + 0.4 * avg_feedback`.
- Recommended max turns: 75th percentile of observed tool call count plus 2, minimum 5; default 10 if no turn counts.
- Learning config defaults include `enabled=false`, `auto_update=false`, `min_improvement=0.02`, skills optimizer min traces `20`, optimizer interval `86400`.

Failure risks:

- Trace-derived config writes can mutate agent behavior.
- Frequency bonus rewards commonly used tools, not necessarily correct tools.
- User feedback can be sparse, biased, or gamed.

Sentinel rewrite:

- Self-improvement must produce a proposal and patch candidate only. No auto-written production config in v1. Every learning promotion requires trace evidence, eval results, rollback plan, and approval.

### 4.12 Execution Surfaces

OpenJarvis contains many optional execution powers. These are important specimens, but they remain blocked as Sentinel runtime features.

#### Filesystem

Source paths:

- `src/openjarvis/tools/file_read.py:17` `FileReadTool`.
- `src/openjarvis/tools/file_read.py:13` max read size 1 MB.
- `src/openjarvis/tools/file_write.py:17` `FileWriteTool`.
- `src/openjarvis/tools/file_write.py:13` max write size 10 MB.
- `src/openjarvis/security/file_policy.py:8-24` sensitive patterns.

Risk:

- If no `allowed_dirs` are configured, read/write path checks allow all non-sensitive files.

Sentinel rewrite:

- File writes limited to `data/generated_projects` by default. Reads require explicit source classification and secret scan.

#### Shell

Source paths:

- `src/openjarvis/tools/shell_exec.py:28` `ShellExecTool`.
- `src/openjarvis/tools/shell_exec.py:71-73` confirmation and `code:execute`.
- `src/openjarvis/tools/shell_exec.py:155-160` `subprocess.run(..., shell=True)`.
- `src/openjarvis/tools/shell_exec.py:15-24` output, timeout, env constants.

Risk:

- Shell is critical impact even with confirmation and env filtering.

Sentinel rewrite:

- No shell execution in Sentinel v1. Later shell requires container-only plan, command allowlist, dry-run, approval, trace, and no host secrets.

#### Code Interpreter and REPL

Source paths:

- `src/openjarvis/tools/code_interpreter.py:14-25` blocked string patterns.
- `src/openjarvis/tools/code_interpreter.py:31` `CodeInterpreterTool`.
- `src/openjarvis/tools/code_interpreter.py:80` subprocess execution.
- `src/openjarvis/tools/repl.py:22-51` blocklist, removed builtins, safe import list.
- `src/openjarvis/tools/repl.py:136` `ReplTool`.
- `src/openjarvis/tools/repl.py:245` session resolver.
- `src/openjarvis/tools/repl.py:304-310` `eval` and `exec` inside restricted namespace.

Risk:

- Pattern blocklists are bypassable. Persistent REPL state can preserve malicious state across calls.

Sentinel rewrite:

- Code execution is not a Sentinel v1 capability. Later code tools require sandbox, deterministic fixtures, no network/filesystem by default, resource limits, and audit.

#### Browser

Source paths:

- `src/openjarvis/tools/browser.py:56` `BrowserNavigateTool`.
- `src/openjarvis/tools/browser.py:88` `network:fetch`.
- `src/openjarvis/tools/browser.py:104-112` SSRF check.
- `src/openjarvis/tools/browser.py:155` `BrowserClickTool`.
- `src/openjarvis/tools/browser.py:235` `BrowserTypeTool`.
- `src/openjarvis/tools/browser.py:294` `page.fill`.
- `src/openjarvis/tools/browser.py:326` `BrowserScreenshotTool`.
- `src/openjarvis/tools/browser.py:364-382` screenshot base64 metadata.
- `src/openjarvis/tools/browser.py:406` `BrowserExtractTool`.

Risk:

- Browser click/type can submit forms indirectly. Screenshots and extracted content can leak sensitive page state.

Sentinel rewrite:

- Browser is read-only first, sandbox profile only, no authenticated user profile, no form submit/click/type until fake benchmark and approval model pass.

#### HTTP

Source paths:

- `src/openjarvis/tools/http_request.py:26` `HttpRequestTool`.
- `src/openjarvis/tools/http_request.py:72` `network:fetch`.
- `src/openjarvis/tools/http_request.py:81-87` method allowlist.
- `src/openjarvis/tools/http_request.py:90-98` SSRF block.
- `src/openjarvis/tools/http_request.py:105-106` environment expansion in headers.
- `src/openjarvis/tools/http_request.py:138-160` response truncation.

Risk:

- HTTP can still exfiltrate to public endpoints even with SSRF protection.

Sentinel rewrite:

- Network access must be research-only with source allowlists and no external POST/PUT/PATCH/DELETE in v1.

#### Docker Sandbox

Source paths:

- `src/openjarvis/sandbox/runner.py:29` `ContainerRunner`.
- `src/openjarvis/sandbox/runner.py:47` default timeout 300 seconds.
- `src/openjarvis/sandbox/runner.py:105` `_build_docker_args`.
- `src/openjarvis/sandbox/runner.py:121` `--network none`.
- `src/openjarvis/sandbox/runner.py:136` `run`.
- `src/openjarvis/sandbox/runner.py:183` subprocess run.
- `src/openjarvis/sandbox/mount_security.py:22` blocked mount patterns.
- `src/openjarvis/sandbox/mount_security.py:129` no roots configured means allow all non-blocked paths.

Risk:

- Good pattern, but default mount allowlist can be permissive if roots are not configured.

Sentinel rewrite:

- Use container sandbox only after explicit sandbox policy. Mount roots must be deny-by-default, read-only unless approved, with secret scanning and generated workspace isolation.

#### Claude Code Bridge

Source paths:

- `src/openjarvis/agents/claude_code.py:43` `ClaudeCodeAgent`.
- `src/openjarvis/agents/claude_code.py:81` reads `ANTHROPIC_API_KEY`.
- `src/openjarvis/agents/claude_code.py:92` `_ensure_runner`.
- `src/openjarvis/agents/claude_code.py:121-125` runs `npm install --production` if `node_modules` missing.
- `src/openjarvis/agents/claude_code.py:155-164` sends prompt, API key, workspace, allowed tools, system prompt, session id to Node subprocess.

Risk:

- Runtime npm install plus workspace authority and API key bridge is critical.

Sentinel rewrite:

- Avoid vendor code bridge. If Sentinel supports coding later, it must use its own patch proposal flow with approval and tests, not autonomous code mutation.

#### WhatsApp Baileys Channel

Source paths:

- `src/openjarvis/channels/whatsapp_baileys.py:45` `WhatsAppBaileysChannel`.
- `src/openjarvis/channels/whatsapp_baileys.py:41` runtime dir under `~/.openjarvis`.
- `src/openjarvis/channels/whatsapp_baileys.py:88` `_ensure_bridge`.
- `src/openjarvis/channels/whatsapp_baileys.py:123-126` `npm install` if `node_modules` missing.
- `src/openjarvis/channels/whatsapp_baileys.py:158-164` auth dir and Node bridge process.
- `src/openjarvis/channels/whatsapp_baileys.py:207-224` outbound send command.
- `src/openjarvis/channels/whatsapp_baileys.py:295-304` QR and inbound message handling.

Risk:

- Real account authentication, outbound messaging, persistent auth state, and Node bridge execution.

Sentinel rewrite:

- Channels are inbound untrusted data only at first. Outbound messages are draft-only with approval and trace.

## 5. Algorithm and Math Audit

| Mechanism | Source | Formula / Pseudocode | Risk | Sentinel Rewrite |
|---|---|---|---|---|
| Engine recommendation | `core/config.py:209` | GPU vendor/model -> engine mapping: none=`llamacpp`, Apple=`mlx`, NVIDIA datacenter=`vllm`, NVIDIA other=`ollama`, AMD datacenter=`vllm`, AMD other=`lemonade` | Hardware naming drift and runtime availability mismatch | Engine recommendation with confidence, proof, and no auto-start |
| Available memory | `core/config.py:231` | GPU: `vram_gb * max(count,1) * 0.9`; RAM: `(ram_gb - 4) * 0.8` | Approximate, ignores fragmentation and quantization | Explicit estimate source and safety margin |
| Model recommendation | `core/config.py:254` | memory tiers -> model family; download estimate `params_b * 0.5 * 1.1` | Approximate storage and capability | Separate model capacity, cost, quality, download risk |
| Query complexity | `learning/routing/complexity.py:101` | weighted sum: length 0.20, domain 0.25, reasoning 0.25, multipart 0.15, creative 0.15 | Regex can be gamed | Use deterministic score as input, not authority |
| Token tier | `learning/routing/complexity.py:57` | trivial 1024, simple 2048, moderate 4096, complex 8192, very_complex 16384 | Output budget may explode | Budget reservation before run |
| Thinking multiplier | `learning/routing/complexity.py:208` | thinking model -> `tokens * 2` | Model naming drift | Maintain dated model registry |
| Heuristic model select | `learning/routing/router.py:118` | urgency > 0.8 -> smallest; code -> coder/largest; math -> largest; low complexity -> smallest; high/reasoning -> largest | Task quality may be underweighted | Add quality eval and evidence-based override |
| Learned router | `learning/routing/learned_router.py:50` | learned mapping only if confidence >= 5 | No policy approval for learned change | Proposal-only route update |
| Learned model score | `learning/routing/learned_router.py:234` | `0.6 * success_rate + 0.4 * feedback` | Feedback bias | Keep confidence intervals and eval holdout |
| Heuristic reward | `learning/routing/heuristic_reward.py:38-53` | `0.4*latency_score + 0.3*cost_score + 0.3*efficiency_score` | Efficiency may reward short low-quality output | Add accuracy/evidence score |
| Tool score | `learning/agents/agent_evolver.py:333` | `0.4*success + 0.4*feedback + 0.2*min(log1p(count)/10,1)` | Frequency bias | Use eval-backed utility, not raw frequency |
| Agent score | `learning/agents/agent_evolver.py:356` | `0.6*success_rate + 0.4*avg_feedback` | Sparse feedback | Human-reviewed promotion |
| Max turns | `learning/agents/agent_evolver.py:171-179` | `max(p75(tool_call_count)+2, 5)` else 10 | Can increase cost/loop surface | Hard run budget and loop guard |
| Loop guard identical call | `agents/loop_guard.py:71-126` | SHA-256 tool+args count, block after 3 | Similar calls can evade | Semantic loop detection later |
| RRF memory fusion | `tools/storage/hybrid.py:12` | `sum(weight_i / (k + rank_i(d)))`, default k=60 | Ranking confidence not calibrated | Evidence confidence and source class |
| Dense retrieval | `tools/storage/dense.py:625` | normalized vectors, `matrix @ query`, argpartition top-k | Embedding similarity can surface poisoned memory | Memory trust classes |
| ColBERT MaxSim | `tools/storage/colbert_backend.py:114` | max cosine per query token, sum | Expensive and not policy-aware | Use only for evidence retrieval with citations |
| Cost estimate | `engine/cloud.py:136` | input/output tokens per 1M price | Pricing drift | Dated pricing source and pre-run budget |
| Savings estimate | `server/savings.py:87` | cost, FLOPs, energy, monthly projection | Local cost treated as zero | Include amortized local cost |
| FLOPs estimate | `telemetry/flops.py:45` | `2 * params * total_tokens` | Approximate | Store assumptions in trace |
| No-KV FLOPs | `telemetry/flops.py:65` | `params * total_tokens * (total_tokens + 1)` | Worst-case may overstate | Label methodology |
| MFU | `telemetry/flops.py:84` | actual TFLOPs / peak TFLOPs * 100 | GPU peak table drift | Dated hardware table |
| Benchmark stats | `bench/_stats.py:20` | mean, median, p95, min, max, std | Small samples unstable | Require sample count and CI |

## 6. Prompt and Skill Instruction Audit

| Prompt / instruction surface | Source | Mechanism | Risk | Sentinel Rewrite |
|---|---|---|---|---|
| Default system prompt | `agents/_stubs.py:129-158` | Builds messages with system prompt from prompt builder, explicit system prompt, or config default | Prompt source can change behavior globally | Versioned prompt registry with trace hash |
| Prompt overrides | `agents/prompt_loader.py:1-62` | Loads `$OPENJARVIS_HOME/agents/{name}/system_prompt.md` and `few_shot.json` | Local file can silently override behavior | Prompt overrides must be signed, versioned, and surfaced |
| Orchestrator prompt | `agents/orchestrator.py:101-109` | Uses explicit prompt or registry-built prompt | Tool descriptions can become prompt attack surface | Tool prompt compiler must include capability/risk labels |
| Deep research prompt | `agents/deep_research.py:38` and `:223-227` | Builds system prompt with current date and override support | Research prompt can over-trust web context | Evidence ledger with source ranking |
| RLM prompt | `agents/rlm.py:27-167` | Gives Python REPL-like language model interface and sub-query tools | Tool instructions can encourage code execution | No runtime code loop in Sentinel v1 |
| Claude Code prompt bridge | `agents/claude_code.py:155-160` | Sends prompt, workspace, allowed tools, system prompt to Node bridge | Workspace authority and external SDK behavior | Avoid bridge; use patch proposal flow |
| Skill markdown | `skills/loader.py:146-248` | Loads YAML/frontmatter/markdown skill instruction | Skill text can inject behavior | Skill text is untrusted until scanned and approved |
| Skill required capabilities | `skills/loader.py:99`, `skills/parser.py` | Manifest declares required capabilities | Declaration is not enforcement by itself | Firewall maps declared and inferred capabilities |
| Context memory injection | `tools/storage/context.py:53-103` | Formats retrieval into a system message | Untrusted memory becomes high-priority prompt context | Memory injected as quoted evidence, not policy |

## 7. Runtime Side-Effect Map

| Side effect | Trigger | Source path | Risk | Existing mitigation | Sentinel mitigation |
|---|---|---|---|---|---|
| Filesystem read | `file_read` tool | `tools/file_read.py:17` | Reads local files | sensitive filename block, 1 MB cap, optional allowed dirs | Default deny, allowed project roots, secret scan, trace |
| Filesystem write | `file_write` tool | `tools/file_write.py:17` | Writes/overwrites/appends local files | sensitive filename block, 10 MB cap, optional allowed dirs | Writes only under generated projects in v1 |
| Shell/process | `shell_exec` tool | `tools/shell_exec.py:28`, `:155` | Host shell execution | confirmation, `code:execute`, timeout, env filtering | Blocked in Sentinel v1 |
| Python subprocess code | `code_interpreter` | `tools/code_interpreter.py:31`, `:80` | Code execution | string blocklist, timeout | Blocked in Sentinel v1 |
| Persistent code state | `repl` | `tools/repl.py:136`, `:304-310` | Persistent eval/exec state | restricted builtins/imports, blocklist, timeout | Blocked in Sentinel v1 |
| Browser navigation | `browser_navigate` | `tools/browser.py:56` | Network/browser state | SSRF check | Read-only sandbox later |
| Browser typing/clicking | `browser_click`, `browser_type` | `tools/browser.py:155`, `:235` | Form submit/external action | none beyond tool layer/capability if configured | Blocked until fake benchmarks and approval |
| Screenshot capture | `browser_screenshot` | `tools/browser.py:326` | Sensitive page capture | headless local session | Screen sanitizer and sandbox profile |
| HTTP request | `http_request` | `tools/http_request.py:26` | Network exfiltration | SSRF block, response cap | Research-only GET allowlist in v1 |
| Skill import | `jarvis skill install/sync` | `cli/skill_cmd.py:199`, `:270` | Supply chain import | scripts opt-in, `.source` metadata | Scanner/quarantine, scripts blocked |
| Skill overwrite | `SkillImporter.import_skill` | `skills/importer.py:115` | Deletes existing skill dir | force flag | No runtime skill overwrite |
| Node package install | Claude Code runner | `agents/claude_code.py:121-125` | Host npm install | runtime dir | Avoid |
| Node package install | WhatsApp bridge | `channels/whatsapp_baileys.py:123-126` | Host npm install | runtime dir | Avoid |
| External message send | WhatsApp send | `channels/whatsapp_baileys.py:207-224` | Real outbound messaging | channel status only | Draft-only channels |
| Account auth state | WhatsApp auth dir | `channels/whatsapp_baileys.py:158-164` | Persistent credentials | local runtime dir | No real accounts in lab/v1 |
| Docker container | Sandbox runner | `sandbox/runner.py:183` | Container lifecycle and mounts | `--network none`, mount blocklist | Explicit sandbox policy, deny-by-default mounts |
| Learned config write | Agent evolver | `learning/agents/agent_evolver.py:193` | Behavior mutation | archive/rollback | Proposal-only improvement |
| Security audit write | AuditLogger | `security/audit.py:85` | SQLite audit events | Merkle hash chain | Trace ledger mandatory |

## 8. Security and Failure Autopsy

### Prompt Injection

How it can happen:

- External messages, web pages, memory chunks, imported skill markdown, prompt override files, and tool outputs can all become prompt context.

Source paths:

- `security/injection_scanner.py:21-96`.
- `skills/loader.py:127-143`.
- `tools/storage/context.py:53-103`.
- `channels/whatsapp_baileys.py:299-319`.

Existing protection:

- Pattern scanner exists and skill loader can scan if `scan_for_injection=True`.

Gap:

- Scanning is optional in some paths and regex-based.

Sentinel prevention:

- Treat all inbound channel/web/skill/memory text as untrusted evidence. Never allow untrusted text to change policy, tools, or approvals.

Required test:

- Imported skill with instruction to override policy; memory chunk with fake system prompt; channel message with exfiltration instruction.

### Malicious Skill Supply Chain

How it can happen:

- Skill import from Hermes/OpenClaw/GitHub can bring prompt instructions, assets, templates, and optionally scripts into `~/.openjarvis/skills`.

Source paths:

- `cli/skill_cmd.py:159-199`, `skills/importer.py:62-135`, `skills/sources/github.py`, `skills/security.py:10`.

Existing protection:

- Scripts skipped by default; `.source` metadata; dangerous capability list.

Gap:

- External skill text can still shape behavior. Verification/scanning is optional. `with_scripts=True` imports executable material.

Sentinel prevention:

- Skill Scanner v0 must infer capabilities from content and files, not trust declared manifest only. Scripts blocked in v1.

Required test:

- Fake GitHub skill with hidden shell instructions, script dir, network request, and fake signature.

### Unauthorized External Action

How it can happen:

- WhatsApp send, HTTP POST/PUT/PATCH/DELETE, browser click/type, channel bridge, or shell command can create external effects.

Source paths:

- `channels/whatsapp_baileys.py:207-224`, `tools/http_request.py:26-98`, `tools/browser.py:155-294`, `tools/shell_exec.py:155-160`.

Existing protection:

- Tool capability metadata, confirmation on shell, SSRF for network/browser navigation.

Gap:

- Not every external action requires approval. Capability policy can be open-by-default.

Sentinel prevention:

- All outbound contact, browser form interaction, external POST, and shell are high/critical actions requiring approval or v1 block.

Required test:

- Fake channel message asks to send a WhatsApp response; fake browser task attempts form submit; fake HTTP task posts data.

### Credential Leakage

How it can happen:

- Claude Code runner passes API key to Node subprocess. WhatsApp bridge stores auth state. HTTP headers expand environment variables. Browser screenshots can expose secrets. File read can read non-patterned secret files.

Source paths:

- `agents/claude_code.py:81`, `:155-164`; `channels/whatsapp_baileys.py:158-164`; `tools/http_request.py:105-106`; `tools/browser.py:364-382`; `security/scanner.py`.

Existing protection:

- Secret scanners, file sensitivity patterns, boundary guard.

Gap:

- Scanner coverage is not proof; streaming guard can scan after output is emitted.

Sentinel prevention:

- No credentials passed to vendor runtimes. Secret scanners run before storage, before external send, before trace display, and before streaming release.

Required test:

- Fake tool output contains API key; browser screenshot metadata contains token-looking text; HTTP header references env secret.

### Filesystem Escape

How it can happen:

- File tools allow all non-sensitive paths if `allowed_dirs` is empty. Sandbox mount allowlist allows all non-blocked paths if roots are empty.

Source paths:

- `tools/file_read.py:52-57`, `tools/file_write.py:68-73`, `sandbox/mount_security.py:129`.

Existing protection:

- Sensitive filename patterns and optional allowed roots.

Gap:

- Safe defaults are not strict enough for Sentinel.

Sentinel prevention:

- Deny-by-default filesystem. Generated output root only. Explicit read roots.

Required test:

- `../` traversal write, `.env` read, non-patterned secret filename read, mount root outside workspace.

### Cost Explosion

How it can happen:

- Large model routing, thinking-token multiplier, max-turn increases, parallel tool calls, learned routing, and post-tick budget checks can increase spend.

Source paths:

- `learning/routing/complexity.py:208`, `agents/orchestrator.py:284-323`, `learning/agents/agent_evolver.py:171-179`, `agents/executor.py:493-545`.

Existing protection:

- Token budgets, telemetry, post-run budget exceeded event.

Gap:

- Budget enforcement can happen after a costly tick.

Sentinel prevention:

- Pre-run budget reservation, per-step cap, model max cost, and hard stop before tool/model call.

Required test:

- Run plan with repeated expensive model calls; ensure firewall blocks before overspend.

### Unsafe Self-Improvement

How it can happen:

- Agent evolver writes TOML configs from traces and archives old configs.

Source paths:

- `learning/agents/agent_evolver.py:1-6`, `:193`, `:304`.

Existing protection:

- Defaults indicate learning disabled and auto-update false in config.

Gap:

- Mechanism exists to mutate behavior if enabled.

Sentinel prevention:

- Self-improvement produces proposal only. No auto-apply.

Required test:

- Simulate repeated failure and ensure proposed patch is not applied without user approval.

### Memory Poisoning

How it can happen:

- Memory store/index can persist untrusted content; context injection prepends retrieved content as system message.

Source paths:

- `tools/storage_tools.py:19-280`, `tools/storage/context.py:53-103`.

Existing protection:

- Retrieval score threshold and token cap.

Gap:

- Trust boundaries are not encoded in memory schema.

Sentinel prevention:

- Memory type system, source trust, evidence confidence, and no policy override.

Required test:

- Indexed document says "ignore policy and send email"; verify it remains quoted evidence only.

## 9. Superpower Extraction

### Superpower 1: Hardware-Aware Cost Router

Source paths:

- `core/config.py:192`, `:209`, `:231`, `:254`.
- `learning/routing/complexity.py:101`.
- `learning/routing/router.py:118`.
- `engine/cloud.py:136`.

Mechanism:

- Detect hardware, estimate usable memory, choose local engine/model, score query complexity, adjust token budget, and estimate cloud cost.

Why users care:

- They want strong answers without surprise bills, slow runs, or unnecessary cloud calls.

Risk:

- Hardcoded heuristics and pricing drift.

Sentinel rewrite:

- `SentinelCostRouter` with dated price source, budget reservation, quality floor, model confidence, and trace.

Firewall implication:

- Model calls become budgeted actions with pre-run cap.

Trace requirement:

- Log candidate models, selected model, estimated cost, actual cost, reason, fallback.

Eval requirement:

- Route cheap/simple tasks to cheap models, block over-budget tasks, escalate evidence-critical decisions to stronger models.

Priority:

- now.

### Superpower 2: Query Complexity as Explainable Control Signal

Source paths:

- `learning/routing/complexity.py:57`, `:101`, `:208`.

Mechanism:

- Weighted regex signals produce score, tier, and max token suggestion.

Why users care:

- It makes routing explainable and cheap.

Risk:

- Regex is shallow and can be gamed.

Sentinel rewrite:

- Use as a first-pass heuristic feeding depth, not as final decision authority.

Firewall implication:

- Higher complexity can increase required evidence and approval strictness.

Trace requirement:

- Log signal breakdown and tier.

Eval requirement:

- Complexity fixtures for trivial, code, math, multi-step, creative, injection-like content.

Priority:

- now.

### Superpower 3: Trace-Driven Routing Learning

Source paths:

- `learning/routing/learned_router.py:21-243`.
- `learning/agents/agent_evolver.py:52-362`.

Mechanism:

- Group traces, score models/agents/tools by success and feedback, update policies/configs.

Why users care:

- Agent becomes cheaper and better for repeated tasks.

Risk:

- Auto-learning can encode bad feedback or mutate behavior silently.

Sentinel rewrite:

- Learning proposals only; promotion requires eval and approval.

Firewall implication:

- Any routing policy change is a high-impact configuration action.

Trace requirement:

- Store old policy, proposed policy, evidence traces, eval delta, approval.

Eval requirement:

- Poisoned feedback and sparse trace tests.

Priority:

- later for auto-promotion, now for proposal logs.

### Superpower 4: Skill Import Quarantine Pattern

Source paths:

- `cli/skill_cmd.py:159-199`.
- `skills/importer.py:62-192`.
- `skills/security.py:10-55`.

Mechanism:

- Resolve external source, parse skill, translate tool refs, copy safe dirs, skip scripts by default, write provenance.

Why users care:

- Skill ecosystems can compound agent capability.

Risk:

- External skills are supply-chain and prompt-injection surfaces.

Sentinel rewrite:

- `SentinelSkillScanner` with static analysis, manifest inference, quarantine, eval fixture, and user approval.

Firewall implication:

- Importing a skill is a review action; executing it requires separate approval.

Trace requirement:

- Source URL, commit, file hash, inferred capabilities, scanner result, policy decision.

Eval requirement:

- Fake malicious skills from Hermes/OpenClaw/GitHub shapes.

Priority:

- now as scanner, later as runtime.

### Superpower 5: Permission and Boundary Vocabulary

Source paths:

- `security/capabilities.py:16-181`.
- `tools/_stubs.py:153-226`.
- `security/boundary.py:27-134`.

Mechanism:

- Capabilities, taint checks, confirmation, boundary guard, scanners.

Why users care:

- Agent can expose why a tool is blocked or allowed.

Risk:

- Open-by-default policy and tool-declared capability trust.

Sentinel rewrite:

- Deny-by-default central firewall; capabilities are inferred and declared.

Firewall implication:

- This is core Sentinel moat.

Trace requirement:

- Policy evaluated, matched rule, risk, approval state, scanner findings.

Eval requirement:

- Bypass attempts with missing capability, tainted data, external tool args.

Priority:

- now.

### Superpower 6: Benchmark and Efficiency Telemetry

Source paths:

- `bench/_stats.py:20`.
- `bench/latency.py:24`.
- `bench/throughput.py:20`.
- `bench/energy.py:20`.
- `telemetry/flops.py:45-99`.
- `server/savings.py:87`.

Mechanism:

- Measure latency, throughput, energy, p95 stats, FLOPs, MFU, cost/savings.

Why users care:

- Cost and speed become measurable, not vibes.

Risk:

- Hardcoded pricing/energy assumptions and small sample sizes can mislead.

Sentinel rewrite:

- Cost/quality dashboard with methodology labels, timestamped price table, and confidence.

Firewall implication:

- A run budget can be enforced before execution.

Trace requirement:

- Estimated vs actual token/cost/latency/energy.

Eval requirement:

- Synthetic telemetry traces validate calculations and caps.

Priority:

- now for cost, later for energy.

### Superpower 7: Containerized Execution Concept

Source paths:

- `sandbox/runner.py:29-344`.
- `sandbox/mount_security.py:22-190`.

Mechanism:

- Run payload in Docker/Podman container with `--network none`, read-only mounts, blocked secret path patterns, sentinel-delimited output.

Why users care:

- Enables safer heavy execution without trusting host.

Risk:

- Mount roots can be permissive; container runtime still has host risk.

Sentinel rewrite:

- Later `SentinelSandboxRunner` with deny-by-default mounts, disposable workspace, no secrets, no network by default, reproducible traces.

Firewall implication:

- Sandbox execution is critical action unless limited to generated fixture jobs.

Trace requirement:

- Image digest, mount list, env, timeout, command, output hash.

Eval requirement:

- Mount escape, secret path, timeout, network block, output parser tests.

Priority:

- later.

## 10. TAKE / REWRITE / AVOID

### TAKE

- Hardware/model catalog vocabulary.
- Query complexity scoring as explainable heuristic.
- Cost and token accounting primitives.
- Benchmark stats for latency, throughput, energy, p95.
- Trace-derived learning as a proposal source.
- Skill provenance metadata.
- Script-skip default for imported skills.
- Mount blocklist and read-only mount concept.
- Secret/PII/prompt-injection/SSRF scanner categories.
- Merkle hash chain audit idea.

### REWRITE

- CostRouter with budget reservation and trace.
- Capability policy as deny-by-default central firewall.
- Tool execution pipeline with dry-run and approval before execution.
- Skill import scanner and quarantine.
- Prompt override system as versioned prompt registry.
- Memory injection with trust classes and evidence refs.
- Browser tools as read-only sandbox first.
- HTTP tool as research-only GET with source policy.
- Learning optimizer as proposal-only patch system.
- Sandbox runner with strict mount roots.
- Channel adapters as inbound-untrusted and outbound-draft-only.

### AVOID

- Direct OpenJarvis runtime integration.
- Host `jarvis` CLI execution.
- `uv sync`, `pip install`, or optional extra install in lab.
- Skill sync/import as runtime feature.
- `with_scripts=True` skill import.
- Claude Code bridge.
- WhatsApp/Baileys bridge.
- Shell execution.
- Persistent REPL.
- Browser click/type/form submit.
- Auto-written learned configs.
- Open-by-default capabilities.
- Memory-as-policy.

## 11. Missing Blocks and Unknowns

Not audited yet:

- Full server/dashboard route behavior.
- Full Rust bridge implementation internals.
- Tauri frontend behavior.
- All channel adapters beyond WhatsApp/Baileys source.
- All skill source resolver internals beyond key paths.
- Full model host CLI command behavior.
- All eval dataset execution environments.
- All security scanner Rust regex/logic implementation.
- Full workflow engine execution and expression evaluation behavior.
- Runtime defaults after config loading in a real user profile.

Not verified:

- Actual model routing runtime behavior.
- Actual browser/session behavior.
- Actual Docker sandbox isolation.
- Actual Node bridge install output.
- Actual WhatsApp auth state layout.
- Actual secret scanner coverage.
- Actual learned config update flow.

Next experiment if authorized later:

- Build a deterministic OpenJarvis static scanner that classifies all tools, channel adapters, skill import paths, subprocess surfaces, dynamic loaders, prompt overrides, memory injection sites, and config-write paths into Sentinel risk classes. This remains source-only and fake-fixture-only.

## 12. Final Vendor Verdict

Best superpower:

- Budget-aware local-first routing: OpenJarvis combines hardware detection, model recommendation, query complexity, learned routing, cost estimation, benchmark telemetry, and savings math into a coherent cost-control specimen.

Biggest weakness:

- The system's optional powers are broad: shell, code, REPL, browser, channels, Node bridges, skill imports, Docker, prompt overrides, memory injection, and learned config writes. Without a central deny-by-default firewall, this becomes too much runtime authority.

Biggest security risk:

- Supply-chain plus execution convergence: an imported skill or prompt override can shape behavior, then tools/channels/browser/shell/code can create real effects.

Most valuable Sentinel rewrite:

- `SentinelCostRouter` and `SentinelSkillScanner`, backed by `SentinelCapabilityKernel`, where every model decision and capability decision is scored, simulated, approved when needed, and traced.

What not to copy:

- Do not copy OpenJarvis runtime, CLI commands, skill importers, Node bridges, browser/shell/code tools, or learned config write path into Sentinel.

Overall usefulness score:

- 8/10 as a lab specimen.

Rewrite readiness score:

- 7/10. The source clearly exposes useful algorithms and failure surfaces, but runtime behavior remains deliberately unverified.

North star for Sentinel:

- OpenJarvis teaches Sentinel how to make agents cost-aware; Sentinel must make that cost awareness permissioned, evidence-backed, and traceable before any runtime power is allowed.
