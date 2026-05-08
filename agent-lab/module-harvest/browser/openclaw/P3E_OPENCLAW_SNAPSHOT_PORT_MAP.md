# P3E OpenClaw Snapshot Port Map

Date: 2026-04-28
Status: implemented and validated
Scope: rendered snapshot structure, stable refs, and screenshot metadata only

## Source Files Inspected

| Source file | Extracted primitive |
| --- | --- |
| `src/browser/pw-tools-core.snapshot.ts` | Snapshot assembly, ref storage concept, AI/ARIA snapshot separation. |
| `src/browser/pw-role-snapshot.ts` | Role snapshot lines, stable `eN` refs, duplicate `nth`, interactive stats. |
| `src/gateway/protocol/schema/snapshot.ts` | Schema discipline and snapshot metadata pattern. |
| `src/browser/pw-role-snapshot.test.ts` | Interactive refs, duplicate nth, max depth, stats, AI refs. |
| `src/browser/screenshot.ts` | Screenshot max side/max bytes normalization contract. |
| `src/browser/screenshot.test.ts` | Screenshot metadata/limits test pattern. |

## Port Decisions

| Primitive | Sentinel destination | Decision | Reason | Tests adapted |
| --- | --- | --- | --- | --- |
| Stable role refs | `browser/accessibility_snapshot.py` | translated | Sentinel now builds deterministic refs from captured HTML without enabling page interaction. | `test_accessibility_snapshot_builder_creates_stable_refs_and_duplicate_nth` |
| Duplicate `nth` disambiguation | `browser/accessibility_snapshot.py` | translated | Keeps duplicated role/name refs addressable later without clicking now. | `test_accessibility_snapshot_builder_creates_stable_refs_and_duplicate_nth` |
| Role snapshot stats | `models.py`, `accessibility_snapshot.py`, `rendered_snapshot.py` | translated | Receipt/event payload now expose ref and interactive counts. | rendered snapshot tests |
| Snapshot hash binding | `models.py`, `accessibility_snapshot.py`, `rendered_snapshot.py` | Sentinel-native | Snapshot and page hashes bind extracted structure to the captured HTML artifact. | `test_rendered_snapshot_records_accessibility_snapshot_and_screenshot_metadata` |
| Screenshot metadata | `browser/screenshot.py`, `rendered_snapshot.py` | Sentinel-native | Width/height/format/bytes/max limits are recorded in receipt and event payload. | `test_rendered_snapshot_records_accessibility_snapshot_and_screenshot_metadata` |
| Screenshot max-side gate | `browser/screenshot.py`, `rendered_snapshot.py` | Sentinel-native | Sentinel rejects oversized screenshots until binary resizing is implemented. | `test_rendered_snapshot_rejects_screenshot_that_exceeds_max_side` |
| Full Playwright/CDP ARIA tree | none | deferred | Requires deeper Playwright/CDP integration and network ledger first. Current P3E stays read-only and parser-backed. | Not ported |
| Element interaction refs | none | rejected for P3E | Refs are evidence structure only. They do not authorize click/type/submit. | Not ported |

## Sentinel Files Changed

| File | Change |
| --- | --- |
| `sentinel/agent/browser/accessibility_snapshot.py` | New deterministic HTML role snapshot builder. |
| `sentinel/agent/browser/screenshot.py` | New screenshot metadata parser for PNG/JPEG dimensions and limits. |
| `sentinel/agent/browser/models.py` | Added role snapshot, screenshot metadata, and receipt/result fields. |
| `sentinel/agent/browser/rendered_snapshot.py` | Adds accessibility snapshot and screenshot metadata to artifact, receipt, and event. |
| `sentinel/agent/final_gate.py` | Requires snapshot events to include accessibility hash/count metadata. |
| `tests/test_agent_browser_accessibility_snapshot.py` | P3E regression tests. |

## Rejected For P3E

```text
click/type/fill/select
form submit
session refs
cookies/storage
arbitrary JavaScript
download handling
live CDP control routes
```
