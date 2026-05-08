# P4E Visual Grounding Tasks

Date: 2026-04-30
Status: Complete

## Purpose

The visual grounding slice checks whether Browser V2.5 observations are usable
inside the benchmark path.

## Task Group

```text
visual_grounding
```

Signals:

```text
BROWSER_UI_OBSERVATION_CAPTURED
BROWSER_VERIFICATION_COMPLETED
```

The fixture creates visually similar actions and verifies that the task is
grounded through `BrowserUIObservation`, not raw page text.

## Metrics

- mission success;
- trace quality;
- source quality;
- interaction correctness;
- latency p50/p95;
- step count p50/p95;
- Wilson interval.

## Boundary

This is a self-hosted visual grounding proxy. A future external campaign still
needs VisualWebArena-style screenshot-heavy tasks.
