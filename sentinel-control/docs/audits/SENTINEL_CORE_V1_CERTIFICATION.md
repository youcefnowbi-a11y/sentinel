# Sentinel Core V1 Certification

Date: 2026-04-28

This document records the current certification boundary for the Sentinel agent
brain. It is a code-level certification of the local core runtime, not a claim
that browser, network, email, desktop, payment, credential, shell, or production
mutation powers are enabled.

## Certified Scope

- AgentRuntime cognitive loop from context building to terminal result.
- EventBus append-only trace with hash-chain verification.
- State replay, runtime certification, and CoreFinalGate checks.
- MissionAuthorityEnvelope separation from memory and user input.
- Capability manifest registry and policy decisions.
- Tool selection through registry and mission authority, without execution.
- Tool-call canonicalization with strict ambiguity rejection.
- Hypothesis verification, evidence chains, world-model scoring, effort routing.
- Bounded cognitive repair loop.
- Controlled local artifact execution for approved reversible local file writes.
- Artifact capture, receipts, rollback metadata, and final-gate binding.
- Execution posture for SAFE, OPERATOR, POWER, and related mission modes without
  expanding authority.

## Non-Negotiable Invariants

- Memory never grants authority.
- Mission authority is immutable during a run.
- Unknown tools do not execute.
- Candidate tools do not execute.
- Blocked/black-zone side effects do not execute.
- Every selected tool decision must be trace-bound.
- Every controlled execution must have a receipt bound to policy, tool call,
  capture, artifact id, path, and hash.
- Every controlled rejection result must be trace-bound.
- A worker crash must close its worker lifecycle before the runtime terminates.
- Learning output is proposal-only and requires human approval.
- Repair is bounded and cannot expand authority.

## Current Verification

Last local certification run:

```text
python -m pytest sentinel-control\services\sentinel-core\tests -q
300 tests passed
```

Additional checks:

- Python compile check over `sentinel` and tests passes.
- Public `sentinel.agent.__all__` has no missing exports or duplicates.
- Dangerous primitive scan currently shows only blocklists, classifiers, and
  fixture declarations, not live shell/browser/email/payment execution.

## Remaining Before External Powers

- Keep browser/network/email/desktop/shell/payment/credentials disabled until a
  separate P2 capability spec, sandbox, receipts, dry-run model, and final-gate
  contract exist.
- Before any new real capability, add fail-to-pass and pass-to-pass evals to
  SentinelEvalBench.
- Run a fresh code review on the exact new capability boundary before enabling it.
