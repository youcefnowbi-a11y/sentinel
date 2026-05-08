# Browser V1 Exhaustive Review

Date: 2026-04-29
Status: Browser V1 certified, Browser V2 certified for cortex integration

This report reviews Browser V1 module by module. It is intentionally limited to
the Sentinel browser implementation and does not include vendor comparison. The
vendor gap analysis lives in `agent-lab/module-harvest/`.

## Direct Verdict

Browser V1 is a real governed evidence browser capability, not only a design
stub. P3H added the first limited real interaction gate, P3I added a public
stateless session/tab lifecycle ledger, P3J added richer browser artifacts, and
P3K now adds reliability supervision: stateless leases, health checks, bounded
retries, release receipts, and FinalGate proof. It is wired through:

```text
AgentRuntime
-> canonical tool call
-> ToolRegistry policy
-> MissionAuthorityEnvelope
-> BrowserControlledCapabilityRunner
-> PublicUrlGuard
-> fetch/render/interaction adapter
-> ArtifactCaptureSandbox
-> EventBus
-> CoreFinalGate
```

It is strong for public evidence collection. It is not yet a full browser
operator. It can execute narrow public interactions from a certified dry-run
plan, recapture after action, track public stateless tab/session lifecycle, and
capture richer proof artifacts while supervising repeated browser operations.
It still cannot submit forms, keep private sessions, upload, download, log in,
read cookies, mutate storage, run arbitrary JavaScript, or control private
browser state.

## Certification Snapshot

Observed implementation:

| Surface | Count |
| --- | ---: |
| Browser source files | 19 |
| Browser source lines | 5,605 |
| Browser test files | 14 |
| Browser tests | 98 |

Current validation:

```text
python -m pytest tests -q
python -m compileall sentinel
execution-boundary primitive scan
product vendor-trace scan
```

Result:

- full test suite passes;
- browser-targeted tests pass;
- compileall passes;
- no non-delegated execution primitives found in browser/core scan;
- product docs and code are Sentinel-native.

## Module Review Matrix

