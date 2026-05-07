# P5A Brain L4 Roadmap

Date: 2026-05-07
Status: Architecture audit

## Roadmap Doctrine

P5 builds the Brain into an adaptive intelligence allocator. It must stay
docs-first, test-first, and authority-bound.

```text
Brain allocates cognition.
MissionAuthorityEnvelope grants authority.
CoreFinalGate certifies outcomes.
```

## P5B MissionEntropyEstimator

Purpose: estimate how much uncertainty and breadth a mission contains.

Inputs:

```text
MissionAuthorityEnvelope
AgentContext
open questions
tool selection result
hypothesis result
budget fields
```

Outputs:

```text
mission_entropy
domain_breadth
evidence_gap
parallelizability
impact_level
tool_uncertainty
budget_pressure
```

Authority boundary: estimator is advisory only.

Trace events: `MISSION_ENTROPY_ESTIMATED`.

Failure modes: entropy inflated by vague prompt, entropy hidden by overconfident prompt, unsupported domain detection.

Tests: low/medium/high/very-high fixtures, budget pressure fixtures, no authority expansion.

Lock criteria: deterministic scores and trace payloads pass BrainBench starter cases.

## P5C AgentCountController

Purpose: convert entropy, breadth, and budget into bounded agent allocation.

Inputs:

```text
MissionEntropyEstimate
MissionAuthorityEnvelope
ExecutionPosture
```

Outputs:

```text
recommended_agent_count
brain_mode
max_parallel_agents
agent_budget
reason
```

Authority boundary: can reduce agent count, never expand allowed tools/actions.

Trace events: `AGENT_COUNT_ROUTED`.

Failure modes: over-spawn, under-spawn, budget mismatch, extreme swarm requested without proof.

Tests: 1, 3-5, 8-20, 20-100 decisions; extreme swarm blocked by default.

Lock criteria: controller selects correct count bands and blocks unbudgeted swarm.

## P5D AgentSocietyManager

Purpose: create role-scoped cognitive work packages for a bounded agent society.

Inputs:

```text
AgentCountRoute
MissionGlobalWorkspace snapshot
MissionAuthorityEnvelope
```

Outputs:

```text
AgentSocietyPlan
AgentRoleAssignment
AgentOutputContract
```

Authority boundary: every role inherits a subset of mission authority.

Trace events: `AGENT_SOCIETY_PLANNED`, `AGENT_ROLE_ASSIGNED`.

Failure modes: duplicate roles, missing verifier, missing aggregator, role receives excess context.

Tests: role planning fixtures, authority subset checks, output schema checks.

Lock criteria: society plans are deterministic, bounded, and traceable.

## P5D.5 Capital Operator Doctrine

Purpose: lock capital-operator doctrine before the workspace starts storing
signals and operating state.

Inputs:

```text
explicit spend authority
mission objective
budget and risk boundaries
capital mission signals
P5C.5 entropy-budget doctrine
```

Outputs:

```text
RootAuthorityEnvelope doctrine
AdaptiveOperatingEnvelope doctrine
SignalLedger doctrine
BudgetReallocator doctrine
DynamicSpendPolicy doctrine
SpendDecisionTrace doctrine
```

Authority boundary: doctrine-only. It does not make spend, trading, account
creation, credentials, browser powers, external APIs, or agents executable.

Trace events: future-only spend and adaptive envelope traces are specified by
doctrine, not implemented.

Failure modes: passive refusal despite explicit spend authority, hardcoded
budget examples, silent authority expansion, untraceable spend, profit
guarantees, KYC bypass, hidden subscriptions, trading without explicit trading
authority.

Tests: docs-only diff check; verify doctrine distinguishes fixed root authority
from adaptive operating allocation and acknowledges current black-zone runtime
limits.

Lock criteria: P5D.5 docs are coherent, no runtime powers are added, and
`CURRENT_STATE_LOCK.md` points to P5E next.

## P5E MissionGlobalWorkspace

Purpose: maintain versioned shared mission cognition without context pollution.

Inputs:

```text
mission context
evidence chains
belief states
agent outputs
open questions
rejected claims
```

Outputs:

```text
WorkspaceSnapshot
BroadcastSlice
WorkspaceDelta
```

Authority boundary: workspace stores facts and beliefs, never grants permission.

Trace events: `WORKSPACE_SNAPSHOT_CREATED`, `WORKSPACE_BROADCAST_PREPARED`, `WORKSPACE_DELTA_APPLIED`.

Failure modes: stale broadcast, unsupported fact accepted, context overflow, rejected claim reintroduced.

Tests: snapshot versioning, broadcast minimization, rejected-claim preservation.

Lock criteria: workspace updates are deterministic and replayable.

## P5F BayesianBeliefState

Purpose: move hypotheses from binary status to probability plus uncertainty.

Inputs:

```text
hypotheses
evidence items
adversarial findings
workspace facts
```

Outputs:

