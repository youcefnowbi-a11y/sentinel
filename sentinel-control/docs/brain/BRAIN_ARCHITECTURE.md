# Brain Architecture

Date: 2026-04-28
Status: Core Brain Lock documentation

## Purpose

Sentinel's brain is the control system that turns a mission into bounded,
traceable work. It is not a browser, channel sender, desktop sidecar, shell, or
plugin marketplace.

The brain is split into three layers:

```text
AgentRuntime        cognitive controller
MissionRunner       controlled mission execution
SafeExecutors       local reversible artifact actions
```

This split must stay intact. Cognition does not belong inside
`MissionRunner`, and raw execution does not belong inside `AgentRuntime`.

## Main Packages

### `sentinel/agent/`

Owns cognition and certification:

- identity and doctrine;
- context building and compression;
- orientation and uncertainty;
- method and capability selection;
- tool selection decisions;
- hypothesis verification and adversarial findings;
- world-model prediction and objective scoring;
- effort routing;
- planner bridge;
- worker coordination;
- review, repair, and learning proposal;
- event bus, replay, audit, and final gate.

### `sentinel/mission/`

Owns authority and controlled mission execution:

- `MissionAuthorityEnvelope`;
- `MissionState`;
- `MissionAction`;
- `MissionPlan`;
- `RiskRouter`;
- `MissionTraceTimeline`;
- `MissionRunner`;
- `SafeMissionExecutors`;
- artifact receipts and rollback metadata.

### `sentinel/capabilities/`

Owns declared capability manifests and tool registry policy. A capability can
be considered only if it is declared and mapped through mission authority.

## Runtime Components

| Component | Role | Must not do |
| --- | --- | --- |
| `ContextBuilder` | Build context from mission, input, evidence, memory. | Grant authority from memory or user text. |
| `ContextCompressor` | Reduce context while preserving trace/evidence refs. | Drop authority, evidence refs, or critical findings. |
| `CognitiveCycle` | Populate active facts and open questions. | Execute tools. |
| `MethodSelector` | Choose deterministic methods. | Invent undeclared powers. |
| `CapabilitySelector` | Declare required capabilities. | Execute a capability. |
| `ToolSelector` | Classify registry tools under mission authority. | Treat candidates as executable. |
| `HypothesisVerifier` | Generate, verify, and attack hypotheses. | Pass unverified hypotheses to planning. |
| `ActionEvaluator` | Score internal/external cognitive actions. | Execute external actions. |
| `EffortRouter` | Select cognitive effort from uncertainty/risk/budget. | Expand budget or authority. |
| `ExecutionPosturePolicy` | Make local reversible work more or less aggressive. | Add tools, paths, systems, or actions. |
| `PlannerBridge` | Create a mission plan from selected tools and verified hypotheses. | Plan tools outside selected policy. |
| `WorkerCoordinator` | Invoke `MissionRunner` as the controlled worker. | Hide worker failure or skip lifecycle events. |
| `ReviewLoop` | Find plan/artifact/tool/hypothesis problems. | Approve completion outside authority. |
| `CognitiveRepairLoop` | Decide bounded internal repair. | Retry forever or expand authority. |
| `LearningLoop` | Produce improvement proposals. | Mutate code, policy, prompts, tools, or permissions. |
| `CoreFinalGate` | Certify trace, replay, evidence, receipts, budget, scope. | Accept untraceable success. |

## Authority Boundary

Authority lives in `MissionAuthorityEnvelope`, not in:

- memory items;
- user input;
- web content;
- vendor modules;
- skill text;
- model output;
- evidence summaries;
- learning proposals.

Every future module must submit to this boundary through a Sentinel capability
contract before it can execute.

## Execution Boundary

The current brain can perform only controlled local artifact work through
approved local reversible paths. It must not perform:

- browser automation;
- external network/API calls;
- email or channel send;
- shell/process execution;
- desktop/sidecar control;
- credential access;
- payment/spend;
- dependency install;
- production mutation.

These are future organs, not current brain functions.
