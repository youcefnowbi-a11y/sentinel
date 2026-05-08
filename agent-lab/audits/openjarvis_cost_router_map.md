# OpenJarvis Cost Router Map

Date: 2026-04-26

This file replaces the earlier shallow note with source-backed routing mechanics.

## Verified Routing Primitives

| Primitive | Source | Mechanism | Sentinel rewrite |
| --- | --- | --- | --- |
| Engine recommendation | `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:209-228` | Maps GPU vendor/name to `llamacpp`, `mlx`, `vllm`, `ollama`, or `lemonade` | `EngineSelector` with hardware, task class, risk class, and measured availability |
| Memory availability | `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:231-238` | GPU VRAM reserve or system RAM reserve | Add safety margin, observed OOM telemetry, and concurrent-load awareness |
| Model tiering | `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:241-295` | Qwen3.5 tier table by available GB; fallback scan by engine compatibility | Use model tiers per Sentinel phase: extract, debate, judge, generate, review |
| Download estimate | `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:298-300` | `parameter_count_b * 0.5 * 1.1` | Estimate storage/download but separate from runtime memory and API cost |
| Cloud pricing metadata | `agent-lab/vendors/openjarvis/source/src/openjarvis/intelligence/model_catalog.py:656-709` | Built-in model metadata includes pricing fields for some cloud models | Sentinel stores live pricing version and budget run ledger |
| Reward weights | `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:667-675`, `:726-760` | Accuracy/latency/cost/efficiency weights | Weights vary by run mode and action risk |

## Sentinel CostRouter Spec Seed

Inputs:

- `run_mode`: quick, standard, deep, firewall_review.
- `task_stage`: import, extraction, research, debate, pack_generation, policy_review.
- `risk_level`: low, medium, high, critical.
- `budget_usd`.
- `expected_tokens`.
- `evidence_density`.
- `local_hardware`.
- `model_capabilities`.
- `latency_target`.

Decision output:

```json
{
  "selected_model": "...",
  "selected_provider": "...",
  "route_reason": "...",
  "estimated_cost_usd": 0.0,
  "budget_remaining_usd": 0.0,
  "fallback_model": "...",
  "hard_stop_at_usd": 0.0,
  "trace_id": "..."
}
```

Rules:

- Critical policy decisions cannot use cheapest route if evidence/risk is ambiguous.
- Long creative generation cannot spend from firewall review budget.
- Cache hits are an optimization, not a budget guarantee.
- If cost estimate is unknown, route defaults to conservative cap and asks approval for deep mode.

## Required Evals

- Budget cap stops run.
- Cache-miss does not exceed budget.
- Local model failure falls back without losing trace.
- Expensive model cannot be used for low-value draft unless user opts in.
- Firewall review uses higher-confidence model profile than generic asset generation.
