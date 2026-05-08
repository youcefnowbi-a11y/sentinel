# P3D OpenClaw Extraction Port Map

Date: 2026-04-28
Status: implemented and validating
Scope: evidence quality and extraction only

## Source Files Inspected

| Source file | Extracted primitive |
| --- | --- |
| `src/agents/tools/web-fetch-utils.ts` | HTML stripping, script/style removal, markdown/text fallback, truncation proof, readability fallback. |
| `src/security/external-content.ts` | Suspicious external-content patterns and boundary concept. |
| `src/agents/tools/web-tools.readability.test.ts` | Article extraction should prefer main content over nav/footer. |
| `src/agents/tools/web-tools.fetch.test.ts` | Text wrapping, truncation, fallback, and error-content extraction edge cases. |

## Port Decisions

| Primitive | Sentinel destination | Decision | Reason | Tests adapted |
| --- | --- | --- | --- | --- |
| Remove script/style/noscript/template/svg content | `browser/extraction.py` | translated | Prevent hidden page code from becoming evidence. | `test_readable_extractor_ignores_script_and_style_claims` |
| Prefer article/main content | `browser/extraction.py` | translated | Stronger evidence text than whole-page parser. | `test_readable_extractor_prefers_article_content_over_nav_and_footer` |
| Plain text extraction | `browser/extraction.py` | Sentinel-native | Required for public text documents. | `test_json_and_plain_text_responses_are_captured_with_strategy` |
| JSON text extraction | `browser/extraction.py` | Sentinel-native | Required for JSON evidence endpoints without external tools. | `test_json_and_plain_text_responses_are_captured_with_strategy` |
| Truncation proof | `models.py`, `evidence_adapter.py`, `browser/extraction.py` | translated | Receipts now prove raw chars, truncation, and citation offsets. | `test_huge_page_truncates_with_receipt_proof_and_valid_citation_offsets` |
| Source quality flags | `models.py`, `evidence_adapter.py`, `browser/extraction.py` | Sentinel-native | EvidenceChain can downgrade thin/noisy/prompt-injected pages. | `test_source_quality_low_when_content_is_too_thin` |
| External content warning wrapper | none in runtime prompt | deferred | Sentinel stores flags/receipts now; prompt wrapper belongs in future planner/context integration. | Not ported |
| External scraper fallback | none | rejected | Browser V1 must not call third-party scraper APIs. | Not ported |

## Sentinel Files Changed

| File | Change |
| --- | --- |
| `sentinel/agent/browser/extraction.py` | New deterministic readable extraction module. |
| `sentinel/agent/browser/models.py` | Receipt/result fields for strategy, quality flags, truncation, raw chars, citation offsets. |
| `sentinel/agent/browser/evidence_adapter.py` | Uses readable extraction, rejects empty evidence gaps, records quality metadata. |
| `tests/test_agent_browser_extraction.py` | P3D evidence-quality regression suite. |

## Rejected For P3D

```text
external scraper fallback
LLM extraction
browser interaction
JavaScript execution
cookies/session/private profile use
download parsing
```
