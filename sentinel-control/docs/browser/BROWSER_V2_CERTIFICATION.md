# Browser V2 Certification

Date: 2026-04-29
Status: Browser V2 certified, formally locked, cortex-integrated, LLM-contract integrated, and upgraded to Browser V2.5 P4A

## Direct Verdict

Browser V2 is complete as a public mission-governed browser organ.

It can observe, extract, cite, render, structure, diagnose, plan limited
interactions, execute limited public interactions, recapture post-action state,
track stateless public lifecycle, supervise reliability, and prove its outputs
through trace, artifacts, receipts, and FinalGate.

After P3X, Browser V2 outputs also become cortex inputs: source confidence,
hypothesis deltas, repair signals, action recommendations, and evidence chains.

After P3Y, Browser V2 outputs can be packed into a proof-linked LLM
ContextPack. LLM output remains draft intent until `ToolIntentCompiler`
canonicalizes it, binds refs, checks mission authority, and emits a compiled
intent trace.

Browser V2 is not a private browser session system. It does not include login,
cookies, storage, arbitrary JavaScript, uploads, downloads, payment, credentials,
or broad human-like automation.

P4A adds Browser V2.5 perception and grounding power without opening Browser V3
authority classes: CDP AX normalization, DOMSnapshot/layout normalization,
unified UIObservation records, visual crop/zoom observation metadata, public
multi-tab orchestration, public/stateless pool accounting, verifier, loop
detector, and FinalGate V2.5 checks.

P4A-R confirms the V2.5 outputs are mapped to Browser-Cortex, ContextPack,
ToolIntentCompiler, EvalBench, and future P4B authority classes before Browser
V3 powers begin.

## Certified Capability Set

| Capability | Status | Proof Surface |
| --- | --- | --- |
| Public URL classification | Certified | URL policy trace event. |
| Public HTTP evidence | Certified | Evidence receipt, artifact hash, connection proof, MIME and size gates. |
| Rendered public snapshot | Certified | Snapshot artifact, screenshot metadata, URL policy trace, receipt. |
| Readable extraction | Certified | Extraction strategy, quality flags, truncation proof, citation offsets. |
| Prompt-injection flags | Certified | Evidence/snapshot receipt metadata. |
| Accessibility-style structure | Certified | Stable refs, snapshot hash, page hash, stats. |
| Network diagnostics | Certified | Bounded ledger, ledger hash, counts, health metadata. |
| Interaction dry-run | Certified | Plan hash, snapshot/page hash binding, stable-ref validation. |
| Limited real interaction | Certified | Certified plan, same-origin result, post-action snapshot, receipt. |
| Public lifecycle | Certified | Stateless session/tab events, URL-policy-bound navigation, receipts. |
| Rich artifacts | Certified | Screenshot normalization proof, optional PDF, optional element screenshots. |
| Reliability supervisor | Certified | Stateless leases, health checks, bounded retries, release receipts. |
| Browser-cortex interpretation | Certified | Source confidence, hypothesis updates, repair signals, action recommendations, evidence chain. |
| Browser-LLM ContextPack | Certified | ContextPack hash, citations, stable refs, source flags, prompt flags, available intents. |
| ToolIntentCompiler | Certified | Canonical call hash, ContextPack binding, ref provenance, authority checks, rejection events. |
| Browser V2.5 perception | Certified | CDP AX tree hash, DOMSnapshot hash, UIObservation hash, visual observation hash. |
| Browser V2.5 public operator | Certified | Public/stateless pool, public multi-tab strategy, verifier, loop detector, FinalGate checks. |
| Runtime integration | Certified | ToolRegistry policy, MissionAuthority, controlled runner, CoreFinalGate. |

## Execution Boundary

Browser V2 may:

- classify public URLs;
- fetch public pages through governed GET;
- render public pages in fresh public contexts;
- extract text, links, metadata, citations, and source quality signals;
- capture screenshot, PDF, element screenshot, and snapshot artifacts;
- create stable refs for observed page structure;
- plan browser interactions without executing them;
- execute limited public interactions only from certified plans;
- recapture after-action evidence;
- record public lifecycle and reliability events;
- emit trace, receipts, and artifacts for FinalGate.

Browser V2 may not:

- log in;
- submit/post/send/publish;
- access credentials;
- keep cookies or storage;
- use private profiles;
- upload files;
- execute downloads;
- execute arbitrary JavaScript;
- mutate browser state outside certified interaction plans;
- treat backend availability as authority.

## FinalGate Coverage

`CoreFinalGate` now checks:

- browser URL policy binding;
- evidence artifact and receipt binding;
- rendered snapshot artifact/hash binding;
- screenshot/PDF/element screenshot artifact metadata;
- accessibility hash and ref metadata;
- network ledger hash and counts;
- interaction dry-run plan hash, refs, and snapshot/page hashes;
- limited interaction plan trace, before snapshot, post-action artifacts,
  same-origin result, and ledger hash;
- public lifecycle ordering and stateless payloads;
- reliability supervisor stateless leases, bounded retry attempts, health
  status, release ordering, and rejection reasons.
- Browser V2.5 AX/DOM/UI/visual observation hashes;
- Browser V2.5 public pool and multi-tab boundary flags;
- Browser V2.5 verifier and loop detector events.

## Certification Commands

```text
pytest tests/test_agent_browser_reliability_supervisor.py -q
pytest <all test_agent_browser_*.py> -q
pytest tests -q
python -m compileall sentinel
execution-boundary primitive scan
product vendor-trace scan
browser doctrine scan
```

Current result: certified.

## Formal Lock

P3O adds a hard formal review gate after Browser V2 certification and before
any Browser 2.5/V3 work:

```text
logic review
code review
algorithm review
mathematical review
failure-mode review
eval scorecard
lock verdict
```

Current result: Browser V2 is locked in `BROWSER_V2_LOCK_VERDICT.md`.

## Cortex Integration

P3X connects Browser V2 outputs to reasoning:

```text
BROWSER_* events
-> BrowserEvidenceInterpreter
-> BROWSER_CORTEX_INTERPRETED
-> EvidenceChain(BROWSER_CORTEX_INTERPRETATION)
-> review findings / repair pressure
```

Current result: accepted in `P3X_LOCK_VERDICT.md`.

## LLM Cortex Integration

P3Y connects Browser V2 and P3X to the future LLM layer:

```text
ContextPack
-> bounded LLM draft
-> ToolIntentCompiler
-> ToolRegistry / MissionAuthority
-> FinalGate
```

Current result: accepted in `P3Y_LOCK_VERDICT.md` and audited in
`P3Y_FINAL_AUDIT.md`.

## Remaining Browser Work

The integration lock is complete:

```text
P3O Browser Formal Review Gate (complete)
P3X Browser-Cortex Integration (complete)
P3Y Browser-LLM Cortex Integration (complete)
```

The goal is to ensure the brain and future LLM layer know when to call browser,
what evidence to request, how to interpret weak/noisy sources, when browser
results update hypotheses, when retries or repairs are justified, and how future
modules consume browser outputs without bypassing the brain.

Browser 2.5/V3 can now be planned as explicit authority classes; it is still
not part of Browser V2.

P4A Browser V2.5 is now locked in `P4A_LOCK_VERDICT.md`.

P4A-R readiness is accepted in `P4A_READINESS_REVIEW.md`, with the P4B sequence
defined in `P4B_AUTHORITY_CLASS_PLAN.md`.

P4B has started as explicit Browser V3 authority classes. P4B-0 and P4B-1 are
locked in `P4B_FORM_SUBMIT_LOCK_VERDICT.md`: Sentinel now supports governed
public form submit/post/send/publish from certified plans. P4B-2 is locked in
`P4B_DOWNLOAD_QUARANTINE_LOCK_VERDICT.md`: Sentinel now supports bounded public
download capture into quarantine artifacts with `promoted=false`. P4B-3 is
locked in `P4B_UPLOAD_AUTHORIZED_LOCK_VERDICT.md`: Sentinel now supports
governed upload of certified Sentinel artifacts only.

P4B-4 through P4B-8 are also locked: private session, login authority,
cookie/storage contracts, sandboxed JS evaluate, and HAR/body capture now exist
as separate authority classes with receipts, events, tests, and FinalGate
contracts.

Future Browser work now moves to Browser V3 review/supremacy evaluation rather
than adding more raw surface by implication.
