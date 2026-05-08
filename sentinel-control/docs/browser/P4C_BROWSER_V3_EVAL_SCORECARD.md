# P4C Browser V3 Eval Scorecard

Date: 2026-04-29
Status: Completed through P4C-S

## Tests Added During P4C

- missing authority rejection for P4B-4 through P4B-8;
- forged cookie/storage, JS, and HAR/body FinalGate rejection;
- compiler rejection of raw credential, raw cookie/storage, and raw HAR/body
  payload fields.
- P4C-H.3 local live-adapter harness tests for private session, login,
  cookie/storage, JS no-network, HAR/body redaction, exception redaction, and
  10-run EvalBench stability.
- P4C-S measured corpus test for nine Browser V3 mission groups with repeated
  EvalBench runs and stable signatures.

## Required Validation Matrix

| Category | Status |
| --- | --- |
| P4B-1 form submit targeted tests | Pass |
| P4B-2 download quarantine targeted tests | Pass |
| P4B-3 upload authorized targeted tests | Pass |
| P4B-4..8 remaining authorities tests | Pass |
| P4C-H.3 live adapter harness tests | Pass |
| P4C-S measured supremacy gate tests | Pass |
| P3Y compiler regression tests | Pass |
| Full sentinel-core tests | Pass |
| Compileall | Pass |
| Product vendor-trace scan | Pass |
| Execution-boundary scan | Pass |
| Doctrine wording scan | Pass |

## Review Scores

| Metric | Score | Notes |
| --- | ---: | --- |
| Mission success on targeted V3 pytest | 100% | 41 targeted P4B/P4C/compiler tests passed |
| Trace quality | 91% | events and receipts are structured |
| Source/proof quality | 90% | artifacts and hashes exist for class outputs |
| Interaction correctness | 88% | class tests plus local live-adapter multi-step flow |
| Cross-class denial | 88% | independent grants and missing-authority tests |
| Side-effect containment | 91% | quarantine/redaction/no-network contracts plus live harness proof |
| Live adapter proof | local fixture-bound | P4C-H.3 proves private/login/cookie/JS/HAR paths through Playwright-backed fixtures |
| Multi-run stability | measured for Browser V3 live harness | P4C-H.3 runs Browser V3 live harness case for 10 stable iterations |
| P4C-S measured corpus | 100% local measured pass | 9 mission groups, repeated runs, no unstable iterations in targeted test |

## Validation Commands

```text
pytest tests/test_agent_browser_v3_remaining_authorities.py tests/test_agent_browser_v3_upload_authorized.py tests/test_agent_browser_v3_download_quarantine.py tests/test_agent_browser_v3_form_submit.py tests/test_agent_llm_tool_intent_compiler.py -q
pytest tests/test_agent_browser_v3_live_adapter_harness.py tests/test_agent_browser_v3_fixture_bench.py tests/test_agent_browser_v3_remaining_authorities.py tests/test_agent_eval_bench.py -q
pytest tests/test_agent_browser_v3_measured_supremacy.py -q
python -m compileall sentinel
pytest tests -q
rg product vendor-trace scan
rg execution-boundary scan
rg doctrine wording scan
```

All commands passed.

## Eval Verdict

P4C targeted tests are enough to lock architecture. P4C-H.1 adds the statistical
surface needed for multi-run scoring. P4C-H.2 adds the first Browser V3
multi-run fixture case. P4C-H.3 adds local live-adapter proof with 10-run
stability. P4C-S adds the local measured corpus and produces the first measured
Browser V3 readiness verdict. External open-web benchmark supremacy remains a
separate claim.
