# P4H-W Real Browser-Engine Visual Harness

Date: 2026-04-30
Status: Locked local browser-engine slice

## Goal

P4H-W proves that Sentinel can create visual browser evidence from a real
rendered browser engine without making OCR the source of authority.

This is a small controlled slice, not a large visual subsystem.

## Implemented Path

```text
PlaywrightReadOnlyRenderer
-> BrowserRenderedSnapshotAdapter
-> screenshot artifact
-> element screenshot artifact
-> BrowserVisualObservation
-> visual grounding candidate
-> post-action visual verifier event
-> CoreFinalGate V2.5 contract
-> BF-VIS scorecard
```

## Files

```text
agent-lab/benchmarks/browser_tasks/browser_visual_engine_runner.py
agent-lab/benchmarks/browser_tasks/test_browser_visual_engine_runner.py
agent-lab/benchmarks/browser_tasks/reports/browser_visual_engine_results.jsonl
agent-lab/benchmarks/browser_tasks/reports/browser_visual_engine_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_visual_engine_scorecard.md
```

Core metadata extensions:

```text
sentinel.agent.browser.models.BrowserRenderedElementScreenshot.bbox
sentinel.agent.browser.models.BrowserElementScreenshotMetadata.bbox
sentinel.agent.browser.visual_observation.BrowserVisualObservation.page_sha256
sentinel.agent.browser.visual_observation.BrowserVisualObservation.snapshot_sha256
sentinel.agent.browser.visual_observation.BrowserVisualObservation.viewport
sentinel.agent.browser.visual_observation.BrowserVisualObservation.ui_observation_ref_ids
```

These are metadata-only additions. They do not add a browser action power.

## Safety Boundary

```text
read-only browser context
JavaScript disabled
downloads disabled
storage disabled
fixture document route only
no real account
no real credential
no OCR authority
no open-web claim
```

## Verdict

P4H-W passes as a local Playwright-backed visual/OCR fallback harness.

It proves the controlled visual evidence path:

```text
rendered screenshot + DOM/AX ref + crop/zoom + OCR fallback + verifier + FinalGate
```

It does not prove external open-web visual supremacy.
