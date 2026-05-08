# Sentinel Browser V1 vs OpenClaw Browser Gap Analysis

Date: 2026-04-28
Status: strict local source comparison

This document is a harvest-lab artifact. It must stay outside product docs. Its
purpose is to compare Sentinel Browser V1 against the local OpenClaw source tree
and identify powerful browser capabilities that OpenClaw has and Sentinel does
not have yet.

## Source Basis

Sentinel source inspected:

```text
sentinel-control/services/sentinel-core/sentinel/agent/browser/
sentinel-control/services/sentinel-core/sentinel/agent/runtime.py
sentinel-control/services/sentinel-core/sentinel/agent/final_gate.py
sentinel-control/services/sentinel-core/tests/test_agent_browser_*.py
```

OpenClaw source inspected:

```text
agent-lab/vendors/openclaw/source/src/browser/
agent-lab/vendors/openclaw/source/src/agents/tools/browser-tool.ts
agent-lab/vendors/openclaw/source/src/agents/tools/browser-tool.schema.ts
agent-lab/vendors/openclaw/source/src/agents/tools/web-fetch.ts
agent-lab/vendors/openclaw/source/src/agents/tools/web-fetch-utils.ts
agent-lab/vendors/openclaw/source/src/infra/net/ssrf.ts
agent-lab/vendors/openclaw/source/src/infra/net/fetch-guard.ts
agent-lab/vendors/openclaw/source/src/gateway/server-methods/browser.ts
agent-lab/vendors/openclaw/source/src/gateway/protocol/schema/snapshot.ts
```

Observed size signal:

| Area | Sentinel | OpenClaw |
| --- | ---: | ---: |
| Browser module files | 9 | 81 under `src/browser/` |
| Browser tests | 36 Python tests | 445 browser-related test-case signals |
| Main browser tool schema | small internal action set | broad action schema |
| Runtime style | mission-governed read-only evidence | full browser control server/tool/gateway |

## Direct Verdict

OpenClaw is much stronger as a browser automation runtime.

Sentinel is stronger as a mission-governed, proof-first execution boundary.

The correct next move is not to paste OpenClaw into Sentinel. It is to extract
the strongest missing browser primitives one by one and force each through:

```text
MissionAuthority
-> ToolRegistry
-> RiskRouter
-> URL/Browser policy
-> Artifact/receipt
-> EventBus
-> CoreFinalGate
-> evals
```

## Capability Comparison

