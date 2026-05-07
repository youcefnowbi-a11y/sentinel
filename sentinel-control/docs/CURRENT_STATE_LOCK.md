# Current State Lock

Date: 2026-05-07

## Phase

```text
current_phase = P5K_FULL_LOCKED
previous_phase = P5J_FULL_LOCKED
next_phase = P5L_BRAIN_L4_INTEGRATED_REVIEW
```

P5K is accepted as full locked. It implements `BrainBench` as the Brain L4
certification and evaluation layer. It does not execute external systems, grant
authority, add external powers, implement payment/spend runtime, trading runtime,
account creation, credential access, or authority expansion.

## Verification

```text
targeted P5K tests = 9 passed
targeted full P5 suite = 79 passed
full sentinel-core regression = 595 passed
targeted P5J tests = 6 passed
targeted P5I tests = 10 passed
targeted P5H tests = 7 passed
targeted P5G tests = 7 passed
targeted P5F tests = 6 passed
targeted P5E tests = 11 passed
targeted P5B/P5C/P5D neighbor tests = 23 passed
P5D.5 docs verification = diff check passed
targeted P5D tests = 11 passed
targeted P5B/P5C tests = 12 passed
```

Commands verified:

```bash
python -m pytest tests/test_agent_brainbench.py -v --tb=short
python -m pytest tests/test_agent_mission_entropy.py tests/test_agent_count_controller.py tests/test_agent_society_manager.py tests/test_agent_global_workspace.py tests/test_agent_bayesian_belief_state.py tests/test_agent_adaptive_debate.py tests/test_agent_epistemic_action.py tests/test_agent_resourcefulness_engine.py tests/test_agent_skill_procedure_graph.py tests/test_agent_brainbench.py -v --tb=short
python -m pytest tests -v --tb=short
python -m pytest tests/test_agent_skill_procedure_graph.py -v --tb=short
python -m pytest tests/test_agent_resourcefulness_engine.py -v --tb=short
python -m pytest tests/test_agent_epistemic_action.py -v --tb=short
python -m pytest tests/test_agent_adaptive_debate.py -v --tb=short
python -m pytest tests/test_agent_bayesian_belief_state.py -v --tb=short
python -m pytest tests/test_agent_global_workspace.py -v --tb=short
python -m pytest tests/test_agent_mission_entropy.py tests/test_agent_count_controller.py tests/test_agent_society_manager.py -v --tb=short
git diff --check -- sentinel-control/docs/CURRENT_STATE_LOCK.md sentinel-control/docs/brain
python -m pytest tests/test_agent_society_manager.py -v --tb=short
python -m pytest tests/test_agent_mission_entropy.py tests/test_agent_count_controller.py -v --tb=short
```

Full sentinel-core was rerun after P5K and passed.

## P5K Required Files

These files are required to preserve the P5K full lock:

```text
sentinel-control/services/sentinel-core/sentinel/agent/brainbench.py
sentinel-control/services/sentinel-core/sentinel/agent/events.py
sentinel-control/services/sentinel-core/sentinel/agent/__init__.py
sentinel-control/services/sentinel-core/tests/test_agent_brainbench.py
sentinel-control/docs/brain/P5K_BRAINBENCH_SCORECARD.md
sentinel-control/docs/brain/P5K_LOCK_VERDICT.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## P5K Locked Doctrine

`BrainBench` is evaluation only.

It produces:

```text
BrainBenchCase
BrainBenchReport
allocation_accuracy
belief_update_quality
debate_trigger_precision
information_gain_score
cost_efficiency
trace_integrity
negative authority-expansion cases
```

It may emit:

```text
BRAINBENCH_CASE_RUN
BRAINBENCH_REPORT_CREATED
```

BrainBench rejects forged L4 traces and authority-expansion attempts.

## P5J Required Files

These files are required to preserve the P5J full lock:

```text
sentinel-control/services/sentinel-core/sentinel/agent/skill_procedure.py
sentinel-control/services/sentinel-core/sentinel/agent/events.py
sentinel-control/services/sentinel-core/sentinel/agent/__init__.py
sentinel-control/services/sentinel-core/tests/test_agent_skill_procedure_graph.py
sentinel-control/docs/brain/P5J_SKILL_PROCEDURE_GRAPH_SCORECARD.md
sentinel-control/docs/brain/P5J_LOCK_VERDICT.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## P5J Locked Doctrine

`SkillProcedureGraph` is advisory only.

It produces:

```text
SkillProcedure
SkillProcedureMatch
ProcedurePrecondition
RequiredAuthority
CanonicalStep
SuccessProof
KnownFailureMode
```

It may emit:

```text
SKILL_PROCEDURE_MATCHED
```

Skill memory recommends procedures, but never grants authority or starts
execution.

## P5I Required Files

These files are required to preserve the P5I full lock:

