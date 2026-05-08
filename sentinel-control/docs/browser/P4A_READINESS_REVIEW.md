# P4A-R Browser V2.5 Readiness Review

Date: 2026-04-29
Status: accepted

## Direct Verdict

P4A is ready as Browser V2.5 public/stateless perception and grounding layer.

It can be used before P4B because the new outputs are trace-bound, hash-bound,
FinalGate-checked, and mapped to brain/LLM consumption paths. P4A-R does not add
new runtime power and does not open Browser V3 authority classes.

## Reviewed Scope

P4A-R reviewed:

- `BrowserUIObservation` consumption by Browser-Cortex and ContextPack;
- CDP AX and DOMSnapshot hash/ref binding;
- visual crop/zoom metadata usage;
- public pool lease/release ordering;
- public multi-tab trace/lifecycle coherence;
- post-action verifier integration with repair signals;
- loop detector integration with repair/effort routing;
- FinalGate rejection of forged V2.5 events;
- EvalBench coverage for P4A.

## Findings

| Area | Verdict | Notes |
| --- | --- | --- |
| UIObservation | Pass with P4B bridge requirement | The model is a unified reasoning surface. Before P4B execution classes, P4B planners must bind actions to UIObservation refs or stable browser refs. |
| CDP AX / DOMSnapshot | Pass | Both adapters emit canonical hashes and counts, and FinalGate rejects hash/count mismatch. |
| Visual crop/zoom | Pass | Metadata is bounded, OCR remains a stub, and FinalGate checks source screenshot hash and bytes. |
| Public pool | Pass | Lease/release ordering is stateless and FinalGate rejects stateful forged events. |
| Public multi-tab | Pass | Strategy events bind to lifecycle trace refs and enforce `max_tabs`. |
| Post-action verifier | Pass | Verifier emits receipt-bound before/after snapshot hashes and findings. |
| Loop detector | Pass | Repeated state keys become explicit loop events. |
| FinalGate | Pass | V2.5 events are rejected when forged, hash-inconsistent, stateful, or structurally incomplete. |
| EvalBench slice | Pass | Targeted tests cover accepted and forged P4A paths. |

## Current Consumption Status

Browser-Cortex currently consumes the core Browser V2 event surface:

```text
BROWSER_EVIDENCE_COLLECTED
BROWSER_SNAPSHOT_CAPTURED
BROWSER_INTERACTION_PLAN_CREATED
BROWSER_INTERACTION_EXECUTED
browser rejection events
```

P4A events are currently consumed through:

```text
EventBus trace
-> FinalGate V2.5 contract
-> docs/contracts
-> P4B required preflight mapping
```

That is acceptable for P4A-R because P4A is a perception/readiness layer, not a
new action authority class. For P4B, each new authority class must explicitly
reference the P4A observation or verification surfaces it depends on.

## Required P4B Preflight Rule

Every P4B authority class must declare:

- which P4A observation sources it requires;
- whether AX, DOMSnapshot, visual observation, or multi-tab evidence is needed;
- how refs are bound to page/snapshot hashes;
- what post-action verifier condition must pass;
- which loop detector state key prevents repeated attempts;
- which ContextPack fields expose the proof to the LLM.

## Non-Delegated Powers Confirmed

P4A-R confirms P4A did not add:

- login;
- cookies/storage;
- private sessions;
- submit/post/send/publish;
- upload/download execution;
- arbitrary JavaScript evaluate;
- credentials/payment;
- remote browser node.

## Acceptance

P4A-R passes because:

- no new runtime power was added;
- P4A outputs are mapped to brain and LLM consumption;
- P4B is split into explicit authority classes;
- tests and scans pass;
- `P4B_AUTHORITY_CLASS_PLAN.md` defines the next phase boundaries.

## Final Decision

P4A-R is accepted.

Next phase can be P4B only if each Browser V3 power enters as a separate
authority class with request model, mission authority field, tool registry
manifest, receipt, event, FinalGate check, negative tests, EvalBench mission,
and rollback or quarantine behavior where applicable.
