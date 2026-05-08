# CORE 01 - Agent Organism Architecture

Date: 2026-04-27

## 1. Design Principle

Sentinel should be modeled as an organism plus operating system.

Not metaphor for style. This gives concrete engineering boundaries.

```text
organism: perception, memory, attention, planning, action, feedback, learning
operating system: authority, scheduling, resources, drivers, interrupts, logs
control system: state, error, feedback loop, stability, constraints
```

## 2. The Core Agent

```text
SentinelCoreAgent
|
|-- Identity
|-- MissionAuthority
|-- PerceptionGateway
|-- ContextBuilder
|-- WorkingMemory
|-- WorldModel
|-- AttentionFilter
|-- MethodSelector
|-- Planner
|-- ActionSelector
|-- WorkerCoordinator
|-- Supervisor
|-- Reviewer
|-- TraceSystem
|-- LearningProposer
```

## 3. Nervous System Mapping

| Biological/System Concept | Sentinel Component | Engineering Meaning |
| --- | --- | --- |
| senses | PerceptionGateway | input from user, evidence, files, tools, future browser/media |
| thalamus/attention | AttentionFilter | decide what input matters now |
| working memory | WorkingMemory | temporary mission state and active facts |
| cortex/world model | WorldModel | structured knowledge about internet, PC, code, media, business, safety |
| prefrontal cortex | Planner/MethodSelector | choose methods and plan under constraints |
| basal ganglia | ActionSelector | choose next action from candidates |
| motor cortex | WorkerCoordinator | dispatch concrete work |
| spinal cord | MissionRunner/SafeExecutors | safe low-level action execution |
| cerebellum | Reviewer | error correction and quality check |
| autonomic system | Budget/KillSwitch/ScopeChecker | stability, resource limits, emergency stop |
| memory consolidation | LearningProposer | convert traces into future improvement proposals |

## 4. PC / Operating System Mapping

Sentinel also needs an OS-like architecture.

| OS Concept | Sentinel Equivalent |
| --- | --- |
| kernel | MissionAuthority + Supervisor |
| process | Mission run |
| thread/task | WorkerTask |
| scheduler | WorkerCoordinator |
| system call | Tool/capability call |
| driver | Capability adapter |
| permissions | MissionAuthorityEnvelope |
| interrupt | Escalation, kill switch, budget exceeded |
| logs | TraceTimeline/EventBus |
| filesystem | Artifact workspace |
| sandbox | SafeExecutor boundary |

This prevents vague "agent thinking".

Every action is a controlled system call from the agent to the world.

## 5. Electronics / Control System Mapping

The agent should behave like a feedback controller.

```text
desired state = mission success criteria
current state = AgentState + artifacts + evidence + review findings
error = desired state - current state
controller = CognitiveCycle + Planner + Reviewer
actuator = WorkerCoordinator + MissionRunner
sensor = PerceptionGateway + Trace + Reviewer
constraints = authority, budget, risk, time
```

Core control loop:

```text
measure -> compare -> choose correction -> act -> measure again
```

This gives Sentinel stability:

- no endless action loop;
- no action without state update;
- no completion without review;
- no escalation without reason;
- no learning without trace.

## 6. Mathematical Model

At any moment, Sentinel has state:

```text
S_t = {
  mission,
  authority,
  context,
  working_memory,
  plan,
  artifacts,
  budget,
  risk,
  confidence,
  open_questions,
  trace
}
```

It chooses an action:

```text
a_t = policy(S_t)
```

The action is valid only if:

```text
scope(a_t, mission) = true
risk(a_t) <= allowed_threshold
cost(a_t) <= remaining_budget
authority(a_t) = granted
```

Objective function:

```text
maximize:
  mission_success
+ evidence_quality
+ artifact_quality
+ learning_value

minimize:
  risk
+ cost
+ uncertainty
+ user_interruptions
+ irreversible_side_effects
```

This means Sentinel should not ask permission for everything.

It should ask only when the expected risk of acting exceeds the mission authority boundary.

## 7. Algorithmic Core

The agent loop:

```text
1. Intake mission
2. Build context
3. Identify knowns / unknowns / constraints
4. Select reasoning methods
5. Generate candidate plan
6. Review plan
7. Select next executable step
8. Route action through authority
9. Dispatch worker
10. Capture result
11. Review result
12. Repair or continue
13. Evaluate mission success
14. Emit learning proposal
```

## 8. Knowledge Domains The Core Must Represent

The agent core does not need to know all facts.

It needs structured operational models:

### Internet Model

- web content is untrusted;
- URLs identify sources;
- APIs have auth/cost/rate limits;
- browser state can contain credentials;
- forms mutate external state.

### PC / OS Model

- files can escape via paths/symlinks;
- shell can mutate host;
- environment variables may contain secrets;
- processes can persist;
- package install is supply-chain risk.

### Electronics / Device Model

- sensors read the world;
- actuators change the world;
- latency, energy, local compute, and hardware capability matter;
- raw capture can leak private information.

### LLM Model

- outputs can hallucinate;
- context can be injected;
- tool calls need validation;
- model effort costs money;
- confidence must be earned from evidence.

### Cognitive Model

- attention is limited;
- working memory is temporary;
- memory is not authority;
- reflection without action can loop;
- action without review can drift.

## 9. Core Boundary

The core agent is allowed to:

- reason;
- plan;
- select methods;
- request tools;
- coordinate safe workers;
- review artifacts;
- ask for escalation;
- write traces.

The core agent is not allowed to:

- call arbitrary tools directly;
- bypass mission authority;
- expand its own permissions;
- mutate production code;
- use credentials;
- contact external people;
- run shell;
- operate desktop;
- install dependencies.

Those powers come later through capability adapters.
