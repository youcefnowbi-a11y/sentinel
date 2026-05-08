# Browser-Cortex Eval Missions

Date: 2026-04-29
Status: P3X initial evals implemented

## Implemented Tests

```text
tests/test_agent_browser_cortex.py
```

Current P3X tests verify:

- high-confidence browser evidence confirms a linked hypothesis;
- browser-cortex interpretation emits trace and evidence chain;
- prompt-injection-like page text is confidence-limited;
- prompt flags create evidence-only review finding;
- rejected browser output recommends alternative source search;
- AgentRuntime interprets browser output into a browser-cortex evidence chain.

## Required Mission Evals Before Browser 2.5/V3

1. Browser validates competitor pricing.
2. Browser finds contradiction against initial evidence.
3. Browser detects weak/noisy source and searches alternative source.
4. Browser result changes a GTM hypothesis confidence.
5. Browser result triggers bounded repair.
6. Browser limited interaction changes mission progress.
7. Browser output is consumed by LLM ContextPack without authority leakage.
8. Forged browser evidence remains rejected by FinalGate.

## Success Criteria

Browser-cortex evals pass only when browser output influences reasoning through
explicit contracts and never creates authority.
