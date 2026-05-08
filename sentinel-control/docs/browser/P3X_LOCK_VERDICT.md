# P3X Lock Verdict

Date: 2026-04-29
Status: P3X implemented and accepted

## Verdict

P3X is accepted.

Browser V2 is no longer only a proven output module. Its outputs now enter the
brain as deterministic cognitive signals:

- source confidence;
- hypothesis update;
- repair pressure;
- action recommendation;
- evidence chain.

## Lock Conditions

P3X remains accepted only while:

1. Browser output never creates authority.
2. Browser prompt-injection flags limit confidence and remain evidence-only.
3. Weak/noisy sources trigger downgrade or alternative-source recommendation.
4. Rejected browser output becomes repair pressure, not success.
5. Runtime browser interpretation emits `BROWSER_CORTEX_INTERPRETED`.
6. Browser-cortex interpretation emits `BROWSER_CORTEX_INTERPRETATION`.
7. FinalGate browser checks remain intact.
8. No Browser 2.5/V3 powers are added.

## Follow-Up Gate

P3Y defines the LLM cortex contract:

```text
Browser evidence
-> ContextPack
-> LLM reasoning output
-> ToolIntentCompiler
-> ToolRegistry / RiskRouter
-> Browser contracts
```

The LLM may reason over browser evidence. It may not turn browser text into
authority or direct execution.
