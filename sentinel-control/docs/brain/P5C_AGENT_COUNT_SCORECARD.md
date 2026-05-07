# P5C Agent Count Scorecard

Date: 2026-05-07
Status: Implemented

## Targeted Test Result

```text
test file = sentinel-control/services/sentinel-core/tests/test_agent_count_controller.py
tests = 7
passed = 7
```

Command verified:

```bash
python -m pytest tests/test_agent_count_controller.py -v --tb=short
```

Full sentinel-core was not rerun for P5C. Verification stayed targeted to the
new advisory controller, per the small-test instruction.

## Outputs Verified

`AgentCountRoute` deterministically emits:

```text
recommended_agent_count
brain_mode
max_parallel_agents
agent_budget
reason
```

It also records:

```text
entropy_band
extreme_swarm_blocked
advisory_only = true
authority_expansion = false
agent_spawning = false
runtime_multi_agent_execution = false
trace_refs
```

## Coverage

| Case | Result |
| --- | --- |
| 1-agent low entropy route emits `AGENT_COUNT_ROUTED` | pass |
| 3-5 medium entropy route | pass |
| 8-20 high entropy route | pass |
| 20-100 very-high entropy route | pass |
| Extreme swarm blocked by default | pass |
| Budget pressure reduces count | pass |
| No authority expansion | pass |

## Boundary Metrics

```text
new browser powers = 0
new external systems = 0
agent spawning = 0
runtime multi-agent execution = 0
authority expansion = 0
```

## Decision

P5C targeted scorecard passes.
