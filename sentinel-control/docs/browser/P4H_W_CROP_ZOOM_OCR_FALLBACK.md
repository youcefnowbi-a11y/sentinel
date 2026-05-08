# P4H-W Crop, Zoom, OCR Fallback

Date: 2026-04-30
Status: Locked

## Crop

P4H-W captures a real element screenshot through the existing read-only browser
renderer. The crop is stored as a bounded artifact and linked to:

```text
runtime ref
bbox
source screenshot hash
page hash
snapshot hash
artifact hash
FinalGate trace
```

## Zoom

The zoom observation is a metadata-level observation over the same bounded crop
artifact. It is used to prove the escalation path:

```text
DOM/AX enough -> no OCR
DOM/AX weak -> crop/zoom
crop/zoom weak -> OCR fallback evidence only
```

## OCR Fallback

P4H-W keeps OCR as a stub/evidence fallback. The runner checks the fallback
boundary rather than adding a heavyweight OCR dependency.

Required rule:

```text
OCR text may support an evidence summary.
OCR text may not mint authority.
OCR text may not create a runtime ref.
OCR text may not bypass ToolIntentCompiler.
```

## Missions

```text
BF-VIS-001 viewport screenshot hash binding
BF-VIS-002 element crop bound to runtime ref and bbox
BF-VIS-003 zoom observation bound to crop artifact
BF-VIS-004 OCR fallback evidence with no action authority
BF-VIS-005 post-action visual verifier proof
BF-VIS-006 OCR-only or stale ref downgrade/repair
```
