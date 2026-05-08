# P4H-AB Browser Operator Long-Horizon Mission Trial

Date: 2026-04-30
Status: Implemented

## Goal

P4H-AB proves that the central browser operator can continue across longer
missions instead of only routing isolated powers.

The executable runner is:

```text
agent-lab/benchmarks/browser_tasks/browser_operator_long_horizon_runner.py
```

## Operator Path

P4H-AB keeps the P4H-X/AA path:

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

## Mission Groups

The runner executes 10 long-horizon fixture missions:

```text
BF-LONG-001 research -> form submit -> verify
BF-LONG-002 private session -> login -> cookie summary -> HAR -> close
BF-LONG-003 download quarantine -> inspect/certify artifact -> upload
BF-LONG-004 multi-tab compare event -> choose target -> submit
BF-LONG-005 failed first action -> repair -> continue
BF-LONG-006 ambiguous visual crop/zoom -> grounded action
BF-LONG-007 JS network denial -> alternative HAR diagnostic
BF-LONG-008 step-budget pressure -> compact plan execution
BF-LONG-009 cross-class wrong-ref verifier repair -> HAR capture
BF-LONG-010 end-to-end artifact pack
```

## Boundary

P4H-AB adds no browser power.

It only composes existing classes:

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
```

## Execution Meaning

P4H-AB tests continuity:

```text
read -> act -> verify -> repair -> continue -> final proof
```

It does not claim:

```text
open-web fluency
desktop runtime
real account login
raw browser supremacy against a live peer
new V3 authority classes
```

The result is browser-only and fixture-backed, but the loop is executable and
measured.
