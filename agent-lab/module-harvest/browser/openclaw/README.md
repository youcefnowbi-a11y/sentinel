# OpenClaw Browser Harvest

Date: 2026-04-28
Status: isolated static harvest started

This folder is a research workspace only. Nothing here is product code and
nothing here is integrated into `sentinel-control`.

## Rule

```text
study -> classify -> extract patterns -> rewrite Sentinel-native -> test -> integrate later
```

Do not copy a live browser runtime into Sentinel. Do not run the vendor browser
runtime from this folder. Do not install dependencies for this harvest without a
separate approval step.

## Local Source Root

```text
agent-lab/vendors/openclaw/source/
```

The local source is present, so the first harvest pass uses local files. GitHub
is only needed if this local snapshot is incomplete or stale.

## Current Artifacts

| File | Purpose |
| --- | --- |
| `OPENCLAW_BROWSER_HARVEST_PROTOCOL.md` | Static-analysis rules and review sequence. |
| `OPENCLAW_BROWSER_INITIAL_SOURCE_MAP.md` | First browser-related source map from local files. |
| `OPENCLAW_BROWSER_ENTRYPOINTS.md` | Browser server, route, and action entrypoint forensic map. |
| `OPENCLAW_BROWSER_DEPENDENCIES.md` | Runtime dependencies and lifecycle coupling map. |
| `OPENCLAW_BROWSER_SECURITY_MAP.md` | Guard patterns, high-risk surfaces, Sentinel requirements. |
| `OPENCLAW_BROWSER_TEST_MAP.md` | Tests worth adapting into Sentinel evals and negative checks. |
| `OPENCLAW_BROWSER_EXTRACTION_MATRIX_DRAFT.md` | Initial classify/reuse/rewrite/reject matrix. |
| `SENTINEL_BROWSER_CAPABILITY_CONTRACT_DRAFT.md` | Sentinel-native read-only browser contract draft. |
| `SENTINEL_BROWSER_FAKE_EVAL_PLAN.md` | Required fake evals before implementation. |
| `OPENCLAW_BROWSER_FORENSIC_VERDICT.md` | Pass 1 technical decision and next code target. |
| `SENTINEL_BROWSER_V1_OPENCLAW_GAP_ANALYSIS.md` | Strict comparison between certified Sentinel Browser V1 and local OpenClaw browser source. |
| `P3C_OPENCLAW_PORT_MAP.md` | Harvest-driven guard hardening map for DNS/redirect/MIME/size primitives. |
| `OPENCLAW_BROWSER_POWER_FILES_MAP.md` | Quarantined browser power-file classification. |
| `P3D_OPENCLAW_EXTRACTION_PORT_MAP.md` | Extraction-quality port map and decisions. |
| `P3D_EXTRACTION_PORT_PLAN.md` | Sentinel-native P3D implementation plan. |
| `P3E_OPENCLAW_SNAPSHOT_PORT_MAP.md` | Snapshot/ARIA/refs/screenshot metadata port map. |
| `P3E_SNAPSHOT_PORT_PLAN.md` | Snapshot/ARIA/refs next-phase plan. |
| `P3F_OBSERVABILITY_PORT_PLAN.md` | Network/console/page-error observability plan. |
| `BROWSER_SUPREMACY_ROADMAP.md` | Browser-only sequence before another organ. |

## Product Boundary

The final product must not mention this source or keep vendor identity in code,
docs, package names, runtime logs, tool ids, or user-facing artifacts.

Vendor names are allowed only in `agent-lab` research artifacts while the harvest
is active.
