# Brain Runtime Flow

Date: 2026-04-28
Status: Core Brain Lock documentation

## Top-Level Flow

`AgentRuntime.run()` is the canonical brain loop.

The success path is:

```text
created
-> initialized
-> context_building
-> orienting
-> method_selecting
-> capability_selecting
-> tool_selecting
-> hypothesis_verifying
-> action_scoring
-> effort_routing
-> planning
-> plan_reviewing
-> executing
-> artifact_reviewing
-> repair_deciding
-> optional repairing
-> success_evaluating
-> learning_proposing
-> completed | failed | blocked | escalated | revoked
```

The runtime writes trace events as it moves through this flow. The final result
must include the trace, runtime certification, replay snapshot, evidence chains,
review findings, learning proposals, mission result, and active plan when
available.

## Phase Details

### 1. Initialize

Creates an `EventBus` for the mission id, initializes `AgentState`, and emits
`AGENT_INITIALIZED`.

### 2. Context Build

`ContextBuilder` creates `AgentContext` from:

- `MissionAuthorityEnvelope`;
- user input;
- evidence refs;
- memory items.

The supervisor checks that the mission can run and that context did not expand
authority.

### 3. Context Compression

`ContextCompressor` reduces context while preserving evidence refs and mission
authority. Compression is deterministic and does not authorize anything.

### 4. Orientation

`CognitiveCycle` updates the working state with active facts, assumptions,
suspicions, and open questions.

### 5. Method Selection

`MethodSelector` selects deterministic work methods and records them in state.

### 6. Capability Selection

`CapabilitySelector` declares needed capabilities from the mission and selected
methods. The supervisor checks that capabilities are declared rather than
hallucinated.

### 7. Tool Selection

`ToolSelector` maps capability needs to registry tools under mission authority.
It emits policy decisions and produces:

- selected tools;
- candidate tools;
- blocked tools;
- unavailable capabilities;
- missing capabilities.

Critical findings block execution and move to learning proposals.

### 8. Hypothesis Verification

`HypothesisVerifier` generates hypotheses, runs deterministic verification
tests, creates adversarial findings, and emits a hypothesis evidence chain.

Critical hypothesis findings block execution.

### 9. Action Scoring And Effort Routing

`ActionEvaluator` uses the world model and objective scoring to evaluate
cognitive actions. `EffortRouter` uses uncertainty, verification quality, risk,
and budget pressure to select the effort level.

### 10. Planning

`PlannerBridge` creates a `MissionPlan` from:

- context;
- selected methods;
- capability needs;
- selected tool policy;
- verified hypotheses.

The planner must not receive unverified hypotheses as planning facts.

### 11. Execution Posture

`ExecutionPosturePolicy` selects how aggressively Sentinel can use already
granted local reversible authority. It does not grant new tools, paths, actions,
systems, credentials, or network access.

### 12. Plan Review

`ReviewLoop` checks the plan against capabilities, selected tools, and verified
hypotheses. Critical plan findings block execution.

### 13. Controlled Execution

Execution happens through two bounded routes:

- direct controlled local capability calls, if budget and posture allow them;
- `WorkerCoordinator` -> `MissionRunner` for mission plan execution.

Both routes must emit trace events and receipts for artifacts.

### 14. Artifact Review

Artifacts and mission results are reviewed before success evaluation. Worker
lifecycle must close with `WORKER_COMPLETED` even if the worker crashes.

### 15. Repair Decision

`CognitiveRepairLoop` computes a bounded repair decision. Repair can trigger one
internal repair pass only when cycles and action budget allow it.

### 16. Success Evaluation

Success requires a successful mission result and no critical unresolved
findings. The runtime emits `SUCCESS_EVALUATED` and builds a success evidence
chain.

### 17. Learning Proposal

`LearningLoop` creates proposal-only improvements. Learning cannot mutate
policy, tools, prompts, code, permissions, or authority.

### 18. Terminal Phase

The runtime emits one terminal event:

- `AGENT_COMPLETED`;
- `AGENT_FAILED`;
- `AGENT_BLOCKED`;
- `AGENT_ESCALATED`;
- `AGENT_REVOKED`.

The terminal phase must match the result success flag and the final trace event.

## Exception Flow

Exceptions are not silent. The runtime maps exceptions to bounded terminal phases:

- `MissionRevokedError` -> `REVOKED`;
- `AgentBlockedError` or invariant violation -> `BLOCKED`;
- other exceptions -> `FAILED`.

When possible, the runtime writes a bounded learning proposal before the terminal
failure event.