| Module | Role | Current Strength | Main Gap | Open Gap Level |
| --- | --- | --- | --- | --- |
| `models.py` | Typed browser contracts and receipts. | Clear separation between URL policy, fetch evidence, rendered snapshot, rich artifacts, controlled runtime result, interaction execution, public lifecycle, byte accounting, MIME policy, connection proof, and network ledger metadata. | No private profile/session authority model yet. | Low |
| `url_guard.py` | Public URL classification. | Enforces granted schemes, userinfo exclusion, localhost/internal boundary, private IP boundary, IPv4-mapped loopback handling, obfuscated IP handling, DNS checks, redirect loops, over-limit redirects, domain scope. | No IDNA homograph policy beyond ASCII IDNA normalization. | Low |
| `evidence_adapter.py` | HTTP page -> evidence/artifact/receipt. | Requires URL decision, revalidates each redirect hop, rejects bad MIME and over-budget compressed/uncompressed bodies, can enforce pinned connection proof, creates artifact hash, receipt, trace, extraction metadata. | It still does not decide source truth; EvidenceChain must rank/cross-check claims. | Medium |
| `extraction.py` | Readable evidence extraction. | Prefers article/main content, ignores hidden script/style claims, handles HTML/text/JSON, records strategy, quality flags, truncation proof, and citation offsets. | Heuristic parser, not full DOM/readability engine yet. | Medium |
| `live_fetch.py` | Controlled public GET fetcher. | GET only, no cookies, no session reuse, timeout, compressed/uncompressed byte limits, MIME is enforced by adapter, `trust_env=False` for mock/custom transport, and default live path uses pinned address connection proof. | Needs broader HTTPS/CDN stress tests for pinned transport edge cases. | Medium |
| `rendered_snapshot.py` | Rendered page -> snapshot/screenshot/citations. | Requires URL policy, unchanged final URL, artifacts, receipt, bounded citations, screenshot hash, accessibility snapshot hash, screenshot metadata, network ledger hash/counts, trace. | Still not an interaction planner. | Medium |
| `accessibility_snapshot.py` | Rendered HTML -> role snapshot. | Builds deterministic role snapshots, stable refs, duplicate `nth`, stats, page hash, and snapshot hash without enabling interactions. | Parser-backed, not full CDP accessibility tree yet. | Medium |
| `screenshot.py` | Screenshot metadata and normalization proof. | Extracts PNG/JPEG dimensions, content type, byte count, max-side/max-byte warnings, and normalized/original metadata when a Sentinel-owned normalizer is provided. | Default path still requires an injected normalizer for actual resize/transcode. | Medium |
| `pdf.py` | PDF artifact metadata. | Validates PDF header, size budget, and page-count estimate for optional rendered PDF capture. | Metadata estimator is not a full PDF parser. | Low |
| `observability.py` | Browser network and diagnostic ledger. | Canonical request/response/failure/console/page-error ledger, bounded size, truncation proof, health metadata, hash verification. | No HAR/body capture or cross-frame diagnostics yet. | Medium |
| `interaction_dry_run.py` | Browser interaction action planning. | Produces no-op plans bound to snapshot hash, page hash, stable refs, and FinalGate-verifiable plan hash. | Does not execute interactions; no state mutation. | Medium |
| `supervisor.py` | Browser reliability supervision. | Records stateless public leases, health checks, bounded retries, releases, and supervisor rejections with FinalGate-verifiable proof. | Does not yet own a persistent real browser pool; it is the contract layer for that future step. | Medium |
| `interaction_execution.py` | Limited interaction execution gate. | Consumes certified dry-run plans, validates delegated intents, recaptures after action, emits receipt and FinalGate-verifiable execution event. | No multi-step browser strategy or private-session authority yet. | Medium |
| `public_lifecycle.py` | Public session/tab lifecycle ledger. | Tracks public stateless sessions/tabs, URL-policy-bound opens/navigations, lifecycle receipts, and FinalGate-verifiable state order. | No persistent browser profile, pool, or private-session authority yet. | Medium |
| `playwright_renderer.py` | Real rendered browser backend. | Fresh context, JavaScript disabled, downloads disabled, no storage state, route blocks subresources and redirects, records request/response/failure/console/page-error ledger. | No browser pool, lifecycle supervisor, or screenshot normalization/resizing. | Medium |
| `playwright_interaction_backend.py` | Real limited browser interaction backend. | Fresh context, no storage state, downloads disabled, JavaScript disabled, same-origin document routing, stable-ref locator execution. | No session reuse, no JS-enabled app workflows, no submit/upload/download. | Medium |
| `controlled_runner.py` | Runtime browser executor boundary. | Enforces registry decision before browser action and maps accepted/rejected results to traceable objects. | Browser action set is still bounded: read/render/limited interaction only. | Low |
| `fake_eval.py` | Browser negative/positive evals. | Covers public, local, metadata, prompt injection, oversized body cases. | Not yet a rolling browser task benchmark. | Medium |
| `__init__.py` | Public browser package boundary. | Explicit exports only. | No issue. | Low |

## `models.py`

What it does:

- defines `PublicUrlPolicy`, `PublicUrlDecision`, and browser result status
  enums;
- defines fetch request/result/receipt contracts;
- defines rendered snapshot request/result/receipt contracts;
- defines screenshot, PDF, and element screenshot metadata contracts;
- defines public session/tab lifecycle result and receipt contracts;
- defines citation and controlled capability result contracts.

What is correct:

- receipts keep trace refs, artifact hashes, URL policy trace IDs, and content
  metadata;
- fetch receipts include compressed/uncompressed byte accounting, MIME gate
  result, and optional connection proof;
- fetch and rendered snapshot receipts are separate, avoiding one generic
  "browser receipt" that hides semantics;
- controlled runtime result does not embed raw artifact content, only IDs and
  trace references;
- public lifecycle records explicitly prove stateless public mode with cookies
  and storage disabled;
- rendered receipts can include optional PDF and element screenshot artifacts
  without collapsing them into the generic snapshot artifact.

