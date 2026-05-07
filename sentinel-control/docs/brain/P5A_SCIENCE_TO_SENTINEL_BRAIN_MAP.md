# P5A Science To Sentinel Brain Map

Date: 2026-05-07
Status: Architecture audit

## Purpose

This map translates useful science and engineering research into Sentinel-native
Brain L4 requirements. These references guide design. They do not override
Sentinel authority, tests, or FinalGate.

## Research Anchors

| Anchor | Useful Signal For Sentinel | Sentinel Translation |
| --- | --- | --- |
| Anthropic multi-agent research system | Multi-agent systems help breadth-first work but cost much more and need orchestration | AgentCountController plus budget gates |
| Anthropic context engineering | Context is finite and must be curated continuously | MissionGlobalWorkspace and context routing |
| Mixture-of-Agents | Layered agent aggregation can improve answer quality | Sparse MoA with fan-in limits |
| Debate Only When Necessary | Debate should be triggered by confidence/uncertainty, not always on | Adaptive debate gate |
| Tree of Thoughts | Hard planning benefits from exploring and scoring multiple paths | SlowBrain plan branching with pruning |
| HypoAgents | Bayesian plus entropy loops support hypothesis refinement | BayesianBeliefState and entropy-driven evidence search |
| Active inference | Action value includes expected information gain | EpistemicActionEvaluator |
| Production agent reliability | Agents need retries, checkpoints, fallbacks, and observability | ResourcefulnessEngine / DebrouilleLane |

Sources:

```text
https://www.anthropic.com/engineering/multi-agent-research-system
https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
https://arxiv.org/abs/2406.04692
https://arxiv.org/abs/2504.05047
https://arxiv.org/abs/2305.10601
https://arxiv.org/abs/2508.01746
https://arxiv.org/abs/2412.10425
```

## What Sentinel Accepts

Sentinel accepts these design principles:

```text
multi-agent helps when work is parallel and broad
context must be routed, not broadcast blindly
debate should be uncertainty-triggered
belief should be probabilistic where evidence is incomplete
actions should be scored partly by information gain
agent count must be controlled by budget, entropy, and parallelizability
blocked agents should try authorized alternatives before escalating
external verification remains necessary
```

## What Sentinel Rejects

Sentinel rejects these overclaims:

```text
more agents always means more intelligence
1000 agents should be available by default
variance always falls as 1/sqrt(N) for correlated LLM agents
MoA automatically beats every frontier single model
debate is always better than direct execution
research systems prove safe real-world mutation
resourcefulness means bypassing authority
```

## Layer Mapping

| Science/Engineering Layer | Sentinel Module |
| --- | --- |
| Information cost and uncertainty | MissionEntropyEstimator |
| No Free Lunch / meta-selection | AgentCountController |
| Society of specialized agents | AgentSocietyManager |
| Global Workspace style coordination | MissionGlobalWorkspace |
| Fast/slow cognition | FastBrain / SlowBrain route |
| Bayesian hypothesis update | BayesianBeliefState |
| Information gain / active inference | EpistemicActionEvaluator |
| Tactical adaptation inside fixed authority | ResourcefulnessEngine / DebrouilleLane |
| Debate and multi-path search | Adaptive Debate / Sparse MoA |
| Procedural know-how | SkillProcedureGraph |
| External certification | CoreFinalGate and BrainBench |

## Design Translation

The L4 Brain should optimize:

```text
expected_progress
+ expected_information_gain
- execution_risk
- authority_impact
- token_cost
- action_cost
- latency_cost
```

This score is advisory. It cannot authorize an action. Execution remains bound
to the mission envelope and the selected tool/capability policy.

## Required Proof Standard

Every future science-derived module must prove:

```text
deterministic bounded output for tests
trace event contract
budget behavior
authority non-expansion
failure-mode handling
CoreFinalGate or BrainBench check
```

Research becomes Sentinel power only after it becomes a tested Sentinel
contract.

## Debrouille Translation

The scientific lesson is not only "use more agents." Real competence also
requires fallback behavior under constraints. Sentinel translates that into:

```text
Authority is fixed.
Strategy is flexible.
POWER means initiative inside the mandate.
Blocked execution triggers authorized alternatives first.
Missing authority triggers a proposal, not silent expansion.
Partial success must be explicit and evidence-linked.
```
