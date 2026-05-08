# Power Harvest Map

## Rule

Harvest mechanisms, not vendor code.

| Source | Power to harvest | Why it matters | Failure to control | Sentinel rewrite | Target phase |
| --- | --- | --- | --- | --- | --- |
| OpenClaw | Gateway/action kernel, plugin scanner, browser/channel patterns, subagents | Shows how a runtime connects many execution surfaces | Gateway blast radius; shell/browser/channel too close to execution | `ExternalOrganFoundry`, `ActionKernel`, `SkillScanner`, organ contracts | P6A, P6B, P6C |
| Hermes | Persistent memory, skill index, tool hooks, delegation, context compression | Turns chat into persistent reusable operation | Memory as hidden policy; unscanned skills; fail-open hooks | Non-authoritative memory, scanned skills, fail-closed hook chain | P7, P8 |
| OpenJarvis | Cost router, query complexity, hardware/model routing, telemetry | Makes cost, latency, model fit, and budget first-class controls | Unsafe acceleration; learned config mutation; remote skill import | `CostRouter`, `BrainBudgetRouter`, proposal-only learning | P7, P9 |
| JARVIS | Authority engine, approval lifecycle, sidecar, desktop awareness, workflows | Shows machine-operation and approval patterns | Host overreach; clipboard/screenshot leakage; weak sidecar boundaries | Permissioned sidecar, screen sanitizer, workflow firewall | P6J, P9 |
| Financial Services repo | Domain agents, skills, commands, connectors, cookbooks | Gives Sentinel finance/operator procedure maps | Investment advice, transaction execution, blind recommendations | `FinancialProcedureGraph`, `CapitalAnalysisBench`, human review gates | P6G, P7, P8 |
| CloakBrowser | Fingerprint-consistent browser runtime, profile continuity, humanized interaction, detection tests | Browser reliability on real sites can become major operator power | Misuse objectives, out-of-authority stealth, fake identity, unlawful evasion | `BrowserPowerGovernor`, `StealthBrowserSpecialAuthority`, `BrowserDetectionBench` | P6C, P6K, P9 |

## Harvest Pipeline

```text
vendor/source observation
-> extraction matrix
-> Sentinel contract
-> fake eval
-> dry-run
-> sandbox
-> limited execution
-> production-scoped execution
-> continuous OrganBench monitoring
```