```text
belief_probability
belief_variance
supporting_evidence_refs
contradicting_evidence_refs
posterior_update_reason
```

Authority boundary: belief confidence informs planning but cannot authorize execution.

Trace events: `BELIEF_STATE_UPDATED`.

Failure modes: false precision, circular evidence, unsupported posterior jumps.

Tests: prior/posterior fixtures, contradiction fixtures, variance widening/narrowing.

Lock criteria: belief updates are bounded, explainable, and evidence-linked.

## P5G Adaptive Debate / Sparse MoA

Purpose: trigger debate and layered synthesis only when uncertainty or impact requires it.

Inputs:

```text
belief state
entropy estimate
agent count route
workspace snapshot
budget
```

Outputs:

```text
debate_needed
debate_roles
moa_layers
fan_in_limit
aggregated_claims
unresolved_disputes
```

Authority boundary: debate cannot execute tools outside the mission envelope.

Trace events: `DEBATE_ROUTED`, `MOA_LAYER_COMPLETED`, `DEBATE_AGGREGATED`.

Failure modes: endless debate, hallucination convergence, context fan-in explosion.

Tests: debate-off for low uncertainty, debate-on for contradiction, fan-in limit checks.

Lock criteria: debate is adaptive, sparse, budget-bound, and aggregator-checked.

## P5H EpistemicActionEvaluator

Purpose: score actions by progress and information gain, not only immediate completion.

Inputs:

```text
candidate actions
belief state
world model prediction
mission budget
authority policy
```

Outputs:

```text
expected_progress
expected_information_gain
risk_penalty
cost_penalty
authority_impact
total_action_value
```

Authority boundary: action value is advisory and still passes through policy.

Trace events: `EPISTEMIC_ACTION_SCORED`.

Failure modes: curiosity loop, high-info unsafe action, low-value evidence gathering.

Tests: informative-safe action preferred, unsafe high-info action rejected, low-entropy direct route.

Lock criteria: scoring improves information selection without authority expansion.

## P5I ResourcefulnessEngine / DebrouilleLane

Purpose: make Sentinel resourceful inside a fixed MissionAuthorityEnvelope.

Inputs:

```text
mission envelope
execution posture
blocked action
tool selection result
workspace snapshot
remaining budget
review findings
```

Outputs:

```text
resourcefulness_level
fallback_decision
tool_substitution_decision
fallback_plan_set
partial_success_report
authority_extension_proposal
```

Authority boundary: may only choose already-authorized alternatives. AuthorityExtensionProposal is proposal-only.

Trace events: `RESOURCEFULNESS_ROUTED`, `FALLBACK_PLAN_CREATED`, `TOOL_SUBSTITUTION_PROPOSED`, `PARTIAL_SUCCESS_DECLARED`, `AUTHORITY_EXTENSION_PROPOSED`.

Failure modes: fallback loop, policy bypass, partial success mislabeled as full success, extension silently applied.

Tests: D0-D5 fixtures, authorized substitution, unauthorized substitution rejected, partial success evidence refs, extension proposal no-activation.

Lock criteria: Debrouille levels work without authority expansion and FinalGate rejects silent expansion.

## P5J SkillProcedureGraph

Purpose: store reusable know-how as procedures rather than loose text.

Inputs:

```text
mission objective
selected capabilities
available tools
workspace facts
```

Outputs:

```text
matched_procedure
preconditions
required_authority
canonical_steps
success_proofs
known_failure_modes
```

Authority boundary: skill memory can recommend, never authorize.

Trace events: `SKILL_PROCEDURE_MATCHED`.

Failure modes: stale skill, missing authority, skill overfits one domain.

Tests: matching fixtures, missing authority block, procedure evidence refs.

Lock criteria: skills improve planning while preserving envelope authority.

## P5K BrainBench

Purpose: certify L4 Brain behavior.

Inputs:

```text
mission fixtures
expected allocation bands
belief update fixtures
debate trigger fixtures
cost and trace expectations
```

Outputs:

```text
BrainBenchReport
allocation_accuracy
belief_update_quality
debate_trigger_precision
information_gain_score
cost_efficiency
trace_integrity
```

Authority boundary: BrainBench is evaluation only.

Trace events: `BRAINBENCH_CASE_RUN`, `BRAINBENCH_REPORT_CREATED`.

Failure modes: benchmark overfitting, LLM judge drift, missing negative cases.

Tests: deterministic fixture suite plus negative authority-expansion cases.

Lock criteria: BrainBench passes and FinalGate rejects forged L4 traces.

## Phase Order

```text
P5A Brain L4 Architecture Audit
P5B MissionEntropyEstimator
P5C AgentCountController
P5D AgentSocietyManager
P5D.5 Capital Operator Doctrine
P5E MissionGlobalWorkspace
P5F BayesianBeliefState
P5G Adaptive Debate / Sparse MoA
P5H EpistemicActionEvaluator
P5I ResourcefulnessEngine / DebrouilleLane
P5J SkillProcedureGraph
P5K BrainBench
```
