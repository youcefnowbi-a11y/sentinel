# P5C.5 Entropy Budget Model

Date: 2026-05-07
Status: First-principles grounding tranche

## Purpose

P5C.5 defines the future entropy-budget doctrine that P5D and later modules must
respect.

The Brain should not ask only:

```text
How many agents can I use?
```

It should ask:

```text
How much uncertainty can I reduce for this cost?
```

## Conceptual Model

Future entropy budgeting should track:

```text
initial_uncertainty
residual_uncertainty
expected_information_gain
observed_uncertainty_reduction
cognitive_cost
cost_per_uncertainty_reduction
budget_remaining
```

P5C.5 does not add these code models yet. It defines the required shape so P5D
does not design agent roles without cost discipline.

## Relationship To Existing P5B/P5C

P5B estimates:

```text
mission_entropy
domain_breadth
evidence_gap
parallelizability
impact_level
tool_uncertainty
budget_pressure
```

P5C routes:

```text
recommended_agent_count
brain_mode
max_parallel_agents
agent_budget
reason
```

P5C.5 clarifies:

```text
agent_count is not the objective
agent_count is a spend decision
the rational objective is uncertainty reduction under constraints
```

## Budget Bands

The current P5C count bands remain valid v0 routing:

```text
low entropy      -> 1 agent
medium entropy   -> 3-5 agents
high entropy     -> 8-20 agents
very high        -> 20-100 agents
extreme swarm    -> blocked by default
```

Future versions must justify each increase by:

```text
parallelizability
expected information gain
role diversity
context routing safety
aggregation plan
budget availability
FinalGate/BrainBench criteria
```

## Extreme Swarm Rule

Extreme swarm remains disabled by default.

It can only be reconsidered in a later phase with:

```text
explicit mission budget
parallelizability proof
agent independence strategy
trace fan-in limits
context compression plan
timeout ceiling
cost ceiling
BrainBench suite
FinalGate acceptance criteria
```

## Partial Success

If entropy remains high after budget is spent, the Brain should return:

```text
partial useful artifact
residual uncertainty
missing evidence list
blocked authority list
recommended next budget
AuthorityExtensionProposal when needed
```

Partial success must never be mislabeled as full success.
