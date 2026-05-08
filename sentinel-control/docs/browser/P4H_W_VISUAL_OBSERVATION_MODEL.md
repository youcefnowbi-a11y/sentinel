# P4H-W Visual Observation Model

Date: 2026-04-30
Status: Locked

## Model

`BrowserVisualObservation` is now the bounded metadata object used by P4H-W.

Required proof anchors:

```text
mission_id
url
kind
region.bbox
region.source_screenshot_sha256
page_sha256
snapshot_sha256
viewport
ui_observation_ref_ids
artifact_id
artifact_sha256
observation_sha256
trace_refs
```

## Meaning

```text
source_screenshot_sha256 = rendered pixel state
page_sha256 = page text/representation hash from AX snapshot builder
snapshot_sha256 = AX/browser snapshot hash
ui_observation_ref_ids = Sentinel runtime refs, not LLM refs
artifact_sha256 = crop or zoom artifact hash
observation_sha256 = canonical hash of the metadata object
```

## Invariants

```text
visual observation is evidence, not authority
OCR text cannot mint action refs
runtime refs must come from Sentinel observations
crop/zoom must bind to a source screenshot hash
page/snapshot hashes must be present for P4H-W harness observations
FinalGate validates visual observation hashes and public/stateless flags
```

## Runtime Ref Rule

P4H-W uses element screenshot metadata bound to an accessibility ref. A visual
grounding candidate is valid only when:

```text
candidate.ref_id exists in the rendered accessibility snapshot
candidate.bbox has non-zero width and height
candidate.source is DOM/AX plus rendered element screenshot
candidate.stale is false
```

An OCR-only string cannot become a click target.
