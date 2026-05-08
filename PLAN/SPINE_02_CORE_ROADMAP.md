# SPINE 02 - Sentinel Agent Core Roadmap

Date: 2026-04-27
Status: canonical implementation roadmap for P1A

## 0. Rule

Build only the core runtime.

No new powers.

No tools before the agent can reason about missing capabilities.

## 1. Phase P1A Goal

Create a deterministic AgentRuntime above the existing MissionRunner.

Current state:

```text
MissionRunner = controlled workflow executor
```

Target state:

```text
AgentRuntime = cognitive operating system
MissionRunner = spinal execution layer
SafeExecutors = local muscles
EventBus = nervous trace
ReviewLoop = correction system
LearningLoop = safe improvement proposal
```

## 2. Build Sequence

### Step 1 - Identity and phases

Files:

```text
identity.py
phases.py
events.py
```

Build:

- immutable `AgentIdentity`;
- `AgentPhase`;
- `AgentEventType`.

Acceptance:

- Sentinel has explicit identity and forbidden modes.
- All runtime phases are enumerated.
- Unknown phase transitions are impossible.

### Step 2 - Core models

Files:

```text
models.py
uncertainty.py
```

Build:

- `Fact`;
- `Assumption`;
- `Hypothesis`;
- `Question`;
- `UncertaintyState`;
- `MethodRef`;
- `CapabilityNeed`;
- `WorkerTask`;
- `WorkerResult`;
- `ReviewFinding`;
- `LearningProposal`;
- `AgentContext`;
- `AgentRunResult`.

Acceptance:

- The runtime can represent known, assumed, suspected, and unknown.
- Capability needs are declarative, not tool calls.
- Learning proposals require human approval.

### Step 3 - Event bus

Files:

```text
event_bus.py
```

Build:

- append-only in-memory event bus;
- monotonically ordered events;
- exportable event list.

Acceptance:

- every state transition can emit event;
- event bus cannot delete or rewrite events;
- events can be attached to final AgentRunResult.

Later:

- hash chain / Merkle style audit can come after v0.

### Step 4 - Agent state and invariants

Files:

```text
state.py
invariants.py
```

Build:

- `AgentState`;
- deterministic transition helper;
- invariant checker.

Required invariant checks:

- authority invariant;
- trace invariant;
- memory-not-authority invariant;
- capability declaration invariant;
- completion invariant;
- learning proposal invariant;
- bounded loop invariant.

Acceptance:

- invariant failures are explicit runtime failures;
- tests can call invariant checks directly;
- invariant logic is not hidden in the supervisor.

### Step 5 - Context builder and compressor

Files:

```text
context_builder.py
context_compressor.py
```

Build:

- context from mission envelope;
- user input;
- evidence refs;
- existing mission constraints;
- deterministic context summary;
- trace-ref preserving compression.

Acceptance:

- raw context can be summarized without losing mission ID, evidence refs, trace refs, and authority fields;
- context cannot add allowed actions/tools.

### Step 6 - Cognitive cycle

Files:

```text
cognitive_cycle.py
```

Build deterministic v0:

- orient mission;
- identify constraints;
- identify unknowns;
- identify risk notes;
- update uncertainty state.

Acceptance:

- no LLM required;
- no tool call;
- outputs are state updates only.

### Step 7 - Method selector

Files:

```text
method_selector.py
```

Build:

- deterministic rules by mission type.

V0 methods:

- evidence ladder;
- contradiction mining;
- premortem;
- ROI tree;
- source ranking for research summary.

Acceptance:

- GTM mission selects methods;
- research summary mission selects methods;
- unknown mission type selects safe generic methods or escalates.

### Step 8 - Capability selector

Files:

```text
capability_selector.py
```

Build:

- declare needed capabilities from selected methods and mission type;
- mark missing capabilities;
- do not execute anything.

Example:

```text
gtm -> local_file_write, gtm_pack_generation, outreach_draft_generation, watchlist_generation
future launch -> brand_assets, browser_research, image_generation marked missing
```

Acceptance:

- missing capability is reported;
- unknown capability is never turned into a fake tool call.

### Step 9 - Planner bridge

Files:

```text
planner_bridge.py
```

Build:

- connect AgentRuntime to existing MissionRegistry;
- request mission plan;
- attach method/capability context to planning event.

Acceptance:

