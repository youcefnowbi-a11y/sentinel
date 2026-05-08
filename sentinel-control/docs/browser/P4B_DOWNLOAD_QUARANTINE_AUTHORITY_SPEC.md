# P4B Download Quarantine Authority Spec

Date: 2026-04-29
Status: implemented and validated

## Authority Class

```text
browser_download_quarantine
```

This class allows a bounded public file download only into Sentinel artifact
quarantine. It does not promote the file, open it, upload it, execute it, or
grant private browser state.

## Required Chain

Execution requires:

- `MissionAuthorityEnvelope.allowed_tools` includes `browser_download_quarantine`;
- `MissionAuthorityEnvelope.allowed_actions` includes `browser_download_quarantine`;
- `browser_v3_authority_grants` includes a `browser_download_quarantine` grant;
- ToolRegistry manifest is approved;
- ContextPack contains `browser_download_quarantine` as available action intent;
- ToolIntentCompiler compiles the LLM draft intent;
- source refs, if present, are runtime-minted and hash-bound;
- source URL passes public URL policy;
- MIME type is allowlisted;
- bytes are within the V3 grant budget;
- artifact lands under `browser/download_quarantine/`;
- receipt marks `promoted=false`;
- FinalGate certifies the policy/action/artifact chain.

## Runtime Contract

Implemented code:

```text
sentinel/agent/browser/download_quarantine.py
```

Events:

```text
BROWSER_DOWNLOAD_QUARANTINED
BROWSER_DOWNLOAD_REJECTED
```

Receipt:

```text
BrowserDownloadQuarantineReceipt
```

The receipt binds:

- authority class;
- authority grant id;
- ContextPack id;
- compiled intent trace id;
- source URL and final URL;
- URL policy trace id;
- status code;
- content type and MIME allow decision;
- size bytes and max bytes;
- download SHA-256;
- artifact id and artifact SHA-256;
- quarantine relative path;
- filename hash;
- promoted flag set to false.

## Rejections

The executor rejects:

- missing V3 authority grant;
- URL outside grant domains;
- URL policy rejection;
- final URL policy mismatch;
- cross-origin result without grant;
- missing allowed MIME list;
- MIME outside allowlist;
- body larger than grant/request limit;
- artifact path escape or capture failure;
- missing ContextPack id;
- missing compiled intent trace.

## Boundary

P4B-2 does not implement artifact promotion, upload, private sessions, login,
cookies/storage, arbitrary JavaScript, payment, credentials, or remote browser
nodes.
