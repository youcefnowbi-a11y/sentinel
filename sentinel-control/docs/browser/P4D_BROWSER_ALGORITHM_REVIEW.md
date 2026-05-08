# P4D Browser Algorithm Review

Date: 2026-04-29
Status: Complete

## Reviewed Algorithms

P4D reviewed these algorithmic areas:

- runtime ref binding;
- interaction plan validity;
- page/snapshot hash binding;
- network ledger hash validation;
- V3 grant lookup and domain matching;
- cookie/storage and HAR redaction;
- JS no-network detection;
- live profile lifecycle proof;
- EvalBench multi-run scoring.

## Ref And Plan Binding

The ToolIntentCompiler resolves runtime refs from canonical call arguments and
checks them against ContextPack stable refs. It rejects missing refs and stale
page/snapshot hashes.

The V3 executors that depend on interaction plans validate plan hashes and
check that target refs belong to the certified plan.

Verdict: strong for local deterministic refs.

Remaining hardening: add DOM-epoch or observation-epoch binding in later
browser phases so dynamic pages cannot reuse structurally similar refs after
large UI churn.

## Network And Artifact Hashing

FinalGate validates network ledger hashes for form submit and upload paths and
artifact hashes for download, upload, snapshots, JS results, private-session
receipts, cookie/storage summaries, and HAR/body capture.

Verdict: strong.

Remaining hardening: use a shared helper to reduce duplicated hash/order checks
across V3 classes.

## Redaction Algorithms

Cookie/storage and HAR/body redaction use redacted summaries, hash-only fields,
bounded artifacts, and secret-marker rejection. Backend reality validators reject
summaries or HAR entries that still contain obvious sensitive markers.

Verdict: good initial adversarial coverage.

Remaining hardening:

- nested JSON secrets;
- form-encoded secrets;
- Authorization, Cookie, Set-Cookie headers;
- bearer tokens in query parameters;
- base64-like payloads;
- mixed-case key names;
- exception strings carrying secret-like values.

## JS No-Network Algorithm

The live harness instruments routed browser requests during JS execution and
rejects network calls even when script hash is allowlisted.

Verdict: correct direction.

Remaining hardening: the corpus must cover fetch, XHR, WebSocket, sendBeacon,
dynamic image/script loads, and dynamic import. A single `fetch('/leak')` style
case is not enough for a final claim.

## EvalBench Statistics

Current EvalBench metrics compute:

```text
accepted_rate
success_rate
CI95 half-width
unstable_iterations
```

The CI95 half-width currently uses the normal approximation:

```text
1.96 * sqrt(p * (1-p) / n)
```

This becomes `0.0` when `p = 1.0`, even if `n = 2`. That is mathematically
misleading for a browser supremacy claim.

P4D requires replacing or augmenting this with:

- Wilson score interval for binomial rates; or
- Jeffreys interval; or
- a conservative rule-of-three note for zero observed failures.

Recommended reporting:

```text
observed success rate
run count
Wilson lower bound
Wilson upper bound
failure upper bound when zero failures
unstable iterations
```

## Algorithm Verdict

The operational algorithms are sound enough for local V3 authority proof.

The benchmark statistics are not yet sound enough for scientific supremacy.
