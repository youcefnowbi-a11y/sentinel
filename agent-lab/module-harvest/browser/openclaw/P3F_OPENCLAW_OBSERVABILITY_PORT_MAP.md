# P3F OpenClaw Observability Port Map

Date: 2026-04-28
Status: implemented and validated in Sentinel-owned code

## Scope

P3F ports observability strength from the isolated OpenClaw browser specimens
into Sentinel-native rendered browser evidence. No vendor runtime, gateway,
route, package name, session lifecycle, profile, storage, cookie, click, submit,
download, or arbitrary JavaScript surface was imported into product code.

## Port Summary

| Source file | Extracted primitive | Sentinel destination | Port decision | Reason | Tests adapted |
| --- | --- | --- | --- | --- | --- |
| `power-files/src/browser/pw-session.ts` | Bounded console message collection. | `sentinel/agent/browser/models.py`, `observability.py`, `playwright_renderer.py` | translate_algorithm | The bounded diagnostic idea is useful, but the OpenClaw session state is coupled to a persistent browser runtime. Sentinel uses immutable receipt metadata instead. | `test_rendered_snapshot_records_failures_console_and_page_errors_without_blocking` |
| `power-files/src/browser/pw-session.ts` | Request id mapping and request/response/failure tracking. | `BrowserRequestRecord`, `BrowserResponseRecord`, `BrowserRequestFailureRecord`, `BrowserNetworkLedger` | translate_algorithm | The event model is strong; the product implementation must bind it to MissionAuthority, EventBus, receipts, and FinalGate. | `test_rendered_snapshot_records_request_response_network_ledger`, `test_playwright_read_only_renderer_captures_rendered_fixture` |
| `power-files/src/browser/pw-session.ts` | Ledger bounding by record count. | `build_browser_network_ledger(max_records=...)` | translate_algorithm | Sentinel keeps bounded evidence logs with `original_counts` and `truncated` proof instead of mutable session arrays. | `test_network_ledger_is_bounded_and_truncated_with_proof` |
| `power-files/src/browser/pw-tools-core.responses.ts` | Response lookup and recent network activity concept. | `BrowserResponseRecord` and receipt count/hash fields | rewrite_required | Raw response body retrieval is not part of Browser V1 authority. Sentinel keeps status/content-type diagnostics only. | Browser evidence and snapshot tests |
| `power-files/src/browser/pw-tools-core.trace.ts` | Trace start/stop concept. | EventBus trace + `BrowserNetworkLedger.ledger_sha256` | reject_runtime | Playwright trace zip control is not needed for V1 and would add a new runtime surface. Sentinel hashes structured diagnostics instead. | FinalGate forged/missing ledger tests |
| `power-files/src/browser/routes/agent.debug.ts` | Debug endpoints for console, requests, trace. | `BROWSER_SNAPSHOT_CAPTURED` payload and snapshot artifact JSON | rewrite_required | Product code does not expose a debug HTTP route. The same information is emitted as mission-scoped trace and artifact data. | `test_final_gate_rejects_forged_browser_network_ledger_hash`, `test_final_gate_rejects_browser_snapshot_missing_network_ledger_metadata` |

## Sentinel-Owned Implementation

| Destination | Added capability |
| --- | --- |
| `sentinel/agent/browser/models.py` | Typed request, response, failure, console, page-error, health, and ledger models. |
| `sentinel/agent/browser/observability.py` | Canonical ledger hashing, bounded ledger construction, minimal fallback ledger, hash verification. |
| `sentinel/agent/browser/playwright_renderer.py` | Read-only Playwright event listeners for requests, responses, failures, console messages, page errors, and health metadata. |
| `sentinel/agent/browser/rendered_snapshot.py` | Ledger included in snapshot artifact, receipt, event payload, and result object. |
| `sentinel/agent/final_gate.py` | Ledger hash/count/metadata validation for `BROWSER_SNAPSHOT_CAPTURED`. |
| `tests/test_agent_browser_rendered_snapshot.py` | Ledger capture, failure/console/page-error, and truncation proof tests. |
| `tests/test_agent_browser_runtime_integration.py` | Forged/missing network ledger FinalGate rejection tests. |

## Product Boundary

P3F increases browser observability only. It does not grant browser action
authority. The following remain outside Browser V1 authority:

- click/type/fill/select/submit;
- login/private sessions;
- cookies and storage;
- downloads and uploads;
- arbitrary page JavaScript;
- profile reuse;
- debug HTTP routes;
- trace zip control.

## Validation

Executed:

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

Current result:

```text
Browser tests: 61 passed
Full sentinel-core tests: passed
Compileall: passed
Scans: clean
```
