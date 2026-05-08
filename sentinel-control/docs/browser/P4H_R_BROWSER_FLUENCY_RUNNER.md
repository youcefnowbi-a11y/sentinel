# P4H-R Browser Fluency Runner

Date: 2026-04-30
Status: Complete

## Purpose

P4H-R turns the P4H 72-mission Browser Fluency corpus into a runnable lab
scorecard.

This is not a new browser power. It is a benchmark runner that measures where
Sentinel is fluent and where it is still partial.

## Implemented Files

```text
agent-lab/benchmarks/browser_tasks/browser_fluency_runner.py
agent-lab/benchmarks/browser_tasks/test_browser_fluency_runner.py
```

Inputs:

```text
agent-lab/benchmarks/browser_tasks/browser_fluency_missions.json
```

Outputs:

```text
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_first_results.jsonl
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_first_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_first_scorecard.md
```

## First Subset Executed

P4H-R executes the first critical subset requested:

```text
G1 lifecycle
G2 URL/navigation
G3 perception/grounding
G5 forms
G8 JS/HAR/network
G11 safety/adversarial
G12 repair/cognitive integration
```

That is:

```text
42 executed missions
30 catalog missions not run yet
```

## Execution Mode

```text
execution_mode = contract_fixture
```

This means the runner measures current contract/fixture coverage. It does not
claim live browser fluency, open-web fluency, or peer-runtime supremacy.
