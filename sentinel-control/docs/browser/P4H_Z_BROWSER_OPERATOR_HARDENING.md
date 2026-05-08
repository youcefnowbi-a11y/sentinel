# P4H-Z Browser Operator Hardening

Date: 2026-04-30
Status: Implemented

## Goal

P4H-Z stresses the P4H-X/P4H-Y browser operator loop under ambiguity, verifier
failure, weak perception, and budget pressure.

This is execution-heavy. The runner is:

```text
agent-lab/benchmarks/browser_tasks/browser_operator_hardening_runner.py
```

## Mission Groups

```text
BF-HARD-001-ambiguous-context-target
BF-HARD-002-low-confidence-ambiguous-reject
BF-HARD-003-dom-ax-weak-visual-ref
BF-HARD-004-failed-verifier-repair-loop
BF-HARD-005-multistep-budgeted-chain
BF-HARD-006-step-budget-pressure-reject
BF-HARD-007-visual-ocr-ref-denial
BF-HARD-008-fabricated-ref-denial
```

## Operator Path

The runner exercises:

```text
BrowserAccessibilitySnapshot
-> BrowserUIObservation
-> BrowserVisualObservation
-> BrowserPerceptionAdapter
-> PerceptionFrame
-> SceneActionCandidate
-> CompiledMissionPolicy
-> ActionEnvelope
-> BrowserControlledCapabilityRunner
-> BrowserLimitedInteractionExecutor
-> BrowserPostActionVerifier
-> CoreFinalGate
```

## Core Hardening

`ActionEngine` now enforces:

```text
action_budget_exceeded
max_steps_exceeded
repair_budget_exceeded
candidate_confidence_below_threshold
```

These are compiled-policy boundaries, not late audit findings.

## Boundary

No new browser powers were added.

P4H-Z remains:

```text
browser-only
fixture-backed
no desktop runtime
no OS mouse/keyboard
no new Browser V3 authority
no OCR authority
```
