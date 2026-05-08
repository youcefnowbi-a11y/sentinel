# P3N Browser Final Supremacy Review

Date: 2026-04-29
Status: Browser V2 review complete

## Purpose

This is the final Browser V2 comparison against the harvested OpenClaw browser
specimens. It stays in the lab because product code and product docs must remain
Sentinel-native and vendor-neutral.

The question is not whether Sentinel copied OpenClaw. It did not. The question
is whether Sentinel harvested the strongest browser primitives and rebuilt them
under Sentinel's authority, proof, receipt, and FinalGate model.

## Direct Verdict

Sentinel Browser V2 now matches or exceeds the harvested OpenClaw browser
strengths for public evidence, proof, receipts, bounded interactions, lifecycle
accounting, and mission governance.

OpenClaw remains broader as a general browser automation runtime. It still has
more surface area around persistent profiles, private sessions, broad CDP
control, storage/cookies, upload/download, arbitrary evaluation, device
emulation, and remote browser gateway operation.

That breadth is not a gap for Browser V2. It is intentionally outside Browser
V2's public mission-governed operator definition. Those powers belong to later
Browser V2.5/V3 authority classes.

## Final Capability Scorecard

| Axis | OpenClaw strength | Sentinel Browser V2 state | Verdict |
| --- | --- | --- | --- |
| URL / SSRF / host guard | Mature SSRF and fetch guard patterns. | `PublicUrlGuard`, private/internal rejection, redirect loop/count policy, DNS checks, per-hop revalidation. | Sentinel now competitive, with stronger mission proof. |
| DNS pinning / connection proof | Pinned lookup/dispatcher concepts. | `BrowserConnectionProof`, optional enforcement, pinned fetch path, receipt proof. | Sentinel competitive for governed fetch path. |
| Redirect handling | Manual redirect revalidation. | Evidence adapter follows response redirects only after reclassifying each hop. | Sentinel competitive. |
| MIME / size gates | Guarded fetch behavior. | MIME allowlist, compressed/uncompressed accounting, artifact rejection before receipt. | Sentinel stronger as evidence contract. |
| Readability extraction | Readability/linkedom-style extraction and fallback tests. | `ReadablePageExtractor`, strategies, quality flags, evidence-gap handling, truncation proof, citation offsets. | Sentinel competitive; OpenClaw may still be deeper on DOM fidelity. |
| Prompt-injection boundary | External content wrapper patterns. | Structured prompt-injection flags in evidence and receipts. | Sentinel stronger for auditability. |
| Rendered snapshot | Full browser runtime snapshots. | Rendered snapshot with URL policy, artifact capture, screenshot, citations, accessibility hash, network ledger. | Sentinel stronger for proof, OpenClaw broader for runtime. |
| Accessibility / role refs | ARIA/AI role snapshot patterns and stable refs. | Deterministic parser-backed role refs, duplicate `nth`, page/snapshot hash binding. | Sentinel competitive for planning; OpenClaw stronger on CDP-native accessibility tree. |
| Network / console / page errors | Page state ledger. | Canonical bounded `BrowserNetworkLedger`, health metadata, ledger hash, FinalGate verification. | Sentinel stronger for receipt-bound proof. |
| Screenshot quality | Max side/bytes normalization. | Screenshot metadata plus injected normalization proof; PDF and element screenshot contracts. | Sentinel competitive; built-in transcode still adapter-dependent. |
| PDF capture | Browser PDF support. | Optional PDF artifact with metadata and receipt checks. | Sentinel competitive for artifact proof. |
| Element screenshots | Element/ref screenshots. | Ref-bound element screenshots tied to accessibility refs and artifacts. | Sentinel competitive within public evidence boundary. |
| Interaction planning | Broad browser action schema. | P3G dry-run plans bound to stable refs, page hash, snapshot hash, and plan hash. | Sentinel stronger as pre-action reasoning layer. |
| Limited real interactions | click/type/fill/select/hover/waits. | P3H executes limited public interactions from certified plans, same-origin, post-action recapture. | Sentinel competitive for governed first-operator layer. |
| Public tab/session lifecycle | Browser target/page lifecycle. | P3I public stateless lifecycle ledger, URL-policy-bound open/navigation, receipts. | Sentinel stronger for public lifecycle proof; OpenClaw broader for profile lifecycle. |
| Reliability / retries / health | Connection retry, debug/trace/health patterns. | P3K stateless leases, health checks, bounded retries, release receipts, FinalGate contract. | Sentinel competitive as authority-bound supervisor. |
| Final certification | Not Sentinel-style. | EventBus, receipts, artifacts, evidence chains, CoreFinalGate forged-output rejection. | Sentinel clearly stronger. |
| Full browser automation breadth | Very broad. | Deliberately bounded to public evidence/operator V2. | OpenClaw broader; not a Browser V2 target. |

## Harvest Completion Matrix

