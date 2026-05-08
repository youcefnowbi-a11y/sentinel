# Browser-Cortex Integration Report

Date: 2026-04-29
Status: P3X implemented

## Direct Verdict

Browser V2 is now connected to the cortex as a reasoning input. The browser
does not create authority and does not execute new powers. It emits evidence
signals that the brain can use for confidence, hypothesis updates, repair
pressure, and action recommendations.

The integration is deterministic:

```text
browser trace events
-> BrowserEvidenceInterpreter
-> source confidence
-> hypothesis deltas
-> repair signals
-> action recommendations
-> browser-cortex evidence chain
```

## Implemented Contract

Code:

```text
sentinel/agent/browser/cortex.py
```

Runtime connection:

```text
AgentRuntime execution phase
-> BrowserControlledCapabilityRunner
-> BrowserEvidenceInterpreter
-> EvidenceChain(BROWSER_CORTEX_INTERPRETATION)
-> RepairLoop input via ReviewFinding
```

New trace event:

```text
BROWSER_CORTEX_INTERPRETED
```

New evidence chain type:

```text
BROWSER_CORTEX_INTERPRETATION
```

New evidence source type:

```text
BROWSER_OUTPUT
```

## What Changed

Before P3X, browser output was proven and stored. After P3X, browser output is
interpreted:

- high-confidence browser output can confirm linked hypotheses;
- weak/noisy output weakens confidence or requests an alternative source;
- prompt-injection-like content is treated as evidence-only and confidence
  limited;
- rejected browser output becomes repair pressure;
- limited interaction execution can become mission progress evidence;
- every interpretation creates a replayable evidence chain.

## What Did Not Change

P3X does not add:

- private sessions;
- login;
- cookies or storage;
- uploads or downloads;
- arbitrary JavaScript;
- remote browser nodes;
- new browser actions;
- authority created by page text, source text, or LLM output.

## Cortex Rule

Browser evidence may influence reasoning. Browser evidence may never become
authority.

## P3Y Follow-Up

P3Y defines how the LLM sees browser evidence through ContextPack and how LLM
tool intents compile back into existing browser contracts.
