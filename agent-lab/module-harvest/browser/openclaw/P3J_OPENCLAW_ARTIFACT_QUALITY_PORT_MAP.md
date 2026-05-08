# P3J OpenClaw Artifact Quality Port Map

Date: 2026-04-29
Status: implemented and validated in Sentinel-owned code

## Scope

P3J ports the useful screenshot artifact quality pattern from the isolated
OpenClaw browser files into Sentinel-native contracts for normalized
screenshots, optional PDF artifacts, and element screenshots tied to stable
refs.

No vendor media pipeline or runtime is imported into product code.

## Source Classification

| Source file | Primitive | Sentinel destination | Classification | Reason | Tests adapted |
| --- | --- | --- | --- | --- | --- |
| `src/browser/screenshot.ts` | max-side/max-bytes screenshot normalization contract | `sentinel/agent/browser/screenshot.py` | translate_algorithm | Keep the resize-until-bounded contract; Sentinel uses an injected normalizer hook so product code does not depend on vendor media stack. | `test_agent_browser_artifact_quality.py` |
| `src/browser/screenshot.test.ts` | oversized screenshot shrinks, small screenshot stays unchanged | Sentinel pytest cases | test_pattern_only | Test shape is useful; Sentinel uses deterministic PNG metadata fixtures and injected normalizer. | normalization proof tests |
| `src/browser/pw-tools-core.snapshot.ts` | element-level artifact tied to structural refs | `BrowserRenderedElementScreenshot`, `BrowserRenderedSnapshotAdapter` | translate_algorithm | Ref-bound element artifact idea is useful; broad snapshot route lifecycle is rejected. | element screenshot tests |

## Ported Primitives

| Primitive | Sentinel implementation | Notes |
| --- | --- | --- |
| Screenshot normalization proof | `normalize_browser_screenshot` | Keeps small screenshots unchanged; oversized screenshots require a Sentinel-owned normalizer hook and record original dimensions/bytes. |
| PDF artifact contract | `BrowserRenderedSnapshotRequest.capture_pdf`, `BrowserPdfMetadata` | Captures PDF only when explicitly requested and metadata validates `%PDF-` plus size. |
| Element screenshot contract | `BrowserRenderedElementScreenshot`, `BrowserElementScreenshotMetadata` | Captures screenshots only for refs present in the accessibility snapshot and requested by the caller. |
| FinalGate artifact checks | `browser_capability_receipts` | Verifies PDF and element screenshot artifacts/hashes alongside existing snapshot/screenshot artifacts. |
| Playwright artifact hooks | `PlaywrightReadOnlyRenderer` | Can produce PDF and element screenshots while keeping fresh context, no storage state, downloads disabled, and JavaScript disabled. |

## Rejected Runtime Surfaces

- vendor image/media stack import;
- unbounded screenshot storage;
- element screenshots against arbitrary selectors without stable refs;
- PDF capture without explicit request;
- private profile/session state;
- upload/download flows;
- arbitrary JavaScript evaluation.

## Sentinel Destination Files

- `sentinel/agent/browser/models.py`
- `sentinel/agent/browser/screenshot.py`
- `sentinel/agent/browser/pdf.py`
- `sentinel/agent/browser/rendered_snapshot.py`
- `sentinel/agent/browser/playwright_renderer.py`
- `sentinel/agent/browser/interaction_execution.py`
- `sentinel/agent/browser/controlled_runner.py`
- `sentinel/agent/final_gate.py`
- `tests/test_agent_browser_artifact_quality.py`

## Validation

```text
pytest tests/test_agent_browser_artifact_quality.py -q
pytest <all test_agent_browser_*.py> -q
pytest tests -q
python -m compileall sentinel
execution-boundary primitive scan
product vendor-trace scan
```

Observed result: targeted, browser, and full sentinel-core suites pass;
compileall passes; execution-boundary, product vendor-trace, and doctrine scans
are clean.
