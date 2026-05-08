# Sentinel Runtime Capability Roadmap

Date: 2026-04-26
Status: G10 architecture spec, amended by G11 Power Mode doctrine and G12 Mission Authority doctrine

## Principle

Runtime power is earned and authority is scoped.

No capability graduates because a vendor has it. A capability graduates only after Sentinel has a source lesson, original spec, risk class, policy rule, dry-run format, approval rule, trace schema, fake benchmark, and regression eval.

G11 correction:

- safe, reversible, local, draft-only actions should execute quickly after policy check;
- high-impact actions remain blocked by default;
- future high-impact actions may become unlockable only through scoped Power Mode authority envelopes;
- Power Mode is not a global bypass and does not enable any risky runtime now.

G12 correction:

- the primary runtime primitive is mission authority, not action approval;
- Power Mode is an authority level inside a mission, not the product center;
- permission is granted once for a mission, then Sentinel acts inside scope and escalates only at the boundary.

## Promotion Ladder

```text
forensic lesson
-> Sentinel spec
-> fixture dataset
-> static scanner
-> fake benchmark
-> policy rule
-> dry-run schema
-> trace schema
-> local v0 implementation
-> eval gate
-> private staging
```

## Capability Roadmap

| Phase | Capability | Vendor Lesson | Allowed Work | Runtime Status |
|---|---|---|---|---|
| Now | CueIdea-backed GTM Pack | Sentinel S1/S2 | improve evidence density and specificity | allowed |
| Now | Trace Ledger | all vendors need stronger trace | log every trust-changing event | allowed |
| Now | Firewall v0 | OpenClaw/JARVIS | risk, policy, dry-run, approval | allowed |
| Now | SafeActionKernel | OpenClaw gateway lesson | local files/drafts only | allowed |
| Now | SkillScanner v0 | OpenClaw/OpenJarvis/Hermes | static scan and canonical reports | allowed |
| Now | Memory v0 | Hermes/JARVIS | typed context, no authority | allowed |
| Now | CostRouter Lite | OpenJarvis/Hermes | budget caps and route trace | allowed |
| Now | Mission Authority spec | deep research G12 | mission envelope, state, actions, escalation, trace | allowed |
| Now | Power Mode spec | G11 debate correction | authority envelope design only | spec only |
| Next | Research verifier | CueIdea plus independent research | source ranking and evidence gaps | allowed |
| Next | Approval inbox | JARVIS approval lesson | dry-run review UI | allowed |
| Next | Trace viewer | JARVIS/OpenJarvis telemetry | explain decisions and actions | allowed |
| Next | Mission-aware Tempo Router | G11/G12 correction | green execute, amber log, red escalate, black block | allowed |
| Next | Mission Control | G12 UX research | live mandate, timeline, budget, stop, revoke | allowed |
| Later | Browser read-only | OpenClaw/JARVIS | public-source extraction only | disabled until fake eval |
| Later | Channel inbound | all channel vendors | untrusted inbound context | disabled until fake eval |
| Later | Channel outbound drafts | all channel vendors | drafts only | disabled until compliance eval |
| Later | Workflow proposals | JARVIS/OpenJarvis | proposal generation only | disabled until workflow firewall |
| Later | PermissionedSidecar | JARVIS | fake-only sidecar benchmark | disabled |
| Later | Desktop awareness | JARVIS | sanitizer design and fixtures | disabled |
| Future Power Mode candidate | Browser submit | OpenClaw/JARVIS | no implementation now; future scoped eval only | blocked by default |
| Future Power Mode candidate | Real channel send | all channel vendors | no implementation now; future scoped eval only | blocked by default |
| Future Power Mode candidate | Desktop control | JARVIS | no implementation now; future scoped sidecar only | blocked by default |
| Future Power Mode candidate | Shell execution | all runtime vendors | no implementation now; future isolated sandbox only | black-zone |
| Future Power Mode candidate | Runtime install | all vendors | no implementation now; future signed package flow only | black-zone |

## Capability Kill Criteria

Kill or defer a capability if:

- it requires real credentials during development;
- it cannot produce a dry-run preview;
- it cannot be traced with evidence/action/output refs;
- it cannot be blocked by a deterministic policy rule;
- it has no GTM Operator or AgentOps Firewall value;
- it pushes Sentinel toward generic desktop assistant before GTM pack quality is paid-ready;
- it needs vendor runtime code;
- it cannot pass fake benchmark before real use.

## Release Gates

| Release | Minimum Capabilities | Blocked Capabilities |
|---|---|---|
| Local GTM v1 | evidence, research enrichment, debate, GTM pack, safe files, trace, firewall | browser, channel send, shell, desktop, sidecar |
| Mission Authority v0 | mission envelope, deterministic classifiers, safe mission executors, trace timeline, escalation gateway | real browser submit, real send, shell, desktop, sidecar |
| AgentOps Scanner v0 | skill scanner, risk report, policy mapping, fake fixtures | runtime skill execution |
| CostRouter Lite | budget route trace, cap enforcement | auto model/policy mutation |
| Browser Research Alpha | read-only public extraction | submit, send, upload, login |
| Channel Draft Alpha | inbound untrusted, outbound draft | send |
| Sidecar Lab | fake RPC, manifest, sanitizer fixtures | real host control |
| Power Mode Harness | fake authority envelopes, scope checks, revocation, emergency stop | real shell, real desktop, real send, real payment |
