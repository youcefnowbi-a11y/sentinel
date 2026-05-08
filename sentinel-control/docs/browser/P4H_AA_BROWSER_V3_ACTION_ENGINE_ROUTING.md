# P4H-AA Browser V3 ActionEngine Routing

Date: 2026-04-30
Status: Implemented

## Goal

P4H-AA routes the existing Browser V3 authority classes through the P4H-X
`ActionEngine` path.

This is execution-heavy. The runner is:

```text
agent-lab/benchmarks/browser_tasks/browser_operator_cross_class_runner.py
```

## Boundary

P4H-AA does not add a new browser power.

It only proves that already-existing Browser V3 classes can flow through:

```text
BrowserUIObservation
-> BrowserPerceptionAdapter
-> PerceptionFrame
-> SceneActionCandidate
-> CompiledMissionPolicy
-> ActionEnvelope
-> BrowserControlledCapabilityRunner
-> Browser V3 executor
-> V3 receipt / event
-> CoreFinalGate
```

## Routed Classes

```text
browser_form_submit
browser_download_quarantine
browser_upload_authorized
browser_private_session
browser_login_authority
browser_cookie_storage_contract
browser_js_evaluate_sandboxed
browser_har_body_capture
```

## Core Change

`BrowserPerceptionAdapter.build_frame(...)` now accepts:

```text
action_classes_by_ref: dict[str, list[str]]
```

This lets the brain/operator expose V3 action candidates on runtime-minted
browser refs without authorizing them.

The constitution remains intact:

```text
visible != understood != actionable != authorized
```

A V3 action class on a `PerceptionTarget` means only:

```text
this runtime ref can support this action class
```

It does not mean:

```text
the action is authorized
```

Authorization still comes from:

```text
MissionAuthorityEnvelope
-> BrowserV3AuthorityGrant
-> CompiledMissionPolicy
-> BrowserControlledCapabilityRunner
-> FinalGate
```

## Manifest Hardening

The P4H-AA runner exposed one manifest mismatch:

```text
browser_cookie_storage_contract
declared risk = PRIVATE_DATA_READ
actual side effects = browser read + local draft artifact write
```

The manifest was corrected to:

```text
DRAFT_ONLY_WRITE
```

This does not grant a new power. It makes the registry risk declaration match
the existing redacted artifact write behavior.
