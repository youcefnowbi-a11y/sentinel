# P4H-AF Runtime Mini-Corpus

Date: 2026-05-07
Status: Implemented

## Scope

P4H-AF extends the P4H-AE runtime route from a single integration proof to a
small deterministic mini-corpus. It uses the existing `browser_form_submit`
authority only.

```text
new browser powers = none
new authority classes = none
real network/browser dependency = none
```

## Runtime Route Under Test

Every accepted case flows through the governed runtime path:

```text
AgentRuntime or MissionRunner
-> BrowserOperatorRuntimeRoute
-> Browser UI observation
-> PerceptionFrame
-> SceneActionCandidate
-> CompiledMissionPolicy
-> ActionEnvelope
-> BrowserControlledCapabilityRunner
-> BrowserFormSubmitExecutor
-> receipt/artifacts/events
-> CoreFinalGate
```

## Mini-Corpus Cases

| Case | Purpose | Result |
| --- | --- | --- |
| `messy_duplicate_context_submit` | Duplicate controls bind to the authorized runtime ref | pass |
| `weak_dom_ax_visual_bound_action` | Weak semantic label still produces a governed ref/action route | pass |
| `dynamic_state_after_action_verify` | Post-action state differs and is receipt-bound | pass |
| `redirect_revalidate_submit` | Same-origin redirect stays within policy and receipt chain | pass |
| `deep_scroll_budget_pressure` | Larger planned step count stays inside budget | pass |

## Negative Guards

| Guard | Expected Behavior | Result |
| --- | --- | --- |
| Fabricated runtime ref | Reject before Browser V3 execution | pass |
| Exhausted action budget candidate | Reject in ActionEngine prepare phase before Browser V3 execution | pass |

## Test File

```text
sentinel-control/services/sentinel-core/tests/test_agent_browser_operator_runtime_minicorpus.py
```

## Boundary

P4H-AF does not prove:

```text
open-web external success
real peer superiority
real account login
CAPTCHA/bot-wall handling
desktop/image/PDF/video runtime
new Browser V3 authority classes
```

It proves breadth of the locked P4H-AE runtime route across multiple
P4H-AD-style browser form scenarios.
