# P4H-AC Browser Operator Live Long-Horizon Harness

Date: 2026-05-01
Status: Implemented

## Goal

P4H-AC moves the P4H-AB long-horizon operator loop onto live self-hosted
browser fixtures.

The executable runner is:

```text
agent-lab/benchmarks/browser_tasks/browser_operator_live_long_horizon_runner.py
```

## What Changed

P4H-AB proved long-horizon continuity with fixture-composed V3 action paths.
P4H-AC adds a live local HTTP layer before the governed ActionEngine path:

```text
self-hosted page observation
-> live fixture action or diagnostic
-> Perception/Action operator path
-> Browser V3 executor
-> receipt / event
-> CoreFinalGate
```

This is still browser-only and self-hosted. It is not an open-web supremacy
claim.

## Operator Path

P4H-AC keeps the central operator spine:

```text
BrowserUIObservation
-> BrowserPerceptionAdapter
-> PerceptionFrame
-> SceneActionCandidate
-> CompiledMissionPolicy
-> ActionEnvelope
-> BrowserControlledCapabilityRunner
-> Browser V3 executor
-> receipt / event
-> CoreFinalGate
```

The live layer adds:

```text
SelfHostedFixtureServer
-> guarded local URL
-> live observation hash
-> live response/action receipt
-> redaction proof where needed
-> ActionEngine routed mission step
```

## Mission Groups

The runner executes 10 live long-horizon missions:

```text
BF-LIVE-LONG-001 research -> form submit -> verify
BF-LIVE-LONG-002 state/cookie redaction -> login -> cookie summary -> HAR -> close
BF-LIVE-LONG-003 live download -> upload -> governed artifact flow
BF-LIVE-LONG-004 live multi-tab comparison -> selected submit
BF-LIVE-LONG-005 failed first action -> resnapshot -> repair -> continue
BF-LIVE-LONG-006 live visual fixture -> rendered crop/zoom verifier -> action
BF-LIVE-LONG-007 JS network denial -> HAR redaction alternative
BF-LIVE-LONG-008 external boundary and step budget pressure
BF-LIVE-LONG-009 cross-class wrong-ref verifier repair
BF-LIVE-LONG-010 live end-to-end final artifact pack
```

## Boundary

P4H-AC adds no browser power.

It only composes existing authorities and fixtures:

```text
browser_form_submit
browser_download_quarantine
browser_upload_authorized
browser_private_session
browser_login_authority
browser_cookie_storage_contract
browser_js_evaluate_sandboxed
browser_har_body_capture
browser_interaction_limited-style perception/action routing
self-hosted public fixture observation
```

It does not add:

```text
desktop runtime
OS mouse/keyboard
real account login
real user browser profile access
non-fixture form submit
raw credential/cookie/storage/HAR exposure
open-web or peer supremacy claim
```

## Execution Meaning

P4H-AC tests live continuity:

```text
live observe -> ground -> act -> verify -> repair -> continue -> final proof
```

The important difference from P4H-AB is that each mission now starts from a
real local HTTP fixture interaction before the ActionEngine route is exercised.