What is missing:

- no browser profile identity;
- no capture viewport variants.

Decision:

Keep as V1. Add richer metadata only when the runtime actually supports those
surfaces.

## `url_guard.py`

What it does:

- classifies URLs before fetch or render;
- normalizes scheme, host, port, and path;
- rejects out-of-contract control characters, missing schemes, unsupported schemes,
  userinfo, invalid ports, non-delegated hostnames, private/internal IPs, obfuscated
  IP literals, DNS failures, private DNS answers, redirect loops, and too many
  redirects;
- can enforce `allowed_domains`.

What is strong:

- it is pure classification: no fetch, no browser launch;
- it requires DNS resolution by default;
- it blocks loopback and metadata style targets before DNS;
- it revalidates provided redirect chains.

What is not yet strong enough:

- no IDNA homograph policy beyond ASCII IDNA normalization;
- rendered browser navigation does not yet expose socket-level connection proof
  equivalent to the HTTP fetch path.

Strict finding:

V1 is acceptable for public evidence. The HTTP evidence path now converts
redirect responses into fresh URL policy decisions before any second fetch. The
default live fetch path can connect to a pre-approved address and emit a pinned
connection proof; custom transports must provide their own proof when a mission
requires it.

## `evidence_adapter.py`

What it does:

- receives an injected fetcher;
- emits `BROWSER_URL_CLASSIFIED`;
- rejects URL decisions outside mission authority before any content is trusted;
- fetches only after policy approval;
- follows only response redirects returned by the injected fetcher, revalidating
  every hop before the next fetch;
- rejects non-2xx statuses and final URL changes;
- rejects disallowed MIME types;
- rejects compressed and uncompressed bodies over their separate budgets;
- rejects forged or unapproved connection proofs when proof is required;
- extracts title, readable text, links, summary, source quality flags, citation
  offsets, and prompt-injection flags;
- captures an evidence artifact;
- emits `BROWSER_EVIDENCE_COLLECTED` or `BROWSER_EVIDENCE_REJECTED`.

What is strong:

- evidence is not accepted without artifact capture;
- the receipt contains content hash, artifact hash, URL policy trace, and
  citation refs;
- the receipt includes MIME decision, byte accounting, and connection proof
  metadata when provided;
- prompt-injection language is not hidden from downstream modules;
- weak or empty extraction becomes explicit metadata or `browser_evidence_gap`.

What is weak:

- no cross-source contradiction handling inside browser module;
- no freshness/last-modified validation.

Strict finding:

The adapter is good enough to create public evidence. It is not good enough yet
to rank source quality or decide truth. That remains the role of EvidenceChain
and future research evaluators.

## `extraction.py`

What it does:

- extracts public evidence text from HTML, plain text, and JSON responses;
- prefers `<main>` and `<article>` content over nav/footer/header page chrome;
- ignores hidden `script`, `style`, `noscript`, `template`, and `svg` content;
- records extraction strategy, source quality flags, raw chars, truncation, and
  citation offsets;
- marks empty extraction as an evidence gap.

What is strong:

- evidence is more focused than whole-page text;
- script/style claims cannot become extracted evidence;
- truncation is visible in receipt and event payloads;
- citation offsets map back into the extracted text.

What is weak:

- this is heuristic readability, not a full DOM/readability engine;
- it does not score publisher reputation or source freshness;
- it does not resolve contradictions across pages.

Strict finding:

P3D improves evidence quality without adding browser power. It gives later
EvidenceChain components better metadata instead of pretending extraction equals
truth.

## `live_fetch.py`

What it does:

- performs HTTP GET;
- uses a pinned address path by default when a URL decision provides approved
  resolved addresses;
- keeps redirects manual so the adapter can revalidate each hop;
- sets a read-only browser user agent;
- uses no reusable cookie jar;
- applies timeout, compressed-byte, and decoded-byte enforcement;
- ignores environment proxy/auth settings via `trust_env=False` on the
  `httpx` custom-transport path.

What is strong:

- no POST/PUT/DELETE;
- no cookies;
- no session reuse;
- no automatic redirects;
- no external artifact writes;
- no JavaScript.

What is missing:

- no per-response network receipt beyond headers kept by the fetcher.
- pinned transport needs broader HTTPS/CDN stress tests beyond the local pinned
  HTTP regression.

Strict finding:

This is intentionally smaller than a browser. It is now strong enough for
governed public evidence fetches, with the next network hardening step being a
larger HTTPS/CDN corpus and a structured network ledger.

## `rendered_snapshot.py`

What it does:

- wraps an injected rendered browser backend;
- applies URL guard before render;
- rejects final URL changes and non-2xx status;
- captures rendered text, links, HTML, screenshot, citations, accessibility
  role snapshot, screenshot metadata, optional PDF, optional element
  screenshots, network ledger, prompt-injection flags, artifacts, receipt, and
  trace.

What is strong:

- rendered output cannot bypass URL policy;
- artifacts are captured before success is reported;
- screenshot and snapshot hashes are trace-bound;
- citations are bounded and tied to text offsets;
- role snapshot hash and ref counts are trace-bound;
- screenshot width/height/format/byte metadata and normalization proof are
  recorded;
- network ledger hash, counts, truncation proof, and health metadata are
  trace-bound;
- optional PDF and element screenshot artifact hashes are receipt-bound and
  FinalGate-verifiable.

What is missing:

- parser-backed role snapshot, not a full CDP accessibility tree;
- no frame-aware snapshot;
- no labelled screenshot;
- default runtime needs an injected normalizer for actual resize/conversion;
- no viewport variants.

Strict finding:

The module is strong as an evidence capture layer. It now has stable structural
refs, but those refs are evidence metadata only; they do not authorize
interaction.

## `screenshot.py`

What it does:

- extracts PNG/JPEG content type, dimensions, byte size, max-side budget, and
  max-byte budget;
- keeps already bounded screenshots unchanged;
- when a Sentinel-owned normalizer hook is provided, converts oversized
  screenshots into bounded artifacts and records original dimensions/bytes;
- returns metadata consumed by rendered snapshot and post-interaction receipts.

What is strong:

- screenshot bounds are proof metadata, not implicit assumptions;
- normalization is explicit and testable;
- artifacts record whether they were normalized and what the original capture
  dimensions/bytes were.

What is missing:

- no bundled image transcode dependency yet;
- no viewport-specific normalization presets.

Strict finding:

P3J makes screenshot artifact size a governed contract. The next reliability
phase can decide whether to ship a built-in normalizer or keep the hook
adapter-driven.

## `pdf.py`

What it does:

- validates optional rendered PDF artifacts by header and byte budget;
- records estimated page count as metadata;
- rejects invalid PDF bytes before artifact success.

What is strong:

- PDF capture is explicit opt-in, not a side effect of rendering;
- PDF artifacts are bound to receipt, artifact hash, event payload, and
  FinalGate checks.

What is missing:

- not a full PDF parser;
- no text extraction or citation mapping from PDFs yet.

Strict finding:

P3J adds browser PDF as a proof artifact, not as a document reasoning engine.

## `observability.py`

What it does:

- builds a canonical browser network and diagnostics ledger;
- records requests, responses, request failures, console messages, page errors,
  and browser health metadata;
- bounds each ledger category by count;
- preserves original counts and a truncation flag;
- computes a stable ledger SHA-256;
- verifies ledger hashes for FinalGate.

What is strong:

- diagnostics become proof-bearing metadata rather than transient logs;
- FinalGate can reject missing or forged ledger data;
- bounded ledgers prevent a hostile/noisy page from expanding artifacts without
  proof;
- a minimal fallback ledger keeps injected test renderers trace-compatible.

What is missing:

- no HAR export;
- no response body capture;
- no frame-specific diagnostic grouping;
- no source-level timing waterfall.

Strict finding:

P3F turns rendered browser evidence into an auditable observation, not just a
page capture. It improves diagnosis and replay without granting interaction
authority.