| Capability | Sentinel Browser V1 | OpenClaw Browser | Strict Verdict |
| --- | --- | --- | --- |
| Public URL guard | Yes. Blocks private/internal/metadata/obfuscated/redirect-loop/domain mismatch. | Yes, plus DNS pinning and guarded fetch. | OpenClaw stronger on DNS pinning. |
| Live public fetch | Yes. GET only, no redirects, no cookies, `trust_env=False`. | Yes. Guarded fetch with redirects and pinning. | OpenClaw stronger. |
| Rendered page capture | Yes. Fresh Playwright context, JS off, no downloads, no storage, document-only. | Yes. Full Playwright/CDP runtime. | OpenClaw stronger in breadth; Sentinel stronger in mission authority. |
| Screenshot | Yes, full-page PNG artifact. | Yes, PNG/JPEG, element/ref/full-page, normalization and max-byte control. | OpenClaw stronger. |
| HTML/text extraction | Yes, simple parser. | Yes, readability/linkedom fallback and markdown/text modes. | OpenClaw stronger. |
| Citation extraction | Yes, bounded quote snippets from rendered text. | Not observed as direct citation receipts in browser core, but has richer snapshots. | Sentinel stronger for evidence receipts; OpenClaw stronger for page structure. |
| Prompt injection flagging | Yes, basic flags. | Uses external content wrappers in web fetch. | Different; combine both patterns later. |
| ARIA/accessibility snapshot | No. | Yes: CDP AX tree, Playwright aria snapshot, AI snapshot fallback. | OpenClaw much stronger. |
| Stable element refs | No. | Yes: role/aria refs cached per target. | OpenClaw much stronger. |
| Click/type/press/hover | No. | Yes. | OpenClaw stronger; Sentinel must add as dry-run first. |
| Drag/select/fill | No. | Yes. | OpenClaw stronger; high-risk for Sentinel. |
| Wait predicates | No. | Yes: text, textGone, selector, URL, loadState, optional fn. | OpenClaw stronger. |
| JS evaluate | No, outside V1 authority. | Yes but gated by config. | Powerful high-impact primitive; not V1. |
| Downloads | No. | Yes: wait/download and click-to-download. | OpenClaw stronger but risky. |
| Upload/file chooser | No. | Yes: file chooser hooks and set input files. | OpenClaw stronger but high-risk. |
| Dialog handling | No. | Yes. | OpenClaw stronger. |
| Cookies/storage | No. | Yes: get/set/clear cookies, local/session storage. | OpenClaw stronger but outside V1 public-evidence authority. |
| Extra headers/credentials | No. | Yes. | OpenClaw stronger but high-risk. |
| Geolocation/timezone/media emulation | No. | Yes. | OpenClaw stronger. |
| PDF capture | No. | Yes. | OpenClaw stronger. |
| Network ledger | Minimal. | Yes: requests, responses, failures, console, page errors. | OpenClaw stronger. |
| Browser profiles | No. | Yes: named profiles, CDP port allocation, extension relay profile. | OpenClaw stronger. |
| Tab lifecycle | No. | Yes: open/list/focus/close/targetId. | OpenClaw stronger. |
| Remote browser node/proxy | No. | Yes through gateway/node browser proxy. | OpenClaw stronger. |
| Browser health/server lifecycle | Minimal. | Yes: control server, context, routes, service startup. | OpenClaw stronger. |
| Artifact receipts | Yes, with FinalGate proof. | Saves media/proxy files but not Sentinel-style mission receipts. | Sentinel stronger for audit. |
| Final gate | Yes. | Not Sentinel-style. | Sentinel stronger. |

## Powerful OpenClaw Features Sentinel Does Not Have Yet

Priority list from strongest to lowest leverage:

1. **DNS pinning for guarded fetch**
   - OpenClaw has `resolvePinnedHostname`, `createPinnedLookup`, and
     `createPinnedDispatcher`.
   - Sentinel checks DNS before fetch, but the actual HTTP connection is not
     pinned to the checked IPs.
   - Sentinel next action: implement pinned resolver/transport or equivalent
     proof that the connected address matches the approved DNS decision.

2. **Redirect-following with revalidation**
   - OpenClaw `fetchWithSsrFGuard` manually follows redirects, revalidates each
     URL, and limits redirect count.
   - Sentinel blocks live redirects instead of following them.
   - Sentinel next action: add controlled redirect-following only after DNS
     pinning exists.

3. **Readability-grade web extraction**
   - OpenClaw uses readability/linkedom fallback with markdown/text modes.
   - Sentinel uses simple HTMLParser extraction.
   - Sentinel next action: add `ReadablePageExtractor` with source metadata,
     fallback path, extracted title, text, links, and truncation proof.

4. **ARIA/accessibility snapshots**
   - OpenClaw captures CDP AX tree and Playwright ARIA/AI snapshots.
   - Sentinel only captures visible text, links, HTML, screenshot, and citations.
   - Sentinel next action: add `BrowserAccessibilitySnapshot` as read-only
     evidence, not interaction authority.

5. **Stable element references**
   - OpenClaw stores role/aria refs per target so later actions can refer to
     page elements.
   - Sentinel has no element ref model.
   - Sentinel next action: create refs only in dry-run planning first. Refs
     must expire and bind to page hash/snapshot trace.

6. **Network/console/page-error ledger**
   - OpenClaw tracks requests, responses, failed requests, console messages, and
     page errors in page state.
   - Sentinel currently records only high-level browser capture events.
   - Sentinel next action: capture a bounded read-only network ledger and attach
     it to the browser receipt.

