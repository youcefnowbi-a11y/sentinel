# OpenJarvis Algorithm Map

Date: 2026-04-26

## A1. Engine Recommendation

Source: `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:209-228`.

Function:

- `recommend_engine(hw: HardwareInfo)`.

Inputs:

- `hw.gpu.vendor`.
- `hw.gpu.name`.

Pseudocode:

```text
if no GPU: llamacpp
if apple GPU: mlx
if nvidia GPU:
  if name contains A100/H100/H200/L40/A10/A30: vllm
  else: ollama
if amd GPU:
  if name contains MI300/MI325/MI350/MI355: vllm
  else: lemonade
else: llamacpp
```

Failure risk:

- String matching can misclassify hardware.
- Engine fit does not equal task fit.

Sentinel rewrite:

- CostRouter uses hardware signal plus task class, evidence depth, risk level, and budget cap.

## A2. Available Memory Estimate

Source: `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:231-238`.

Function:

- `_available_memory_gb(hw)`.

Formula:

```text
if GPU VRAM exists:
  available = gpu.vram_gb * max(gpu.count, 1) * 0.9
elif system RAM exists:
  available = (ram_gb - 4) * 0.8
else:
  available = 0
```

Failure risk:

- Assumes 10 percent VRAM reserve or 4GB RAM reserve is enough.
- Ignores fragmentation, concurrent processes, context length, quantization variance.

Sentinel rewrite:

- Add observed failure telemetry and fallback route.

## A3. Model Tiering

Source: `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:241-300`.

Function:

- `recommend_model(hw, engine)`.
- `estimated_download_gb(parameter_count_b)`.

Formula:

```text
model tiers:
  <=8 GB -> qwen3.5:2b
  <=16 GB -> qwen3.5:4b
  <=32 GB -> qwen3.5:9b
  <=64 GB -> qwen3.5:27b
fallback -> qwen3.5:27b

estimated_download_gb = parameter_count_b * 0.5 * 1.1
```

Failure risk:

- Parameter count is rough proxy for download/runtime size.
- Chooses maximum fitting local model, not necessarily best for task quality.

Sentinel rewrite:

- Route by expected value:
  - cheap model for extraction;
  - stronger model for verdict/debate;
  - deterministic tools for schema transformation.

## A4. Reward Weights

Source: `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:667-675`, `:726-760`.

Config:

- accuracy weight: 0.6.
- latency weight: 0.2.
- cost weight: 0.1.
- efficiency weight: 0.1.

Risk:

- Static weights can conflict with product context. For Sentinel, a high-risk action may justify slower/expensive verification, while a draft-only asset can use cheaper models.

Sentinel rewrite:

- Weight profile by run type:
  - `quick_pack`;
  - `deep_research`;
  - `firewall_review`;
  - `policy_decision`;
  - `asset_generation`.

## A5. Agent Config Evolution

Source: `agent-lab/vendors/openjarvis/source/src/openjarvis/learning/agents/agent_evolver.py:84-182`, `:193-223`, `:323-362`.

Classes/functions:

- `AgentConfigEvolver.analyze`.
- `AgentConfigEvolver._analyze_class`.
- `AgentConfigEvolver.write_config`.
- `_ToolScore.composite_score`.
- `_AgentScore.composite_score`.

Formulas:

```text
tool_score = 0.4 * success_rate + 0.4 * avg_feedback + 0.2 * min(log1p(count)/10, 1)
agent_score = 0.6 * success_rate + 0.4 * avg_feedback
recommended_max_turns = max(p75(tool_call_count) + 2, 5)
```

Failure risk:

- Bad or sparse traces can mutate future agent configs.
- Success/outcome labels may hide risk or user dissatisfaction.

Sentinel rewrite:

- Learning produces `ImprovementProposal`, not config mutation.
- Proposal includes trace sample size, formula, confidence, risk, tests needed, and patch diff.

## A6. Skill Script Quarantine

Source: `agent-lab/vendors/openjarvis/source/src/openjarvis/skills/importer.py:7-43`, `:62-139`.

Mechanism:

- Always copies safe subdirectories.
- Copies `scripts/` only when `with_scripts=True`.
- Writes `.source` metadata with `scripts_imported`.

Risk:

- Opt-in scripts still need scanning; prompt-only skills can still be malicious.

Sentinel rewrite:

- `scripts/` always quarantined until scan and sandbox tests pass.
- Prompt-only skills still scanned for policy override and tool injection.
