# P4H-AF Runtime Scorecard

Date: 2026-05-07
Status: Implemented

## Targeted Test Result

```text
test file = sentinel-control/services/sentinel-core/tests/test_agent_browser_operator_runtime_minicorpus.py
tests = 5
passed = 5
```

## Regression Result

```text
neighbor regression tests = 84 passed
full sentinel-core tests = 516 passed
```

Commands verified:

```bash
python -m pytest tests/test_agent_browser_operator_runtime_minicorpus.py -v --tb=short
python -m pytest tests/test_agent_browser_operator_runtime_minicorpus.py tests/test_agent_browser_operator_runtime_integration.py tests/test_agent_tool_selection.py tests/test_agent_core_final_gate.py tests/test_agent_trace_replay.py tests/test_agent_repair_loop.py -v --tb=short
python -m pytest tests -v --tb=short
```

## Coverage

| Case | Result |
| --- | --- |
| MissionRunner executes a five-case runtime browser mini-corpus | pass |
| AgentRuntime worker executes mini-corpus plan and FinalGate accepts | pass |
| AgentRuntime direct tool calls preserve unique browser receipts | pass |
| Fabricated runtime ref rejects before browser form submit execution | pass |
| Exhausted action budget rejects before browser form submit execution | pass |

## Runtime Metrics

```text
targeted_pass_rate = 1.0
neighbor_pass_rate = 1.0
full_core_pass_rate = 1.0
mission_runner_minicorpus_success = 1.0
agent_runtime_worker_minicorpus_success = 1.0
direct_tool_call_receipt_uniqueness = 1.0
fabricated_ref_rejection = 1.0
budget_guard_rejection = 1.0
finalgate_acceptance = 1.0
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

P4H-AF is a runtime mini-corpus integration gate. It is not a new open-web
benchmark tranche and it does not authorize additional browser actions.
