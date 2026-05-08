# Brain State, Events, Replay, And Audit

Date: 2026-04-28
Status: Core Brain Lock documentation

## State Model

`AgentState` is the mutable cognitive state of one mission run. It tracks:

- phase;
- selected methods;
- capability needs;
- tool selection;
- hypotheses and verification tests;
- adversarial findings;
- cognitive actions;
- world-model predictions;
- objective scores;
- effort route;
- execution posture;
- repair counters;
- review findings.

State is mission-scoped. It cannot outlive or override the
`MissionAuthorityEnvelope`.

## Event Model

`AgentEvent` is frozen and append-only. It includes:

- event id;
- mission id;
- sequence;
- logical time;
- event type;
- phase before and after;
- actor;
- summary;
- payload;
- trace refs;
- parent event id;
- previous hash;
- event hash;
- timestamp.

The `EventBus` is the truth ledger for the brain. State snapshots are derived
from events. Events are not decorative logs.

## Hash-Chain Rule

Every event contains a hash linked to the previous event hash. This protects the
topology of the run:

```text
event_0.hash
event_1.previous_hash = event_0.hash
event_2.previous_hash = event_1.hash
...
```

If an event is removed, reordered, or mutated, replay/certification should fail.

## Required Event Families

The success path must include events for:

- context;
- orientation;
- methods;
- capabilities;
- tool policy;
- hypothesis review;
- world model and objective score;
- effort route;
- plan;
- execution posture;
- plan review;
- worker lifecycle;
- artifact review;
- repair decision;
- success evaluation;
- learning proposal;
- terminal completion.

Controlled local capability actions also require canonicalization,
execution/rejection, artifact capture, and receipt-linked events.

## Replay

`AgentTraceReplayer` reconstructs an `AgentStateSnapshot` from trace events.
The snapshot includes:

- final phase;
- trace hash;
- selected methods/tools;
- missing capabilities;
- verified/rejected hypotheses;
- selected action;
- effort route;
- execution posture;
- direct tool-call budget;
- repair state;
- controlled capability counts;
- project path;
- success;
- evidence chain ids and types.

Replay must match the `AgentRunResult.state_snapshot`.

## Runtime Certification

`RuntimeCertificationGate` checks whether a trace is structurally acceptable:

- mission consistency;
- hash-chain integrity;
- terminal state;
- planning and execution visibility;
- evidence chain presence where required;
- errors recorded when certification fails.

The certification stored in `AgentRunResult.runtime_certification` must match a
fresh certification computed from the trace.

## Audit

`AgentTraceAuditor` and the final gate are not optional tooling. They are the
reason future external powers can be trusted. A run is not brain-certified just
because it produced files; it is certified only if its trace, state, evidence,
policy, receipts, and final phase agree.

## Failure Handling

Failures must still be auditable. A failed run should preserve:

- the mission id;
- the trace up to failure;
- the terminal event;
- runtime certification result;
- replay snapshot;
- learning proposal if the runtime reached a phase where bounded proposal was
  possible.
