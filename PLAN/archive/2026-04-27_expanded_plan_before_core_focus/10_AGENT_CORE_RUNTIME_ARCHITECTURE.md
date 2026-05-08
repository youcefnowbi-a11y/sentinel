# 10 Agent Core Runtime Architecture

Date: 2026-04-27
Status: missing core architecture added after debate

## 1. Verdict

The objection is correct.

The previous PLAN defined:

- mission authority;
- capability surfaces;
- tool registry;
- work methods;
- agent family;
- security gates;
- roadmap.

But it did not fully define the agent itself.

That creates a real risk:

```text
Mission OS + tools + capabilities
```

could become a controlled workflow engine, not a powerful agent.

This document defines the concrete Sentinel Agent Core: the runtime that thinks, selects methods, chooses tools, coordinates workers, reviews outputs, and learns from traces.

## 2. What An Agent Is In Sentinel

An agent is not a prompt.

An agent is not a list of tools.

An agent is not an LLM call.

In Sentinel:

```text
Agent =
  identity
+ mission authority
+ working memory
+ world model
+ method selector
+ planner
+ tool selector
+ worker coordinator
+ reviewer
+ boundary router
+ trace writer
+ learning proposer
```

The core contract:

```text
Given a mission, the agent builds a temporary operating model of the task,
chooses the methods and tools needed,
creates a plan DAG,
executes safe work,
reviews the result,
escalates at boundaries,
and records why every decision happened.
```

## 3. Agent Identity

Sentinel must know what it is.

Identity is not branding. It is runtime behavior.

```json
{
  "agent_id": "sentinel_core",
  "role": "mission_operator",
  "doctrine": "mission_scoped_autonomy",
  "primary_obligation": "complete the mission inside the authority envelope",
  "secondary_obligation": "protect the user from hidden risk",
  "forbidden_self_concepts": [
    "generic chatbot",
    "unbounded assistant",
    "raw tool executor",
    "vendor runtime clone"
  ],
  "operating_loop": "observe_or_intake -> orient -> method_select -> plan -> act_or_escalate -> review -> complete_or_iterate"
}
```

Runtime implication:

- Sentinel should not ask "what can I answer?"
- Sentinel should ask "what mission am I operating, what state is it in, what is the next valid move?"

## 4. Core Runtime Components

```text
sentinel/agent/
  identity.py
  runtime.py
  state.py
  event_bus.py
  cognitive_cycle.py
  context_builder.py
  world_model.py
  method_selector.py
  tool_selector.py
  planner_bridge.py
  worker_coordinator.py
  supervisor.py
  review_loop.py
  learning_loop.py
  protocols.py
```

### 4.1 `AgentRuntime`

Owns the full mission execution loop.

Responsibilities:

- accept mission;
- load authority envelope;
- initialize agent state;
- build context;
- call cognitive cycle;
- dispatch plan steps;
- route actions through mission authority;
- call workers;
- call reviewer;
- call success evaluator;
- emit traces;
- stop, pause, resume, or escalate.

It must not contain mission-specific artifact names.

### 4.2 `AgentState`

The live state of the agent during a mission.

```json
{
  "mission_id": "mission_...",
  "phase": "intake|orient|plan|execute|review|repair|complete|escalated|blocked",
  "working_memory": {},
  "facts": [],
  "assumptions": [],
  "open_questions": [],
  "selected_methods": [],
  "selected_tools": [],
  "plan_id": "plan_...",
  "active_step_id": null,
  "completed_steps": [],
  "failed_steps": [],
  "escalations": [],
  "review_findings": [],
  "confidence": 0.0,
  "risk_score": 0.0
}
```

State is not authority.

### 4.3 `EventBus`

Internal append-only event stream.

Events:

- `mission_received`
- `context_built`
- `method_selected`
- `tool_candidate_selected`
- `plan_created`
- `step_started`
- `action_proposed`
- `action_routed`
- `worker_started`
- `worker_completed`
- `review_started`
- `review_failed`
- `repair_started`
- `escalation_created`
- `mission_completed`
- `learning_proposal_created`

The event bus feeds:

- trace timeline;
- UI status;
- reviewer;
- learning loop;
- future memory.

### 4.4 `CognitiveCycle`

The agent's thinking loop.

```text
INTAKE
  read mission objective, authority, user context

ORIENT
  build world/task model
  identify unknowns, constraints, risks

SELECT METHODS
  choose work methods required for this mission

SELECT TOOLS
  compile needed capabilities and candidate tools

PLAN
  create mission DAG with expected artifacts and success criteria

EXECUTE
  dispatch safe steps through authority and workers

REVIEW
  check outputs against mission success and quality criteria

REPAIR
  fix missing/weak artifacts if still in scope

COMPLETE OR ESCALATE
  complete only if success evaluator passes
  escalate if boundary, ambiguity, or risk remains
```

