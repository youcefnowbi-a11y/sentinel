# P4H-X-R Lock Verdict

Date: 2026-04-30
Status: Locked

## Verdict

P4H-X-R is accepted as a research lock.

```text
doctrine = Power-first, mission-governed, proof-backed
runtime code added = no
new browser power added = no
desktop/image/pdf/video backend activated = no
next code direction = PerceptionEngine v0 + ActionEngine v0 with browser backend only
```

## Locked Decisions

1. Replace defensive `safe/danger` language with operator language:

```text
granted
out-of-scope
impactful
irreversible
external
higher-authority
```

2. Use `CompiledMissionPolicy` to reduce micro-friction:

```text
MissionAuthorityEnvelope -> CompiledMissionPolicy -> fast execution inside scope
```

3. Build the next code phase around two engines:

```text
PerceptionEngine = see / understand / ground
ActionEngine = act / manipulate / execute
```

4. Keep the constitution:

```text
visible != understood != actionable != authorized
```

5. Future code locations:

```text
sentinel.agent.perception/
sentinel.agent.action_engine.py
sentinel.agent.browser.perception_adapter.py
```

6. Browser remains the only active backend for v0.

## Not Allowed Yet

```text
desktop runtime
host screen control
real OS mouse/keyboard
image/PDF/video runtime backend
new browser V3 power
ungoverned action execution
authority from OCR or page text
```

## Final Decision

```text
start PerceptionEngine v0 + ActionEngine v0 code with browser backend only
```

The next implementation should create the smallest useful code slice:

```text
BrowserVisualObservation / UIObservation
-> PerceptionFrame
-> SceneActionCandidate
-> CompiledMissionPolicy
-> ActionEnvelope
-> existing browser controlled runner
-> PostActionVerifier
-> FinalGate
```

## Boundary

P4H-X-R does not claim browser completion or open-web visual supremacy.

It changes the next build target from:

```text
more browser visual tests
```

to:

```text
mission-governed perception/action engine
```
