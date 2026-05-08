# P3I OpenClaw Public Lifecycle Port Map

Date: 2026-04-29
Status: implemented and validated in Sentinel-owned code

## Scope

P3I ports the useful session/page-state ideas from the isolated OpenClaw
browser files into a Sentinel-native public lifecycle ledger.

This is not a persistent browser profile. It is a mission-scoped record of
public sessions and tabs with URL-policy proof, stateless guarantees, and
FinalGate validation.

## Source Classification

| Source file | Primitive | Sentinel destination | Classification | Reason | Tests adapted |
| --- | --- | --- | --- | --- | --- |
| `src/browser/pw-session.ts` | page state, request ids, console/errors, role-ref cache, browser session lifecycle | `sentinel/agent/browser/public_lifecycle.py` | translate_algorithm | Page/session state concepts are useful; persistent CDP connection, auth headers, dialogs, uploads, downloads, profile state, and vendor server lifecycle are rejected for P3I. | `test_agent_browser_public_lifecycle.py` |
| `src/browser/pw-session.ts` | role-ref cache attached to page state | `BrowserPublicTab.current_url_policy_trace_id`, P3E/P3G ref/hash contracts | copy_pattern | Keep the idea that refs belong to a page state, but Sentinel binds refs through snapshot/page hashes rather than vendor runtime state. | dry-run/execution/lifecycle tests |
| `src/browser/pw-session.ts` | browser health and diagnostic state | P3F `BrowserNetworkLedger` / `BrowserHealthMetadata` | already_ported | Observability was ported in P3F; P3I reuses the doctrine that lifecycle is traceable metadata. | P3F rendered snapshot tests |

## Ported Primitives

| Primitive | Sentinel implementation | Notes |
| --- | --- | --- |
| Public session identity | `BrowserPublicSession` | Mission-scoped, stateless, no cookies/storage. |
| Public tab identity | `BrowserPublicTab` | Tracks current URL, policy trace, navigation count, and trace refs. |
| Lifecycle result/receipt | `BrowserPublicLifecycleResult`, `BrowserPublicLifecycleReceipt` | Every accepted lifecycle change has a receipt-like proof. |
| Lifecycle controller | `BrowserPublicLifecycleController` | Starts/closes sessions, opens/navigates/closes tabs, and emits URL-policy-bound events. |
| FinalGate lifecycle validation | `browser_public_lifecycle_contract` | Rejects forged tab opens, missing URL policy, unknown tabs, invalid navigation order, and stateful payloads. |

## Rejected Runtime Surfaces

- persistent profile lifecycle;
- cookies or storage state;
- auth/header injection;
- dialog, upload, or download arms;
- remote CDP browser connection ownership;
- vendor route/server lifecycle;
- private/account session state;
- arbitrary JavaScript evaluation.

## Sentinel Destination Files

- `sentinel/agent/browser/models.py`
- `sentinel/agent/browser/public_lifecycle.py`
- `sentinel/agent/browser/__init__.py`
- `sentinel/agent/final_gate.py`
- `tests/test_agent_browser_public_lifecycle.py`

## Validation

```text
pytest tests/test_agent_browser_public_lifecycle.py -q
pytest <all test_agent_browser_*.py> -q
pytest tests -q
python -m compileall sentinel
execution-boundary primitive scan
product vendor-trace scan
```

Observed result: P3I targeted, browser, and full sentinel-core suites pass;
compileall passes; execution-boundary and product vendor-trace scans are clean.
