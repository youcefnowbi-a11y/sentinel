# P4H-W-R Sentinel Visual Architecture

Date: 2026-04-30
Status: Research architecture

## Principle

Browser visual perception must remain governed by Sentinel's existing doctrine:

```text
browser sees
brain verifies
LLM reasons from bounded ContextPack
proof decides
```

Visual evidence is never authority.

## Proposed P4H-W Architecture

```text
BrowserRenderedFrame
  -> full viewport screenshot hash
  -> viewport size / device scale factor
  -> URL / page hash / snapshot hash

BrowserVisualRegion
  -> crop hash
  -> bbox
  -> source screenshot hash
  -> target stable ref if available

BrowserVisualGroundingCandidate
  -> ref_id
  -> role/name/text
  -> bbox
  -> DOM path / AX path
  -> visual label if detected
  -> confidence
  -> uncertainty reason

BrowserVisualVerifier
  -> before screenshot hash
  -> action receipt
  -> after screenshot hash
  -> expected visual delta
  -> verdict
```

## Modalities

Sentinel should score four modalities separately:

| Modality | Purpose | Authority |
| --- | --- | --- |
| DOM/AX | structure, role/name, stable refs | evidence only |
| Screenshot | actual visual state | evidence only |
| Crop/zoom | precision on target region | evidence only |
| OCR | fallback for text inside images/PDFs | evidence only |

## Required Invariants

```text
runtime refs are minted by Sentinel, not LLM
screenshot hashes bind to page/snapshot hash
crop hashes bind to source screenshot hash
OCR text cannot create action authority
LLM visual interpretation is draft only
post-action visual verifier cannot certify without receipt
prompt-injected visual text is quarantined as evidence
FinalGate rejects forged screenshot/crop/visual-verifier events
```

## Why Hybrid Beats OCR-Only

OCR can read text inside pixels, but it does not know:

```text
which button is actionable
whether an element is disabled
whether a crop maps to the current DOM epoch
whether a coordinate is stale
whether a visual label came from adversarial page content
whether a post-action state actually satisfies the mission
```

So OCR is useful only inside a larger grounding and verification system.
