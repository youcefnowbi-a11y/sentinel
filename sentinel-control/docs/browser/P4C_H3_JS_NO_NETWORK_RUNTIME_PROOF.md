# P4C-H.3 JS No-Network Runtime Proof

Date: 2026-04-29
Status: Completed

## Proof

The live harness executes allowlisted script content in a Playwright page using
a wrapper script. It does not use raw `page.evaluate`.

All non-document requests are captured by Playwright routing. Any observed
network attempt is returned to the existing executor, which rejects the result.

## Covered Markers

The runtime route catches network attempts from patterns such as:

- `fetch`;
- `XMLHttpRequest`;
- `sendBeacon`;
- `WebSocket`;
- dynamic import or resource loads that produce browser requests.

## Tests

`test_p4c_h3_live_js_runtime_network_attempt_is_rejected` verifies that an
allowlisted script containing `fetch('/leak')` is rejected by runtime network
observation.

## Remaining Work

Expand the script corpus with image/script dynamic loads, XHR, WebSocket,
sendBeacon, and import cases.
