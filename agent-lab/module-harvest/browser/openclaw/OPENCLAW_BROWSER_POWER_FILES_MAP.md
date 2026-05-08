# OpenClaw Browser Power Files Map

Date: 2026-04-28
Status: lab quarantine created

This file tracks browser power files copied into:

```text
agent-lab/module-harvest/browser/openclaw/power-files/
```

These files are source specimens only. They are not product code and must never
be imported directly into `sentinel-control`.

## Classification Rules

| Classification | Meaning |
| --- | --- |
| `copy_pattern` | File contains a pattern that can be mirrored conceptually, not copied into product. |
| `translate_algorithm` | Algorithm is useful and should be rewritten Sentinel-native. |
| `rewrite_required` | Capability is useful, but runtime coupling requires a new implementation. |
| `test_pattern_only` | Keep edge cases and assertions, not implementation. |
| `reject_runtime` | Too coupled or too powerful for current browser phase. |

## Power File Matrix

| Source path | Classification | Strong primitive | Sentinel destination | Phase | Risk |
| --- | --- | --- | --- | --- | --- |
| `src/agents/tools/web-fetch-utils.ts` | `translate_algorithm` | HTML-to-text fallback, readability fallback, truncation proof. | `sentinel/agent/browser/extraction.py` | P3D | Low |
| `src/security/external-content.ts` | `translate_algorithm` | Suspicious prompt patterns, untrusted content boundary concept, marker sanitization. | `evidence_adapter.py`, future prompt wrapper | P3D | Low |
| `src/agents/tools/web-tools.readability.test.ts` | `test_pattern_only` | Article extraction avoids nav/footer noise. | `test_agent_browser_extraction.py` | P3D | Low |
| `src/agents/tools/web-tools.fetch.test.ts` | `test_pattern_only` | Wrapping, truncation, fallback, error body sanitization cases. | `test_agent_browser_extraction.py` | P3D | Low |
| `src/browser/pw-tools-core.snapshot.ts` | `rewrite_required` | Snapshot assembly and page-state capture. | Future `browser/snapshot.py` | P3E | Medium |
| `src/browser/pw-role-snapshot.ts` | `translate_algorithm` | ARIA/role snapshot and stable references. | Future `browser/accessibility_snapshot.py` | P3E | Medium |
| `src/gateway/protocol/schema/snapshot.ts` | `copy_pattern` | Snapshot schema shape. | Future Sentinel schema | P3E | Low |
| `src/browser/pw-role-snapshot.test.ts` | `test_pattern_only` | Role/ref regression cases. | Future tests | P3E | Low |
| `src/browser/pw-session.ts` | `rewrite_required` | Session health, page lifecycle, browser context shape. | Future observability module only | P3F | High |
| `src/browser/pw-tools-core.responses.ts` | `translate_algorithm` | Response status ledger. | Future `browser/network_ledger.py` | P3F | Medium |
| `src/browser/pw-tools-core.trace.ts` | `translate_algorithm` | Trace assembly and browser diagnostics. | Future `browser/network_ledger.py` | P3F | Medium |
| `src/browser/routes/agent.debug.ts` | `test_pattern_only` | Debug surfaces and health inspection ideas. | Future tests/docs only | P3F | Medium |
| `src/browser/screenshot.ts` | `translate_algorithm` | Screenshot size/type normalization. | Future `browser/screenshot_normalizer.py` | P3E | Medium |
| `src/browser/screenshot.test.ts` | `test_pattern_only` | Size/format regression cases. | Future screenshot tests | P3E | Low |
| `src/browser/routes/agent.act.ts` | `reject_runtime` | Real browser action routing. | Future dry-run taxonomy only | P3G | High |
| `src/browser/pw-tools-core.interactions.ts` | `reject_runtime` | Click/type/fill/select execution. | Future dry-run plan generator | P3G | High |
| `src/agents/tools/browser-tool.schema.ts` | `copy_pattern` | Broad browser action taxonomy. | Future Sentinel action contract | P3G | High |
| `src/browser/server.agent-contract-form-layout-act-commands.test.ts` | `test_pattern_only` | Interaction edge cases. | Future dry-run tests | P3G | Medium |

## Current Product Rule

P3D may only improve extraction quality. It must not add browser interactions,
cookies, storage, login, submit, arbitrary JavaScript, downloads, or private
sessions.
