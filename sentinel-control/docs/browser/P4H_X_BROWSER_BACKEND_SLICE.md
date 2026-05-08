# P4H-X Browser Backend Slice

Date: 2026-04-30
Status: Implemented

## Slice

P4H-X implements this browser-only path:

```text
BrowserUIObservation
+ BrowserVisualObservation
-> BrowserPerceptionAdapter
-> PerceptionFrame
-> SceneActionCandidate
-> CompiledMissionPolicy
-> ActionEnvelope
-> BrowserControlledCapabilityRunner-compatible interface
-> BrowserPostActionVerifier
-> CoreFinalGate V2.5 verifier contract
```

## No New Browser Power

P4H-X does not add:

```text
new submit authority
new download authority
new upload authority
new private session authority
new login authority
new cookie/storage authority
new JS authority
new HAR/body authority
desktop control
host screen control
OS mouse/keyboard
image/PDF/video runtime backend
```

## Runtime Ref Rule

`SceneActionCandidate` must bind to a runtime-minted browser ref.

OCR text, page text, visual labels, and model claims are insufficient on their
own.

## Existing Runner Rule

`ActionEngine.execute_browser_action()` takes a runner implementing:

```text
run(CanonicalToolCall, MissionAuthorityEnvelope, event_bus=EventBus)
```

This matches the existing governed browser runner shape and prevents a second
execution path.
