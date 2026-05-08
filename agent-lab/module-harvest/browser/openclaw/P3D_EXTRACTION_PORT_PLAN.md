# P3D Extraction Port Plan

Date: 2026-04-28
Status: implemented in Sentinel-native code

## Goal

Improve Browser evidence quality beyond simple HTML parsing while preserving the
read-only Browser V1 authority boundary.

## Implemented Contract

```text
BrowserFetchedPage
-> ReadablePageExtractor
-> extraction strategy
-> source quality flags
-> truncation proof
-> citation offsets
-> EvidenceItem metadata
-> artifact payload
-> BrowserEvidenceFetchReceipt
```

## Strategies

| Strategy | Use case |
| --- | --- |
| `readability` | HTML with useful `<main>` or `<article>` content. |
| `simple_html` | HTML without strong article landmarks. |
| `text_plain` | Plain text public evidence. |
| `json_text` | JSON public evidence endpoints. |
| `fallback` | Unsupported or malformed markup fallback. |

## Quality Flags

| Flag | Meaning |
| --- | --- |
| `empty_extraction` | No usable public evidence text. Adapter rejects as `browser_evidence_gap`. |
| `thin_content` | Text exists but is too weak to trust highly. |
| `boilerplate_heavy` | Page appears dominated by non-content page chrome. |
| `fallback_text_extraction` | Extractor had to fall back to tag stripping. |
| `json_parse_failed` | JSON MIME was declared but body did not parse cleanly. |
| `no_title` | No title was extracted. |
| `truncated` | Extracted text exceeded `max_chars` and was cut. |
| `prompt_injection_detected` | Suspicious instruction-like content was detected. |

## Acceptance

- no new browser actions;
- no cookies/storage/login/session;
- no external scraper API;
- extracted text is more selective;
- weak extraction becomes explicit metadata or evidence gap;
- receipts keep enough proof for replay/audit/final gate.
