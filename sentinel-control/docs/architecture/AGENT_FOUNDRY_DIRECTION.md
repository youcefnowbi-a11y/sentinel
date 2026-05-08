# Agent Foundry Direction

Sentinel should become a mission operating system plus agent foundry, not a single GTM generator.

The platform pattern is:

```text
Mission type
-> planner
-> autonomy engine
-> tool/executor registry
-> reviewer
-> success evaluator
-> trace timeline
-> artifact index
-> escalation gateway
```

Every future agent is a mission type with explicit tools, risks, gates, and success criteria.

## Product Rule

Do not add power as raw tools.

Add power as mission-scoped capabilities:

```text
capability
-> manifest
-> scanner
-> policy
-> fake benchmark
-> mission registry
-> reviewer
-> trace
-> UI preview
```

## Mission Family

| Agent | Mission Type | Purpose | Tools Needed | Future Risks | Required Gates |
| --- | --- | --- | --- | --- | --- |
| GTM Agent | `gtm` | Convert market evidence into first-customer pack, landing copy, outreach drafts, watchlist, roadmap. | CueIdea import, research enrichment, local file writer, draft generator. | Generic output, weak WTP proof, spammy outreach, fake certainty. | Evidence contract, WTP gate, draft-only outbound, ReviewerLite, success evaluator. |
| Research Agent | `research_summary`, later `deep_research` | Verify market, competitors, pricing, communities, objections, and evidence gaps. | Public web read-only, source ranker, citation extractor, evidence mapper. | Prompt injection, fake evidence, low-quality sources, cost explosion. | Read-only browser sandbox, source ranking tests, citation preservation, prompt injection evals. |
| Sales Agent | `sales_outreach` | Prepare and later send controlled outreach to approved contacts. | Contact import, CRM draft, email draft, approved sender, rate limiter. | Spam, deceptive personalization, bad list provenance, reputation damage. | Contact ownership proof, opt-out policy, rate limits, approval per campaign, outbound trace. |
| Coding Agent | `code_patch_proposal` | Analyze code, propose patches, run tests, prepare change summaries. | Repo reader, patch proposal, test runner sandbox, branch manager. | Production mutation, secret exposure, destructive commands, flaky tests. | No auto-production mutation, patch proposal only, sandbox tests, diff review, user approval. |
| Browser Agent | `browser_research` | Read public pages, collect sources, extract evidence. | Sandbox browser profile, page fetch, screenshot, extractor. | Form submit, login, credential capture, prompt injection. | Read-only first, no login, no submit, browser injection tests, source trace. |
| Ops Agent | `ops_workspace` | Prepare operational docs, checklists, dashboards, local exports. | File writer, CSV/JSON exporter, watchlist updater. | Bad data writes, path traversal, stale decisions. | Generated-project path boundary, artifact index, rollback metadata, reviewer. |
| Self-Improvement Agent | `improvement_proposal` | Convert repeated failures into proposal, patch plan, tests needed. | Trace reader, failure classifier, patch sketcher, eval suggester. | Auto-mutation, policy drift, reward hacking, unsafe tool grants. | Proposal only, no automatic code mutation, test requirement, human approval, policy immutability. |

## Capability Gates

### Gate 1: Local Artifacts

Status: implemented in G12B.

Allowed:

- create project folder
- create markdown files
- export JSON
- draft outreach without sending
- create watchlist
- create roadmap
- write trace

Blocked:

- shell
- browser submit
- real email send
- desktop control
- payment
- dependency install
- credentials
- production mutation

### Gate 2: Read-Only Research

Required before browser research:

- sandbox browser profile
- no login
- no submit
- no credential fields
- source URL preservation
- source ranker
- prompt injection detector
- evidence mapper
- trace events for every source

### Gate 3: Controlled Outbound

Required before email/channel sending:

- contact ownership or user-provided contacts
- campaign-level mission authority
- recipient caps
- rate limits
- opt-out text
- deception checks
- approval preview
- sent-message ledger
- reputation kill switch

### Gate 4: Skill Scanner

Required before any skill/plugin system:

- manifest schema
- permission declaration
- dependency scan
- dynamic loading scan
- network/filesystem/shell detection
- secret access detection
- fake benchmark fixture
- policy mapping
- block/review/draft-only classification

### Gate 5: Coding Agent

Required before code mutation:

- branch-only writes
- no production mutation
- no destructive shell
- test sandbox
- diff trace
- reviewer pass
- human approval
- rollback plan

### Gate 6: Sidecar Lab

Required before desktop control:

- fake RPC sidecar first
- capability manifest
- protected apps list
- screenshot sanitizer
- clipboard sanitizer
- user-visible control surface
- stop/revoke always visible
- no silent background authority

## How Sentinel Uses Other Agents Without Copying Them

| Vendor Lesson | Sentinel Rewrite |
| --- | --- |
| Runtime-power specimens show channels, skills, browser, and shell surfaces. | Mission-scoped executor registry, SkillScanner, black-zone policy, dry-run, trace. |
| Memory/delegation specimens show long-running behavior. | Mission state, trace timeline, future memory-as-context only, never memory-as-authority. |
| Cost-routing specimens show local/cloud routing. | Budget controller now, CostRouter later, with authority separated from effort. |
| Host-control specimens show sidecar and desktop awareness. | PermissionedSidecar later, fake sidecar lab first, no silent desktop control. |

## Near Roadmap

### G13: Mission UI

- Mission creation flow.
- Authority preview.
- Mission Control dashboard.
- Artifact viewer.
- Escalation inbox.
- Stop/revoke controls.

### G14: Fake Power Harness

- Fake browser.
- Fake email.
- Fake channel.
- Fake shell.
- Fake desktop.
- Fake payment.

Purpose: test authority routing without real-world side effects.

### G15: Read-Only Browser Sandbox

- Public web only.
- No login.
- No submit.
- Evidence extraction and citation preservation.

### G16: Controlled Outbound Draft To Send

- Approved contacts only.
- Rate-limited.
- Opt-out.
- Campaign approval.
- No spam automation.

### G17: Sidecar Lab

- Fake desktop sidecar.
- Capability manifest.
- Screen/clipboard sanitizer.
- Stop/revoke.

### G18: Skill Scanner v0

- Scan skills before registration.
- Classify blocked/review/draft-only/safe.
- Create skill risk report.

### G19: Cost Router + Reviewer Loop

- Budget per mission.
- Model effort separation from authority.
- Reviewer/fix pass for artifacts.

## North Star

Sentinel becomes the agent foundry where every new power is born as a scoped mission capability, not as an uncontrolled tool.
