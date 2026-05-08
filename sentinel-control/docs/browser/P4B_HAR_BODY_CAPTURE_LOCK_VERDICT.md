# P4B-8 HAR Body Capture Lock Verdict

Date: 2026-04-29
Status: locked

## Implemented

- HAR/body capture request/result/receipt models.
- EventBus captured/rejected events.
- ToolRegistry manifest for `browser_har_body_capture`.
- ToolIntentCompiler grant rules.
- Controlled runner branch with injected backend.
- FinalGate redaction/bounds/artifact checks.
- Tests for accepted bounded capture and missing-redaction rejection.

## Verdict

P4B-8 is locked. Sentinel can capture HAR/body diagnostics only as bounded,
redacted, artifact-bound evidence under explicit Browser V3 authority.
