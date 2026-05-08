# P4B Upload Authorized Authority Spec

Date: 2026-04-29
Status: implemented and validated

## Authority Class

```text
browser_upload_authorized
```

This class allows upload only from a certified Sentinel artifact to a granted
public browser target. It does not allow arbitrary disk paths, private sessions,
credentials, cookies/storage, payment flows, or JavaScript evaluation.

## Required Chain

Execution requires:

- `MissionAuthorityEnvelope.allowed_tools` includes `browser_upload_authorized`;
- `MissionAuthorityEnvelope.allowed_actions` includes `browser_upload_authorized`;
- `browser_v3_authority_grants` includes a `browser_upload_authorized` grant;
- source artifact id appears in the grant `allowed_artifact_ids`;
- source artifact has a Sentinel artifact capture trace;
- source artifact MIME and bytes fit the authority grant;
- source artifact hash is bound to the capture event and upload receipt;
- ContextPack contains `browser_upload_authorized` as available action intent;
- ToolIntentCompiler compiles the LLM draft intent;
- upload target ref is runtime-minted and hash-bound;
- certified dry-run plan exists;
- pre-upload snapshot trace exists;
- post-upload snapshot artifact is captured;
- FinalGate certifies the source/action/post-state chain.

## Runtime Contract

Implemented code:

```text
sentinel/agent/browser/upload_authorized.py
```

Events:

```text
BROWSER_UPLOAD_AUTHORIZED_EXECUTED
BROWSER_UPLOAD_AUTHORIZED_REJECTED
```

Receipt:

```text
BrowserUploadAuthorizedReceipt
```

The receipt binds authority grant, ContextPack, compiled intent, plan,
before/after snapshots, source artifact metadata, upload ref, post-upload
artifacts, network ledger, and FinalGate trace refs.

## FinalGate Contract

FinalGate accepts an upload only when the event chain proves:

- the compiled intent event exists before the upload execution event;
- the certified plan hash, page hash, snapshot hash, and upload ref match;
- the source artifact was captured before upload and its SHA-256 matches;
- the post-upload snapshot artifact exists and its SHA-256 matches;
- same-origin or explicitly granted cross-origin result;
- network ledger hash and receipt ids are present.

## Rejections

The executor rejects missing authority, ungranted artifact id, artifact without
trace proof, MIME/byte mismatch, stale refs, invalid plan hash, missing pre/post
snapshot, cross-origin result without grant, and missing compiled intent trace.

## Boundary

P4B-3 does not implement artifact download promotion, private sessions, login,
cookies/storage, arbitrary JavaScript, payment, credentials, or remote browser
nodes.
