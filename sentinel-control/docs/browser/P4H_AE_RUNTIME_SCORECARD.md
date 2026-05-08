# P4H-AE Runtime Scorecard

Date: 2026-05-01
Updated: 2026-05-07
Status: Implemented

## Targeted Test Result

```text
test file = sentinel-control/services/sentinel-core/tests/test_agent_browser_operator_runtime_integration.py
tests = 3
expanded_tests = 8
passed = 8
```

## Coverage

| Case | Result |
| --- | --- |
| AgentRuntime routes Browser V3 form submit through BrowserOperatorRuntimeRoute | pass |
| CoreFinalGate accepts runtime-routed Browser V3 receipt chain | pass |
| Missing compiled policy authority rejects before browser execution | pass |
| MissionRunner invokes `browser_operator_route` action | pass |
| Mission trace records neutral operator route result | pass |
| RepairLoop recovers after first browser route failure | pass |
| Mission max_actions prevents over-execution | pass |
| Global repair budget blocks projected overflow | pass |
| Browser receipts, artifacts, and operator IDs survive FinalGate | pass |
| Revoked mission envelope blocks before browser route start | pass |

## Runtime Metrics

```text
agent_runtime_operator_route_success = 1.0
mission_runner_operator_route_success = 1.0
finalgate_acceptance = 1.0
authority_rejection_correctness = 1.0
repair_recovery = 1.0
budget_block_correctness = 1.0
revoked_pre_route_block = 1.0
false_action_rate = 0.0
new_browser_powers = 0
```

## Accepted Event Chain

```text
browser_operator_route_started
browser_ui_observation_captured
context_pack_assembled
context_pack_validated
tool_intent_compiled
browser_operator_route_prepared
tool_policy_decided
artifact_captured
browser_form_submit_executed
browser_operator_route_completed
```

## Boundary

P4H-AE is an integration gate. It is not a new 30-run benchmark tranche.
P4H-AD remains the current open-web-like 30-run hardening scorecard.
