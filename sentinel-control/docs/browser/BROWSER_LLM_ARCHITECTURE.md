# Browser LLM Architecture

Date: 2026-04-29
Status: P3Y implemented

## Architecture

```text
Browser V2 events / P3X cortex interpretation
-> ContextPackAssembler
-> ContextPackValidator
-> BrowserPlannerRole draft
-> ToolIntentCompiler
-> ToolRegistry / MissionAuthority
-> governed browser module
-> receipt / post-state proof
-> BrowserVerifierRole draft
-> FinalGate
```

## Roles

| Role | Can Do | Cannot Do |
| --- | --- | --- |
| Browser module | Capture public evidence, refs, diagnostics, receipts. | Create authority or speak for the user. |
| ContextPack | Carry compact proof-linked state to LLM. | Embed raw browser content as trusted instruction. |
| BrowserPlannerRole | Draft JSON intent from a validated pack. | Execute tools or invent refs. |
| ToolIntentCompiler | Canonicalize, check authority, bind refs, reject invalid draft. | Expand mission authority. |
| BrowserVerifierRole | Critique grounding and receipt shape. | Certify success alone. |
| FinalGate | Certify trace and contract integrity. | Replace module-specific receipts. |

## P3Y Boundary

P3Y does not add:

- CDP-native accessibility tree;
- DOMSnapshot;
- private sessions;
- cookies or storage;
- login;
- upload/download;
- form submit;
- arbitrary JavaScript;
- remote browser execution.

Those remain Browser 2.5/V3 authority classes.
