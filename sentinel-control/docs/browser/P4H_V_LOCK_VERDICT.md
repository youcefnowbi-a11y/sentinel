# P4H-V Lock Verdict

Date: 2026-04-30
Status: Locked

## Verdict

```text
P4H-V full live self-hosted runner = complete
full Browser Fluency catalog = 72/72 missions
run_count_per_mission = 30
total_iterations = 2160
success_rate = 1.0
wilson_lower_overall = 0.9982
wilson_lower_per_group = 0.9791
wilson_lower_per_mission = 0.8865
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
final decision = browser_fluency_full_live_self_hosted_pass
```

## Boundary

P4H-V locks Sentinel's self-hosted Browser Fluency baseline.

It does not lock:

```text
open-web benchmark supremacy
real OpenClaw peer comparison
real OCR model performance
real external login/session compatibility
```

## Next

```text
P4H-W - real browser-engine visual/OCR harness
P4G-R2 - real peer container execution only when Docker/Podman is available
```
