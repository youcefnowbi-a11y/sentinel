# P4D OpenClaw Browser Forensic Research

Date: 2026-04-29
Status: Complete

## Boundary

OpenClaw is a source specimen only.

No OpenClaw runtime is imported into Sentinel product code.

This review asks why the OpenClaw-style browser is strong and how Sentinel
should evaluate against that strength.

## Local Specimens Reviewed

Key quarantined specimens:

- `agent-lab/module-harvest/browser/openclaw/power-files/src/browser/routes/agent.act.ts`;
- `agent-lab/module-harvest/browser/openclaw/power-files/src/browser/pw-tools-core.interactions.ts`;
- `agent-lab/module-harvest/browser/openclaw/power-files/src/browser/pw-tools-core.snapshot.ts`;
- `agent-lab/module-harvest/browser/openclaw/power-files/src/browser/pw-session.ts`;
- `agent-lab/module-harvest/browser/openclaw/power-files/src/browser/pw-role-snapshot.ts`;
- `agent-lab/module-harvest/browser/openclaw/power-files/src/agents/tools/browser-tool.schema.ts`;
- `OPENCLAW_BROWSER_POWER_FILES_MAP.md`;
- `OPENCLAW_BROWSER_FORENSIC_VERDICT.md`.

## Why Its Browser Is Strong

The OpenClaw-style browser is strong because it combines a broad browser runtime
surface with mature Playwright/CDP primitives:

- action route for real browser operations;
- click/type/fill/select/hover/drag/press/wait;
- element and page screenshots;
- PDF generation;
- file chooser and upload hooks;
- download wait and download save routes;
- response body extraction;
- role refs cached in session state;
- CDP accessibility tree capture;
- session/page/target lifecycle helpers;
- trace, response, and debug routes;
- broad browser tool schema.

The key point: it is not just "click support". It is an integrated browser
runtime with page targeting, ref cache, session state, action taxonomy, and
debug/trace surfaces.

## What Sentinel Already Matches Or Exceeds

| Axis | Sentinel status |
| --- | --- |
| URL/public guard | Stronger through mission authority and FinalGate. |
| Evidence receipts | Stronger through artifact/receipt/certification chain. |
| LLM boundary | Stronger through ContextPack and ToolIntentCompiler. |
| V3 authority classes | Stronger governance; local runtime proof exists. |
| Redaction and quarantine | Stronger by design. |
| Forged-output rejection | Stronger by FinalGate contracts. |

## Where OpenClaw-Style Runtime Still Teaches Sentinel

| Area | Why it matters |
| --- | --- |
| session/page target lifecycle | Long-running browser tasks depend on resilient target management. |
| role ref cache | Mature automation needs ref reuse and invalidation discipline. |
| action breadth | Real sites require hover, drag, press, scroll, wait, submit, upload, download, dialogs. |
| response body tooling | Debugging and evidence sometimes need bounded body access. |
| trace/debug routes | Large browser failures need forensic replay and diagnosis. |

## Sentinel Gap Table

| Capability | Sentinel V3 state | Remaining proof needed |
| --- | --- | --- |
| public evidence and snapshots | strong | external corpus |
| interaction and form submit | locally measured | varied live form tasks |
| download/upload | authority-class local proof | real MIME/path/artifact corpus |
| private session/login | local harness proof | external sandbox accounts and crash cleanup |
| cookie/storage | redacted local proof | adversarial storage corpus |
| sandboxed JS | allowlist/no-network local proof | adversarial network-attempt corpus |
| HAR/body | bounded/redacted local proof | larger redaction corpus |
| raw runtime breadth | good but not externally benchmarked | peer benchmark |

## Forensic Verdict

OpenClaw-style browser strength comes from runtime breadth and mature
Playwright/CDP ergonomics.

Sentinel strength comes from governed authority, evidence, receipts, compiler
boundaries, and FinalGate.

To claim superiority, Sentinel must prove both:

```text
runtime breadth comparable to OpenClaw-style agents
governance/proof stronger than OpenClaw-style agents
```

P4D finds the second claim strong and the first claim still pending external
benchmark proof.
