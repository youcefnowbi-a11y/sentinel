# P4C-H.3 Live Adapter Harness

Date: 2026-04-29
Status: Completed

## Goal

P4C-H.3 moves Browser V3 from deterministic fixture backends to a
Playwright-backed local live adapter harness.

This does not add browser powers. It uses the same V3 authority classes,
executors, receipts, EventBus events, artifacts, and FinalGate contracts.

## Implemented Code

- `BrowserV3LiveAdapterHarness`
- `BrowserV3LiveHarnessAccount`
- `BrowserV3LiveHarnessSession`

The harness is fixture-bound and same-origin. It does not browse arbitrary
internet targets and does not expose credentials outside the adapter boundary.

## Proof Areas

| Area | Live harness proof |
| --- | --- |
| Private session | Playwright runtime opens a local context and profile marker; close destroys profile directory. |
| Login | Account id maps to a harness account inside the adapter; credentials are used only inside the adapter. |
| Cookie/storage | Redacted summaries are produced without raw export. |
| JS sandbox | Allowlisted script runs in a Playwright page; network attempts are observed and rejected. |
| HAR/body | Playwright routing records redacted request metadata and artifact-bound HAR fixtures. |
| EvalBench | 10-run Browser V3 live harness case reports stable accepted/success metrics. |

## Boundary

P4C-H.3 proves local live-adapter behavior, not open-web supremacy.
