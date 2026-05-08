# P4H-R Next Hardening Plan

Date: 2026-04-30
Status: Complete

## Next Objective

Move from first subset scorecard to full Browser Fluency coverage.

## Recommended Order

```text
P4H-S1 - turn visual/OCR group from F0 to F2/F3
P4H-S2 - turn cookies/storage/session group from F0 to F3/F4
P4H-S3 - turn file/download/upload/PDF group from F0 to F3/F4
P4H-S4 - turn multi-tab group from F0 to F3/F4
P4H-S5 - turn research browsing group from F0 to F3/F4
P4H-S6 - harden partial critical missions to target level
P4H-S7 - run 30-run Browser Fluency scorecard
```

## Highest Priority Hardening Items

```text
1. Visual/OCR artifact fixtures.
2. Session/cookie/storage fluency fixtures.
3. Research browsing with conflict and recency.
4. Cognitive integration fixtures proving RepairLoop/EffortRouter/SuccessEvaluator movement.
5. CAPTCHA/bot-wall safe-stop fixture.
6. SPA route and stale dynamic DOM fixtures.
```

## Rule

Do not claim Browser Fluency until:

```text
all critical groups >= F3
cross-class groups >= F4
research/visual/safety groups >= F4
open-web representative slice >= F5
```
