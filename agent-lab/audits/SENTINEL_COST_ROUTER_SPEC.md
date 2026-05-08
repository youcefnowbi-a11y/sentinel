# Sentinel Cost Router Spec

Date: 2026-04-26
Status: G10 architecture spec

## Principle

Cost is a firewall dimension.

Budget exhaustion is not a billing detail. It is a safety boundary that prevents runaway agents, fake certainty, hidden cloud usage, and low-quality fallback decisions.

## Inputs

```json
{
  "run_id": "run_...",
  "stage": "import|research|debate|generation|firewall|eval|learning",
  "mode": "quick|standard|deep",
  "risk_level": "low|medium|high|critical",
  "evidence_density": 0.0,
  "evidence_gap_count": 0,
  "data_sensitivity": "public|private|secret_suspected",
  "required_capabilities": ["json_schema", "citation_reasoning"],
  "estimated_input_tokens": 0,
  "estimated_output_tokens": 0,
  "remaining_budget_usd": 0.0,
  "latency_target_ms": null
}
```

## Decision Formula

```text
candidate_score =
  quality_weight(stage, risk_level) * quality_score
  + latency_weight(stage, mode) * latency_score
  + cost_weight(remaining_budget) * cost_score
  + privacy_weight(data_sensitivity) * privacy_score
  + reliability_weight(stage) * reliability_score
  + schema_weight(required_capabilities) * schema_support_score
```

Hard reject if:

- estimated cost exceeds remaining budget;
- provider/model pricing is unknown for deep mode;
- required schema/tool capability is missing;
- data sensitivity violates model/provider boundary;
- model is below minimum confidence tier for policy/firewall decisions.

## Output

```json
{
  "route_id": "route_...",
  "selected_provider": "...",
  "selected_model": "...",
  "fallback_provider": null,
  "fallback_model": null,
  "estimated_cost_usd": 0.0,
  "hard_cap_usd": 0.0,
  "remaining_budget_usd": 0.0,
  "reason": "...",
  "rejected_candidates": [],
  "policy_version": "...",
  "trace_id": "trace_..."
}
```

## Stage Priorities

| Stage | Quality Priority | Cost Priority | Rule |
|---|---:|---:|---|
| import | medium | high | normalize cheaply unless schema risk |
| research | high | medium | budget preview for deep mode |
| debate | high | low-medium | weak model cannot produce final verdict |
| generation | medium | high | drafts can use cheaper models |
| firewall | maximum | low | policy decisions require reliability |
| eval | high | medium | test accuracy before cost |
| learning | medium | high | proposals can be cheap |

## Budget Gates

- Quick mode: low cap, no deep research.
- Standard mode: default cap, balanced routing.
- Deep mode: user-visible budget preview.
- Critical firewall review: quality floor overrides cheap routing.
- Budget exhausted: output partial result with evidence gaps.

## Trace Requirements

Every model call records:

- selected model/provider;
- candidates considered;
- estimated and actual cost;
- budget remaining;
- route reason;
- fallback reason if used;
- stage and risk level.

## Required Evals

- Deep mode requires budget preview.
- Unknown pricing blocks deep route.
- Cache miss cannot exceed hard cap.
- Firewall decision cannot use below-threshold model.
- Budget exhaustion cannot mark pack ready.
- Fallback preserves trace continuity.