7. **Screenshot normalization**
   - OpenClaw normalizes screenshots by max side and max bytes, converting to
     JPEG when needed.
   - Sentinel captures PNG screenshot and enforces only max screenshot bytes at
     adapter level.
   - Sentinel next action: add max-side/max-byte normalization to artifact
     capture before accepting screenshots.

8. **Element/ref screenshots**
   - OpenClaw supports full page, element selector, and ref screenshots.
   - Sentinel supports only page screenshot.
   - Sentinel next action: add ref screenshot after ARIA refs exist.

9. **Browser profiles and tab lifecycle**
   - OpenClaw has named profiles, CDP port allocation, tab targeting, last target
     tracking, extension relay support.
   - Sentinel has no session/profile/tab concept.
   - Sentinel next action: only add stateless tab lifecycle for public pages
     first; persistent profiles require separate authority class.

10. **Wait predicates**
    - OpenClaw supports waits on time, text, textGone, selector, URL, loadState,
      and optionally JS function.
    - Sentinel currently waits only for `domcontentloaded` in renderer.
    - Sentinel next action: add non-JS wait predicates for read-only capture.

11. **Response-body extraction from browser network**
    - OpenClaw can wait for and read matching response bodies.
    - Sentinel has no response matching.
    - Sentinel next action: add read-only response ledger first, response body
      extraction second.

12. **PDF capture**
    - OpenClaw can capture page PDF.
    - Sentinel cannot.
    - Sentinel next action: add as artifact-only, no mutation, gated by receipt
      and file-size limits.

13. **Controlled interactions**
    - OpenClaw supports click, type, press, hover, drag, select, fill.
    - Sentinel deliberately does not.
    - Sentinel next action: add `BrowserInteractionPlan` dry-run before any real
      execution. Submit/post/send must remain blocked until a later phase.

14. **Download handling**
    - OpenClaw can wait for downloads and save them.
    - Sentinel blocks downloads.
    - Sentinel next action: keep blocked until file quarantine, MIME scan, hash,
      receipt, and explicit mission authority exist.

15. **Cookie/storage/header/credential/geolocation/timezone controls**
    - OpenClaw supports these.
    - Sentinel has none, and should not add them early.
    - Sentinel next action: treat as private/session power, not public browser
      evidence. Requires separate authority envelope fields.

16. **Remote browser node/proxy**
    - OpenClaw routes browser requests through gateway nodes when available.
    - Sentinel has no remote browser node runtime.
    - Sentinel next action: not before Browser V1.5 is stable locally.

## What Sentinel Has That OpenClaw Browser Does Not Provide Natively

This matters because the goal is not "copy the bigger browser." The goal is a
browser organ inside Sentinel's brain.

| Sentinel Strength | Why It Matters |
| --- | --- |
| `MissionAuthorityEnvelope` | Browser power is mission-scoped, not globally available. |
| `ToolRegistry` decision before use | Browser code existing does not imply permission. |
| `EventBus` hash-chain | Every browser decision is auditable. |
| Browser-specific receipts | Captured output has hashes, trace refs, and receipt IDs. |
| `CoreFinalGate` browser receipt check | Forged browser success is rejected. |
| Evidence-first result shape | Browser output becomes evidence, not truth. |
| Product-doc separation | Vendor harvest stays in lab, Sentinel docs stay clean. |

## Strict Assessment Of Our "From Scratch" Choice

The current Browser V1 implementation was built Sentinel-native rather than as a
direct import. That was correct for the core boundary but incomplete for browser
depth.

What was correct:

- not importing OpenClaw runtime lifecycle;
- not importing broad act/storage/download/session powers;
- building receipts and FinalGate around browser output;
- keeping Browser V1 read-only and public.

What was weaker:

- we did not reuse enough of OpenClaw's mature browser test patterns yet;
- we did not port DNS pinning;
- we did not port readability extraction;
- we did not port ARIA/role snapshot patterns;
- we did not port screenshot normalization;
- we did not create a full extraction matrix per OpenClaw browser file before
  coding V1.

