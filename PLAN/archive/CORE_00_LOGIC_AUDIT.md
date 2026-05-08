# CORE 00 - Logic Audit

Date: 2026-04-27
Scope: everything created so far, judged by whether it helps build the actual agent core

## 1. Verdict

The user's objection is valid.

We created a lot of planning material. Much of it is useful, but the center of gravity drifted toward future capability surfaces:

- browser;
- OCR;
- image/video;
- public APIs;
- sidecar;
- outbound;
- tool registry;
- agent family.

Those are not wrong, but they are premature if the actual agent core is not defined.

The correct current focus is:

```text
build the mind and nervous system before adding more limbs
```

## 2. What We Have Built

### 2.1 Mission Kernel

The existing `sentinel/mission/` code is valuable.

It provides:

- mission authority envelope;
- mission state;
- mission action;
- escalation request;
- mission trace event;
- plan steps;
- artifact index;
- safe local executor;
- autonomy/risk routing;
- budget controller;
- reviewer;
- success evaluator;
- registry-based mission types.

This is not wasted work.

It is the agent's spinal cord and local motor safety layer.

### 2.2 Mission Types

Existing mission types:

- `gtm`;
- `research_summary`.

This proved the runner is not fully hardcoded to GTM.

But these mission types do not yet prove a true agent. They prove controlled workflows.

### 2.3 UI And Database Work

The Mission UI and Supabase migrations are useful later.

But UI should not drive the core.

For now, UI is secondary.

### 2.4 Agent Lab Research

The vendor forensics remain useful.

The durable extraction:

| Vendor | Useful Organ | Rewrite Into Sentinel |
| --- | --- | --- |
| OpenClaw | execution surfaces, gateway, plugins, channels | action/capability system under mission authority |
| Hermes | memory, context, skills, delegation | working memory, long-term memory, method/skill proposals without authority |
| OpenJarvis | routing, cost, local/cloud choices | future cost/effort router |
| JARVIS | sidecar, desktop, screen, clipboard | future permissioned I/O surfaces |

But none of those should be copied.

## 3. What Is Wrong With The Current Plan

### Problem A - Capability Before Cognition

We planned tool registry, API catalog, browser, OCR, media, sidecar.

But a registry does not make an agent.

The agent needs a runtime loop that decides:

- what matters;
- what is unknown;
- what method to use;
- what tools are needed;
- whether the current plan is good;
- whether to repair, continue, or escalate.

### Problem B - Layers Without Execution Semantics

The old plan said:

```text
Mission OS + Agent Foundry + Tool Intelligence + Capability Governance
```

This is directionally correct but incomplete.

Missing:

- state transition semantics;
- action selection algorithm;
- worker scheduling;
- confidence update;
- uncertainty handling;
- error correction;
- cognitive memory boundaries.

### Problem C - "Super Agent" Was Too Far Away

Jumping from mission kernel to super agent creates vague architecture.

The next step must be smaller and harder:

```text
make one agent runtime that can run existing missions intelligently
```

### Problem D - Too Many Root PLAN Files

The root `PLAN/` became noisy.

Resolution:

- archive broad future plans;
- keep only core docs now;
- future capabilities return only after the core runtime passes tests.

## 4. What The Agent Core Must Prove

A true Sentinel core must prove:

1. It has identity.
2. It receives mission authority.
3. It builds an internal state.
4. It builds context from evidence, memory, constraints, and available systems.
5. It chooses methods before tools.
6. It creates or asks mission planners for a plan.
7. It selects actions based on state, risk, cost, and confidence.
8. It dispatches workers.
9. It reviews output.
10. It repairs if possible.
11. It escalates at boundaries.
12. It traces every trust-changing event.
13. It produces learning proposals, not dangerous self-mutation.

If any of these are missing, Sentinel is not yet a full agent.

## 5. Current Code Gap

Current core code has:

```text
MissionRunner.run_mission()
```

This function:

- gets a mission definition;
- creates project directory;
- builds timeline;
- creates mission state;
- gets plan from mission planner;
- loops through plan steps;
- routes actions;
- executes safe actions;
- writes artifact index;
- runs reviewer and success evaluator.

This is good.

But it does not yet:

- orient around a mission;
- select methods;
- reason about unknowns;
- select tools/capabilities;
- coordinate different worker types;
- run a cognitive review/repair cycle;
- maintain working memory;
- create learning proposals.

So:

```text
MissionRunner = controlled workflow executor
AgentRuntime = missing cognitive operating system
```

## 6. Correct Next Move

Build:

```text
sentinel/agent/
```

as a layer above `sentinel/mission/`.

It should use the mission kernel, not replace it.

Correct relationship:

```text
AgentRuntime
  -> MissionAuthorityEnvelope
  -> AgentState
  -> ContextBuilder
  -> MethodSelector
  -> PlannerBridge
  -> WorkerCoordinator
  -> MissionRunner / AutonomyEngine / SafeExecutors
  -> ReviewLoop
  -> LearningLoop
```

## 7. Stop Rules

Do not implement yet:

- tool registry;
- live browser;
- live APIs;
- image/video generation;
- sidecar;
- outbound send;
- memory persistence;
- self-improvement mutation.

Implement only the agent core skeleton first.
