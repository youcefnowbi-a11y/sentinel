# P3G OpenClaw Interaction Dry-Run Port Map

Date: 2026-04-28
Status: implemented and validated in Sentinel-owned code

## Scope

P3G ports browser interaction intelligence from the isolated OpenClaw specimens
as a dry-run planning layer only. It does not import OpenClaw runtime routes,
Playwright action functions, profiles, tabs, uploads, downloads, evaluate,
gateway state, or package names into product code.

## Port Summary

| Source file | Extracted primitive | Sentinel destination | Port decision | Reason | Tests adapted |
| --- | --- | --- | --- | --- | --- |
| `power-files/src/browser/routes/agent.act.ts` | Action taxonomy: click/type/press/hover/select/fill/wait. | `BrowserInteractionIntent`, `BrowserInteractionStep`, `BrowserInteractionDryRunPlanner` | translate_algorithm | The taxonomy is useful, but route execution, profile context, target tabs, hooks, downloads, and evaluate are outside P3G authority. | `test_creates_interaction_plan_from_stable_refs`, `test_wait_and_form_steps_are_dry_run_plans_only` |
| `power-files/src/browser/pw-tools-core.interactions.ts` | Ref-bound action model and wait predicates. | `BrowserInteractionTarget`, `BrowserWaitPredicate`, ref validation against `BrowserAccessibilitySnapshot.refs` | translate_algorithm | Sentinel keeps the ref semantics and rejects stale/missing refs, without calling Playwright. | `test_rejects_unknown_ref_target`, `test_rejects_stale_snapshot_or_page_hash` |
| `power-files/src/agents/tools/browser-tool.schema.ts` | Flattened browser tool schema and act discriminator pattern. | Sentinel typed Pydantic models | rewrite_required | Product code needs mission-scoped, hash-bound contracts instead of vendor tool schemas. | `test_rejects_non_delegated_interaction_actions` |
| `power-files/src/browser/server.agent-contract-form-layout-act-commands.test.ts` | Form/layout action cases and negative evaluate behavior. | P3G dry-run tests and FinalGate checks | test_pattern_only | The test corpus is valuable; the live server/action behavior is intentionally not ported. | `test_final_gate_rejects_forged_interaction_plan_hash`, `test_final_gate_rejects_real_browser_interaction_event_during_p3g` |

## Sentinel-Owned Implementation

| Destination | Added capability |
| --- | --- |
| `sentinel/agent/browser/models.py` | Interaction intent, target, impact, wait predicate, step, plan, dry-run proof/result models. |
| `sentinel/agent/browser/interaction_dry_run.py` | Dry-run planner, stable-ref validation, stale hash rejection, non-delegated action rejection, plan hash verification. |
| `sentinel/agent/events.py` | `BROWSER_INTERACTION_PLAN_CREATED`. |
| `sentinel/agent/browser/rendered_snapshot.py` | Snapshot events now expose page hash and ref IDs for downstream plan validation. |
| `sentinel/agent/final_gate.py` | Dry-run plan hash, snapshot binding, ref binding, and no-real-interaction checks. |
| `tests/test_agent_browser_interaction_dry_run.py` | P3G dry-run and FinalGate regression tests. |

## Supported Dry-Run Intents

- `click_plan`
- `type_plan`
- `fill_plan`
- `select_plan`
- `press_plan`
- `hover_plan`
- `wait_for_text_plan`
- `wait_for_selector_plan`
- `wait_for_url_plan`

## Outside P3G Authority

- real click/type/fill/select/press/hover;
- submit/post/send;
- upload/download;
- arbitrary JavaScript/evaluate;
- cookies/storage/session/profile reuse;
- dialog/file chooser hooks;
- browser state mutation.

## Validation

Executed:

```text
pytest sentinel-control/services/sentinel-core/tests/test_agent_browser_interaction_dry_run.py -q
pytest <all test_agent_browser_*.py> -q
pytest sentinel-control/services/sentinel-core/tests -q
python -m compileall sentinel-control/services/sentinel-core/sentinel
execution-boundary primitive scan
product vendor-trace scan
browser action-surface scan
browser doctrine scan
```

Current result:

```text
P3G tests: 13 passed
Browser tests: 69 passed
Full sentinel-core tests: passed
Compileall: passed
Scans: clean
```
