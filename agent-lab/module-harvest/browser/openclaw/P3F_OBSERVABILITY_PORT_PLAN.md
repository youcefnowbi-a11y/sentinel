# P3F Observability Port Plan

Date: 2026-04-28
Status: implemented and validated

## Goal

Make rendered browser evidence auditable through a network and diagnostics
ledger, without adding browser action powers.

## Source Specimens

| Source file | Primitive |
| --- | --- |
| `src/browser/pw-session.ts` | Session health and lifecycle patterns. |
| `src/browser/pw-tools-core.responses.ts` | Response ledger patterns. |
| `src/browser/pw-tools-core.trace.ts` | Trace assembly patterns. |
| `src/browser/routes/agent.debug.ts` | Debug and health inspection patterns. |

## Sentinel Target

```text
BrowserRenderedSnapshotAdapter
-> BrowserNetworkLedger
-> request/response/error records
-> console/page-error records
-> trace refs
-> receipt metadata
-> final gate validation
```

## Hard Limits

Observability cannot become authority. It may report what happened, but it may
not create mission authority, tools, sessions, or interactions.

## Implemented Sentinel Targets

- `BrowserNetworkLedger`
- `BrowserRequestRecord`
- `BrowserResponseRecord`
- `BrowserRequestFailureRecord`
- `BrowserConsoleRecord`
- `BrowserPageErrorRecord`
- `BrowserHealthMetadata`
- canonical ledger hash and verification
- bounded ledger size with truncation proof
- rendered snapshot artifact/receipt/event metadata
- FinalGate rejection for missing or forged ledger metadata

## Validation

```text
pytest sentinel-control/services/sentinel-core/tests/test_agent_browser_rendered_snapshot.py sentinel-control/services/sentinel-core/tests/test_agent_browser_runtime_integration.py -q
pytest sentinel-control/services/sentinel-core/tests/test_agent_browser_playwright_renderer.py sentinel-control/services/sentinel-core/tests/test_agent_browser_accessibility_snapshot.py -q
pytest <all test_agent_browser_*.py> -q
pytest sentinel-control/services/sentinel-core/tests -q
python -m compileall sentinel-control/services/sentinel-core/sentinel
execution-boundary primitive scan
product vendor-trace scan
browser action-surface scan
browser doctrine scan
```

Result: validated.
