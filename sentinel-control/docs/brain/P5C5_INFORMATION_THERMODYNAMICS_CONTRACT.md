# P5C.5 Information Thermodynamics Contract

Date: 2026-05-07
Status: First-principles grounding tranche

## Contract

Sentinel treats cognition as bounded uncertainty reduction.

```text
Tokens are a proxy cost.
Actions are a proxy cost.
Money is a proxy cost.
The objective is useful uncertainty reduction per bounded cost.
```

P5C.5 does not add runtime cost accounting. It locks the contract that future
Brain modules must optimize cost against information gain, not agent count for
its own sake.

## L0 Translation

Landauer-style information thermodynamics:

```text
information processing has physical cost
irreversible uncertainty reduction is not free
```

Sentinel product translation:

```text
do not spend cognition unless it reduces mission uncertainty or improves proof
do not launch agents unless their expected information gain justifies cost
do not debate unless uncertainty, contradiction, or impact warrants debate
```

## Operational Terms

| Term | Sentinel Meaning |
| --- | --- |
| `EntropyBudget` | Advisory budget for how much uncertainty-reducing cognition a mission can spend |
| `InformationGainEstimate` | Expected uncertainty reduction from evidence, action, debate, or agent role |
| `UncertaintyReductionScore` | Measured or estimated drop in unresolved mission uncertainty |
| `CognitiveCostEstimate` | Token, action, latency, risk, and authority-impact cost |
| `CostPerUncertaintyReduction` | Efficiency ratio for cognitive spend |

These are contracts for future P5 phases. P5C.5 does not integrate new runtime
models.

## Required Objective Shape

Future Brain scoring should preserve this shape:

```text
expected_progress
+ expected_information_gain
- execution_risk
- authority_impact
- token_cost
- action_cost
- latency_cost
```

This score is advisory. It cannot authorize execution.

## Cost Doctrine

A mission is expensive when:

```text
uncertainty is high
evidence is weak
impact is high
tool availability is uncertain
actions are irreversible or externally visible
budget is tight
```

A mission is cheap when:

```text
confidence is high
evidence is already present
actions are local and reversible
tool route is known
scope is narrow
budget is roomy
```

## Authority Boundary

Information gain does not grant authority.

Even if an action is highly informative, it remains blocked unless already
allowed by:

```text
MissionAuthorityEnvelope
ToolRegistry
ToolSelector
RiskRouter
ToolCallProtocol
EvidenceChain
FinalGate
```

Missing authority must become an `AuthorityExtensionProposal`, not silent
expansion.

## P5B/P5C Requalification

```text
MissionEntropyEstimator v0 = heuristic operational entropy estimate
AgentCountController v0 = advisory spend regulator
```

They are accepted v0 primitives, not final physical models.