## `interaction_dry_run.py`

What it does:

- creates browser interaction plans without executing them;
- supports `click_plan`, `type_plan`, `fill_plan`, `select_plan`,
  `press_plan`, `hover_plan`, `wait_for_text_plan`, `wait_for_selector_plan`,
  and `wait_for_url_plan`;
- binds each plan to the accessibility snapshot hash and page hash;
- validates ref-based steps against stable P3E refs;
- rejects stale snapshot/page hashes;
- rejects submit/post/send/upload/download/evaluate-style actions;
- emits `BROWSER_INTERACTION_PLAN_CREATED`;
- computes a stable plan hash and dry-run proof.

What is strong:

- Sentinel can now reason about browser action intent before receiving action
  authority;
- refs are evidence-bound, not free-form selectors;
- FinalGate can reject forged plans, missing snapshot binding, unknown refs,
  and any real interaction event during P3G;
- the planner has no browser backend dependency and cannot mutate page state.

What is missing:

- no real click/type/fill/select/press/hover execution;
- no interaction result receipt;
- no post-action screenshot/evidence comparison;
- no interaction-specific mission budget yet.

Strict finding:

P3G gives Sentinel action-planning intelligence without granting interaction
execution. It prepares P3H while keeping the Browser authority chain intact.

## `interaction_execution.py`

What it does:

- consumes a certified `BrowserInteractionPlan`;
- validates plan hash, snapshot hash, page hash, trace refs, and delegated
  intents before calling a backend;
- permits only limited public interaction intents: click, type/fill, select,
  hover, and wait predicates;
- rejects press/submit/upload/download/evaluate/storage/cookie/login/payment
  style actions;
- requires same-origin final URL after action;
- captures post-action snapshot JSON and optional screenshot artifact;
- emits `BROWSER_INTERACTION_EXECUTED` or `BROWSER_INTERACTION_REJECTED`;
- creates `BrowserInteractionExecutionReceipt`.

What is strong:

- real interaction is not free-form browser control; it is execution of a
  previously proved plan;
- post-action state is recaptured before success is reported;
- FinalGate can reject forged plans, stale before snapshots, cross-origin
  outcomes, missing artifacts, and forged ledger hashes;
- the executor is backend-injected, so the proof contract is separate from the
  browser implementation.

What is missing:

- no multi-tab strategy;
- no JS-enabled workflows;
- no submit authority;
- no private session authority;
- no browser-specific retry policy yet.

Strict finding:

P3H turns Sentinel from browser observer into limited browser operator while
preserving mission authority, evidence, receipts, and FinalGate proof.

## `public_lifecycle.py`

What it does:

- starts and closes mission-scoped public browser lifecycle sessions;
- opens, navigates, and closes public tabs in an in-memory lifecycle ledger;
- classifies every tab open/navigation URL through `PublicUrlGuard`;
- emits `BROWSER_PUBLIC_SESSION_STARTED`, `BROWSER_PUBLIC_TAB_OPENED`,
  `BROWSER_PUBLIC_TAB_NAVIGATED`, `BROWSER_PUBLIC_TAB_CLOSED`,
  `BROWSER_PUBLIC_SESSION_CLOSED`, or `BROWSER_PUBLIC_LIFECYCLE_REJECTED`;
- creates lifecycle receipts that prove stateless public mode, cookies disabled,
  storage disabled, URL policy trace refs, and session/tab identity.

What is strong:

- tab state is not free browser state; it is a trace-bound lifecycle ledger;
- tab opens and navigations cannot be accepted without a prior URL policy event;
- FinalGate can reject forged tab opens, unknown tabs, invalid navigation order,
  stateful payloads, or missing lifecycle receipts;
- lifecycle close events release active tabs and prevent further accepted
  navigation through the same session.

What is missing:

- no persistent browser profile;
- no reusable Playwright pool;
- no private/account session authority;
- no multi-tab interaction strategy yet.

Strict finding:

P3I gives Sentinel public tab/session memory without inheriting private browser
state. This is the right bridge between single-call P3H interaction and later
browser reliability/pool work.

