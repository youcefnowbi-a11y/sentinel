# P3K OpenClaw Reliability Port Map

Date: 2026-04-29
Status: implemented and validated

## Goal

Port the useful browser reliability patterns into Sentinel-native code:
bounded retries, backend health proof, public/stateless lease accounting, and
FinalGate validation.

This phase does not import the vendor runtime. It does not enable private
profiles, cookies, storage, arbitrary JavaScript, downloads, uploads, or broad
browser automation.

## Source Classification

| Source file | Primitive | Sentinel destination | Port verdict | Reason | Tests adapted |
| --- | --- | --- | --- | --- | --- |
| `power-files/src/browser/pw-session.ts` | connection cache, connection retry, page/context observation, disconnect cleanup | `sentinel/agent/browser/supervisor.py` + `browser/models.py` | translate_algorithm | Useful lifecycle/retry ideas, but vendor code is CDP/profile/runtime coupled. | bounded retry and lease release tests |
| `power-files/src/browser/pw-tools-core.trace.ts` | trace active state and trace start/stop invariants | `CoreFinalGate._browser_reliability_supervisor_contract` | rewrite_required | Sentinel uses EventBus trace proofs instead of Playwright trace zip lifecycle. | forged/unbounded retry tests |
| `power-files/src/browser/routes/agent.debug.ts` | page error/debug/trace inspection routes | `BrowserHealthCheck` and supervisor health event | test_pattern_only | Route server lifecycle is rejected; health/debug concept is retained as typed evidence. | health check trace binding test |
| `power-files/src/browser/pw-tools-core.responses.ts` | bounded response wait and error diagnostics | `BrowserRetryPolicy`, `BrowserOperationError`, `BrowserSupervisedOperationResult` | translate_algorithm | Retry/error classification is useful, but response-body runtime belongs to evidence adapters. | retry success/failure tests |

## Implemented Sentinel Primitives

- `BrowserReliabilitySupervisor`
- `BrowserPoolLease`
- `BrowserPoolLeaseReceipt`
- `BrowserPoolLeaseResult`
- `BrowserHealthCheck`
- `BrowserRetryPolicy`
- `BrowserOperationAttempt`
- `BrowserSupervisedOperationResult`
- `BrowserOperationError`
- events:
  - `BROWSER_POOL_LEASED`
  - `BROWSER_POOL_RELEASED`
  - `BROWSER_HEALTH_CHECKED`
  - `BROWSER_OPERATION_RETRIED`
  - `BROWSER_SUPERVISOR_REJECTED`
- FinalGate contract:
  - stateless public lease proof;
  - cookies/storage/JS/download flags remain false;
  - retry attempts must stay below max attempts;
  - release requires a known active lease;
  - health checks are lease-bound when a lease is referenced.

## Rejected Runtime Pieces

- persistent vendor CDP connection cache;
- profile context lifecycle;
- auth headers;
- storage/cookie persistence;
- route server lifecycle;
- arbitrary debug endpoint exposure;
- Playwright trace zip writing as an authority source.

## Current Limits

P3K is a reliability supervisor and contract layer. It does not yet replace the
fresh-context browser execution model with a persistent real browser pool. That
pool can be added later only if it remains public/stateless and stays bound to
MissionAuthority, receipts, EventBus, and FinalGate.

## Validation

```text
pytest tests/test_agent_browser_reliability_supervisor.py -q
pytest <all test_agent_browser_*.py> -q
pytest tests -q
python -m compileall sentinel
execution-boundary primitive scan
product vendor-trace scan
browser doctrine scan
```

Result: validated.