- mission plans still come from `sentinel/missions/*`;
- no mission-specific artifact names in AgentRuntime.

### Step 10 - Worker coordinator

Files:

```text
worker_coordinator.py
```

Build v0:

- sequential worker coordinator;
- one local mission worker path;
- delegates to existing MissionRunner;
- records worker started/completed.

Acceptance:

- MissionRunner remains unchanged as much as possible;
- WorkerCoordinator owns the bridge between cognition and mission execution.

### Step 11 - Supervisor

Files:

```text
supervisor.py
```

Build:

- enforce invariant checks;
- enforce revoked/stopped mission;
- enforce bounded repair cycles;
- enforce no authority expansion;
- handle pause/stop/revoke as absorbing states.

Acceptance:

- revoked mission does not run;
- memory/context cannot expand authority;
- max repair cycles prevents infinite loop.

### Step 12 - Review loop

Files:

```text
review_loop.py
```

Build:

- review plan before execution;
- review mission result after MissionRunner;
- translate mission review into agent review findings.

Acceptance:

- no final completion without review;
- weak/missing artifacts produce review findings.

### Step 13 - Learning loop

Files:

```text
learning_loop.py
```

Build:

- learning proposal from failed mission;
- learning proposal from missing capabilities;
- learning proposal from escalation/block;
- no mutation.

Acceptance:

- every learning proposal requires human approval;
- no code/policy/tool/prompt mutation happens.

### Step 14 - Agent runtime

Files:

```text
runtime.py
```

Build:

```text
AgentRuntime.run(envelope, user_input)
```

Strict sequence:

```text
initialize
-> build_context
-> compress_context
-> orient
-> select_methods
-> select_capabilities
-> bridge_plan
-> review_plan
-> coordinate_worker
-> review_result
-> evaluate_success
-> propose_learning
-> finalize
```

Acceptance:

- the sequence cannot be shortcut;
- every phase emits an event;
- final result includes state, methods, capabilities, missing capabilities, review findings, learning proposals, and mission result.

## 3. Tests Required For P1A

Create:

```text
sentinel-control/services/sentinel-core/tests/test_agent_core_models.py
sentinel-control/services/sentinel-core/tests/test_agent_event_bus.py
sentinel-control/services/sentinel-core/tests/test_agent_invariants.py
sentinel-control/services/sentinel-core/tests/test_agent_runtime.py
```

Required tests:

1. identity is immutable.
2. state transitions are deterministic for known events.
3. event bus is append-only.
4. context builder cannot expand mission authority.
5. context compressor preserves mission ID, evidence refs, trace refs.
6. uncertainty state separates known, assumed, suspected, unknown.
7. GTM mission selects required methods.
8. capability selector reports missing future capabilities.
9. unknown capability does not execute.
10. planner bridge uses MissionRegistry.
11. AgentRuntime can run a safe GTM mission through MissionRunner.
12. AgentRuntime returns selected methods and capability needs.
13. revoked mission cannot run.
14. completion requires review.
15. learning proposal requires human approval.
16. bounded repair cycles prevent infinite loop.
17. memory/context cannot expand allowed actions.

## 4. P1A Definition Of Done

P1A is done only when:

- `sentinel/agent/` exists;
- all P1A tests pass;
- no risky runtime power is enabled;
- AgentRuntime can complete the current safe GTM mission;
- AgentRuntime can explain what methods it selected;
- AgentRuntime can explain what capabilities it needed;
- missing powers are explicit;
- MissionRunner remains execution-focused;
- no cognitive logic is moved into MissionRunner.

## 5. What Comes After P1A

Only after P1A:

```text
P1B - Capability Manifest And Tool Registry
```

P1B plugs into `CapabilitySelector`.

It does not bypass AgentRuntime.

## 6. Build Command Discipline

When implementation starts:

1. add models first;
2. add tests for models;
3. add event bus;
4. add invariant tests;
5. add runtime only after primitives are stable;
6. run sentinel-core tests after each meaningful slice.

Do not build from the UI inward.

Build from the core outward.

## 7. Final Roadmap Statement

The path is:

```text
P1A SPINE: cognitive core
P1B MANIFEST: tool/capability declaration
P1C SELECTION: capability selection through runtime
P2+ POWERS: browser, media, API, code, outbound, sidecar
```

No P2 power is allowed until P1A proves the agent has a brain.
