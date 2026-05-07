# P5C.5 Math To Algorithm Translation

Date: 2026-05-07
Status: First-principles grounding tranche

## Purpose

P5C.5 locks the translation from mathematical principles to future Sentinel
algorithms before P5D creates agent societies.

## Translation Table

| Principle | Formula Shape | Future Sentinel Module | Implementation Rule |
| --- | --- | --- | --- |
| Shannon entropy | `H(X)` | MissionEntropyEstimator / EntropyBudget | Estimate uncertainty explicitly |
| Mutual information | `I(X;Y)` | EpistemicActionEvaluator | Score evidence/actions by information gain |
| Bayesian update | `P(H|E)` | BayesianBeliefState | Beliefs become probability plus variance |
| Surprise/free-energy inspiration | expected surprise + cost | EpistemicActionEvaluator / BrainBench | Prefer actions that reduce surprise under budget |
| Bellman value | current reward + future value | Planner / SlowBrain | Score plans by future impact, not immediate output only |
| Kalman-like update | prior + gain * innovation | BayesianBeliefState | Smooth noisy evidence into continuous belief updates |
| Monte Carlo / Tree-of-Thought | sample paths, score, prune | SlowBrain / FallbackPlanner | Explore hard plans with bounded branching |
| Min-max | proposer vs adversary | SkepticAgent / Verifier / FinalGate | Treat contradiction as first-class signal |
| No Free Lunch | no universal best method | AgentCountController / AgentSocietyManager | Select method and roles per mission |

## Role Design Rule For P5D

P5D must not invent roles by vibe. A role exists only if it serves at least one
algorithmic purpose:

```text
exploration
verification
aggregation
contradiction
cost control
context compression
fallback generation
authority boundary analysis
```

Examples:

| Role | Mathematical/Algorithmic Purpose |
| --- | --- |
| ResearchAgent | Increase evidence and expected information gain |
| VerifierAgent | Reduce false-positive belief updates |
| SkepticAgent | Min-max contradiction pressure |
| AggregatorAgent | Compress diverse outputs and reduce context entropy |
| CostAgent | Preserve entropy budget and reduce waste |
| PlannerAgent | Convert belief state into bounded action value |

## Search Rule

Tree/branching search is allowed only when:

```text
mission_entropy is high enough
parallelizability is high enough
budget pressure permits it
authority boundary is unchanged
branch count is bounded
trace fan-in is bounded
```

## Belief Rule

Future `BayesianBeliefState` must distinguish:

```text
low confidence because evidence is absent
low confidence because evidence contradicts
high confidence with narrow variance
high confidence with hidden model uncertainty
```

Binary verified/rejected status can remain as a compatibility view, but it must
not be the only internal representation once P5F begins.

## Advisory Boundary

All math-derived scores are advisory until a later explicitly locked runtime
phase integrates them.

They cannot grant:

```text
tools
actions
paths
browser powers
external systems
credentials
payments
channel sending
desktop control
```
