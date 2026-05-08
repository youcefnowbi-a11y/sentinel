# Sentinel Brain Documentation

Date: 2026-04-28
Status: Core Brain Lock documentation

This folder is the canonical documentation for the Sentinel brain before any
module harvest work starts.

The code is intentionally not moved into a `brain/` package yet. The current
runtime boundary remains:

```text
sentinel/agent/    cognition, event trace, replay, evidence, final gate
sentinel/mission/  authority, routing, controlled mission execution, timeline
sentinel/capabilities/ declared tool manifests and registry
```

## Current Certification Boundary

The current certification is code-level certification for the local core
runtime. It is not a claim that browser, network, email, desktop, payment,
credential, shell, sidecar, or production mutation powers are enabled.

Certified scope:

- mission-scoped `AgentRuntime` cognitive loop;
- append-only `EventBus` hash-chain trace;
- state replay and runtime certification;
- `MissionAuthorityEnvelope` separation from memory and user input;
- capability selection and tool selection without external execution;
- canonical tool-call parsing with ambiguity rejection;
- hypothesis verification, world-model scoring, effort routing;
- bounded cognitive repair;
- controlled local artifact execution for approved reversible local writes;
- artifact capture, receipts, rollback metadata, and final-gate binding;
- execution posture without authority expansion.

## Brain Lock Doctrine

The brain exists to answer five questions before any external power is allowed:

```text
What is the mission?
What authority was granted?
What does the agent know or not know?
Which action is allowed, useful, traceable, and reversible?
Can the result be reconstructed from evidence, receipts, and replay?
```

If the answer cannot be reconstructed, Sentinel should not consider the run
certified.

## Documents

| File | Purpose |
| --- | --- |
| `BRAIN_ARCHITECTURE.md` | Component map and ownership boundaries. |
| `BRAIN_RUNTIME_FLOW.md` | Exact run order from context building to final phase. |
| `BRAIN_STATE_EVENTS_REPLAY.md` | State machine, event bus, hash-chain, replay, audit. |
| `BRAIN_PUBLIC_CONTRACT.md` | Public brain interfaces and forbidden future-module bypasses. |
| `BRAIN_EVENT_CATALOG.md` | Current event catalog, payload contracts, replay/audit/final-gate use. |
| `BRAIN_AUTHORITY_POLICY.md` | Mission authority, posture, RiskRouter, black-zone. |
| `BRAIN_EVIDENCE_RECEIPTS_FINAL_GATE.md` | Evidence chains, receipts, artifact capture, final gate. |
| `BRAIN_EVAL_CERTIFICATION.md` | Test/eval strategy and freeze criteria. |
| `BRAIN_LIMITS_NEXT_INTERFACES.md` | What is still disabled and how future modules connect. |
| `BRAIN_REVIEW_MATRIX.md` | Module-to-invariant review matrix for code review. |
| `BRAIN_LOCK_FINAL_REVIEW.md` | Executed brain-lock review and certification evidence. |

## Non-Negotiable Invariants

- Memory never grants authority.
- Mission authority is immutable during a run.
- Unknown tools do not execute.
- Candidate tools do not execute.
- Blocked and black-zone side effects do not execute.
- Every tool selection decision is trace-bound.
- Every controlled execution has a receipt bound to policy, call, capture,
  artifact id, path, and hash.
- A worker crash closes the worker lifecycle before the runtime terminates.
- Learning output is proposal-only and requires human approval.
- Repair is bounded and cannot expand authority.
- POWER posture changes aggressiveness only inside already granted authority.

## Module Harvest Rule

After Brain Lock, external module work follows this sequence:

```text
local source first
-> official GitHub source if local source is incomplete
-> isolate module
-> forensic audit
-> extraction matrix
-> Sentinel capability contract
-> fake evals
-> adapter
-> controlled integration
```

Research priority is maintained in `agent-lab`, not in product docs. The brain
docs must describe only Sentinel-native interfaces and constraints.
- Eval harness: Sentinel-owned, inspired by production-like benchmark patterns.
