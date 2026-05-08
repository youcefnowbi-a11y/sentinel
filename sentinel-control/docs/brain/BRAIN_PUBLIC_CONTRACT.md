# Brain Public Contract

Date: 2026-04-28
Status: Core Brain Lock contract

This document defines the public interface that future modules may use to
connect to the Sentinel brain. It is intentionally restrictive: modules can
offer evidence, declared capabilities, canonical calls, artifacts, and eval
cases, but they cannot create authority or mutate the brain directly.

This contract applies to every future browser, desktop, sidecar, memory, skill,
media, channel, or external data module.

## Core Rule

Future modules are capability providers, not authority providers.

```text
MissionAuthorityEnvelope
-> ToolRegistry / RiskRouter
-> controlled runner or dry-run path
-> EventBus trace
-> EvidenceChain / receipt / final gate
```

A module that cannot fit this route is not allowed to connect to the brain.

## Public Interfaces Modules May Use

| Interface | Module May Do | Module Must Not Do |
| --- | --- | --- |
| `MissionAuthorityEnvelope` | Read granted mission id, allowed actions, allowed tools, allowed paths, limits, mode, and expiry. | Modify authority, add paths/tools/actions, infer authority from user text, memory, or vendor state. |
| `ToolRegistry` | Register reviewed capability manifests through Sentinel-owned configuration. Ask for policy decisions through registry APIs. | Execute a tool because it exists in vendor code. Skip manifest status, risk class, side effects, or mission scope. |
| `RiskRouter` | Ask for a route for a typed mission action. Use the returned route as a constraint. | Treat posture as permission. Continue after `BLOCK` or `ESCALATE` without a governing transition. |
| `ToolCallProtocol` | Submit raw model/vendor tool-call text for canonicalization. Use the canonical call only as intent. | Execute raw text, recovered XML, recovered regex fields, or non-canonical calls. |
| `ContextPack` / `ContextPackValidator` | Provide a typed, proof-linked context contract for bounded LLM reasoning. | Put raw browser content into trusted control fields, expand mission authority, or accept verified claims without citations. |
| `BrowserPlannerRole` / `BrowserVerifierRole` | Draft next-intent JSON or critique grounding from a validated ContextPack. | Execute tools, grant authority, mint refs, or certify success alone. |
| `ToolIntentCompiler` | Compile LLM draft intent only after ContextPack binding, mission authority checks, provenance binding, and registry policy. | Execute a draft, accept fabricated/stale refs, or compile non-delegated powers without explicit authority classes. |
| `PublicUrlGuard` | Classify a candidate public URL and redirect chain before any future browser evidence fetch. Use fake or controlled DNS resolver input. | Open a browser, fetch a page, trust redirects without revalidation, resolve DNS implicitly, allow private/internal targets. |
| `BrowserEvidenceFetchRequest` / `BrowserEvidenceFetchReceipt` | Declare the future read-only evidence-fetch input and receipt shape. | Treat the contract as an implemented fetcher or claim browser evidence without trace/receipt. |
| `ReadOnlyHttpFetcher` | Execute a controlled public `GET` only after URL policy has passed and only through `BrowserEvidenceAdapter`. | Follow redirects, keep cookies/sessions, POST/submit/upload, run JavaScript, or emit accepted evidence without adapter receipt. |
| `BrowserRenderedSnapshotAdapter` / `PlaywrightReadOnlyRenderer` | Capture rendered public page text/screenshot/structure/network diagnostics plus optional PDF and element screenshots through URL policy, fresh browser context, artifact capture, receipt, and FinalGate-verifiable ledger. | Enable JavaScript, preserve session state, allow downloads, follow unvetted redirects, load private subresources, capture elements without stable refs, or bypass artifact receipts. |
| `BrowserInteractionDryRunPlanner` | Plan browser interactions against stable refs and page/snapshot hashes without executing them. | Click, type, fill, submit, upload, download, evaluate JavaScript, or mutate browser state. |
| `BrowserLimitedInteractionExecutor` | Execute a certified browser interaction plan through a Sentinel-owned backend, then recapture post-action state with receipt and FinalGate-verifiable proof. | Execute without a P3G plan, use stale refs, cross origin without authority, submit/post/send/upload/download, use cookies/storage, login, or execute arbitrary JavaScript. |
| `PlaywrightLimitedInteractionBackend` | Perform bounded click/type-fill/select/hover/wait actions in a fresh public browser context after the executor validates the plan. | Preserve sessions, accept downloads, use private profiles, run arbitrary page scripts, or provide authority by itself. |
| `BrowserPublicLifecycleController` | Record public stateless session/tab lifecycle with URL-policy-bound tab open/navigation, receipts, and FinalGate-verifiable ordering. | Create private profiles, preserve cookies/storage, bypass URL policy, treat tab existence as authority, or mutate browser state without trace. |
| `BrowserReliabilitySupervisor` | Record stateless public browser leases, health checks, bounded retries, releases, and supervisor rejections with FinalGate-verifiable proof. | Keep private browser objects as authority, enable cookies/storage/JS/downloads, retry without max attempts, or treat a healthy backend as permission to execute. |
| `BrowserControlledCapabilityRunner` | Execute Browser V1 only from canonical tool calls after registry policy and mission authority pass. | Treat browser availability as permission, execute without `allowed_tools`/`allowed_actions`, or create browser evidence outside trace. |
| `EventBus` | Emit approved `AgentEventType` events through the owning brain/runtime component. Attach trace refs to decisions. | Create arbitrary event names, rewrite old events, reorder events, or emit a state-changing event from a vendor module. |
| `ArtifactCaptureSandbox` | Capture already-produced local outputs under a mission capture root. Return artifact id, path, hash, and trace id. | Write outside capture root, overwrite different content, or claim an artifact without capture metadata. |
| `ControlledCapabilityReceipt` | Bind policy decision, canonical call, captured artifact, rollback strategy, and trace ids. | Mark a controlled action successful without a receipt. |
| `EvidenceChainBuilder` | Bind major decisions to mission authority, trace refs, contradictions, and confidence. | Use evidence as authority. Hide contradictions or missing evidence. |
| `AgentTraceReplayer` | Reconstruct run state from immutable events. | Call tools, files, registry, network, or workers during replay. |
| `RuntimeCertificationGate` / `CoreFinalGate` | Certify trace order, evidence chains, receipts, scope, budget, terminal state. | Override a failed certification inside a module. |
| `SentinelEvalBench` | Add production-like F2P, P2P, negative, and stability eval cases. | Replace certification with demo-only tests. |