```text
sentinel-control/services/sentinel-core/sentinel/agent/resourcefulness.py
sentinel-control/services/sentinel-core/sentinel/agent/events.py
sentinel-control/services/sentinel-core/sentinel/agent/__init__.py
sentinel-control/services/sentinel-core/tests/test_agent_resourcefulness_engine.py
sentinel-control/docs/brain/P5I_RESOURCEFULNESS_ENGINE_SCORECARD.md
sentinel-control/docs/brain/P5I_LOCK_VERDICT.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## P5I Locked Doctrine

`ResourcefulnessEngine` is advisory only.

It produces:

```text
ResourcefulnessDecision
DebrouilleLevel D0-D5
FallbackPlanSet
ToolSubstitutionDecision
PartialSuccessReport
AuthorityExtensionProposal
```

It may emit:

```text
RESOURCEFULNESS_ROUTED
FALLBACK_PLAN_CREATED
TOOL_SUBSTITUTION_PROPOSED
PARTIAL_SUCCESS_DECLARED
AUTHORITY_EXTENSION_PROPOSED
```

AuthorityExtensionProposal is proposal-only and cannot activate new authority.

## P5H Required Files

These files are required to preserve the P5H full lock:

```text
sentinel-control/services/sentinel-core/sentinel/agent/epistemic_action.py
sentinel-control/services/sentinel-core/sentinel/agent/events.py
sentinel-control/services/sentinel-core/sentinel/agent/__init__.py
sentinel-control/services/sentinel-core/tests/test_agent_epistemic_action.py
sentinel-control/docs/brain/P5H_EPISTEMIC_ACTION_EVALUATOR_SCORECARD.md
sentinel-control/docs/brain/P5H_LOCK_VERDICT.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## P5H Locked Doctrine

`EpistemicActionEvaluator` is advisory only.

It produces:

```text
EpistemicActionScore
expected_progress
expected_information_gain
risk_penalty
cost_penalty
authority_impact
total_action_value
```

It may emit:

```text
EPISTEMIC_ACTION_SCORED
```

Action value never authorizes execution. Unsafe high-information actions remain
blocked or proposal-only outside this evaluator.

## P5G Required Files

These files are required to preserve the P5G full lock:

```text
sentinel-control/services/sentinel-core/sentinel/agent/adaptive_debate.py
sentinel-control/services/sentinel-core/sentinel/agent/events.py
sentinel-control/services/sentinel-core/sentinel/agent/__init__.py
sentinel-control/services/sentinel-core/tests/test_agent_adaptive_debate.py
sentinel-control/docs/brain/P5G_ADAPTIVE_DEBATE_SPARSE_MOA_SCORECARD.md
sentinel-control/docs/brain/P5G_LOCK_VERDICT.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## P5G Locked Doctrine

`AdaptiveDebateRouter` is advisory only.

It produces:

```text
DebateRoute
DebateRolePlan
SparseMoAPlan
DebateAggregationPlan
unresolved_disputes
fan_in_limit
max_layers
max_debate_rounds
```

It may emit:

```text
DEBATE_ROUTED
MOA_LAYER_COMPLETED
DEBATE_AGGREGATED
```

Debate planning never executes agents, calls tools, or expands authority.

## P5F Required Files

These files are required to preserve the P5F full lock:

```text
sentinel-control/services/sentinel-core/sentinel/agent/belief_state.py
sentinel-control/services/sentinel-core/sentinel/agent/events.py
sentinel-control/services/sentinel-core/sentinel/agent/__init__.py
sentinel-control/services/sentinel-core/tests/test_agent_bayesian_belief_state.py
sentinel-control/docs/brain/P5F_BAYESIAN_BELIEF_STATE_SCORECARD.md
sentinel-control/docs/brain/P5F_LOCK_VERDICT.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## P5F Locked Doctrine

`BayesianBeliefState` is advisory only.

It produces:

```text
Belief
BeliefUpdate
EvidenceSupport
ContradictionSupport
belief_probability
belief_variance
posterior_update_reason
```

It may emit:

```text
BELIEF_STATE_UPDATED
```

Belief confidence informs cognition only. It never grants tools, actions, paths,
browser powers, payment powers, credentials, or authority.

## P5E Required Files

These files are required to preserve the P5E full lock:

