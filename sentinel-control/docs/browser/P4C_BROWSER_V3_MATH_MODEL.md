# P4C Browser V3 Math Model

Date: 2026-04-29
Status: Completed

## Validity Model

For an accepted Browser V3 action `a`, define:

```text
V3(a) =
  G(a) * C(a) * T(a) * P(a) * R(a) * F(a)
```

Where:

- `G(a)` = mission authority grant exists and matches the class;
- `C(a)` = ContextPack exposes the action intent without authority expansion;
- `T(a)` = ToolIntentCompiler accepts the canonical intent;
- `P(a)` = provenance refs, page hashes, artifact ids, or session ids bind;
- `R(a)` = receipt/event/artifact output is complete;
- `F(a)` = FinalGate accepts the class contract.

If any factor is zero, the action is not certifiable.

## Class Scores

These are engineering review scores, not external benchmark scores.

| Dimension | Score | Reason |
| --- | ---: | --- |
| Authority model completeness | 94% | all P4B classes have grants and class contracts |
| FinalGate proof coverage | 92% | class contracts cover forged/missing proof paths |
| Compiler boundary | 90% | P4C added sensitive payload rejection |
| ContextPack boundary | 88% | V3 intents are brain-authored and compiler-bound |
| Real backend proof depth | 62% | several classes still use injected backend results |
| EvalBench realism | 45% | targeted pytest exists; multi-run/live benchmarks not complete |
| Overall V3 architecture readiness | 86% | strong architecture, runtime hardening still needed |

## Supremacy Function

External browser supremacy requires:

```text
S = capability_surface * proof_integrity * runtime_reality * eval_stability
```

Sentinel is currently high on `proof_integrity`, medium-high on
`capability_surface`, medium on `runtime_reality`, and early on
`eval_stability`.

## Math Verdict

Browser V3 architecture is above the lock threshold. Browser V3 external
supremacy remains below the declaration threshold until backend-reality and
EvalBench scores improve.
