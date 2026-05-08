# OpenClaw Browser Extraction Matrix Draft

Date: 2026-04-28
Status: initial classification, not approved for reuse

| Source | Verdict | Why It Matters | Main Risk | Sentinel Mapping |
| --- | --- | --- | --- | --- |
| `src/browser/cdp.ts` | `adapter_only` | CDP command taxonomy and connection lifecycle. | Too coupled to vendor service lifecycle. | Rewrite minimal CDP adapter later if needed. |
| `src/browser/cdp.helpers.ts` | `test_pattern_only` | Helper behavior may reveal edge cases. | Helper assumptions may hide authority-weak defaults. | Convert edge cases into Sentinel tests. |
| `src/browser/chrome.ts` | `rewrite_required` | Browser executable/profile launch logic. | Launching browser is outside current phase. | Future controlled launcher, not P3A docs stage. |
| `src/browser/pw-session.ts` | `rewrite_required` | Session model and page targeting. | Profiles/cookies/private state. | Sentinel-owned session with mission authority only. |
| `src/browser/pw-tools-core.snapshot.ts` | `adapter_only` | Snapshot extraction patterns. | May depend on active Playwright runtime and page state. | Evidence snapshot schema and fake evals. |
| `src/browser/pw-role-snapshot.ts` | `adapter_only` | Accessibility/role snapshot ideas. | Can expose private page structure if uncontrolled. | Read-only public-page extraction only. |
| `src/browser/screenshot.ts` | `adapter_only` | Screenshot size/capture conventions. | Screenshot may include sensitive/private content. | Future artifact capture with public URL guard. |
| `src/browser/routes/agent.snapshot.ts` | `adapter_only` | HTTP route shape for read-only observation. | Route bypasses Sentinel authority if copied directly. | Sentinel browser observe command contract. |
| `src/browser/routes/agent.act.ts` | `reject` for P3A | Mutating browser actions. | Click/input/submit can mutate external state. | Negative tests only until separate authority exists. |
| `src/browser/routes/agent.storage.ts` | `reject` for P3A | Storage/session operations. | Cookies/session/private state. | Do not expose in read-only browser. |
| `src/browser/routes/agent.debug.ts` | `adapter_only` / `reject trace` | Console/errors/requests can support evidence; trace zip writes are too broad. | Debug traces may capture sensitive state. | Future metadata receipt, no trace zip in P3A. |
| `src/browser/routes/tabs.ts` | `rewrite_required` | Tab open/list/focus/close surface. | Raw URL navigation and UI mutation. | Rewrite only `open_public_url` with URL guard. |
| `src/browser/routes/basic.ts` | `docs_only` / `reject` | Browser server status and profile lifecycle. | Starts/stops/deletes profiles. | No product import. |
| `src/browser/pw-tools-core.interactions.ts` | `reject` for P3A | Click/type/input operations. | External mutation and prompt-injection amplification. | Future gated action module only. |
| `src/browser/pw-tools-core.downloads.ts` | `reject` for P3A | Download capture/wait logic. | Malware, executable downloads, path handling. | Future download policy after evidence engine. |
| `src/infra/net/ssrf.ts` | `copy_candidate` / `test_pattern_only` | SSRF and private address guard logic. | Must be audited for completeness and language/runtime differences. | Sentinel URL guard and negative evals. |
| `src/infra/net/fetch-guard.ts` | `copy_candidate` / `test_pattern_only` | Redirect revalidation, DNS pinning, max redirect handling. | TypeScript/undici-specific dispatcher. | Python `PublicUrlGuard` plus tests. |
| `src/agents/tools/web-fetch.ts` | `adapter_only` | Tool-facing fetch pattern. | Direct network access if copied. | Capability manifest and fake evals, not runtime. |
| `src/agents/tools/web-fetch-utils.ts` | `adapter_only` | HTML-to-markdown/text and readability fallback. | Parser output can hide evidence gaps or hallucinated structure. | Sentinel evidence extraction helper with source refs. |
| `src/agents/tools/web-fetch.ssrf.test.ts` | `test_pattern_only` | Negative tests for hostile URLs. | Test assumptions may not match Sentinel policy. | Convert to Sentinel browser fake evals. |
| `src/security/external-content.ts` | `adapter_only` | Untrusted content wrapping and injection-pattern detection. | Warning-text approach is prompt-layer, not proof-layer. | Structured `injection_flags` and `content_trust`. |
| `src/agents/tools/browser-tool.schema.ts` | `adapter_only` | Tool schema and action taxonomy. | Schema may include actions Sentinel forbids. | Minimal read-only manifest schema. |
| `src/gateway/protocol/schema/snapshot.ts` | `adapter_only` | Snapshot payload contract. | Coupled to gateway protocol. | Evidence item schema reference. |
| `src/cli/browser-cli*.ts` | `docs_only` | Operational behavior and edge cases. | CLI is not Sentinel authority. | Manual forensic notes only. |
| `Dockerfile.sandbox-browser` and scripts | `docs_only` | Future sandbox assumptions. | Runtime launch, dependency install. | Future sandbox design, not current implementation. |

## Initial Decision

The first Sentinel browser should not import a live browser server, CLI, profile
manager, gateway route, or action router.

The useful extraction is:

- URL/SSRF guard ideas;
- redirect-by-redirect public URL validation;
- external content wrapping and injection flagging;
- snapshot schemas;
- text/link/title extraction patterns;
- screenshot capture conventions;
- negative tests for action routes, storage, downloads, and private URLs.

## Pass 1 Correction

The first Sentinel browser implementation should be split:

```text
P3A.0 PublicUrlGuard + public evidence fetch contract
P3A.1 Read-only browser snapshot using the same guard
P3A.2 Screenshot artifact capture
```

Do not start with the full browser control server. The server is too coupled to
profiles, tabs, storage, action routes, downloads, credentials, and local
runtime lifecycle.
