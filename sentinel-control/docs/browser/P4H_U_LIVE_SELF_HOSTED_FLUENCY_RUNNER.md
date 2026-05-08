# P4H-U Live Self-Hosted Browser Fluency Runner

Date: 2026-04-30
Status: Complete

## Goal

P4H-U converts the P4H-T contract-ready result into repeated self-hosted
runtime evidence.

This gate does not add browser powers and does not execute OpenClaw or any peer
runtime. It runs Sentinel-owned browser fluency missions against a disposable
local HTTP fixture server.

## Runner

Implementation:

```text
agent-lab/benchmarks/browser_tasks/browser_fluency_live_runner.py
```

Outputs:

```text
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_live_results.jsonl
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_live_scorecard.json
agent-lab/benchmarks/browser_tasks/reports/browser_fluency_live_scorecard.md
```

## Live Fixture Surfaces

The runner starts a self-hosted HTTP fixture on loopback and exercises:

```text
open/close lifecycle
allowed URL navigation
readable extraction
OCR-stub visual fixture
safe local form submit
redacted cookie/storage summary
download quarantine hash preservation
HAR/body redaction
two-tab comparison
research citation
prompt-injection detection
repair signal from network failure
```

## Representative Mission Slice

P4H-U executes one mission per Browser Fluency group:

| Group | Mission | Capability |
| --- | --- | --- |
| `life` | `BF-LIFE-001` | `open_close_context` |
| `nav` | `BF-NAV-001` | `allowed_url_navigation` |
| `perc` | `BF-PERC-001` | `readable_extraction` |
| `vis` | `BF-VIS-004` | `image_ocr` |
| `form` | `BF-FORM-004` | `safe_form_submit` |
| `state` | `BF-STATE-002` | `redacted_storage_summary` |
| `file` | `BF-FILE-001` | `download_quarantine` |
| `net` | `BF-NET-002` | `har_redaction` |
| `tab` | `BF-TAB-001` | `multi_tab_compare` |
| `res` | `BF-RES-001` | `simple_fact_citation` |
| `safe` | `BF-SAFE-001` | `prompt_injection_detection` |
| `cog` | `BF-COG-001` | `repair_loop_signal` |

## Safety Boundaries

```text
no external account
no real credential
no host browser profile
no OpenClaw/vendor runtime import
no Docker/Podman dependency
no raw cookie/HAR/credential payload in reports
```

## Important Limitation

This is live local fixture proof, not open-web proof.

It proves the harness can operate real local pages and preserve proof/authority
rules repeatedly. It does not prove broad website compatibility or external peer
supremacy.
