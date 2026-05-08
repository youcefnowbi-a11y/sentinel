# SPINE 01 - Sentinel Agent Core Architecture

Date: 2026-04-27
Status: canonical architecture for P1A

## 0. Final Reset

This document replaces the previous broad planning direction for the current phase.

For P1A, Sentinel is not building:

- browser;
- OCR;
- image generation;
- video;
- sidecar;
- shell;
- real APIs;
- outbound sending;
- tool marketplace;
- generic assistant UI.

P1A builds only the cognitive core.

The goal is not to add more hands. The goal is to build the brain and nervous system that will later control the hands.

## 1. Core Thesis

Sentinel must not be defined as:

```text
LLM + tools
```

or:

```text
MissionRunner + capabilities
```

Sentinel must be defined as:

```text
bounded deliberative agent =
  identity
+ mission authority
+ state machine
+ perception
+ working memory
+ uncertainty state
+ world model
+ method selection
+ capability declaration
+ plan synthesis
+ action selection
+ worker coordination
+ review loop
+ learning proposal
+ trace ledger
```

If any of these components is missing, Sentinel is not yet an agent. It is a workflow executor.

## 2. What We Learned From The Vendor Agents

The vendor agents are specimens, not parents.

| Specimen | Real power | Fatal weakness | Sentinel rewrite |
| --- | --- | --- | --- |
| OpenClaw | execution gateway, plugins, channels, browser/shell surfaces | too much execution power too close to untrusted skills | typed action kernel under mission authority |
| Hermes | memory, context, skills, delegation | memory and hooks can become hidden policy | memory informs context but never grants authority |
| OpenJarvis | cost routing, local/cloud routing, workflow patterns | capability policy can become open-by-default | budget and effort routing as constraints, not freedom |
| JARVIS | sidecar, desktop, screen, clipboard, approval lifecycle | host-level blast radius | future typed sidecar, no raw shell, no silent desktop |

The shared failure:

```text
They built execution agents and called them cognitive agents.
```

Sentinel must do the reverse:

```text
build cognition first, then attach execution surfaces through typed authority.
```

## 3. Formal Agent Model

At time `t`, Sentinel state is:

```text
S_t = {
  M, A, C_t, W_t, U_t, P_t, F_t, B_t, R_t, K_t, T_t
}
```

Where:

- `M` = MissionAuthorityEnvelope, immutable during a run.
- `A` = AgentIdentity, immutable.
- `C_t` = AgentContext, current filtered context.
- `W_t` = WorkingMemory, active task memory.
- `U_t` = UncertaintyState.
- `P_t` = active plan DAG.
- `F_t` = produced artifacts.
- `B_t` = budget state: money, actions, time, repair cycles.
- `R_t` = current risk score.
- `K_t` = confidence state.
- `T_t` = append-only trace/event ledger.

The runtime transition is:

```text
S_t + event/action -> S_t+1
```

Every transition must be deterministic for known event types.

## 4. Objective Function

Sentinel should choose actions that maximize mission progress while minimizing unsafe change.

Action score:

```text
score(a | S) =
  + progress_gain(a, M)
  + evidence_gain(a)
  + artifact_quality_gain(a)
  + uncertainty_reduction(a)
  + learning_value(a)
  - risk_cost(a)
  - money_cost(a)
  - time_cost(a)
  - user_interrupt_cost(a)
```

This score does not grant permission.

Permission is checked by gates.

## 5. Execution Gates

Every candidate action must pass gates in this exact order:

```text
GATE 1: forbidden(action, mission) -> BLOCK
GATE 2: out_of_scope(action, mission) -> ESCALATE
GATE 3: black_zone(action) -> BLOCK
GATE 4: cost_exceeds_budget(action) -> ESCALATE
GATE 5: external_or_irreversible_or_sensitive(action) -> ESCALATE
GATE 6: unknown_tool_or_capability(action) -> REPORT_MISSING_CAPABILITY
GATE 7: local_reversible_in_scope(action) -> EXECUTE
```

The important distinction:

```text
unknown capability is not hallucinated into a tool call.
unknown capability becomes a declared missing capability.
```

## 6. Seven Core Invariants

These are the Sentinel constitution.

### INV-1 Authority

```text
execute(a) => a is inside MissionAuthorityEnvelope
```

### INV-2 State Transition

```text
every action consumes prior state and emits new state
```

### INV-3 Trace

```text
every trust-changing event is written to EventBus/TraceTimeline
```

### INV-4 Memory Boundary

```text
memory can influence context, but cannot expand authority
```

### INV-5 Capability Boundary

```text
unknown capability cannot execute
```

### INV-6 Completion

```text
mission completed => reviewer passed and success evaluator passed
```

### INV-7 Learning Safety

```text
learning output is proposal only, never automatic mutation
```

No future feature is allowed to violate these invariants.

## 7. Stability Conditions

Do not claim full mathematical proof yet.

What P1A can honestly guarantee:

- deterministic state transitions for known events;
- bounded action count;
- bounded budget;
- bounded repair cycles;
- exception phases are absorbing unless user intervention occurs;
- every transition is traceable;
- no unknown tool execution.

