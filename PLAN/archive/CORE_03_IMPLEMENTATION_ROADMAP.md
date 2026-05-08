# CORE 03 - Implementation Roadmap

Date: 2026-04-27

## Rule

Do not add new powers until the agent core exists.

The next coding phase is:

```text
P1A - Agent Core Runtime Skeleton
```

## P1A Files

Create:

```text
sentinel-control/services/sentinel-core/sentinel/agent/
  __init__.py
  identity.py
  models.py
  event_bus.py
  state.py
  context_builder.py
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

No browser, email, shell, desktop, sidecar, payment, dependency install, real API calls, or media generation.

## P1A Build Order

### Step 1 - Agent models

Implement:

- `AgentIdentity`
- `AgentState`
- `AgentContext`
- `AgentEvent`
- `MethodRef`
- `CapabilityNeed`
- `WorkerTask`
- `WorkerResult`
- `LearningProposal`

### Step 2 - Event bus

Implement append-only in-memory event bus.

Purpose:

- feed trace;
- feed reviewer;
- feed UI later;
- feed learning proposal.

### Step 3 - Context builder

Build context from:

- mission envelope;
- user input;
- evidence refs;
- current mission capabilities;
- mission constraints;
- current project artifacts if any.

V0 can use deterministic summaries.

### Step 4 - Cognitive cycle

Implement deterministic phases:

- orient;
- identify constraints;
- identify unknowns;
- produce mission operating notes.

No LLM required for v0.

### Step 5 - Method selector

V0 rules:

- GTM/Launch missions select evidence ladder, contradiction mining, premortem, ROI tree.
- Research missions select source ranking, contradiction mining, evidence ladder.
- Code missions later select systems decomposition and test planning.

### Step 6 - Capability selector

V0 does not use real tool registry.

It emits needed capability names and marks missing capabilities.

Example:

```text
gtm mission -> local_file_write, gtm_pack_generation, outreach_draft_generation
launch mission later -> brand_assets, image_generation, browser_research
```

### Step 7 - Planner bridge

Connect `AgentRuntime` to existing `MissionRegistry`.

The agent asks the mission definition for a plan, then reviews it before execution.

### Step 8 - Worker coordinator

For v0:

- one local worker path;
- delegates execution to existing mission runner/executor components;
- records worker start/completion.

### Step 9 - Supervisor

Enforce:

- mission not revoked;
- max actions;
- max cost;
- no authority expansion;
- pause/stop/revoke handling.

### Step 10 - Review loop

Run review:

- after plan creation;
- after mission runner result;
- before completion.

### Step 11 - Learning loop

Generate proposal if:

- reviewer found issues;
- missing capability blocked quality;
- escalation occurred;
- mission failed.

No automatic changes.

### Step 12 - Agent runtime

Implement:

```python
AgentRuntime.run(envelope, user_input) -> AgentRunResult
```

It should call:

```text
context -> cognitive cycle -> method selector -> capability selector
-> planner bridge -> mission runner -> review loop -> learning loop
```

## P1A Tests

Required:

1. agent initializes with identity.
2. agent builds context from mission envelope.
3. agent selects methods for GTM mission.
4. agent reports needed capabilities.
5. agent reports missing future capabilities instead of hallucinating tools.
6. agent creates plan through mission registry.
7. agent runs existing safe GTM mission through runtime.
8. agent records event bus events.
9. agent review loop runs before completion.
10. agent creates learning proposal on failed mission.
11. memory/context cannot expand mission authority.
12. revoked mission cannot run.

## P1A Acceptance

Pass only if:

- `sentinel/agent/` exists;
- a safe GTM mission can run through `AgentRuntime`, not only `MissionRunner`;
- `AgentRuntime` shows selected methods and needed capabilities;
- missing capabilities are explicit;
- no new risky capability is enabled;
- tests pass.

## After P1A

Then:

```text
P1B - Capability Manifest + Tool Registry
```

Only after the agent loop exists should tools be registered.
