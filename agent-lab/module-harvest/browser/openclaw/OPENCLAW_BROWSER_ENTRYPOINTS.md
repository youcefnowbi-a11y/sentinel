# OpenClaw Browser Entrypoints

Date: 2026-04-28
Status: static forensic pass 1

Source root:

```text
agent-lab/vendors/openclaw/source/
```

This file maps browser entrypoints and separates observation paths from mutating
paths. It is a harvest artifact only.

## Server Lifecycle

Primary server:

```text
src/browser/server.ts
```

Observed lifecycle:

```text
startBrowserControlServerFromConfig()
-> loadConfig()
-> resolveBrowserConfig()
-> express()
-> registerBrowserRoutes()
-> listen on 127.0.0.1:controlPort
-> optionally start Chrome extension relay for extension profiles
```

Verdict:

```text
rewrite_required
```

Reason: the lifecycle owns browser startup, profiles, relay, config, and local
ports. Sentinel must not import this as-is because authority would come from the
vendor server and profile state rather than `MissionAuthorityEnvelope`.

## Route Registration

```text
src/browser/routes/index.ts
-> registerBrowserBasicRoutes()
-> registerBrowserTabRoutes()
-> registerBrowserAgentRoutes()

src/browser/routes/agent.ts
-> registerBrowserAgentSnapshotRoutes()
-> registerBrowserAgentActRoutes()
-> registerBrowserAgentDebugRoutes()
-> registerBrowserAgentStorageRoutes()
```

Key finding:

```text
Observation and mutation are registered together.
```

Sentinel must split these into separate capability families:

- `browser_readonly_public_evidence`
- future `browser_interaction_controlled`
- future `browser_storage_private` (likely blocked for a long time)

## Basic Routes

Source:

```text
src/browser/routes/basic.ts
```

Observed routes:

| Route | Behavior | Sentinel P3A |
| --- | --- | --- |
| `GET /profiles` | Lists browser profiles and status. | Reject. Profile inventory is vendor state. |
| `GET /` | Browser server status, CDP readiness, user data dir, executable path. | Docs/test pattern only. |
| `POST /start` | Starts browser for selected profile. | Reject for P3A. |
| `POST /stop` | Stops browser for selected profile. | Reject for P3A. |
| `POST /reset-profile` | Stops browser and moves profile data to trash. | Reject. Destructive profile mutation. |
| `POST /profiles/create` | Creates browser profile and writes config. | Reject. Creates authority-like state. |
| `DELETE /profiles/:name` | Deletes browser profile and may move profile dir. | Reject. |

Verdict:

```text
docs_only / reject for runtime
```

## Tab Routes

Source:

```text
src/browser/routes/tabs.ts
```

Observed routes:

| Route | Behavior | Sentinel P3A |
| --- | --- | --- |
| `GET /tabs` | Lists tabs. | Reject for first public evidence version. |
| `POST /tabs/open` | Opens URL in tab. | Rewrite as controlled public URL open only. |
| `POST /tabs/focus` | Focuses a tab. | Reject. UI mutation. |
| `DELETE /tabs/:targetId` | Closes a tab. | Reject. |
| `POST /tabs/action` | list/new/close/select tab actions. | Reject. |

Key finding:

`tabs/open` accepts a raw URL and delegates to the profile context. The inspected
path does not show Sentinel-style URL authority, public-only policy, SSRF checks,
or evidence receipt binding.

Verdict:

```text
rewrite_required
```

## Snapshot Routes

Source:

```text
src/browser/routes/agent.snapshot.ts
```

Observed routes:

| Route | Behavior | Sentinel P3A |
| --- | --- | --- |
| `POST /navigate` | Navigates active tab to raw URL through Playwright. | Rewrite with URL guard and receipt. |
| `POST /pdf` | Generates PDF from active page and saves media. | Reject for P3A. |
| `POST /screenshot` | Captures screenshot, normalizes size, saves media. | Adapter pattern for future capture. |
| `GET /snapshot` | Returns ARIA/AI/role snapshot, optional labels/screenshot. | Adapter pattern for read-only snapshot. |

Key findings:

- The file name suggests observation, but it includes navigation and PDF.
- Snapshot can use Playwright private `_snapshotForAI` or ARIA fallback.
- `mode=efficient` defaults to compact interactive role snapshot.
- `labels=true` creates a labeled screenshot artifact.
- There is max-char limiting for AI snapshots.

Sentinel extraction:

```text
snapshot schema + max char limits + ARIA/role fallback = useful
route structure + profile/session authority = reject
navigation in same module as observation = reject
```

Verdict:

```text
adapter_only / rewrite_required
```

## Action Routes

Source:

```text
src/browser/routes/agent.act.ts
```

Observed actions:

```text
click
type
press
hover
scrollIntoView
drag
select
fill
resize
wait
evaluate
close
file chooser hook
dialog hook
wait/download
download
response/body
highlight
```

P3A decision:

```text
reject
```

Reason: these actions can mutate external state, upload files, trigger
downloads, execute page JavaScript, accept dialogs, submit forms, alter browser
state, or extract response bodies from a live session.

Useful extraction:

- negative tests;
- action taxonomy;
- future permission categories.

## Storage Routes

Source:

```text
src/browser/routes/agent.storage.ts
```

Observed routes:

```text
GET /cookies
POST /cookies/set
POST /cookies/clear
GET /storage/:kind
POST /storage/:kind/set
POST /storage/:kind/clear
POST /set/offline
POST /set/headers
POST /set/credentials
POST /set/geolocation
POST /set/media
POST /set/timezone
POST /set/locale
POST /set/device
```

P3A decision:

```text
reject
```

Reason: cookies, local/session storage, HTTP credentials, headers, geolocation,
timezone, locale, media emulation, and device emulation are stateful/private
browser capabilities. They do not belong in first read-only public evidence.

## Debug Routes

Source:

```text
src/browser/routes/agent.debug.ts
```

Observed routes:

```text
GET /console
GET /errors
GET /requests
POST /trace/start
POST /trace/stop
```

P3A decision:

```text
adapter_only for console/errors/requests
reject trace start/stop for P3A
```

Reason: console/errors/requests can be evidence metadata after a page is
captured. Trace start/stop writes zip files and captures richer page state, so it
needs a later artifact policy.

## Entrypoint Verdict

The browser organ is powerful but not separable by default.

Sentinel should not import:

- server lifecycle;
- profile management;
- tab management;
- action routes;
- storage routes;
- direct debug trace routes.

Sentinel should extract:

- URL/public-network guard patterns from fetch/SSRF modules;
- snapshot schema and max-char ideas;
- screenshot normalization idea;
- untrusted content wrapper and injection detection pattern;
- negative tests for action/storage/download/evaluate.