## `supervisor.py`

What it does:

- creates stateless public browser pool leases;
- releases leases with receipt and trace proof;
- records backend health checks and consecutive failure counts;
- runs browser operations through a bounded retry policy;
- emits `BROWSER_POOL_LEASED`, `BROWSER_POOL_RELEASED`,
  `BROWSER_HEALTH_CHECKED`, `BROWSER_OPERATION_RETRIED`, or
  `BROWSER_SUPERVISOR_REJECTED`;
- keeps cookies, storage, JavaScript, downloads, and private profile state out
  of P3K supervisor contracts.

What is strong:

- retry is finite and trace-visible;
- backend health is diagnostic evidence, not execution authority;
- lease events prove public/stateless boundaries before repeated operations;
- FinalGate rejects forged stateful leases, unbounded retry attempts, and
  release events without known active leases.

What is missing:

- no persistent real browser object pool yet;
- no lease-aware browser quota in `AgentRuntime`;
- no cross-worker browser lease scheduler;
- no Browser-Cortex policy deciding when to retry, repair, or switch source.

Strict finding:

P3K is the reliability contract layer. It makes repeated browser work auditable
without turning backend availability into authority.

## `playwright_renderer.py`

What it does:

- launches a headless Chromium instance;
- creates a fresh context per render;
- disables JavaScript;
- disables downloads;
- does not load storage state;
- routes requests so only the initial document URL is allowed;
- aborts subresources and redirects by URL mismatch;
- captures HTML, text, title, links, screenshot, optional PDF, optional element
  screenshots, request/response events, request failures, console messages,
  page errors, and health metadata.

What is strong:

- no persistent session;
- no login state;
- no download acceptance;
- no arbitrary `page.evaluate`;
- no third-party subresource loading;
- deterministic fixture support for tests;
- bounded network and diagnostics ledger;
- optional element screenshots are resolved through role refs, not arbitrary
  page script evaluation.

What is weak:

- it launches a browser per call, which is simple but not efficient;
- it has no pool or lifecycle supervisor;
- screenshot resize/transcode is still handled by the adapter normalizer hook,
  not by the backend itself.

Strict finding:

This backend is conservative and certifiable. It is not yet a high-performance
browser runtime.

## `playwright_interaction_backend.py`

What it does:

- creates a fresh Chromium context for limited interactions;
- disables downloads;
- avoids storage state;
- keeps JavaScript disabled for P3H;
- allows same-origin document navigation only;
- blocks subresources;
- resolves P3G role refs into Playwright role locators;
- executes bounded click/type-fill/select/hover/wait steps;
- returns post-action rendered page payload for receipt capture.

What is strong:

- one backend call cannot inherit cookies or private session state;
- action execution is tied to stable refs from the plan;
- same-origin routing prevents unexpected cross-site drift;
- the backend validates the before snapshot before acting.

What is weak:

- not yet efficient: fresh browser per call;
- no JS-enabled public app workflows;
- no CDP-native accessibility tree;
- no browser pool/lifecycle supervisor.

Strict finding:

This backend is a deliberate first operator step. It proves real limited
interaction is possible without importing a broad browser runtime.

## `controlled_runner.py`

What it does:

- accepts only canonical tool calls;
- asks `ToolRegistry.decide()` before browser work;
- supports `browser_read_public_page`, `browser_render_public_page`, and
  `browser_interaction_limited`;
- uses mission-scoped artifact capture root;
- returns controlled results with policy trace, browser trace, receipt ID, and
  artifact IDs;
- emits controlled rejection events when policy or browser boundary fails.

What is strong:

- browser capability is not available merely because code exists;
- rejected browser calls are traceable;
- accepted browser calls carry enough IDs for FinalGate to prove causality.

What is missing:

- no action-specific risk route inside the browser runner;
- no browser-specific budget beyond direct tool-call budget;
- no source quota per domain;
- no parallel fetch/render orchestration.

Strict finding:

The boundary is correct. The next power upgrade should extend policy and budget,
not bypass this runner.

