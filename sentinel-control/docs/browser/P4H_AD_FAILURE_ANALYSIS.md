# P4H-AD Failure Analysis

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

## Hard Cases Covered

```text
duplicate Open buttons resolved by surrounding context
weak DOM/AX target recovered by visual binding
covered overlay target rejected before wrong action
dynamic DOM epoch verified after action
503 network failure repaired through bounded alternative
same-origin redirect revalidated
deep-scroll target found under step budget
visual prompt injection denied as OCR-only authority
cookie/storage/HAR diagnostics redacted
end-to-end open-web-like mission pack completed
```

## Visual Verifier Pressure

P4H-AC had high p95 latency on the visual verifier mission because every visual
proof forced a rendered Playwright capture.

P4H-AD changes the execution profile:

```text
visual_render_count = 1
visual_cache_hit_rate = 0.9833
visual_latency_p95_ms = 0.5
```

This does not remove visual proof. It avoids unnecessary repeated cold renders
for the same static visual fixture.

## Remaining Gaps

P4H-AD still does not prove:

```text
external open-web stability
arbitrary site compatibility
real peer superiority
real account login
CAPTCHA or bot-wall handling
desktop/image/pdf/video runtime backends
```

## Next Hardening Risk

The next real risk is not the local operator loop. It is external variability:

```text
third-party scripts
real-world SPAs
infinite scroll
cookie banners
bot mitigations
layout shifts
slow network
unpredictable selectors
```
