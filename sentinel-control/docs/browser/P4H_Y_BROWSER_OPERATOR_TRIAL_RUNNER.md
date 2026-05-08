# P4H-Y Browser Operator Trial Runner

Date: 2026-04-30
Status: Implemented

## Goal

P4H-Y proves that the P4H-X skeleton can move.

This is not a docs-only gate. It adds an executable runner:

```text
agent-lab/benchmarks/browser_tasks/browser_operator_trial_runner.py
```

## Execution Path

Each executable mission uses the real P4H-X and browser contracts:

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

## Mission Groups

```text
BF-OP-001-click-visible-target
BF-OP-002-fill-grounded-field
BF-OP-003-repair-stale-ref
BF-OP-004-deny-ocr-only-target
BF-OP-005-deny-out-of-policy-action
BF-OP-006-multistep-fast-policy
```

## Boundary

The runner is browser-only and fixture-backed.

It does not add:

```text
new browser powers
desktop runtime
host mouse/keyboard
image/pdf/video runtime
ungoverned action
OCR authority
```

## Operator Meaning

P4H-Y measures whether Sentinel can:

```text
observe
ground
prepare action
execute through existing runner
verify after action
repair stale refs
deny invalid targets
continue inside compiled mission policy
```