## Forbidden Direct Couplings

These are hard blockers for module integration:

- Direct mutation of `AgentState`.
- Direct mutation of `MissionAuthorityEnvelope`.
- Direct mutation of `EventBus` history or event hashes.
- Bypassing `MissionAuthorityEnvelope`.
- Bypassing `ToolRegistry`.
- Bypassing `RiskRouter`.
- Bypassing `ToolCallProtocol` for model/vendor tool calls.
- Bypassing `ContextPackValidator` for LLM reasoning.
- Bypassing `ToolIntentCompiler` for LLM-generated tool intent.
- Treating LLM output as authority or execution.
- Letting the LLM mint browser refs, page hashes, snapshot hashes, or receipt ids.
- Bypassing artifact capture for file outputs.
- Bypassing receipts for controlled artifact actions.
- Bypassing evidence chains for major decisions.
- Creating new authority from vendor configuration, cookies, sessions,
  credentials, profiles, environment variables, UI state, cached memory, or
  user prompt text.
- Treating `POWER` posture as a permission grant.
- Treating a candidate, dry-run, blocked, unavailable, or unknown tool as an
  executable tool.

## Module Adapter Shape

Every future module must enter through a Sentinel-owned adapter.

```text
Vendor or external module
-> static forensic review
-> Sentinel capability contract
-> manifest
-> fake evals
-> adapter
-> ToolRegistry
-> RiskRouter
-> controlled runner or dry-run
-> receipt/evidence/final gate
```

The adapter is responsible for:

- translating vendor concepts into Sentinel capability manifests;
- removing or disabling vendor authority models;
- normalizing side effects into Sentinel enums;
- enforcing mission id consistency;
- returning typed outputs only;
- preserving provenance and trace refs;
- refusing work when authority is missing;
- creating no hidden background loops.

## Public Extension Points By Future Module Type

| Module Type | First Allowed Output | Required Gate | Disallowed In First Version |
| --- | --- | --- | --- |
| Browser read-only | `EvidenceItem` / captured page text / citation artifact. | Public URL guard, prompt-injection detector, receipt, evidence chain. | Login, submit, upload, arbitrary JS, private pages, downloads-as-execution. |
| Desktop sidecar | Observation receipt or dry-run action plan. | User-visible scope, explicit approval, screen/privacy guard. | Background control, credential scraping, hidden clicks, destructive actions. |
| Memory or skills | Evidence refs, reusable templates, eval cases, capability proposals. | Human-approved registry entry and evidence provenance. | Authority grants, self-install, policy mutation. |
| Media/data sandbox | Captured artifact with type, hash, and provenance. | Capture sandbox, size/type limits, receipt. | Unbounded code execution, dependency install, network fetch. |
| Channels | Draft artifact and send-intent evidence. | Explicit send permission, recipient scope, final receipt. | Sending messages, emails, payments, or files without a separate authority grant. |

## Event Ownership

Events are public records, not public write access.

Future modules may request trace emission through the owning Sentinel component,
but they do not own event semantics. New events require:

- a named `AgentEventType` or `MissionTraceEventType`;
- required payload contract;
- replay/audit/final-gate behavior;
- tests that reject missing or forged payloads;
- documentation in `BRAIN_EVENT_CATALOG.md`.

## Artifact Ownership

An output is not a certified artifact until it has:

- mission id;
- normalized relative path;
- content type;
- size;
- sha256 hash;
- capture trace id;
- provenance refs;
- receipt when produced by a controlled capability.

Files created outside this route can exist on disk, but the brain must treat
them as uncertified until captured and reviewed.

## Authority Ownership

Only the mission envelope grants authority.

```text
vendor module config != authority
profile/session/cookie != authority
memory item != authority
user prompt != authority
posture != authority
availability != authority
```

If future work requires additional authority, the module must return a proposal
or escalation. It must not silently expand the mission.

## Integration Acceptance

A new module can only leave harvest mode when all of these are true:

- its public contract is documented;
- every tool/action has a manifest;
- black-zone side effects are represented and blocked;
- fake evals prove positive and negative routing;
- non-delegated primitives are scanned;
- every useful output has trace/evidence/receipt coverage;
- final gate rejects forged success;
- product docs remain Sentinel-native and vendor-neutral.
