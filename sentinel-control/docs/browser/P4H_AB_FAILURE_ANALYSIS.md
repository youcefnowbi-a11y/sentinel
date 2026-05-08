# P4H-AB Failure Analysis

Date: 2026-04-30
Status: No remaining failing missions

## Final Mission State

```text
failed_missions = []
unstable_iterations = []
false_action_rate = 0.0
budget_violation_rate = 0.0
authority_correctness = 1.0
finalgate_pass_rate = 1.0
```

## Important Negative Paths

P4H-AB intentionally exercises failures and denials:

```text
fabricated ref rejected before execution
wrong HAR/body ref rejected before capture
JS network attempt rejected before result artifact
oversized step plan rejected by CompiledMissionPolicy
compact plan rerouted and executed after budget pressure
```

These are not benchmark failures. They are expected operator behavior.

## Implementation Hardening

The first local smoke attempt exposed an environment issue in the benchmark
runner: Python `TemporaryDirectory` created fixture workspaces whose child
capture directories were not writable under this Windows sandbox.

Fix:

```text
runner now uses an explicit workspace-local tmp_p4h_ab root
runner creates fixture workspaces directly
pytest tests avoid tmp_path to stay inside writable project paths
```

The same sandbox-compatible temp workspace pattern was applied to the existing
P4H-Y, P4H-Z, and P4H-AA operator runners so the combined operator suite can
run under the same Windows workspace constraints.

This is not a Browser runtime defect. It was a benchmark harness filesystem
placement issue.

## Remaining Reality Gap

P4H-AB remains:

```text
browser-only
fixture-backed
self-hosted/local
not real open-web
not Desktop/Image/PDF/Video runtime
not a live peer comparison
```

The operator is stronger, but the next proof must either broaden live
self-hosted tasks or run a controlled open-web campaign.
