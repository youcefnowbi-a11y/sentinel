# P4D-H Adversarial Corpus

Date: 2026-04-29
Status: Complete

## Purpose

P4D required adversarial corpora for the highest-risk Browser V3 outputs:

- sandboxed JS network attempts;
- cookie/storage redaction;
- HAR/body redaction;
- secret-like exception and payload strings.

## JS Corpus

The P4D-H JS corpus covers:

```text
fetch
XMLHttpRequest
sendBeacon
WebSocket
Image load
script element load
dynamic import
```

Each script is allowed by hash for the test, then rejected because it attempts a
network operation.

This proves the rule:

```text
hash allowlist is necessary, not sufficient
runtime no-network observation still decides
```

## Cookie/Storage Corpus

The redaction corpus includes:

- mixed-case token keys;
- `Set-Cookie` headers;
- form-style `password=...`;
- nested structures.

The executor rejects these as backend-reality failures when a supposedly
redacted summary still contains sensitive payload indicators.

## HAR/Body Corpus

The HAR corpus includes:

- `Authorization: Bearer ...`;
- nested JSON `access_token`;
- `api_key`;
- form-style `credential=...`.

The executor rejects those entries before accepting the capture.

## Runtime Redaction Fix

P4D-H found and fixed a real redaction issue in the live harness: redacted URLs
masked query values but kept sensitive query key names such as `api_key`.

The live harness now hashes query parameter names in redacted URLs:

```text
api_key=[REDACTED]
-> param_<hash>=[REDACTED]
```

## Verdict

The adversarial corpus is still internal, but it is now materially stronger than
the P4C-S fixture set.

Next external campaigns should expand it with real-world headers, nested API
responses, and browser exception paths.
