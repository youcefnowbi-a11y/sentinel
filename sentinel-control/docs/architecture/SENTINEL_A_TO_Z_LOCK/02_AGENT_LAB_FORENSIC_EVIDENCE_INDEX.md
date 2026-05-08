# Agent Lab Forensic Evidence Index

## Primary Local Evidence

Use these files as the official forensic source before building organs:

```text
agent-lab/audits/final/g9_cross_agent_synthesis.md
agent-lab/audits/SUPERPOWER_EXTRACTION_TABLE.md
agent-lab/audits/AGENT_COMPARISON_MATRIX.md
agent-lab/audits/SENTINEL_RUNTIME_CAPABILITY_ROADMAP.md
agent-lab/audits/SENTINEL_SUPER_AGENT_BLUEPRINT.md
agent-lab/audits/final/openclaw_final_forensic_report.md
agent-lab/audits/final/hermes_final_forensic_report.md
agent-lab/audits/final/openjarvis_final_forensic_report.md
agent-lab/audits/final/jarvis_final_forensic_report.md
```

## Evidence Rules

```text
Source-backed finding = may guide architecture.
Synthesis inference = may guide design direction, not runtime proof.
Runtime-unverified vendor behavior = cannot be claimed as live capability.
Vendor code = never copied into Sentinel.
Vendor runtime = never bridged into Sentinel by default.
```

## Forensic Sources By Power Family

| Power family | Main sources | Sentinel use |
| --- | --- | --- |
| Gateway/action kernel | OpenClaw final report, G9 synthesis | Organ contracts and action routing |
| Memory/skills/hooks | Hermes final report, extraction table | Non-authoritative memory and scanned skills |
| Cost/model routing | OpenJarvis final report | Budget-aware Brain and organ routing |
| Sidecar/desktop/approval | JARVIS final report | Future permissioned sidecar and approval lifecycle |
| Finance workflows | Anthropic financial-services repo | Procedure graph and finance evaluation |
| Browser reliability/stealth | CloakBrowser repo | Controlled browser power classification |

