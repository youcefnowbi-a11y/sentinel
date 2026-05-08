# P4H-AC Failure Analysis

Date: 2026-05-01
Status: Passed With No Runtime Failures

## Result

```text
total_iterations = 300
failed_iterations = 0
unstable_iterations = []
false_action_rate = 0.0
authority_violation_rate = 0.0
artifact_leakage_rate = 0.0
budget_violation_rate = 0.0
```

## Issues Found During Implementation

One implementation mismatch was found before lock:

```text
issue = HAR live probe expected a raw secret string
actual = self-hosted HAR fixture exposes a redaction marker, not raw secrets
fix = assert the redaction fixture marker, then test synthetic redaction locally
impact = no raw HAR/body secret was introduced into reports
```

This is the correct behavior. The live fixture should not need to expose raw
secrets just to prove the redaction path.

## Covered Failure Modes

P4H-AC covers:

```text
failed first action repaired with fresh runtime ref
cross-class wrong-ref HAR capture rejected and repaired
JS network attempt denied before execution
external URL boundary denied
step budget pressure rewritten into compact plan
cookie/storage summary redacted
HAR/body diagnostic redacted
artifact upload restricted to certified Sentinel artifact id
visual verifier bound to rendered screenshot/crop/zoom proof
```

## Remaining Gaps

P4H-AC does not prove:

```text
open-web stability
real account login
real user profile isolation
arbitrary site compatibility
CAPTCHA or bot-wall handling
desktop/image/pdf/video runtime backends
OpenClaw real peer superiority
```

## Hardening Notes

The main performance pressure is visual rendering:

```text
BF-LIVE-LONG-006 latency_p50_ms = 3814.47
BF-LIVE-LONG-006 latency_p95_ms = 5305.635
```

This is acceptable for a proof harness but should be optimized before high-volume
operator loops depend on rendered visual verification at every step.
