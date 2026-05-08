# CORE 04 - Review Board

Date: 2026-04-27

This file reviews the core from the requested perspectives:

- coder;
- mathematician;
- algorithm designer;
- electronics/control systems;
- PC/operating systems;
- nervous/cognitive systems.

## 1. Coder Review

### Concern

The current code has a good mission workflow, but it lacks an explicit `sentinel/agent/` runtime.

### Required Fix

Create a layer above `sentinel/mission/`.

Do not put cognition into `MissionRunner`.

Correct split:

```text
sentinel/agent/     = thinks, selects, supervises, reviews
sentinel/mission/   = authority, routing, execution boundary
sentinel/missions/  = mission-specific plans and artifact schemas
```

### Pass Criteria

- `MissionRunner` remains generic and boring.
- `AgentRuntime` owns cognitive phases.
- No GTM-specific logic enters generic agent runtime.

## 2. Mathematician Review

### Concern

The agent must be a state-transition system, not prose.

### Required Model

```text
S_t -> policy -> action -> S_t+1
```

Where state includes:

- mission;
- authority;
- context;
- uncertainty;
- plan;
- artifacts;
- risk;
- budget;
- trace.

### Invariants

- no authority bypass;
- no completion without success evaluation;
- no action without trace;
- no memory-as-authority;
- no unknown tool execution.

### Pass Criteria

Tests should assert invariants directly.

## 3. Algorithm Designer Review

### Concern

If action selection is vague, the agent becomes a script.

### Required Algorithms v0

- deterministic method selection;
- deterministic capability need selection;
- DAG planning through mission registry;
- risk route decision;
- sequential scheduler;
- reviewer repair route;
- learning proposal generator.

### Later Algorithms

- priority scheduling;
- confidence updates;
- budget-aware model routing;
- parallel workers;
- retrieval scoring;
- tool ranking.

### Pass Criteria

V0 can be simple, but every decision must be explicit and inspectable.

## 4. Electronics / Control Systems Review

### Concern

Powerful agents need feedback stability.

### Required Control Loop

```text
sense -> compare -> act -> measure -> correct
```

Mapping:

- sensor = context builder, trace, reviewer;
- desired state = mission success criteria;
- controller = cognitive cycle and planner;
- actuator = worker coordinator and mission runner;
- feedback = artifact review and success evaluator.

### Pass Criteria

The agent must not just run all steps blindly.

It must compare outputs to desired state before completion.

## 5. PC / Operating Systems Review

### Concern

An agent with tools is effectively an OS process with system calls.

### Required Model

- mission = process;
- worker = thread/task;
- tool call = system call;
- capability adapter = driver;
- mission authority = permissions;
- event bus = kernel log;
- kill switch = interrupt;
- safe executor = sandbox.

### Pass Criteria

The agent core should treat every external action as a controlled syscall.

No direct tool call from reasoning code.

## 6. Nervous / Cognitive Systems Review

### Concern

The agent needs working memory, attention, executive control, error correction.

### Required Model

- perception;
- attention;
- working memory;
- world model;
- planning;
- action selection;
- motor execution;
- error correction;
- memory consolidation.

### Pass Criteria

The runtime must store:

- known facts;
- assumptions;
- open questions;
- selected methods;
- missing capabilities;
- review findings.

Without these, it cannot reason over time.

## 7. Unified Verdict

The next build is not tools.

The next build is the agent's nervous system:

```text
AgentRuntime
AgentState
AgentContext
EventBus
CognitiveCycle
MethodSelector
CapabilitySelector
PlannerBridge
WorkerCoordinator
Supervisor
ReviewLoop
LearningLoop
```

Only after this passes tests should Sentinel add Tool Registry, browser, media, APIs, code agent, sidecar, or outbound powers.
