# 02 Capability Matrix

Date: 2026-04-26

## Capability Readiness Levels

| Level | Meaning |
| --- | --- |
| L0 | Design only |
| L1 | Fake benchmark only |
| L2 | Local safe execution |
| L3 | Read-only real-world access |
| L4 | Controlled write/send with approval |
| L5 | Mission-autonomous within strict scoped authority |

No capability jumps levels. Every capability moves through fake tests before real access.

## Matrix

| Capability | User Value | First Use Case | Current Level | Target Level | Risk | Required Gates |
| --- | --- | --- | ---: | ---: | --- | --- |
| Mission authority | Agent works without micro-approval | GTM mission | L2 | L5 | scope drift | envelope tests, trace, kill switch |
| Planner DAG | Long missions become structured | GTM artifacts | L2 | L5 | bad dependencies | DAG validation, success evaluator |
| Reviewer loop | Output quality rises | GTM pack review | L1/L2 | L5 | false confidence | reviewer/fix tests, evidence gaps |
| Tool registry | Tools become governed assets | local tools | L0 | L5 | raw tool sprawl | manifests, policies, fake tool harness |
| API cartographer | Agent discovers useful data sources | public API catalogs | L0 | L4 | bad/unsafe APIs | source scoring, auth policy, bench |
| Tool bench | Agent tests tools before trust | API reliability tests | L0 | L4 | false pass | fixtures, freshness checks, rate limit checks |
| Tool graph | Agent composes tools across domains | trend + jobs + reviews | L0 | L5 | bad causal links | graph evidence tests |
| Work method library | Agent thinks with methods | contradiction mining | L0 | L5 | formula theater | method selection evals |
| CueIdea evidence | Market proof seed | GTM Operator | L2 | L5 | stale/noisy evidence | evidence contract, WTP gate |
| Web research | Independent verification | competitors/pricing | L0 | L4 | prompt injection | read-only browser, source ranker |
| Browser read-only | Agent sees public web | research and audits | L0 | L3 | hidden login/submit | sandbox profile, no submit |
| Browser interaction | Agent operates web apps | launch/publish later | L0 | L4/L5 | external mutation | fake harness, approval, domain scopes |
| OCR image text | Agent reads screenshots/docs | competitor screenshots | L0 | L3 | OCR errors | confidence + manual preview |
| Vision understanding | Agent understands UI/images | landing/page critique | L0 | L3 | misread visuals | source frame trace |
| Image generation | Agent creates campaign assets | brand/social images | L0 | L4 | IP/brand mismatch | prompt trace, asset review |
| Image editing | Agent modifies photos/mockups | ad variants | L0 | L4 | harmful edits, brand drift | input provenance, edit preview |
| Video generation | Agent creates launch clips | product teaser | L0 | L4 | cost, quality, policy | storyboard, preview, approval |
| Video editing | Agent trims/subtitles/repurposes | social clips | L0 | L4 | lost context | frame index, transcript trace |
| Audio transcription | Agent reads calls/videos | interviews | L0 | L3 | privacy | consent flag, local storage boundary |
| PDF/document reading | Agent reads reports/decks | evidence import | L0 | L3 | extraction errors | page refs, quote trace |
| Code intelligence | Agent maps codebases | code agent | L0/L2 manual | L4 | secret exposure | repo read policy, secret filter |
| Patch proposal | Agent improves code safely | tests/docs/refactor | L0 | L4 | production mutation | branch/diff only, approval |
| Shell sandbox | Agent can run tests/builds | coding missions | L0 | L3/L4 | host damage | sandbox only, command allowlist |
| Controlled outbound | Agent sends approved emails | sales launch | L0 | L4 | spam/reputation | contacts proof, rate limit, opt-out |
| CRM/channel adapters | Agent coordinates pipeline | follow-up board | L0 | L4 | account misuse | OAuth scopes, campaign approval |
| Sidecar screenshot | Agent sees desktop context | support/operator | L0 | L3 | privacy leakage | sanitizer, app allowlist |
| Sidecar actions | Agent controls desktop | ops automation | L0 | L4/L5 | host takeover | fake sidecar first, revocation |
| Memory | Agent keeps context | project continuity | L0/L1 | L5 | memory poisoning | typed memory, no policy authority |
| Cost router | Agent controls spend/depth | model selection | L1 budget | L5 | quality loss/cost spike | budgets, telemetry, fallback |
| Self-improvement | Agent proposes better code | failure learning | L0 | L4 | auto-mutation | proposal only, tests, approval |

## Capability Build Law

For each row:

```text
Design -> manifest -> fake harness -> tests -> read-only/local -> controlled write -> mission autonomy
```

Never:

```text
idea -> direct real-world tool access
```

## Capability Packs To Create

### Pack A: Local Launch Studio

- brand naming;
- positioning;
- landing copy;
- outreach drafts;
- visual direction;
- image prompts;
- asset manifest.

### Pack B: Vision and Document Intake

- OCR;
- screenshot analysis;
- PDF extraction;
- image metadata extraction;
- evidence mapping.

### Pack C: Tool Intelligence

- API cartographer;
- tool registry;
- tool bench;
- tool graph;
- mission-to-tool compiler.

### Pack D: Browser Research

- sandbox browser;
- public web read-only;
- no login;
- no submit;
- citation extraction.

### Pack E: Code Intelligence

- repo map;
- dependency scan;
- function/class extraction;
- patch proposal;
- test plan.

### Pack F: Controlled Outbound

- contact import;
- compliance checks;
- message preview;
- campaign approval;
- send ledger.

### Pack G: Sidecar Lab

- fake sidecar RPC;
- screen/clipboard sanitizer;
- protected apps;
- permission manifest;
- stop/revoke.
