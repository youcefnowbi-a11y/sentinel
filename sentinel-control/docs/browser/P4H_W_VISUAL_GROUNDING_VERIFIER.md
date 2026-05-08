# P4H-W Visual Grounding Verifier

Date: 2026-04-30
Status: Locked

## Grounding Candidate

P4H-W introduces the benchmark-level `BrowserVisualGroundingCandidate`:

```text
ref_id
role
name
bbox
confidence
source
stable_ref_bound
stale
```

This object is not a new Sentinel runtime authority. It is a lab proof object
used to score whether a visual target is grounded in Sentinel runtime evidence.

## Valid Candidate

```text
ref_id exists in accessibility snapshot
role/name come from DOM/AX
bbox comes from rendered element screenshot metadata
source = dom_ax_plus_element_screenshot
stable_ref_bound = true
stale = false
```

## Invalid Candidate

```text
OCR text only
LLM-invented ref
stale snapshot/page hash
missing crop artifact
missing source screenshot hash
missing FinalGate trace
```

## Post-Action Visual Verifier

P4H-W emits `BROWSER_VERIFICATION_COMPLETED` with:

```text
checked_receipt_id
before_snapshot_sha256
after_snapshot_sha256
expected_visual_change
verdict
trace_ref_count
public/stateless boundary flags
```

The verifier is checked by the existing Browser V2.5 FinalGate contract.

Boundary: this is a controlled local visual verifier slice. It does not add a
new browser action primitive.
