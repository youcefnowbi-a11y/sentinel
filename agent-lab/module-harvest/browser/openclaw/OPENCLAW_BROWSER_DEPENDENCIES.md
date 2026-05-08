# OpenClaw Browser Dependencies

Date: 2026-04-28
Status: static forensic pass 1

## Runtime Dependencies Observed

| Dependency | Seen In | Role | Sentinel Decision |
| --- | --- | --- | --- |
| `express` | `src/browser/server.ts` | Local browser control HTTP server. | Do not import. Sentinel should expose no vendor browser server. |
| `playwright-core` | `package.json`, `pw-session.ts`, `pw-tools-core.*` | CDP connection, page control, snapshots, screenshots, actions. | Future dependency candidate only after contract/evals. |
| CDP HTTP/WS endpoints | `cdp.ts`, `server-context.ts`, `chrome.ts` | Connect to browser targets and capture state. | Rewrite under Sentinel authority. |
| `undici` | `infra/net/ssrf.ts`, `fetch-guard.ts` | Fetch dispatcher with pinned DNS lookup. | Pattern useful; Python implementation likely differs. |
| `node:dns` | `infra/net/ssrf.ts` | Resolve and pin hostnames. | Strong pattern for URL guard. |
| `@mozilla/readability` | `web-fetch-utils.ts` | Readable HTML extraction. | Good candidate for equivalent extractor. |
| `linkedom` | `web-fetch-utils.ts` | HTML parsing for readability. | Equivalent parser acceptable. |
| media/image pipeline | `screenshot.ts`, `media/image-ops.ts` | Screenshot resize/compression. | Pattern useful for artifact capture. |
| media store | `agent.snapshot.ts` | Saves PDF/screenshot outputs. | Reject vendor store; use Sentinel artifact capture. |
| config/profile system | `config.ts`, `profiles.ts`, `profiles-service.ts` | Browser config, CDP ports, profiles, colors. | Reject for product runtime. |
| extension relay | `server.ts`, `server-context.ts` | Connect Chrome extension tabs. | Reject for P3A. |
| Firecrawl API fallback | `web-fetch.ts` | External scrape fallback with API key. | Reject in P3A. External API is separate capability. |

## Lifecycle Couplings

The browser path is coupled to:

- global config loading and writing;
- local port allocation;
- browser profile creation/deletion;
- persistent Playwright connection cache;
- local Chrome process start/stop;
- extension relay startup;
- media store output path;
- optional external scraping API;
- local HTTP routes.

Sentinel cannot import this lifecycle cleanly because it would bring a second
authority system. The correct move is to rewrite a thin adapter that takes
`MissionAuthorityEnvelope` as its only authority source.

## Dependency Risks

| Risk | Evidence | Sentinel Mitigation |
| --- | --- | --- |
| Profile state becomes authority | Profiles can be created/deleted and carry CDP URLs. | No profile authority in P3A. Public URL only. |
| Browser session leaks private content | Cookies/storage routes and extension relay exist. | No cookies/storage/private profile access. |
| Navigation reaches internal networks | Browser navigation accepts raw URLs; fetch path has SSRF guard but browser navigation path must be reviewed separately. | Build Sentinel URL guard before navigation. |
| Arbitrary JS execution | `evaluate` action and CDP `Runtime.evaluate`. | Block arbitrary JS in P3A. |
| External API fallback | Firecrawl API key/env fallback. | No external API fallback in first browser capability. |
| File output outside Sentinel capture | PDF/screenshot media store writes vendor paths. | Use `ArtifactCaptureSandbox` only. |
| Downloads and uploads | Action routes include download and file chooser hooks. | Block until separate authority and sandbox. |

## Reusable Patterns

- DNS resolution before fetch.
- Private/loopback/internal IP blocking.
- Redirect-by-redirect revalidation.
- DNS pinning for fetch dispatcher.
- Max redirect limit.
- Timeout and abort handling.
- Max char limits.
- Screenshot max side/max bytes normalization.
- Untrusted content wrapping.
- Prompt-injection pattern detection.
- Role/ARIA snapshot fallback structure.

## Not Reusable As-Is

- Browser server lifecycle.
- Route handlers.
- Profile management.
- Storage/cookies/credentials routes.
- Action routes.
- Vendor media store.
- External scrape fallback.
- Extension relay.
