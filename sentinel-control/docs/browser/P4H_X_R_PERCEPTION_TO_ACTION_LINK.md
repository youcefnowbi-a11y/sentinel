# P4H-X-R Perception To Action Link

Date: 2026-04-30
Status: Research lock

## Problem

A visual model can see a target without knowing whether Sentinel may act on it.
This is where many computer-use agents become brittle.

Sentinel must split the flow:

```text
perceive -> ground -> propose -> compile -> execute -> verify
```

## Core Objects

```text
PerceptionTarget
  visible target with bbox, label, confidence, proof refs

SceneActionCandidate
  proposed action over a target, still not executable

PerceptionActionLink
  binding between target, runtime ref, action class, and confidence

VisualActuationPlan
  ordered action plan grounded in visual + structural evidence

ActionEnvelope
  executable unit after compiled mission policy and ToolIntentCompiler approval

PostActionVerifier
  expected state change, before/after evidence, verdict
```

## Valid Action Link

An action link is valid only if:

```text
target is visible
target is understood with sufficient confidence
target maps to a runtime ref or supported coordinate contract
target is fresh for the current frame/snapshot
action class exists in CompiledMissionPolicy
ToolIntentCompiler accepts the canonical action
required receipt and verifier type are declared
```

## Invalid Action Link

Reject or repair when:

```text
OCR-only target
LLM-invented ref
stale ref
ambiguous repeated target
prompt-injected visual text
missing receipt type
missing verifier type
out-of-scope domain/path/action
```

## Browser v0

For the first implementation:

```text
SceneActionCandidate -> existing browser controlled runners
```

Do not build desktop actuation yet.

## Tempo Rule

When the policy grants the action and the link is valid:

```text
execute without extra conversational friction
```

When the link crosses a boundary:

```text
reject or escalate immediately
```