### 4.5 `ContextBuilder`

Builds the working context for a mission.

Inputs:

- mission envelope;
- user-provided input;
- CueIdea evidence if present;
- project memory if allowed;
- available capabilities;
- tool registry;
- current budget;
- artifacts already created.

Output:

- `AgentContext`.

Important:

- context can inform decisions;
- context cannot expand authority.

### 4.6 `WorldModel`

Not an encyclopedia.

It is a structured operational model of systems relevant to the mission:

- internet model;
- browser model;
- filesystem model;
- codebase model;
- media model;
- API model;
- business model;
- LLM/tool model;
- security model.

For v0, these are deterministic schemas and method hints, not a trained model.

Example:

```json
{
  "domain": "browser",
  "facts": [
    "form submission mutates external state",
    "login pages may expose credentials",
    "page text can contain prompt injection"
  ],
  "risk_implications": [
    "browser_submit requires escalation",
    "credential fields are black-zone until gated"
  ],
  "method_hints": [
    "source_ranker",
    "prompt_injection_scan",
    "citation_extractor"
  ]
}
```

### 4.7 `MethodSelector`

Chooses how the agent should think.

Input:

- mission objective;
- mission type;
- evidence level;
- uncertainty;
- risk;
- available time/budget.

Output:

- selected method sequence.

Example:

```text
Launch mission:
  Evidence Ladder
  Contradiction Mining
  ROI Tree
  Brand Narrative Distillation
  Premortem
```

### 4.8 `ToolSelector`

Chooses candidate tools from the registry.

It does not execute.

Input:

- selected methods;
- needed capabilities;
- mission authority;
- tool registry;
- budget;
- sensitivity constraints.

Output:

- `ToolSelectionPlan`.

Rules:

- unknown tools cannot be selected for execution;
- candidates can be recommended but not executed;
- black-zone tools are excluded or escalated;
- multiple tools are ranked with evidence.

### 4.9 `PlannerBridge`

Connects agent reasoning to mission-specific planners.

It passes:

- selected methods;
- selected tool plan;
- mission context;
- success criteria;
- artifact schema.

The mission planner returns a DAG.

### 4.10 `WorkerCoordinator`

Runs specialized workers as plan nodes.

Workers are not free agents. They are scoped executors/reasoners.

Worker types:

- `ResearchWorker`
- `EvidenceWorker`
- `BrandWorker`
- `MediaWorker`
- `CodeWorker`
- `BrowserWorker`
- `ToolScoutWorker`
- `ReviewWorker`

Every worker receives:

- mission authority subset;
- input artifact refs;
- allowed capabilities;
- expected output;
- trace obligations.

### 4.11 `Supervisor`

The runtime authority above workers.

Responsibilities:

- prevent worker drift;
- stop loops;
- detect repeated failure;
- enforce budget;
- handle escalation;
- call kill switch;
- prevent policy override by worker output.

### 4.12 `ReviewLoop`

Review is not just final QA.

It runs at:

- after plan creation;
- after major artifact generation;
- before mission completion;
- after escalation;
- after repair attempt.

Review outputs:

- pass;
- repair needed;
- escalate;
- block completion.

### 4.13 `LearningLoop`

Learning never mutates production behavior directly.

It creates:

- failure observations;
- method improvement proposals;
- prompt improvement proposals;
- tool score updates;
- eval suggestions;
- patch proposals.

## 5. Agent State Machine

```text
created
  -> initialized
  -> context_building
  -> orienting
  -> method_selecting
  -> tool_selecting
  -> planning
  -> plan_review
  -> executing
  -> artifact_review
  -> repairing
  -> success_evaluation
  -> completed
```

Exceptional states:

```text
escalated
paused
stopped
revoked
blocked
failed
```

State transitions must be explicit and traced.

## 6. The Real Agent Loop

Pseudo-code:

