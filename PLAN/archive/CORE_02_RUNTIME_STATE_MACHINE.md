# CORE 02 - Runtime State Machine

Date: 2026-04-27

## 1. Core Data Structures

### 1.1 `AgentIdentity`

```python
class AgentIdentity:
    id: str
    name: str
    role: str
    doctrine: str
    forbidden_modes: list[str]
    operating_loop: str
```

Purpose:

- prevents the system from becoming a generic assistant;
- gives the runtime stable behavioral boundaries.

### 1.2 `AgentState`

```python
class AgentState:
    mission_id: str
    phase: AgentPhase
    working_memory: dict
    known_facts: list[Fact]
    assumptions: list[Assumption]
    open_questions: list[Question]
    selected_methods: list[MethodRef]
    needed_capabilities: list[CapabilityNeed]
    selected_tools: list[ToolRef]
    missing_capabilities: list[CapabilityNeed]
    plan_id: str | None
    active_step_id: str | None
    completed_steps: list[str]
    failed_steps: list[str]
    review_findings: list[ReviewFinding]
    risk_score: float
    confidence_score: float
    cost_used: float
```

### 1.3 `AgentContext`

```python
class AgentContext:
    mission: MissionAuthorityEnvelope
    user_input: dict
    evidence_items: list
    memory_items: list
    available_methods: list
    available_capabilities: list
    available_tools: list
    constraints: list
    world_model_refs: list
```

### 1.4 `WorkerTask`

```python
class WorkerTask:
    id: str
    worker_type: str
    mission_id: str
    input_refs: list[str]
    expected_output: str
    allowed_actions: list[str]
    allowed_tools: list[str]
    authority_subset: dict
    success_criteria: list[str]
```

### 1.5 `WorkerResult`

```python
class WorkerResult:
    task_id: str
    status: str
    output_refs: list[str]
    facts_found: list
    assumptions_created: list
    open_questions: list
    risk_notes: list
    trace_refs: list[str]
```

## 2. Agent Phases

```text
CREATED
INITIALIZED
CONTEXT_BUILDING
ORIENTING
METHOD_SELECTING
CAPABILITY_SELECTING
PLANNING
PLAN_REVIEWING
EXECUTING
ARTIFACT_REVIEWING
REPAIRING
SUCCESS_EVALUATING
LEARNING_PROPOSING
COMPLETED
```

Exceptional phases:

```text
ESCALATED
PAUSED
STOPPED
REVOKED
BLOCKED
FAILED
```

## 3. State Transitions

```text
CREATED -> INITIALIZED
INITIALIZED -> CONTEXT_BUILDING
CONTEXT_BUILDING -> ORIENTING
ORIENTING -> METHOD_SELECTING
METHOD_SELECTING -> CAPABILITY_SELECTING
CAPABILITY_SELECTING -> PLANNING
PLANNING -> PLAN_REVIEWING
PLAN_REVIEWING -> EXECUTING
EXECUTING -> ARTIFACT_REVIEWING
ARTIFACT_REVIEWING -> EXECUTING
ARTIFACT_REVIEWING -> REPAIRING
REPAIRING -> EXECUTING
EXECUTING -> SUCCESS_EVALUATING
SUCCESS_EVALUATING -> LEARNING_PROPOSING
LEARNING_PROPOSING -> COMPLETED
```

Interrupt transitions:

```text
ANY -> ESCALATED
ANY -> PAUSED
ANY -> STOPPED
ANY -> REVOKED
ANY -> BLOCKED
ANY -> FAILED
```

## 4. Invariants

These are mathematical constraints.

### Authority Invariant

```text
No action can execute unless it is inside MissionAuthorityEnvelope.
```

### State Invariant

```text
Every action must consume prior state and produce new state.
```

### Trace Invariant

```text
Every trust-changing transition writes an event.
```

### Memory Invariant

```text
Memory may influence context, but it cannot grant authority.
```

### Tool Invariant

```text
Unknown or undeclared tools cannot execute.
```

This is enforced later by capability registry, but the agent core must already report missing tools instead of inventing them.

### Completion Invariant

```text
A mission cannot complete until reviewer and success evaluator pass.
```

### Externality Invariant

```text
External, irreversible, sensitive, costly, or low-confidence actions escalate.
```

## 5. Action Selection

Candidate action score:

```text
score(a) =
  + mission_progress_gain(a)
  + evidence_gain(a)
  + artifact_quality_gain(a)
  + learning_gain(a)
  - risk_cost(a)
  - money_cost(a)
  - time_cost(a)
  - uncertainty_cost(a)
  - user_interrupt_cost(a)
```

Action route:

```text
if forbidden(a): block
elif out_of_scope(a): escalate
elif black_zone(a): block
elif external_or_irreversible_or_sensitive(a): escalate
elif local_reversible_in_scope(a): auto_execute
else: log_and_continue
```

## 6. Worker Scheduling

For v0:

- deterministic sequential execution;
- DAG dependencies respected;
- no parallel workers yet.

Future:

- parallel independent workers;
- budget-aware scheduling;
- model effort routing;
- retry policy with loop guard.

V0 scheduler:

```text
ready_steps = steps where dependencies complete
choose next step by:
  1. required for success
  2. low risk
  3. high progress
  4. low cost
```

## 7. Review Loop

Review checks:

- mission drift;
- missing artifacts;
- missing evidence;
- generic output;
- unresolved assumptions;
- WTP gap for GTM/launch;
- tool/capability gaps;
- authority boundary events.

Review routes:

```text
pass -> continue
repair -> create repair tasks
escalate -> ask user
block_completion -> fail success evaluator
```

## 8. Learning Loop

Learning output is a proposal only.

```python
class LearningProposal:
    observed_failure: str
    evidence_refs: list[str]
    proposed_change: str
    risk: str
    tests_needed: list[str]
    requires_user_approval: bool = True
```

No automatic:

- policy mutation;
- prompt mutation;
- code mutation;
- tool installation;
- permission expansion.
