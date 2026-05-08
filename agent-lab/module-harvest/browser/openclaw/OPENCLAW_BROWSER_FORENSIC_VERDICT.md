# OpenClaw Browser Forensic Verdict

Date: 2026-04-28
Status: pass 1 verdict

## Direct Verdict

Do not import the browser runtime.

Extract patterns, then build Sentinel-native.

## Why

The inspected browser module is strong but broad. It combines:

- local browser server;
- profile lifecycle;
- CDP and Playwright sessions;
- tab open/focus/close;
- navigate;
- snapshot;
- screenshot;
- PDF;
- click/type/fill/select/drag;
- arbitrary evaluate;
- file upload hooks;
- dialog hooks;
- downloads;
- response-body extraction;
- cookies;
- local/session storage;
- headers;
- credentials;
- geolocation/timezone/locale/device emulation;
- tracing;
- optional external scrape API.

That is too much authority surface for first integration.

## What To Reuse

| Pattern | Source | Sentinel Use |
| --- | --- | --- |
| SSRF/public URL guard | `src/infra/net/ssrf.ts`, `fetch-guard.ts` | Build `PublicUrlGuard`. |
| Redirect revalidation | `fetch-guard.ts` | Revalidate every redirect before fetch/navigation. |
| DNS pinning idea | `ssrf.ts` | Prevent DNS race for fetch path. |
| Untrusted content wrapper | `security/external-content.ts` | Build structured injection flags. |
| HTML extraction | `web-fetch-utils.ts` | Build evidence extraction helper. |
| ARIA/role snapshot schema | `pw-tools-core.snapshot.ts`, `pw-role-snapshot.ts` | Future read-only browser snapshot contract. |
| Screenshot normalization | `screenshot.ts` | Future artifact capture limits. |
| Negative tests | browser/action/storage/download tests | Sentinel forbidden-action evals. |

## What To Reject For P3A

- vendor browser server;
- vendor profile lifecycle;
- cookies and storage;
- credentials and headers;
- geolocation/timezone/locale/device;
- arbitrary JS evaluate;
- click/type/fill/select/drag;
- upload/download/dialog hooks;
- external scraper API fallback;
- browser trace zip capture;
- private or authenticated page flows.

## Correct Sentinel Sequence

```text
P3A.0 PublicUrlGuard + EvidenceFetch contract
P3A.1 Read-only browser snapshot adapter
P3A.2 Screenshot artifact capture
P3B Controlled interaction dry-run only
P3C Controlled interaction execution after separate authority
```

## Next Code Target

The first code target should not be Playwright.

It should be:

```text
sentinel/agent/browser/url_guard.py
sentinel/agent/browser/models.py
tests/test_agent_browser_url_guard.py
```

Reason: if URL authority is wrong, every later browser feature inherits a
critical flaw. Once URL guard and fake evals are green, the browser adapter can
be implemented with far less risk.
