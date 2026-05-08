# P3E Snapshot Port Plan

Date: 2026-04-28
Status: implemented and validated

## Goal

Port snapshot strength without enabling interactions.

## Source Specimens

| Source file | Primitive |
| --- | --- |
| `src/browser/pw-tools-core.snapshot.ts` | Snapshot assembly and page state. |
| `src/browser/pw-role-snapshot.ts` | ARIA role snapshot and references. |
| `src/gateway/protocol/schema/snapshot.ts` | Snapshot schema shape. |
| `src/browser/pw-role-snapshot.test.ts` | Stable ref and role regression cases. |
| `src/browser/screenshot.ts` | Screenshot normalization. |
| `src/browser/screenshot.test.ts` | Screenshot max-size and format tests. |

## Sentinel Target

```text
BrowserRenderedPage
-> BrowserAccessibilitySnapshot
-> stable refs
-> snapshot hash
-> screenshot metadata
-> receipt fields
-> final gate validation
```

## Implemented P3E Surface

- deterministic HTML role snapshot builder;
- stable `eN` refs for interactive/content roles;
- `nth` disambiguation for duplicate role/name pairs;
- role snapshot stats;
- snapshot/page SHA-256 binding;
- PNG/JPEG screenshot metadata;
- screenshot max-side gate;
- receipt/event/final-gate metadata.

## Hard Limits

No click, type, fill, submit, storage, cookies, login, arbitrary JS, or download.