```text
sentinel-control/services/sentinel-core/sentinel/agent/workspace.py
sentinel-control/services/sentinel-core/sentinel/agent/events.py
sentinel-control/services/sentinel-core/sentinel/agent/__init__.py
sentinel-control/services/sentinel-core/tests/test_agent_global_workspace.py
sentinel-control/docs/brain/P5E_MISSION_GLOBAL_WORKSPACE_SCORECARD.md
sentinel-control/docs/brain/P5E_LOCK_VERDICT.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## P5E Locked Doctrine

`MissionGlobalWorkspace` is the versioned shared cognition layer.

It produces:

```text
WorkspaceSnapshot
WorkspaceDelta
BroadcastSlice
WorkspaceFact
WorkspaceClaim
WorkspaceSignal
WorkspaceAgentOutput
WorkspaceOpenQuestion
WorkspaceRejectedClaim
```

It may emit:

```text
WORKSPACE_SNAPSHOT_CREATED
WORKSPACE_BROADCAST_PREPARED
WORKSPACE_DELTA_APPLIED
```

It stores facts, claims, questions, rejected claims, signal observations, and
agent outputs. It never grants tools, actions, paths, browser powers, payment
powers, credentials, or authority.

Rejected claims cannot be reintroduced as accepted facts.

Broadcast slices must be role-specific and minimized rather than dumping the
whole workspace.

## P5D.5 Required Files

These files are required to preserve the P5D.5 full lock:

```text
sentinel-control/docs/brain/P5D5_CAPITAL_OPERATOR_DOCTRINE.md
sentinel-control/docs/brain/P5D5_ADAPTIVE_OPERATING_ENVELOPE.md
sentinel-control/docs/brain/P5D5_SIGNAL_RESPONSIVE_SPEND_POLICY.md
sentinel-control/docs/brain/P5D5_LOCK_VERDICT.md
sentinel-control/docs/brain/P5A_BRAIN_L4_ROADMAP.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## P5D.5 Locked Doctrine

P5D.5 locks:

```text
RootAuthorityEnvelope = fixed user mandate boundaries
AdaptiveOperatingEnvelope = dynamic operating parameters inside root boundaries
SignalLedger = evidence for operating changes
BudgetReallocator = moves spend toward stronger signals without crossing authority
DynamicSpendPolicy = spend/hold/scale/cut/propose-extension doctrine
SpendDecisionTrace = reason, signal, risk, budget, receipt, and stop-condition proof
```

Core rule:

```text
Authority boundaries do not silently expand.
Operational allocation must adapt continuously inside those boundaries.
```

Current core still treats payment/spend/credential actions as blocked black-zone
actions. P5D.5 does not change runtime behavior.

If explicit spend authority is granted in a future runtime, Sentinel should be
able to act inside that authority rather than remain passive. Any action outside
root authority requires an `AuthorityExtensionProposal`.

## P5D Required Files

These files are required to preserve the P5D full lock:

```text
sentinel-control/services/sentinel-core/sentinel/agent/agent_society.py
sentinel-control/services/sentinel-core/sentinel/agent/events.py
sentinel-control/services/sentinel-core/sentinel/agent/__init__.py
sentinel-control/services/sentinel-core/tests/test_agent_society_manager.py
sentinel-control/docs/brain/P5D_AGENT_SOCIETY_SCORECARD.md
sentinel-control/docs/brain/P5D_LOCK_VERDICT.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## P5D Locked Doctrine

`AgentSocietyManager` is advisory only.

It consumes:

```text
AgentCountRoute
MissionEntropyEstimate
MissionAuthorityEnvelope
```

It produces deterministic outputs:

```text
AgentSocietyPlan
AgentRoleAssignment
AgentOutputContract
AgentRolePurpose
AgentSocietyPlanStatus
```

It may emit:

```text
AGENT_SOCIETY_PLANNED
AGENT_ROLE_ASSIGNED
```

Each role must map to at least one P5C.5 first-principles purpose:

```text
exploration
verification
aggregation
contradiction
cost control
context compression
authority-bound fallback
```

It must not grant:

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

It must not spawn agents and must not implement runtime multi-agent execution.

## P5C.5 Required Files

These files remain required to preserve the P5C.5 full lock:

```text
sentinel-control/docs/brain/P5C5_FIRST_PRINCIPLES_BRAIN_STACK.md
sentinel-control/docs/brain/P5C5_INFORMATION_THERMODYNAMICS_CONTRACT.md
sentinel-control/docs/brain/P5C5_ENTROPY_BUDGET_MODEL.md
sentinel-control/docs/brain/P5C5_MATH_TO_ALGORITHM_TRANSLATION.md
sentinel-control/docs/brain/P5C5_LOCK_VERDICT.md
```

## P5C Required Files

These files remain required to preserve the P5C full lock:

```text
sentinel-control/services/sentinel-core/sentinel/agent/agent_count.py
sentinel-control/services/sentinel-core/tests/test_agent_count_controller.py
sentinel-control/docs/brain/P5C_AGENT_COUNT_SCORECARD.md
sentinel-control/docs/brain/P5C_LOCK_VERDICT.md
```

## P5B Required Files

These files remain required to preserve the P5B full lock:

```text
sentinel-control/services/sentinel-core/sentinel/agent/mission_entropy.py
sentinel-control/services/sentinel-core/tests/test_agent_mission_entropy.py
sentinel-control/docs/brain/P5B_MISSION_ENTROPY_SCORECARD.md
sentinel-control/docs/brain/P5B_LOCK_VERDICT.md
```

## Boundary

Do not stop the P5 sprint unless a hard blocker appears.

Do not start the next organ.

Do not add new browser powers.

Do not implement runtime multi-agent execution.

Do not implement payment/spend runtime.

Do not implement trading runtime.

Do not implement account creation.

Do not silently expand authority.
