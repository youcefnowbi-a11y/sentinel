# P4C Browser V3 Code Review

Date: 2026-04-29
Status: Completed

## Code Surfaces Reviewed

| Surface | File |
| --- | --- |
| V3 authority model | `sentinel/agent/browser/v3_authority.py` |
| V3 advanced class executors | `sentinel/agent/browser/v3_advanced_authorities.py` |
| Tool intent compiler | `sentinel/agent/llm/tool_intent_compiler.py` |
| Tool registry catalog | `sentinel/capabilities/static_catalog.py` |
| Controlled runner branches | `sentinel/agent/browser/controlled_runner.py` |
| Event catalog | `sentinel/agent/events.py` |
| FinalGate contracts | `sentinel/agent/final_gate.py` |
| V3 tests | `tests/test_agent_browser_v3_*.py` |

## Code Findings

### Strong

- V3 powers are split into explicit authority classes.
- Each class has accepted/rejected events.
- Each accepted class emits receipt metadata and artifact references where
  required.
- `CoreFinalGate` has a separate contract for every V3 class.
- `ToolIntentCompiler` reuses the existing ToolCallProtocol path instead of
  creating a raw LLM execution lane.

### Fixed During P4C

`ToolIntentCompiler` now rejects sensitive LLM-authored fields:

- `credential_value`, `password`, `secret`, and token-like payloads for login;
- `raw_cookie`, `cookie_value`, and storage value payloads for cookie/storage;
- `raw_body`, `unredacted_body`, and credential body payloads for HAR/body.

### Needs Hardening

- P4B-4 through P4B-8 still rely on injected backend results for many tests.
- JS no-network proof needs adversarial runtime instrumentation, not only
  payload contract checks.
- HAR/body redaction needs fixture-based adversarial payloads with known secrets.
- Private-session destroy proof should be tested against a real browser profile
  directory lifecycle.

## Code Verdict

The code is coherent enough to lock the V3 authority architecture. It is not yet
enough to declare raw live-browser supremacy.
