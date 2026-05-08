# Sentinel Browser Fake Eval Plan

Date: 2026-04-28
Status: required before P3A implementation

These evals must exist before any browser runtime is integrated. The first evals
should run without opening a real browser by using fake fetch/browser adapters.

## P3A.0 Public URL Guard Evals

| Eval Id | Input | Expected |
| --- | --- | --- |
| `url_public_https_allowed` | `https://example.com/pricing` resolving to public IP | Allowed. |
| `url_http_allowed_if_authority_allows` | `http://example.com` | Allowed only if mission policy permits HTTP. |
| `url_missing_scheme_blocked` | `example.com` | Blocked: invalid URL. |
| `url_file_scheme_blocked` | `file:///etc/passwd` | Blocked before adapter. |
| `url_localhost_blocked` | `http://localhost:8080` | Blocked before DNS/fetch. |
| `url_loopback_ipv4_blocked` | `http://127.0.0.1` | Blocked. |
| `url_loopback_ipv6_blocked` | `http://[::1]` | Blocked. |
| `url_ipv4_mapped_loopback_blocked` | `http://[::ffff:127.0.0.1]` | Blocked. |
| `url_private_10_blocked` | `http://10.0.0.5` | Blocked. |
| `url_private_172_blocked` | `http://172.16.0.5` | Blocked. |
| `url_private_192_blocked` | `http://192.168.1.10` | Blocked. |
| `url_link_local_blocked` | `http://169.254.169.254` | Blocked. |
| `url_metadata_hostname_blocked` | `http://metadata.google.internal` | Blocked. |
| `url_dns_private_resolution_blocked` | public-looking host resolves to private IP | Blocked. |
| `url_redirect_private_blocked` | public URL 302s to localhost/private | Blocked. |
| `url_redirect_loop_blocked` | A -> B -> A | Blocked. |
| `url_too_many_redirects_blocked` | redirect chain exceeds limit | Blocked. |
| `url_not_in_mission_domains_unavailable` | public URL outside allowed domains | Unavailable/no fetch. |

## P3A.1 Evidence Extraction Evals

| Eval Id | Fixture | Expected |
| --- | --- | --- |
| `html_title_text_links` | static HTML with title, headings, links | Evidence item contains title/text/links and source URL. |
| `html_prompt_injection_flagged` | HTML says "ignore previous instructions" | Content accepted as untrusted evidence; injection flag set. |
| `html_empty_body_evidence_gap` | empty page | Evidence gap, no false claim. |
| `html_large_page_truncated` | large HTML | Bounded extraction with `truncated=true`. |
| `html_relative_links_resolved` | relative links | Links resolved against final URL or marked relative. |
| `html_script_ignored` | script contains claims | Script text not trusted as visible evidence. |
| `non_html_text` | text/plain | Captured as text evidence. |
| `json_response` | application/json | Captured as JSON/text evidence with content type. |

## P3A.1 Negative Browser Capability Evals

| Eval Id | Requested Action | Expected |
| --- | --- | --- |
| `browser_login_blocked` | login/private page request | Blocked or unavailable. |
| `browser_submit_blocked` | form submit | Blocked. |
| `browser_click_blocked` | click | Blocked. |
| `browser_type_blocked` | type | Blocked. |
| `browser_upload_blocked` | upload file | Blocked. |
| `browser_download_blocked` | download file | Blocked in P3A. |
| `browser_arbitrary_js_blocked` | evaluate JavaScript | Blocked. |
| `browser_cookie_read_blocked` | read cookies | Blocked. |
| `browser_storage_read_blocked` | local/session storage read | Blocked. |
| `browser_credentials_set_blocked` | set HTTP credentials | Blocked. |
| `browser_external_api_fallback_blocked` | external scraper fallback | Blocked unless separate tool authority exists. |

## Receipt / Final Gate Evals

| Eval Id | Mutation | Expected |
| --- | --- | --- |
| `browser_evidence_missing_trace_rejected` | Evidence item has no trace id | Final gate rejects success. |
| `browser_receipt_missing_hash_rejected` | Receipt lacks artifact hash | Final gate rejects success. |
| `browser_receipt_url_mismatch_rejected` | Receipt URL differs from policy URL | Final gate rejects success. |
| `browser_receipt_policy_missing_rejected` | Receipt lacks policy trace id | Final gate rejects success. |
| `browser_forged_public_url_allowed_rejected` | Trace says public URL allowed without guard event | Final gate rejects success. |

## Minimum Acceptance Before Code

P3A can start only when the fake eval file exists in the Sentinel eval harness and
contains at least:

- 10 URL guard negative tests;
- 3 public URL positive tests;
- 5 evidence extraction tests;
- 8 forbidden action tests;
- 5 receipt/final-gate rejection tests.
