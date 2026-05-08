# Browser Decision Matrix

Date: 2026-04-29
Status: P3X accepted

## Purpose

This matrix defines when the cortex should call, trust, downgrade, retry, or
escalate browser evidence.

## Call Browser

| Mission Need | Browser Path | Reason |
| --- | --- | --- |
| Verify public claim | `browser_read_public_page` | Public source can support or weaken hypothesis. |
| Inspect layout/CTA/pricing page | `browser_render_public_page` | Rendered snapshot, refs, screenshot, and ledger are needed. |
| Prepare public interaction | interaction dry-run | Stable refs and page hashes are needed before action. |
| Execute narrow public interaction | limited interaction | Only from certified plan and mission authority. |
| Diagnose failed observation | reliability supervisor | Bounded retry and health metadata explain failure. |

## Trust Browser Output

Browser output can be used as evidence when:

- URL policy event exists;
- receipt exists;
- artifact hash exists when artifact is expected;
- source confidence is high enough;
- prompt flags are absent or explicitly bounded;
- FinalGate accepts the browser trace.

## Downgrade Browser Output

Downgrade when:

- content is thin;
- title is missing;
- extraction is fallback;
- network/page errors exist;
- ledger is truncated;
- screenshot is missing when needed;
- prompt-injection flags exist.

## Seek Alternative Source

Alternative source search is recommended when:

- browser output is rejected;
- source confidence is low;
- evidence gap appears;
- prompt flags limit confidence below mission threshold;
- contradiction exists between browser source and existing mission evidence.

## Interaction Rule

Browser interaction may influence mission progress only when:

```text
certified dry-run plan
+ matching snapshot/page hashes
+ valid refs
+ same-origin result
+ post-action snapshot
+ receipt
+ FinalGate acceptance
```

## Boundary

The decision matrix is a routing contract. It does not grant new tools, actions,
domains, accounts, sessions, or file transfer powers.
