# P4B FinalGate V3 Contract

Date: 2026-04-29
Status: implemented for all P4B authority classes

## Check

`CoreFinalGate` now includes:

```text
browser_v3_form_submit_contract
browser_v3_download_quarantine_contract
browser_v3_upload_authorized_contract
browser_v3_private_session_contract
browser_v3_login_authority_contract
browser_v3_cookie_storage_contract
browser_v3_js_evaluate_sandboxed_contract
browser_v3_har_body_capture_contract
```

## Required For Executed Submit

FinalGate requires:

- authority class is `browser_form_submit`;
- authority grant id exists;
- ContextPack id exists;
- compiled intent trace exists;
- compiled intent event exists before execution;
- plan exists and plan hash is valid;
- plan trace id exists;
- before snapshot trace id exists;
- before/after snapshot hashes exist;
- form and submit refs exist;
- submit kind is one of `submit`, `post`, `send`, `publish`;
- expected effect exists;
- same-origin result or cross-origin authorization;
- network ledger hash is valid;
- post-submit artifact exists and hash matches.

## Rejected Forgery

FinalGate rejects:

- forged post-submit artifact hash;
- missing receipt id;
- missing compiled intent trace;
- forged plan hash;
- cross-origin result without authorization;
- missing post-submit snapshot artifact;
- invalid submit kind.

## Required For Quarantined Download

FinalGate requires:

- authority class is `browser_download_quarantine`;
- authority grant id exists;
- ContextPack id exists;
- compiled intent trace exists;
- compiled intent event exists before quarantine event;
- URL policy trace exists before quarantine event;
- URL policy accepted the final URL;
- receipt id exists;
- artifact exists before quarantine event;
- artifact SHA-256 matches download SHA-256;
- artifact type is `browser_download_quarantine`;
- quarantine relative path starts with `browser/download_quarantine/`;
- MIME type is allowed;
- bytes do not exceed max bytes;
- `promoted=false`.

## Rejected Download Forgery

FinalGate rejects:

- forged artifact hash;
- missing receipt id;
- missing compiled intent trace;
- missing URL policy trace;
- missing artifact event;
- promotion flag set to true;
- MIME or byte metadata mismatch;
- quarantine path outside the expected quarantine prefix.

## Required For Authorized Upload

FinalGate requires:

- authority class is `browser_upload_authorized`;
- authority grant id exists;
- ContextPack id exists;
- compiled intent trace exists;
- compiled intent event exists before upload execution event;
- certified interaction plan and plan hash exist;
- before snapshot trace id exists;
- before/after snapshot hashes exist;
- upload target ref exists;
- source artifact event exists before upload execution event;
- source artifact SHA-256 matches the upload receipt;
- post-upload snapshot artifact exists before upload execution event;
- post-upload snapshot artifact SHA-256 matches;
- expected effect exists;
- same-origin result or cross-origin authorization;
- network ledger hash is valid.

## Rejected Upload Forgery

FinalGate rejects:

- forged source artifact hash;
- missing receipt id;
- missing compiled intent trace;
- missing certified plan;
- missing before snapshot trace;
- missing post-upload snapshot artifact;
- cross-origin result without authorization;
- arbitrary disk-path upload metadata.

## Required For P4B-4 Through P4B-8

FinalGate now also verifies:

- private sessions have start and later close events with destroy proof;
- login authority is bound to a private-session start event and contains no
  credential-bearing payload;
- cookie/storage contract outputs are redacted and session-bound;
- sandboxed JS uses an allowed script hash, no network calls, and bounded result
  artifacts;
- HAR/body capture is bounded, redacted, and artifact-bound.
