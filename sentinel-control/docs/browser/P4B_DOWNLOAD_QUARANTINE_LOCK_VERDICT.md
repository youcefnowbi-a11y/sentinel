# P4B-2 Download Quarantine Lock Verdict

Date: 2026-04-29
Status: locked

## Implemented

- Browser V3 download quarantine request/result/receipt models.
- ToolRegistry manifest for `browser_download_quarantine`.
- ToolIntentCompiler V3 rules for `browser_download_quarantine`.
- Browser download quarantine executor with public URL policy, MIME/byte gates,
  artifact capture, and `promoted=false` receipt.
- EventBus events for quarantined/rejected download.
- FinalGate V3 download-quarantine contract.
- Targeted tests for accepted, rejected, MIME/size, forged, prompt-injection,
  cross-origin, and raw LLM paths.

## Not Implemented By This Verdict

At the P4B-2 lock point, the following remained non-delegated:

- artifact promotion;
- upload authorized;
- private session;
- login authority;
- cookie/storage contracts;
- sandboxed JS evaluate;
- HAR/body capture;
- payment or credential flows.

## Validation

Lock passed:

- targeted P4B-2 tests pass: `pytest tests/test_agent_browser_v3_download_quarantine.py -q`;
- P4B-1 regression tests pass: `pytest tests/test_agent_browser_v3_form_submit.py -q`;
- ToolIntentCompiler regression tests pass;
- full tests pass: `pytest tests -q`;
- compileall passes: `python -m compileall sentinel`;
- vendor-trace scan is clean;
- execution-boundary scan is clean for non-P4B runtime powers;
- doctrine wording scan is clean.

## Verdict

P4B-2 is locked.

Sentinel now supports `browser_download_quarantine`: a bounded public file
capture into quarantine, with URL policy proof, MIME and byte gates, artifact
hash, receipt, EventBus trace, `promoted=false`, and FinalGate certification.

No artifact promotion, private session, login, cookie/storage contract, JS
evaluation, HAR/body capture, payment, credential flow, or remote browser node
is unlocked by this verdict. Subsequent P4B-3 lock covers upload authorized as a
separate authority class.
