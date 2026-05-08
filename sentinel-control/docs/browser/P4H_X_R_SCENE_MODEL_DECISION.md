# P4H-X-R Scene Model Decision

Date: 2026-04-30
Status: Research lock

## Constitution

```text
visible != understood != actionable != authorized
```

## Model

Perception side:

```text
PerceptionFrame
PerceptionRegion
PerceptionText
PerceptionTarget
PerceptionEvidence
PerceptionConfidence
PerceptionVerifierResult
```

Action bridge side:

```text
SceneActionCandidate
PerceptionActionLink
VisualActuationPlan
ActionEnvelope
PostActionVerifier
```

## Meaning

| Layer | Meaning | Authority |
| --- | --- | --- |
| `visible` | A pixel/structure/text signal exists. | None |
| `understood` | Brain or LLM can interpret it with confidence and proof. | None |
| `actionable` | The target maps to a valid runtime ref and action class. | Still none |
| `authorized` | Compiled mission policy grants that action class in scope. | Yes |

## Generic Perception Fields

```text
source_type
visual_artifact_hash
crop_hash
bbox
viewport
text_layer
ocr_layer
candidate_targets
confidence
uncertainty_reasons
proof_refs
trace_refs
```

## Browser-Specific Fields

```text
url
page_sha256
snapshot_sha256
dom_hash
ax_snapshot_hash
browser_ui_ref
browser_stable_ref
browser_receipt_id
```

## Decision

The future code location is:

```text
sentinel.agent.perception/
```

Browser integration belongs in:

```text
sentinel.agent.browser.perception_adapter.py
```

Action orchestration belongs in:

```text
sentinel.agent.action_engine.py
```

The perception kernel must not live inside `sentinel.agent.browser`, because it
will later serve desktop, image, PDF, and video backends.
