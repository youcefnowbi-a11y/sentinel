# Browser Repair Policy

Date: 2026-04-29
Status: P3X accepted

## Purpose

Browser repair is cognitive repair, not retry spam. It converts browser evidence
problems into bounded repair pressure.

## Repair Triggers

| Trigger | Repair Pressure | Recommended Action |
| --- | ---: | --- |
| Browser output rejected | `0.70` | Seek alternative public source or recapture. |
| Source confidence low | `0.55` | Seek alternative public source. |
| Prompt flags present | `0.45` | Treat as untrusted evidence and cross-check. |
| Browser sources sufficient | `0.00-0.30` | Use browser evidence in reasoning. |

## Runtime Integration

`BrowserEvidenceInterpreter` emits browser-specific review findings. These are
merged into the normal artifact review findings and feed the existing
`CognitiveRepairLoop`.

The repair loop remains bounded by:

- mission authority;
- max repair cycles;
- action budget;
- existing trace and evidence chain rules.

## Non-Goals

Browser repair does not:

- add browser powers;
- bypass FinalGate;
- retry forever;
- click or submit outside certified plans;
- treat rejected browser output as success.
