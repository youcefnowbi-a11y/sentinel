# P4H-X Lock Verdict

Date: 2026-04-30
Status: Locked

## Verdict

P4H-X is accepted as a code slice.

```text
PerceptionEngine v0 = implemented
ActionEngine v0 = implemented
CompiledMissionPolicy = implemented
active backend = browser only
new browser powers = none
desktop/image/pdf/video runtime = none
```

## Implemented Files

```text
sentinel-control/services/sentinel-core/sentinel/agent/perception/__init__.py
sentinel-control/services/sentinel-core/sentinel/agent/perception/models.py
sentinel-control/services/sentinel-core/sentinel/agent/perception/engine.py
sentinel-control/services/sentinel-core/sentinel/agent/browser/perception_adapter.py
sentinel-control/services/sentinel-core/sentinel/agent/action_engine.py
sentinel-control/services/sentinel-core/tests/test_agent_perception_action_engine.py
```

## Locked Doctrine

```text
Power-first.
Mission-governed.
Proof-backed.
```

Execution meaning:

```text
visible      = perceptual signal exists
understood   = scene model can interpret it with confidence
actionable   = target maps to a valid runtime ref/action class
authorized   = compiled mission policy grants it
```

No action executes from visibility alone.

## Test Coverage

P4H-X targeted tests verify:

```text
browser observations become PerceptionFrame
PerceptionFrame targets are never authorized by perception
CompiledMissionPolicy grants in-scope browser action
ActionEnvelope requires runtime ref
ActionEngine dispatches through existing browser runner shape
OCR cannot authorize action
future desktop backend is rejected in v0
out-of-scope action class is rejected
post-action verification uses existing BrowserPostActionVerifier and FinalGate V2.5 contract
```

## Next Decision

Next recommended tranche:

```text
P4H-Y Browser Perception/Action Fluency Scorecard
```

Goal: run repeated browser-only perception/action missions through the new
engine path and measure action tempo, ref validity, repair quality, proof
completeness, step count, and latency.