| Harvest primitive | Source specimen | Sentinel destination | Status | Remaining decision |
| --- | --- | --- | --- | --- |
| SSRF and private address rejection | `src/infra/net/ssrf.ts` | `url_guard.py` | Done | Add larger internet/CDN corpus later. |
| Pinned fetch proof | `src/infra/net/ssrf.ts` | `live_fetch.py`, `models.py`, `evidence_adapter.py` | Done | Stress-test HTTPS/SNI edge cases before broad public deployment. |
| Redirect revalidation | `src/infra/net/fetch-guard.ts` | `evidence_adapter.py` | Done | Keep redirect count tight by authority profile. |
| Readability extraction | `src/agents/tools/web-fetch-utils.ts` | `extraction.py` | Done | Consider full DOM/readability dependency after benchmark proof. |
| External content flags | `src/security/external-content.ts` | `evidence_adapter.py`, `extraction.py` | Done | Connect flags to Browser-Cortex confidence routing. |
| Role snapshot and refs | `src/browser/pw-role-snapshot.ts` | `accessibility_snapshot.py` | Done | CDP-native tree remains a V2.5 upgrade. |
| Snapshot schema | `src/gateway/protocol/schema/snapshot.ts` | `models.py`, `rendered_snapshot.py` | Done | Keep product schemas vendor-neutral. |
| Network and diagnostics ledger | `src/browser/pw-session.ts`, `pw-tools-core.responses.ts` | `observability.py` | Done | HAR/body capture remains separately governed. |
| Screenshot normalization | `src/browser/screenshot.ts` | `screenshot.py` | Done | Built-in image transcode dependency remains optional. |
| PDF capture | snapshot/artifact patterns | `pdf.py`, `rendered_snapshot.py` | Done | Full PDF text reasoning is not Browser V2. |
| Element screenshot | snapshot/screenshot patterns | `rendered_snapshot.py`, `playwright_renderer.py` | Done | Requires stable refs; no arbitrary selector screenshot. |
| Interaction taxonomy | `browser-tool.schema.ts`, `agent.act.ts` | `interaction_dry_run.py`, `interaction_execution.py` | Done | Submit/upload/download stay V2.5/V3. |
| Playwright limited actions | `pw-tools-core.interactions.ts` | `playwright_interaction_backend.py` | Done | No arbitrary JS or private state. |
| Tab/session lifecycle | `pw-session.ts` | `public_lifecycle.py` | Done | Persistent private profile lifecycle deferred. |
| Reliability/retry/health | `pw-session.ts`, `agent.debug.ts`, trace/response files | `supervisor.py` | Done | Real persistent pool object deferred. |

## Where Sentinel Now Exceeds OpenClaw

| Sentinel advantage | Why it matters |
| --- | --- |
| MissionAuthority before browser use | Browser availability never becomes mission authority. |
| ToolRegistry policy before execution | A browser action must be declared and routed before it can run. |
| P3G dry-run before P3H execution | Action planning is explicit and hash-bound before real interaction. |
| Receipts for evidence, snapshots, interactions, artifacts, lifecycle, supervisor | Output is provable, not only logged. |
| CoreFinalGate rejection of forged browser success | Fake browser outputs, stale refs, missing ledgers, and forged receipts are rejected. |
| Product/vendor separation | Harvested code informs Sentinel but never becomes product identity or runtime. |
| EventBus trace chain | Browser output can be replayed, audited, and tied to later reasoning. |

## Where OpenClaw Still Exceeds Browser V2

These are real strengths, but they are not Browser V2 blockers.

| OpenClaw advantage | Sentinel status | Correct future phase |
| --- | --- | --- |
| CDP-native accessibility tree | Parser-backed snapshot only. | Browser V2.5 if evals prove value. |
| Persistent named profiles | Explicitly absent. | Private session authority phase. |
| Cookies/storage/header controls | Explicitly absent. | Private/account browser authority phase. |
| Login flows | Explicitly absent. | Separate credential/session contract. |
| Upload/download/dialog hooks | Explicitly absent. | Quarantine and artifact authority phase. |
| Arbitrary JS evaluate | Explicitly absent. | High-impact browser scripting authority, if ever granted. |
| Drag/press/keyboard broad automation | Narrow limited actions only. | Operator V2.5 after action evals. |
| Remote browser gateway/node | Explicitly absent. | Distributed browser execution phase. |
| Built-in screenshot transcode stack | Injected normalizer hook. | Product packaging decision. |
| Full HAR/body capture | Bounded metadata ledger only. | Network evidence V2 with body authority. |

## Browser V2 Definition Achieved

Browser V2 now includes:

- public URL classification;
- live public GET evidence;
- rendered public snapshot;
- readable extraction and citations;
- prompt-injection flags;
- accessibility-style structure and stable refs;
- screenshot metadata and normalization proof;
- optional PDF capture;
- optional element screenshot capture;
- network/console/page-error/health ledger;
- interaction dry-run planning;
- limited real public interaction;
- post-action recapture;
- public stateless lifecycle ledger;
- reliability supervisor with leases, health checks, bounded retries;
- EventBus trace proof;
- artifact receipts;
- CoreFinalGate rejection of forged browser outputs.

## Browser V2 Not Included

These are intentionally not part of Browser V2:

- private/account sessions;
- login automation;
- cookies and storage;
- credential handling;
- submit/post/send/publish;
- upload/download;
- arbitrary JavaScript execution;
- browser extension control;
- persistent profile reuse;
- remote browser gateway;
- broad human-like browsing automation.

## Decision

Browser V2 is complete enough to stop adding raw browser primitives for now.
The next phase should not be another external organ.

Next sequence:

```text
P3X Browser-Cortex Integration
-> P3Y Browser-LLM Cortex Integration
-> Browser V2 mission evals with LLM/context-pack contracts
-> next organ only after the browser is cognitively integrated
```

## Final Ruling

Sentinel has not copied OpenClaw. It has harvested the strongest useful browser
primitives, rejected the vendor runtime, and rebuilt the browser as a
mission-governed operator organ.

OpenClaw remains a broader browser automation runtime.

Sentinel Browser V2 is a stronger mission-governed browser organ.
