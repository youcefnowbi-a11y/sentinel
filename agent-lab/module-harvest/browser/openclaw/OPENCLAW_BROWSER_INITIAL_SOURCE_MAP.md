# OpenClaw Browser Initial Source Map

Date: 2026-04-28
Status: first local static map

Source root:

```text
agent-lab/vendors/openclaw/source/
```

This is an initial map only. It identifies where the browser organ appears to
live and which files deserve forensic review. It does not certify any file for
reuse yet.

## Primary Browser Runtime

```text
src/browser/
```

Observed high-signal files:

```text
src/browser/server.ts
src/browser/server-context.ts
src/browser/server-context.types.ts
src/browser/client.ts
src/browser/client-fetch.ts
src/browser/client-actions.ts
src/browser/client-actions-core.ts
src/browser/client-actions-observe.ts
src/browser/client-actions-state.ts
src/browser/client-actions-types.ts
src/browser/control-service.ts
src/browser/bridge-server.ts
src/browser/constants.ts
src/browser/config.ts
```

## Browser Protocol And Automation

```text
src/browser/cdp.ts
src/browser/cdp.helpers.ts
src/browser/chrome.ts
src/browser/chrome.executables.ts
src/browser/chrome.profile-decoration.ts
src/browser/pw-session.ts
src/browser/pw-ai.ts
src/browser/pw-ai-module.ts
src/browser/pw-role-snapshot.ts
src/browser/pw-tools-core.ts
src/browser/pw-tools-core.activity.ts
src/browser/pw-tools-core.downloads.ts
src/browser/pw-tools-core.interactions.ts
src/browser/pw-tools-core.responses.ts
src/browser/pw-tools-core.screenshots-element-selector.test.ts
src/browser/pw-tools-core.snapshot.ts
src/browser/pw-tools-core.state.ts
src/browser/pw-tools-core.storage.ts
src/browser/pw-tools-core.trace.ts
src/browser/screenshot.ts
```

Dependency signal:

```text
package.json -> playwright-core 1.58.1
```

## Browser Routes

```text
src/browser/routes/index.ts
src/browser/routes/dispatcher.ts
src/browser/routes/basic.ts
src/browser/routes/tabs.ts
src/browser/routes/types.ts
src/browser/routes/utils.ts
src/browser/routes/agent.ts
src/browser/routes/agent.act.ts
src/browser/routes/agent.act.shared.ts
src/browser/routes/agent.debug.ts
src/browser/routes/agent.shared.ts
src/browser/routes/agent.snapshot.ts
src/browser/routes/agent.storage.ts
```

First classification:

- `agent.snapshot.ts` is likely useful for read-only observation patterns.
- `agent.act.ts` is outside P3A authority except as a negative-test source.
- `agent.storage.ts` is high-risk because storage/session state can imply
  private context.

## Gateway Entrypoints

```text
src/gateway/server-browser.ts
src/gateway/server-methods/browser.ts
src/gateway/protocol/schema/snapshot.ts
```

Potential use:

- entrypoint map;
- schema ideas;
- test patterns for snapshot payloads.

Do not import the gateway lifecycle.

## Agent Tool Surface

```text
src/agents/tools/browser-tool.ts
src/agents/tools/browser-tool.schema.ts
src/agents/tools/browser-tool.test.ts
src/agents/tools/web-fetch.ts
src/agents/tools/web-fetch-utils.ts
src/agents/tools/web-fetch.ssrf.test.ts
src/agents/tools/web-tools.fetch.test.ts
src/agents/sandbox/browser.ts
src/agents/sandbox/browser-bridges.ts
```

Potential use:

- tool action taxonomy;
- schema ideas;
- SSRF negative tests;
- browser sandbox contract ideas.

Do not import agent tool execution flow.

## Network And SSRF Guards

```text
src/infra/net/ssrf.ts
src/infra/net/ssrf.pinning.test.ts
src/infra/net/fetch-guard.ts
src/infra/fetch.ts
src/infra/fetch.test.ts
src/media-understanding/attachments.ssrf.test.ts
```

Potential use:

- copy/test-pattern candidate for URL classification;
- negative eval patterns for localhost/private ranges;
- evidence-source guard design.

## CLI And Docs

```text
src/cli/browser-cli.ts
src/cli/browser-cli-state.ts
src/cli/browser-cli-state.cookies-storage.ts
src/cli/browser-cli-shared.ts
src/cli/browser-cli-manage.ts
src/cli/browser-cli-inspect.ts
src/cli/browser-cli-actions-observe.ts
src/cli/browser-cli-actions-input.ts
docs/tools/browser.md
docs/tools/browser-login.md
docs/tools/browser-linux-troubleshooting.md
docs/cli/browser.md
Dockerfile.sandbox-browser
scripts/sandbox-browser-setup.sh
scripts/sandbox-browser-entrypoint.sh
```

Potential use:

- operation model;
- sandbox assumptions;
- docs-only learning;
- negative boundary around login/cookies.

Do not reuse CLI as Sentinel runtime.

## Platform-Specific Visual Surfaces

```text
apps/macos/Sources/OpenClaw/ScreenshotSize.swift
apps/macos/Sources/OpenClaw/CanvasWindowController+Navigation.swift
apps/shared/OpenClawKit/Sources/OpenClawKit/StoragePaths.swift
apps/shared/OpenClawKit/Tests/OpenClawKitTests/CanvasSnapshotFormatTests.swift
```

Potential use:

- future UI/workspace ideas;
- snapshot format tests.

Not part of P3A read-only browser core.

## Immediate Forensic Targets

1. `src/browser/routes/agent.snapshot.ts`
2. `src/browser/pw-tools-core.snapshot.ts`
3. `src/browser/screenshot.ts`
4. `src/browser/cdp.ts`
5. `src/browser/pw-session.ts`
6. `src/infra/net/ssrf.ts`
7. `src/agents/tools/web-fetch.ts`
8. `src/agents/tools/browser-tool.schema.ts`
9. `src/gateway/protocol/schema/snapshot.ts`
10. `src/browser/routes/agent.act.ts` as negative-surface review
