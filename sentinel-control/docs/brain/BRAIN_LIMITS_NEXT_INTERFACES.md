# Brain Limits And Next Interfaces

Date: 2026-04-28
Status: Core Brain Lock documentation

## Current Limits

The certified brain does not currently provide real external powers:

- no browser runtime integrated into `AgentRuntime`;
- no external network/API runtime integrated into `AgentRuntime`;
- no email or channel send;
- no sidecar or desktop control;
- no shell/process execution;
- no credential access;
- no payment/spend action;
- no dependency install;
- no production mutation;
- no vendor runtime bridge.

These limits are deliberate. They keep the brain certifiable before organs are
added.

## Future Module Interface

Every future module must enter through a Sentinel-native capability contract.

Minimum contract fields:

- capability name;
- tool ids;
- action classes;
- input schema;
- output schema;
- side effects;
- authority requirements;
- risk class;
- dry-run format;
- receipt format;
- trace events;
- evidence mapping;
- rollback behavior;
- fake eval cases;
- final-gate additions.

## Module Harvest Protocol

For each future organ:

```text
local source first
-> official GitHub source if local source is incomplete
-> isolate module under agent-lab/module-harvest/
-> static forensic audit
-> extraction matrix
-> Sentinel contract
-> fake evals
-> adapter implementation
-> controlled integration
```

No vendor runtime should govern Sentinel. Vendor code can be studied and
partially reused only after license, dependency, security, and coupling review.

## Research-To-Product Boundary

Research source selection is maintained in `agent-lab`. Product docs describe
Sentinel-native capability contracts only. Before final release, all research
source names, source trees, extraction matrices, and forensic reports must be
absent from the product artifact.

Sentinel-owned eval harnesses must match Sentinel invariants, not source-system
assumptions.

## Browser Interface Direction

First external organ should be Browser Read-Only.

Current implemented groundwork:

- `PublicUrlGuard` classifies public URLs without fetch, browser launch, or
  implicit DNS;
- `PublicUrlPolicy` defines scheme, domain, DNS, and redirect constraints;
- `BrowserEvidenceFetchRequest` and `BrowserEvidenceFetchReceipt` define the
  evidence-fetch contract;
- `BrowserEvidenceAdapter` collects evidence only through an injected source,
  producing trace, artifact, prompt-injection flags, and receipt without real
  network access;
- `ReadOnlyHttpFetcher` provides the controlled public HTTP GET path behind
  mission authority, registry policy, URL guard, trace, artifacts, and receipts;
- `BrowserRenderedSnapshotAdapter` defines rendered page/screenshot artifact
  capture through an injected renderer;
- `PlaywrightReadOnlyRenderer` provides a real rendered browser backend with a
  fresh session, JavaScript disabled, downloads disabled, no session storage,
  subresources blocked, and final URL stability enforced by the adapter;
- `BrowserControlledCapabilityRunner` allows `AgentRuntime` to use Browser V1
  only through canonical tool calls, mission authority, registry policy, URL
  guard, artifact capture, receipts, and trace.

Allowed P3A browser actions:

- open public URL;
- extract text;
- extract links;
- capture title;
- capture citations;
- detect prompt injection;
- create `EvidenceItem`-compatible output;
- write trace and receipt.

Blocked:

- login;
- submit;
- post/send/publish;
- upload;
- payment;
- download execution;
- arbitrary JavaScript evaluation;
- private/account pages;
- CAPTCHA bypass.

## Integration Rule

Future modules must not bypass:

- `MissionAuthorityEnvelope`;
- `ToolRegistry`;
- `ToolSelector`;
- `RiskRouter`;
- `MissionTraceTimeline`;
- `EvidenceChainBuilder`;
- artifact receipts;
- `CoreFinalGate`;
- eval bench.

If a module cannot produce trace, evidence, and receipts, it is not ready for
integration.