## `fake_eval.py`

What it does:

- provides deterministic browser eval cases;
- tests public page acceptance inside mission authority;
- tests local/private/internal rejection;
- tests prompt-injection flagging;
- tests oversized body rejection.

What is strong:

- negative tests are present before broad browser power;
- evals are deterministic and do not need network.

What is missing:

- no real public-page snapshot corpus;
- no prompt-injection adversarial page suite;
- no multi-run stability score;
- no source-quality score.

Strict finding:

Good V1 eval, not enough for V2 browser autonomy.

## Runtime And FinalGate Review

Runtime integration:

- `AgentRuntime` receives optional browser renderer/fetcher/resolver;
- direct tool calls are canonicalized before execution;
- browser actions are routed only if the canonical action is in
  `BrowserControlledCapabilityRunner.SUPPORTED_ACTIONS`;
- everything else goes to the local controlled runner.

FinalGate hardening:

- `browser_capability_receipts` verifies browser capture events;
- accepted browser results must reference a real browser capture event;
- browser capture events must reference a URL policy event;
- artifact IDs and hashes must match `ARTIFACT_CAPTURED`;
- policy event must exist, match tool/action, be allowed, and occur before the
  browser capture event;
- forged browser policy trace IDs are rejected.
- interaction dry-run plans must bind to an existing snapshot hash, page hash,
  stable refs, and plan hash;
- real browser interaction execution events are rejected during P3G.
- limited browser interaction execution must bind to a real dry-run plan,
  before snapshot event, post-action artifacts, same-origin result, receipt,
  and network ledger hash.
- public lifecycle events must stay stateless, reference URL policy for tab
  opens/navigations, preserve session/tab ordering, and carry receipts.
- PDF and element screenshot artifact IDs/hashes must match captured artifacts;
  screenshot metadata must include normalization state and byte/content-type
  proof.
- reliability supervisor events must prove public/stateless leases, bounded
  retries, health status, release ordering, and rejection reasons.

Strict finding:

This is the most important part of Browser V1. Without this, Browser V1 would be
"a browser that logs." With it, Browser V1 is "a browser that proves."

## Current Missing Powers

These are not bugs; they are deliberate exclusions from V1:

- browser profiles;
- session persistence;
- cookies and storage;
- login/private pages;
- JS-enabled rendering;
- form submit;
- broad click/type/hover/drag/select/fill outside certified P3H plans;
- file upload;
- downloads;
- CDP-native accessibility tree;
- broad interaction execution against arbitrary selectors;
- full HAR/body network capture;
- frame-aware diagnostic grouping;
- persistent real browser pooling;
- remote browser node/proxy support.

## Required Before Browser 2.5/V3

Priority order:

1. Browser-cortex decision matrix: complete in P3X.
2. Browser-LLM ContextPack and ToolIntentCompiler contracts: complete in P3Y.
3. CDP-native accessibility tree and frame-aware snapshots.
4. Rendered browser navigation proof equivalent to the HTTP fetch connection
   proof.
5. Built-in screenshot binary transcode dependency or adapter decision.
6. Browser-specific eval corpus: prompt injection, redirects, hostile pages,
   source quality, citation accuracy.
7. Network ledger V2: HAR-style timing/body controls under explicit authority.
8. Formal authority classes for private sessions, file transfer, scripted
   execution, and stronger interaction flows.

## Certification Verdict

Browser V1 is accepted as a public evidence capability. P3H is accepted as the
first bounded operator layer, P3I as the public stateless lifecycle layer, P3J
as the browser artifact-quality layer, and P3K as the browser reliability
supervisor layer. P3N completed the Browser V2 final review, P3O completed the
formal logic/code/algorithm/math lock, and P3X connected browser output to
cortex reasoning. P3Y connected browser output to a bounded LLM contract.
Browser V2 is now a certified public mission-governed browser organ, not a
private-session or unrestricted automation runtime.

The next browser work is Browser 2.5/V3 authority-class planning, not raw
automation or another organ.