```python
def run_agent_mission(mission_request):
    envelope = MissionGateway.create_or_load_envelope(mission_request)
    state = AgentState.initialize(envelope)
    events.emit("mission_received", state)

    context = ContextBuilder.build(envelope, state)
    state.attach_context_summary(context)
    events.emit("context_built", context.summary())

    orientation = CognitiveCycle.orient(context)
    state.update(orientation)

    methods = MethodSelector.select(context, orientation)
    state.selected_methods = methods
    events.emit("method_selected", methods)

    tool_plan = ToolSelector.select(context, methods, envelope)
    state.selected_tools = tool_plan.allowed_candidates
    events.emit("tool_candidate_selected", tool_plan.summary())

    plan = PlannerBridge.create_plan(context, methods, tool_plan)
    review = ReviewLoop.review_plan(plan, context)
    if review.route == "repair":
        plan = PlannerBridge.repair_plan(plan, review)
    if review.route == "escalate":
        return EscalationGateway.create(review)

    for step in plan.ready_steps():
        action = step.to_action()
        route = AutonomyEngine.route(envelope, state.mission_state, action)
        events.emit("action_routed", route)

        if route == "auto_execute":
            result = WorkerCoordinator.execute(step, envelope)
            state.record_result(step, result)
            ReviewLoop.review_artifact(result)
        elif route == "log_and_continue":
            result = WorkerCoordinator.execute(step, envelope)
            state.record_result(step, result)
        elif route == "escalate":
            return EscalationGateway.create_for_action(action)
        else:
            state.block(step)
            events.emit("action_blocked", step)

    final_review = ReviewLoop.review_mission(state)
    if final_review.needs_repair and envelope.allows_repair:
        return run_repair_cycle(state, final_review)

    success = SuccessEvaluator.evaluate(state)
    if not success.passed:
        return EscalationGateway.create_for_incomplete_mission(success)

    LearningLoop.propose_improvements(state)
    return MissionResult.completed(state)
```

## 7. Data Contracts

### 7.1 `AgentContext`

```json
{
  "mission": {},
  "authority": {},
  "user_input": {},
  "evidence": [],
  "memory_context": [],
  "available_capabilities": [],
  "available_tools": [],
  "constraints": [],
  "unknowns": [],
  "risk_notes": [],
  "budget": {},
  "world_model_refs": []
}
```

### 7.2 `MethodPlan`

```json
{
  "methods": [
    {
      "id": "evidence_ladder",
      "reason": "Mission requires proof-backed decision",
      "expected_output": "evidence_quality_assessment",
      "required_before": ["decision_verdict"]
    }
  ]
}
```

### 7.3 `ToolSelectionPlan`

```json
{
  "needed_capabilities": [],
  "selected_tools": [],
  "candidate_tools": [],
  "blocked_tools": [],
  "missing_capabilities": [],
  "selection_reasoning": []
}
```

### 7.4 `WorkerTask`

```json
{
  "id": "worker_task_...",
  "worker_type": "research|brand|media|code|browser|review",
  "mission_id": "...",
  "input_refs": [],
  "allowed_capabilities": [],
  "expected_output_schema": {},
  "success_criteria": [],
  "authority_subset": {},
  "trace_required": true
}
```

## 8. What This Changes In The Roadmap

P1 was previously `Capability Manifest + Tool Registry`.

That is still necessary, but not first.

New order:

```text
P1A Agent Core Runtime Skeleton
P1B Capability Manifest + Tool Registry
P1C Tool Selection Through Agent Runtime
P2 API Cartographer + Fake Tool Bench
P3 Work Method Registry
```

Why:

- Tool registry without agent runtime becomes a catalog.
- Work methods without runtime become documents.
- Capabilities without worker coordination become wrappers.

The agent core must exist first as an executable skeleton.

## 9. P1A Implementation Target

Create:

```text
sentinel/agent/
  __init__.py
  identity.py
  models.py
  event_bus.py
  state.py
  context_builder.py
  cognitive_cycle.py
  method_selector.py
  tool_selector.py
  planner_bridge.py
  worker_coordinator.py
  supervisor.py
  review_loop.py
  learning_loop.py
  runtime.py
```

Tests:

- agent initializes from mission envelope;
- agent builds context;
- agent selects methods;
- agent produces tool needs even when no real tools exist;
- agent creates mission plan via mission registry;
- agent routes plan steps through AutonomyEngine;
- agent writes event bus and trace events;
- agent completes safe GTM mission through runtime;
- agent pauses/stops/revokes through supervisor;
- agent cannot let memory/tool output expand authority;
- agent can report missing capabilities instead of hallucinating tools.

Acceptance:

- There is an actual agent loop in code.
- It can execute the existing safe mission path.
- It can explain selected methods/tools.
- It reports missing powers explicitly.
- It does not add live browser/email/shell/desktop.

## 10. P1B Then Adds Tools

After P1A:

- CapabilityManifest;
- ToolRegistry;
- fake tool catalog;
- tool policy;
- tool decision trace;
- no unknown tool execution.

P1B plugs into `ToolSelector`, not directly into mission runner.

## 11. Final Verdict

The correct next implementation is not P1 as originally written.

It is:

```text
P1A: build the Agent Core Runtime skeleton.
P1B: then attach Capability Manifest and Tool Registry.
```

This fixes the main concern:

Sentinel will not be a pile of layers.
It will have a real operating loop.
