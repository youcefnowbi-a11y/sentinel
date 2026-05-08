# P4H-X PerceptionEngine v0

Date: 2026-04-30
Status: Implemented

## Goal

P4H-X turns the browser visual slice into the first active backend of a
generic perception model.

```text
BrowserUIObservation / BrowserVisualObservation
-> BrowserPerceptionAdapter
-> PerceptionFrame
```

## Code

```text
sentinel.agent.perception.models
sentinel.agent.perception.engine
sentinel.agent.browser.perception_adapter
```

## Active Backend

Only `browser` is active in v0.

Future source types exist only as typed vocabulary:

```text
desktop
image
pdf
video_frame
```

`PerceptionEngine` rejects those source types until their own authority,
adapter, runner, receipt, verifier, and FinalGate contracts exist.

## Model

`PerceptionFrame` contains:

```text
mission_id
source_type
source_url
page_sha256
snapshot_sha256
visual_artifact_sha256
viewport
regions
texts
targets
evidence
confidence
frame_sha256
trace_refs
```

Targets preserve the constitution:

```text
visible != understood != actionable != authorized
```

`PerceptionTarget.authorized` is forbidden at the perception layer. The
ActionEngine can authorize a `PerceptionActionLink` only after compiled policy
checks pass.

## OCR Rule

OCR is represented as `PerceptionText(source="ocr")`.

It can support evidence, but it cannot:

```text
mint a runtime ref
mark a target actionable
authorize action
override DOM/AX/UIObservation
```

## Hash Binding

`PerceptionFrame.frame_sha256` is computed from stable frame content, not random
object ids. It binds page/snapshot/visual evidence into one scene object.
