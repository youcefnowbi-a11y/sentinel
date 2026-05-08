# P4E WebArena-Style Tasks

Date: 2026-04-30
Status: Complete

## Purpose

The WebArena-style slice measures whether Sentinel can complete browser
workflows with trace and authority proof, not just isolated unit contracts.

## Task Groups

| Task group | What it tests | Required signals |
| --- | --- | --- |
| `form_workflow` | governed form commit with before/action/after proof | `BROWSER_FORM_SUBMIT_EXECUTED` |
| `search_navigation` | public navigation and evidence gathering | `BROWSER_PUBLIC_TAB_NAVIGATED`, `BROWSER_EVIDENCE_COLLECTED` |
| `multi_page_task` | multi-step public workflow with verification | `BROWSER_PUBLIC_TAB_NAVIGATED`, `BROWSER_VERIFICATION_COMPLETED` |

## Scoring

Each task reports:

- binary success;
- trace quality;
- proof completeness;
- interaction correctness;
- side-effect containment;
- step count p50/p95;
- latency p50/p95;
- Wilson interval.

## Boundary

These tasks are deterministic self-hosted fixtures. They are closer to
WebArena-style workflow structure, but they are not WebArena itself and they are
not open-web proof.
