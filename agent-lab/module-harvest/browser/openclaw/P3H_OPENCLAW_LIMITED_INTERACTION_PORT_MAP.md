# P3H OpenClaw Limited Interaction Port Map

Date: 2026-04-29
Status: implemented and validated in Sentinel-owned code

## Scope

P3H ports the useful action taxonomy and ref-handling patterns from the isolated
OpenClaw browser files into a Sentinel-native limited interaction gate.

No OpenClaw runtime, server route lifecycle, gateway, profile manager, storage
state, cookies, upload/download flow, or arbitrary evaluation path is imported
into product code.

## Source Classification

| Source file | Primitive | Sentinel destination | Classification | Reason | Tests adapted |
| --- | --- | --- | --- | --- | --- |
| `src/browser/routes/agent.act.ts` | act route taxonomy and required fields for click/type/hover/select/fill/wait | `sentinel/agent/browser/interaction_execution.py` | translate_algorithm | Useful action boundary, but route/server/profile lifecycle is rejected. | `test_agent_browser_interaction_execution.py` |
| `src/browser/pw-tools-core.interactions.ts` | Playwright interaction primitives using refs and timeouts | `sentinel/agent/browser/playwright_interaction_backend.py` | translate_algorithm | Locator/ref execution patterns are useful; evaluate, upload, download, dialog, drag, resize are rejected for P3H. | `test_playwright_backend_performs_one_limited_fill_interaction` |
| `src/agents/tools/browser-tool.schema.ts` | flat browser tool schema with action discriminator | `BrowserInteractionExecutionRequest`, `BrowserInteractionPlan` | copy_pattern | Flat discriminated intent model is kept; vendor action names are not imported into product tool ids. | request/model validation tests |
| `src/browser/server.agent-contract-form-layout-act-commands.test.ts` | interaction contract test cases | Sentinel targeted pytest cases | test_pattern_only | Test shape is useful, but Sentinel uses EventBus, receipts, MissionAuthority, ToolRegistry, and FinalGate instead of HTTP routes. | forged plan, stale refs, same-origin, authority tests |

## Ported Primitives

| Primitive | Sentinel implementation | Notes |
| --- | --- | --- |
| Ref-required action execution | `BrowserLimitedInteractionExecutor` | Consumes a P3G `BrowserInteractionPlan`; no free-form selectors for click/type/fill/select/hover. |
| Limited real action set | `P3H_ALLOWED_EXECUTION_INTENTS` | Allows click/type/fill/select/hover/wait plans. Rejects press/submit/upload/download/evaluate/storage/cookies/login/payment. |
| Backend isolation | `BrowserInteractionBackend` callable contract | The executor governs receipts and proof; backend only performs bounded browser interaction. |
| Real Playwright backend | `PlaywrightLimitedInteractionBackend` | Fresh context, downloads disabled, no storage state, JavaScript disabled, same-origin document routing. |
| Post-action proof | `BrowserInteractionExecutionReceipt` | Captures before/after hashes, plan hash, same-origin proof, artifact IDs, ledger hash, trace refs. |
| FinalGate contract | `browser_interaction_execution_contract` | Rejects forged or unplanned interaction execution. |

## Rejected Runtime Surfaces

- submit/post/send/publish;
- arbitrary JavaScript evaluation;
- upload/download;
- cookies/storage/profile/session import;
- login/private page automation;
- dialog/file chooser hooks;
- drag/resize/close;
- vendor gateway/server runtime.

## Validation

```text
pytest tests/test_agent_browser_interaction_execution.py -q
pytest tests/test_agent_browser_*.py -q
pytest tests -q
```

Observed result: targeted, browser, and full sentinel-core suites pass.