Verdict:

The foundation is correct, but Browser V1 should now enter a harvest-driven
hardening pass instead of moving to another organ.

## Recommended Browser-Only Roadmap

No next organ until these are done.

### P3C - Browser Guard Hardening

- DNS pinning for fetch path;
- redirect-following with revalidation;
- MIME allowlist;
- response compression/size accounting;
- hostile URL regression tests copied as patterns from OpenClaw SSRF tests.

### P3D - Browser Evidence Quality

- readability extractor;
- source metadata;
- source quality flags;
- stronger prompt-injection wrapper;
- citation accuracy tests.

### P3E - Browser Snapshot V2

- accessibility/ARIA snapshot;
- stable refs;
- labelled screenshot option;
- element/ref screenshot;
- screenshot normalization.

### P3F - Browser Runtime Observability

- network request ledger;
- response status ledger;
- HAR/body capture and frame-aware diagnostics;
- trace-bound browser health metadata.

### P3G - Browser Interaction Dry-Run

- create `BrowserInteractionPlan`;
- support click/type/fill/select as simulated planned actions only;
- FinalGate must prove no submit/post/send occurred;
- no real interaction execution yet.

### P3H - Browser Real Interaction Gate

Only after P3G passes:

- limited real clicks on same public page;
- no submit;
- no login;
- no upload/download;
- no credentials;
- no private pages;
- every interaction must be a receipt-bound event.

## Extraction Matrix

| OpenClaw File | Powerful Primitive | Sentinel Status | Verdict |
| --- | --- | --- | --- |
| `src/infra/net/ssrf.ts` | DNS pinning, private IP checks, pinned dispatcher. | Partial URL guard only. | Rewrite required, high priority. |
| `src/infra/net/fetch-guard.ts` | Redirect-following with SSRF revalidation. | Redirects blocked. | Rewrite required after DNS pinning. |
| `src/agents/tools/web-fetch-utils.ts` | Readability extraction and markdown/text fallback. | Simple parser. | Adapter pattern candidate. |
| `src/browser/pw-tools-core.snapshot.ts` | ARIA/AI/role snapshot and refs. | Missing. | Rewrite required, high priority. |
| `src/browser/pw-role-snapshot.ts` | Role snapshot formatting/stats/refs. | Missing. | Rewrite required, high priority. |
| `src/browser/screenshot.ts` | Screenshot normalization. | Partial byte limit only. | Rewrite required. |
| `src/browser/pw-session.ts` | Page state, refs cache, network/console/error ledger. | Missing. | Adapter-only ideas; do not copy lifecycle. |
| `src/browser/routes/agent.snapshot.ts` | Snapshot/screenshot/PDF routes. | Rendered snapshot only. | Test-pattern and schema ideas. |
| `src/browser/routes/agent.act.ts` | Full interaction and download routes. | Blocked. | Negative tests now; dry-run design later. |
| `src/browser/pw-tools-core.interactions.ts` | Click/type/drag/select/fill. | Missing. | Dry-run first, real execution later. |
| `src/browser/pw-tools-core.downloads.ts` | Download/upload/dialog hooks. | Blocked. | Reject for now. |
| `src/browser/pw-tools-core.storage.ts` | Cookies/storage/headers/credentials/geolocation/timezone. | Blocked. | Reject for public Browser V1; separate private authority later. |
| `src/agents/tools/browser-tool.schema.ts` | Broad typed browser action schema. | Small action schema. | Use as taxonomy only. |
| `src/gateway/server-methods/browser.ts` | Node/proxy browser routing. | Missing. | Defer; not Browser V1. |

## Final Decision

Sentinel Browser V1 is acceptable as a certified read-only evidence organ.
Compared to OpenClaw, it is still shallow as a browser runtime.

The next work must stay on browser and should be:

```text
P3C Browser Guard Hardening
-> DNS pinning
-> redirect revalidation
-> MIME gates
-> hostile URL tests
```

Only after that should we move to ARIA snapshots and interaction dry-runs.
