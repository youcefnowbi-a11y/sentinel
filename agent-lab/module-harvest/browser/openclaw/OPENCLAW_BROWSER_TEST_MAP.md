# OpenClaw Browser Test Map

Date: 2026-04-28
Status: static forensic pass 1

This map identifies tests worth adapting into Sentinel evals or negative unit
tests. The tests are not run here.

## Browser Runtime Tests

```text
src/browser/server.agent-contract-snapshot-endpoints.test.ts
src/browser/server.agent-contract-form-layout-act-commands.test.ts
src/browser/server.covers-additional-endpoint-branches.test.ts
src/browser/server.post-tabs-open-profile-unknown-returns-404.test.ts
src/browser/server.serves-status-starts-browser-requested.test.ts
src/browser/server.skips-default-maxchars-explicitly-set-zero.test.ts
src/browser/server-context.ensure-tab-available.prefers-last-target.test.ts
src/browser/server-context.remote-tab-ops.test.ts
```

Sentinel use:

- `server.agent-contract-snapshot-endpoints.test.ts`: adapt expected snapshot
  payload shape into fake browser evals.
- `server.agent-contract-form-layout-act-commands.test.ts`: convert act
  commands into forbidden-action negative tests.
- context and remote-tab tests: docs-only, because Sentinel must avoid vendor
  profile/session lifecycle in P3A.

## Browser Protocol Tests

```text
src/browser/cdp.test.ts
src/browser/cdp.helpers.test.ts
src/browser/pw-session.test.ts
src/browser/pw-session.get-page-for-targetid.extension-fallback.test.ts
src/browser/pw-session.browserless.live.test.ts
src/browser/pw-ai.test.ts
src/browser/pw-role-snapshot.test.ts
src/browser/target-id.test.ts
```

Sentinel use:

- `pw-role-snapshot.test.ts`: adapt role/ARIA snapshot structure.
- `target-id.test.ts`: maybe adapt stable ref/target disambiguation logic later.
- `cdp.*`: keep as edge-case reference only.
- `browserless.live`: do not adapt into core tests.

## Capture And Media Tests

```text
src/browser/screenshot.test.ts
src/browser/pw-tools-core.screenshots-element-selector.test.ts
```

Sentinel use:

- adapt screenshot max-side/max-bytes behavior into artifact capture tests when
  screenshot capture is introduced.
- do not add screenshot runtime in P3A.0.

## Action / Upload / Download Tests

```text
src/browser/pw-tools-core.clamps-timeoutms-scrollintoview.test.ts
src/browser/pw-tools-core.last-file-chooser-arm-wins.test.ts
src/browser/pw-tools-core.waits-next-download-saves-it.test.ts
```

Sentinel use:

- negative evals: file chooser, download, and interaction are blocked in P3A.
- timeout clamping pattern may be useful later.

## Profile / Config Tests

```text
src/browser/config.test.ts
src/browser/profiles.test.ts
src/browser/profiles-service.test.ts
src/browser/chrome.test.ts
src/browser/chrome.default-browser.test.ts
src/browser/extension-relay.test.ts
```

Sentinel use:

- docs-only. These belong to vendor runtime lifecycle, not Sentinel P3A.

## Web Fetch And SSRF Tests

```text
src/agents/tools/web-fetch.ssrf.test.ts
src/agents/tools/web-tools.fetch.test.ts
src/agents/tools/web-tools.readability.test.ts
src/agents/tools/web-tools.enabled-defaults.test.ts
src/infra/net/ssrf.pinning.test.ts
src/infra/fetch.test.ts
src/media-understanding/attachments.ssrf.test.ts
```

Sentinel use:

- high value. Convert into Sentinel `PublicUrlGuard` unit tests and browser
  fake evals.

Critical cases to adapt:

- localhost hostname blocked before fetch;
- private IP literals blocked without DNS;
- IPv4-mapped IPv6 private IP blocked;
- DNS resolving to private address blocked;
- redirect to private host blocked;
- public host allowed;
- too many redirects blocked;
- redirect loop blocked;
- DNS pinning prevents post-resolution address swap;
- attachment/media fetch uses same guard.

## Browser Tool Schema Tests

```text
src/agents/tools/browser-tool.test.ts
src/agents/tools/browser-tool.schema.ts
```

Sentinel use:

- action taxonomy reference;
- negative tests for forbidden browser actions;
- do not copy broad schema because it includes start/stop/profiles/tabs/upload/dialog/act.

## Sentinel Eval Cases To Create

| Case | Expected |
| --- | --- |
| public URL text page | allowed, evidence item, receipt |
| public URL HTML page | title/text/links extracted, external content marked untrusted |
| localhost URL | blocked before navigation/fetch |
| private IPv4 URL | blocked |
| IPv4-mapped IPv6 localhost | blocked |
| hostname resolving to private IP | blocked |
| redirect to private URL | blocked |
| prompt-injection page text | allowed as evidence but injection flagged and not treated as instruction |
| login page | unavailable or blocked; no credential prompt |
| cookie/local storage request | blocked |
| form submit/action request | blocked |
| arbitrary JavaScript request | blocked |
| download request | blocked |
| missing browser receipt | final gate rejects success |