Termination condition:

```text
mission ends in one of:
  COMPLETED
  FAILED
  ESCALATED
  BLOCKED
  STOPPED
  REVOKED
```

No infinite mission loop is permitted.

## 8. Cognitive Architecture

The agent loop:

```text
1. identity load
2. mission intake
3. perception/context build
4. orientation
5. uncertainty modeling
6. method selection
7. capability declaration
8. plan synthesis
9. plan review
10. action selection
11. authority routing
12. worker execution
13. artifact review
14. repair if bounded and allowed
15. success evaluation
16. learning proposal
17. final trace
```

This is not a prompt chain. It is a state machine.

## 9. Nervous System Mapping

| Cognitive function | Sentinel module | Meaning |
| --- | --- | --- |
| identity | `identity.py` | what Sentinel is and refuses to be |
| senses | `context_builder.py` | receive user input, evidence, mission constraints |
| attention | `cognitive_cycle.py` | decide what matters now |
| working memory | `state.py` / `models.py` | active facts and task context |
| uncertainty | `uncertainty.py` | known, assumed, suspected, unknown |
| executive function | `method_selector.py` | choose how to think |
| needs declaration | `capability_selector.py` | declare needed powers, do not invent tools |
| planning | `planner_bridge.py` | connect cognition to mission DAG |
| motor dispatch | `worker_coordinator.py` | dispatch bounded worker tasks |
| reflex safety | `supervisor.py` + `invariants.py` | enforce authority and loop bounds |
| error correction | `review_loop.py` | review plan and artifacts |
| memory consolidation | `learning_loop.py` | create improvement proposals |
| nerves/logs | `event_bus.py` | append-only trace of state changes |

## 10. Operating System Mapping

Sentinel core should behave like a small operating system.

| OS concept | Sentinel concept |
| --- | --- |
| process | mission run |
| thread | worker task |
| syscall | proposed action |
| kernel permission | MissionAuthorityEnvelope |
| driver | future typed capability adapter |
| kernel log | EventBus |
| interrupt | escalation, pause, stop, revoke |
| sandbox | SafeExecutors |
| scheduler | WorkerCoordinator |

No direct external action is allowed from cognitive code.

All external action must pass as a typed syscall through mission authority.

## 11. Control System Mapping

Sentinel is a feedback controller.

```text
desired state = mission success criteria
current state = AgentState + artifacts + review findings
error = desired state - current state
controller = CognitiveCycle + MethodSelector + PlannerBridge
actuator = WorkerCoordinator + MissionRunner
sensor = EventBus + ReviewLoop + SuccessEvaluator
constraints = authority + budget + risk + time
```

The agent acts only to reduce mission error.

It does not act because a tool is available.

## 12. Module Boundaries

### `sentinel/agent/`

Owns cognition:

- state;
- context;
- uncertainty;
- methods;
- capability needs;
- supervision;
- review;
- learning proposal.

### `sentinel/mission/`

Owns authority and controlled execution:

- MissionAuthorityEnvelope;
- action routes;
- scope checks;
- budget;
- safe executors;
- timeline;
- artifact index.

### `sentinel/missions/`

Owns mission-specific planning:

- GTM planner;
- research planner;
- future launch/brand/code planners.

### Hard boundary

No cognition inside `MissionRunner`.

No direct execution inside `AgentRuntime`.

## 13. P1A File Architecture

P1A creates:

```text
sentinel-control/services/sentinel-core/sentinel/agent/
  __init__.py
  identity.py
  phases.py
  events.py
  models.py
  uncertainty.py
  event_bus.py
  state.py
  invariants.py
  context_builder.py
  context_compressor.py
  cognitive_cycle.py
  method_selector.py
  capability_selector.py
  planner_bridge.py
  worker_coordinator.py
  supervisor.py
  review_loop.py
  learning_loop.py
  runtime.py
```

## 14. What P1A Must Not Do

P1A must not:

- call real external APIs;
- open browser;
- run shell;
- send email;
- control desktop;
- install dependencies;
- mutate production code;
- create live tool registry;
- add sidecar;
- add image/video generation.

It may report these as missing capabilities.

## 15. P1A Proof Of Life

P1A succeeds when:

```text
AgentRuntime.run(envelope, user_input)
```

returns:

- final phase;
- selected methods;
- needed capabilities;
- missing capabilities;
- known facts;
- assumptions;
- suspected facts;
- unknown questions;
- event trace;
- review findings;
- learning proposals;
- mission result from existing MissionRunner.

And:

- no unknown capability executes;
- no memory expands authority;
- no mission completes without review and success evaluation;
- no risky runtime power is enabled.

## 16. North Star

Sentinel is born when it can say:

```text
I know my mission.
I know what I know.
I know what I do not know.
I know how I should think.
I know what capability I need.
I know what I am allowed to do.
I can act locally inside scope.
I can stop at the boundary.
I can review my own work.
I can propose how to improve without mutating myself.
```
