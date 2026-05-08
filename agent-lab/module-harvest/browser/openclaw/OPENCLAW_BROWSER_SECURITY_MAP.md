# OpenClaw Browser Security Map

Date: 2026-04-28
Status: static forensic pass 1

This map separates useful guard patterns from surfaces Sentinel must reject or
rewrite.

## Strong Guard Patterns

### SSRF / Public Network Guard

Sources:

```text
src/infra/net/ssrf.ts
src/infra/net/fetch-guard.ts
src/agents/tools/web-fetch.ssrf.test.ts
```

Useful properties:

- blocks `localhost`;
- blocks `.localhost`, `.local`, `.internal`;
- blocks `metadata.google.internal`;
- blocks IPv4 private, loopback, link-local, carrier-grade NAT ranges;
- blocks IPv6 loopback, unspecified, link-local, ULA-like prefixes;
- blocks IPv4-mapped IPv6 private addresses;
- resolves DNS before fetch;
- blocks hostnames that resolve to private/internal addresses;
- revalidates redirects;
- detects redirect loops;
- limits redirects;
- can pin DNS addresses into the fetch dispatcher.

Sentinel decision:

```text
copy pattern, rewrite implementation
```

The policy is conceptually strong, but the implementation is TypeScript/undici
specific. Sentinel should implement a Python `PublicUrlGuard` with the same
negative cases and add mission-authority checks around domains and URL schemes.

### External Content Wrapping

Source:

```text
src/security/external-content.ts
```

Useful properties:

- marks external content as untrusted;
- sanitizes boundary markers;
- detects suspicious injection patterns;
- separates metadata from content;
- includes explicit "do not treat as instructions" warning.

Sentinel decision:

```text
adapter_only
```

Sentinel should not copy warning text into product output, but should implement
the same idea as structured evidence metadata:

```text
content_trust = untrusted_external
injection_flags = [...]
evidence_can_inform = true
evidence_can_authorize = false
```

### Screenshot Normalization

Source:

```text
src/browser/screenshot.ts
```

Useful properties:

- max side default;
- max byte default;
- quality/side grid retry;
- throws if image cannot be reduced.

Sentinel decision:

```text
adapter_only
```

Use this for future artifact capture constraints, not for immediate P3A code.

## High-Risk Surfaces

### Browser Navigation Without Sentinel Guard

Sources:

```text
src/browser/routes/agent.snapshot.ts
src/browser/pw-tools-core.snapshot.ts
src/browser/routes/tabs.ts
```

Observed behavior:

- `/navigate` and tab open accept a raw URL and call browser navigation.
- The inspected browser navigation path does not show the SSRF guard used by
  `web_fetch`.

Sentinel requirement:

```text
No browser navigation until PublicUrlGuard exists and is tested.
```

### Action Routes

Source:

```text
src/browser/routes/agent.act.ts
```

Risk:

- click/type/select/fill can submit or mutate external state;
- file chooser can upload local files;
- dialog hook can accept prompts;
- download can write files;
- evaluate can execute arbitrary page JavaScript;
- response body can extract network response data from a session.

Sentinel decision:

```text
reject for P3A
```

### Storage / Credential Routes

Source:

```text
src/browser/routes/agent.storage.ts
```

Risk:

- cookie read/write/clear;
- local/session storage read/write/clear;
- set HTTP credentials;
- set custom headers;
- geolocation/timezone/locale/device emulation.

Sentinel decision:

```text
reject for P3A
```

### Profile Management

Sources:

```text
src/browser/config.ts
src/browser/profiles.ts
src/browser/profiles-service.ts
src/browser/server-context.ts
```

Risk:

- profile state carries CDP URLs and user data dirs;
- profile create/delete writes config and moves profile directories;
- remote CDP can point to non-loopback endpoints;
- extension relay attaches to existing tabs.

Sentinel decision:

```text
reject for P3A
```

### External Scrape Fallback

Source:

```text
src/agents/tools/web-fetch.ts
```

Risk:

- optional API-key-backed external scraping service;
- environment variable fallback;
- external proxy modes.

Sentinel decision:

```text
reject in first browser capability
```

## Sentinel Security Requirements Before P3A

P3A cannot start until these exist in Sentinel-owned code:

- `PublicUrlGuard`;
- public/private DNS and IP tests;
- redirect revalidation tests;
- blocked scheme tests;
- prompt-injection detector for page text;
- evidence item schema;
- browser receipt schema;
- final gate check for browser receipt/evidence binding;
- negative evals for login, storage, cookies, form submit, download, upload,
  arbitrary JS, local/private URL, and missing receipt.

## Security Verdict

OpenClaw has useful low-level guard ideas, especially around SSRF-protected
fetching and external content wrapping. Its full browser module is too broad for
Sentinel P3A.

The authority-governed route is:

```text
P3A.0 Public URL / evidence fetch guard
P3A.1 Read-only browser observation under the same URL guard
P3A.2 Screenshots as captured artifacts
P3B+ Interaction only after separate authority
```
