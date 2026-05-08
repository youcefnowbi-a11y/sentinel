# P4C-H.3 HAR/Body Live Redaction

Date: 2026-04-29
Status: Completed

## Proof

The live harness uses Playwright routing to observe fixture requests, hash the
source URL, redact query values, and emit bounded HAR/body metadata through the
existing `browser_har_body_capture` executor.

## Redaction Shape

HAR entries contain:

- `url_hash`;
- `redacted_url`;
- `method`;
- `resource_type`;
- `body_redacted`.

Raw token query values are not stored in artifacts.

## Tests

The live flow verifies that captured artifacts do not contain fixture values
such as `secret-token` or `secret-key`.

## Remaining Work

Add a larger redaction corpus for headers, nested JSON, forms, base64-like
secrets, cookies, and set-cookie responses.
