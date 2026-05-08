# P4C Browser V3 OpenClaw Comparison

Date: 2026-04-29
Status: Completed through P4C-S

## Comparison Rule

This document compares capability direction and architecture. It does not import
vendor runtime code and does not claim external live benchmark victory.

## Scorecard

| Axis | OpenClaw-style browser strength | Sentinel Browser V3 | Sentinel score |
| --- | --- | --- | ---: |
| Raw browser automation surface | broad | broad as authority classes with local live-adapter proof for sensitive classes | 82% |
| Public evidence and citations | useful | proof-bound with receipts and FinalGate | 94% |
| URL/redirect/SSRF guard | mature | Sentinel-native guard and connection proof | 95% |
| Snapshot/refs | strong browser runtime | stable refs + P4A UIObservation + CDP/DOM plan | 88% |
| Network diagnostics | strong | ledger + HAR/body authority class with live redaction proof | 89% |
| LLM-to-browser boundary | tool execution oriented | ContextPack + ToolIntentCompiler + provenance binding | 93% |
| Form submit | available | governed and certifiable | 84% |
| Download/upload | available | quarantine/artifact-authorized | 82% |
| Private/login/cookie | available | authority contracts plus local live adapter lifecycle/redaction proof | 82% |
| JS evaluate | broad | hash-allowlisted sandboxed contract with runtime no-network observation | 84% |
| Eval realism | project-dependent | targeted tests plus fixture, local live-adapter proof, and P4C-S measured corpus | 78% |
| Governance/proof superiority | limited | strong | 96% |

## Honest Verdict

Sentinel is ahead on governance, proof, authority, receipts, and LLM boundary.
P4C-H.3 removes the biggest local proof gap for P4B-4 through P4B-8 by exercising
private session, login, cookie/storage, JS no-network, and HAR/body redaction
through a Playwright-backed local harness.

P4C-S now adds a broader local measured corpus with repeated cross-class
missions. It is still not proven ahead on external raw live browser breadth.
That requires a live public benchmark corpus.

## Path to Surpass

1. Expand from local fixtures to live public target corpus.
2. Run direct peer-browser benchmark missions with repeated runs.
3. Add external fault injection and adversarial pages.
4. Re-run this scorecard with external observed results.
