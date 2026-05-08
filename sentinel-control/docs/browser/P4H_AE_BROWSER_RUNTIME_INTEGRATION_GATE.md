# P4H-AE Browser Runtime Integration Gate

Date: 2026-05-01
Status: Implemented

## Goal

P4H-AE moves the proven browser operator route out of benchmark-only harnesses
and into the Sentinel runtime path.

The integrated production code is:

```text
sentinel-control/services/sentinel-core/sentinel/agent/browser/operator_runtime.py
sentinel-control/services/sentinel-core/sentinel/agent/runtime.py
sentinel-control/services/sentinel-core/sentinel/mission/runner.py
```

## Runtime Path

The accepted route is:

```text
AgentRuntime / MissionRunner
-> BrowserOperatorRuntimeRoute
-> BrowserUIObservationSet
-> BrowserPerceptionAdapter
-> PerceptionFrame
-> SceneActionCandidate
-> CompiledMissionPolicy
-> ActionEnvelope
-> BrowserControlledCapabilityRunner
-> existing Browser V3 executor
-> receipt / events
-> CoreFinalGate
```

## What Changed

P4H-AE adds a runtime bridge, not a new browser power.

```text
BrowserOperatorRuntimeRoute
  compiles MissionAuthorityEnvelope into CompiledMissionPolicy
  maps browser UI observation into PerceptionFrame
  prepares an ActionEnvelope through ActionEngine
  dispatches only to BrowserControlledCapabilityRunner
  records operator route events into EventBus
```

`AgentRuntime` can now route supported browser controlled calls through this
operator bridge when a route is injected.

`MissionRunner` can now execute a mission action named `browser_operator_route`
when the same route is injected. This keeps the mission trace separate from the
agent EventBus while preserving a neutral operator result payload.

## Boundary

P4H-AE does not add:

```text
new Browser V3 authority class
new tool manifest
desktop runtime
OS mouse/keyboard
image/PDF/video backend runtime
raw credential/cookie/HAR export
open-web supremacy claim
```

The route can only execute actions already supported by
`BrowserControlledCapabilityRunner.SUPPORTED_ACTIONS` and already granted by the
mission envelope.

## Operator Events

P4H-AE adds route-level trace events:

```text
browser_operator_route_started
browser_operator_route_prepared
browser_operator_route_completed
browser_operator_route_rejected
```

These events do not replace Browser V3 receipts. They make the operator bridge
auditable while the underlying V3 executor still emits the authoritative browser
event and receipt.

## Runtime Rule

```text
visible != understood != actionable != authorized
```

The runtime route preserves this rule:

```text
visible = UI observation exists
understood = BrowserPerceptionAdapter produces a target with confidence
actionable = target binds to a runtime ref and action class
authorized = CompiledMissionPolicy grants the action/tool/domain
```

No browser action is executed from visibility alone.
