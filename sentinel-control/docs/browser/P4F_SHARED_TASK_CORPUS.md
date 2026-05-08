# P4F Shared Task Corpus

Date: 2026-04-30
Status: Complete

## Task Groups

The P4F corpus reuses the P4E self-hosted benchmark groups so both Sentinel and
the peer runner face the same mission definitions.

| # | Group | Purpose |
| ---: | --- | --- |
| 1 | `form_workflow` | Form submit with post-action proof. |
| 2 | `search_navigation` | Public evidence and navigation. |
| 3 | `multi_page_task` | Multi-page browsing and verification. |
| 4 | `download_quarantine` | Download capture into quarantine equivalent. |
| 5 | `upload_authorized` | Upload from certified artifact equivalent. |
| 6 | `login_fixture` | Login/session fixture using account-id indirection. |
| 7 | `cookie_storage_redaction` | Cookie/storage redaction behavior. |
| 8 | `js_no_network_rejection` | Sandboxed JS network-attempt rejection. |
| 9 | `har_body_redaction` | HAR/body diagnostic redaction. |
| 10 | `visual_grounding` | UIObservation-style grounding task. |
| 11 | `research_browsing_citations` | Research browsing with citations. |
| 12 | `cross_class_authority_flow` | Session -> login -> storage -> HAR -> close flow. |
| 13 | `failure_denials` | Prompt injection, stale refs, and cross-origin denial. |

## Run Count

Critical P4F scorecards use:

```text
run_count = 30 per group
```

Dry runs may use fewer iterations, but cannot produce a supremacy verdict.

## Corpus Boundary

This is still self-hosted/lab-oriented. It is broader than unit tests, but it is
not a substitute for open-web external benchmark campaigns.
