# P4H-AD Lock Verdict

Date: 2026-05-01
Status: Locked

## Verdict

P4H-AD is accepted.

```text
browser operator open-web-like hardening runner = implemented
missions = 10
runs per mission = 30
total iterations = 300
verdict = browser_operator_open_web_like_hardening_pass
new browser powers = none
```

## What Is Now Proven

P4H-AD proves that the central browser operator can handle harder self-hosted
pages that resemble common open-web failure modes:

```text
messy layout
ambiguous repeated controls
weak DOM/AX
overlay-covered targets
dynamic state changes
network failures
redirect revalidation
deep scroll
visual prompt injection
redaction under mixed diagnostics
```

## What Passed

```text
success_rate = 1.0
wilson_lower = 0.9874
operator_tempo = 0.9698
open_web_like_success = 1.0
weak_dom_ax_recovery_rate = 1.0
ambiguous_target_accuracy = 1.0
dynamic_state_recovery_rate = 1.0
network_repair_rate = 1.0
visual_cache_hit_rate = 0.9833
visual_render_count = 1
visual_tempo_score = 1.0
proof_completeness = 1.0
finalgate_pass_rate = 1.0
authority_correctness = 1.0
false_action_rate = 0.0
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
budget_violation_rate = 0.0
```

## Boundary

P4H-AD does not add:

```text
new Browser V3 authority classes
desktop runtime
OS mouse/keyboard
real account login
raw credential/cookie/HAR exposure
open-web supremacy claim
real peer runtime comparison
```

## Decision

Browser open-web-like operator hardening is locked at self-hosted fixture level.

Recommended next tranche:

```text
P4H-AE Browser Runtime Integration Gate
```

Goal:

```text
connect the proven browser operator runners to the Sentinel mission runtime path,
so missions can invoke the PerceptionEngine/ActionEngine browser loop as a
first-class execution route instead of only as benchmark harnesses.
```

Parallel spike:

```text
P4G-R2 peer adapter spike
```

This spike should stay bounded: define an approved throwaway OpenClaw container
command that emits neutral JSONL, or stop and continue Sentinel hardening.
