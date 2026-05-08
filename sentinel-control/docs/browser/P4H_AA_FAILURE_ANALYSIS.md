# P4H-AA Failure Analysis

Date: 2026-04-30
Status: No remaining failing missions

## Initial Failure

The first smoke run failed on:

```text
BF-V3ACT-006-cookie-storage-envelope
BF-V3ACT-009-cross-class-authority-flow
```

Root cause:

```text
browser_cookie_storage_contract manifest risk_class understated the declared
side effects.
```

The tool writes redacted local artifacts, so the registry correctly rejected
the old manifest as:

```text
risk_class_understates_side_effects
```

## Fix

The manifest was corrected:

```text
PRIVATE_DATA_READ -> DRAFT_ONLY_WRITE
```

This aligns the manifest with the existing side effects and keeps execution
inside mission authority and scoped artifact paths.

## Second Failure

The cross-class flow initially tried to route HAR/body capture through the
login target ref. `ActionEngine` rejected it before execution:

```text
target_action_class_not_supported
```

That was correct. The fix was to bind HAR/body capture to the `Inspect Network`
runtime ref, the ref that actually exposes `browser_har_body_capture`.

## Final State

```text
failed_missions = []
false_action_rate = 0.0
authority_correctness = 1.0
finalgate_pass_rate = 1.0
```

The important point: both failures were caught before false external action.
