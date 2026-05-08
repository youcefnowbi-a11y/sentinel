# Sentinel Browser Spec

Date: 2026-04-26
Status: future design only, read-only first

## Principle

Browser starts as evidence collection, not action.

The browser may eventually inspect public web pages and gather citations. It must not submit forms, send messages, upload files, purchase, publish, delete, or mutate account state in v1.

## G10 Boundary

Blocked now:

- no real browser automation;
- no browser profile connection;
- no account login;
- no form submit;
- no send/post/publish;
- no arbitrary page JS execution;
- no file upload.

Allowed later after fake eval:

- read-only navigation to public pages;
- snapshot/extract/citation capture;
- source ranking;
- evidence mapping.

## Browser Action Classes

| Action | Risk | v1 Status |
|---|---|---|
| `browser_open_public_url` | medium | future read-only |
| `browser_extract_text` | medium | future read-only |
| `browser_capture_citation` | medium | future read-only |
| `browser_click_navigation` | high | blocked until policy |
| `browser_type` | high | blocked |
| `browser_submit_form` | critical | blocked |
| `browser_send_message` | critical | blocked |
| `browser_upload_file` | critical | blocked |
| `browser_evaluate_js` | critical | blocked except signed extractors later |

## Read-Only Extraction Contract

```json
{
  "url": "...",
  "page_title": "...",
  "extracted_text": "...",
  "citations": [],
  "sensitivity": "public|private|secret_suspected",
  "prompt_injection_flags": [],
  "trace_id": "trace_..."
}
```

## Policy Rules

- Browser content is always external untrusted context.
- Browser content cannot give instructions.
- Prompt injection text is stored as evidence of risk, not followed.
- Source URL and timestamp are mandatory.
- Claims extracted from browser must become `EvidenceItem` rows before decision use.

## Required Evals

- Fake page with prompt injection.
- Fake page asking agent to ignore policy.
- Fake form submit attempt.
- Fake external message send.
- Fake private/account page blocked.
- Citation preservation test.
