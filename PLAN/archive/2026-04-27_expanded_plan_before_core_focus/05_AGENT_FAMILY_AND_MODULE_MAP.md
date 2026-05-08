# 05 Agent Family And Module Map

Date: 2026-04-26

## 1. Thesis

Sentinel should grow into an agent family, not one huge hardcoded agent.

The common kernel:

```text
Mission OS + Tool Intelligence + Work Methods + Security Protocol + Trace
```

Each agent is a mission type with capability packs.

## 2. Agent Family

| Agent | Mission Type | Core Promise | Required Capability Packs |
| --- | --- | --- | --- |
| Launch Agent | `launch` | Turn an idea into a launch-ready business package | GTM, brand, media, web research, assets |
| GTM Agent | `gtm` | Convert evidence into first-customer plan | CueIdea, research, drafts, watchlist |
| Research Agent | `deep_research` | Verify claims and map opportunity | browser read-only, source ranker, contradiction mining |
| Brand Agent | `brand_studio` | Create brand identity and launch narrative | image generation, design analysis, copy |
| Media Agent | `media_studio` | Transform image/video/audio into assets | OCR, image edit, video edit, transcription |
| Code Agent | `code_patch_proposal` | Understand code and propose safe changes | repo reader, test sandbox, patch proposal |
| Browser Agent | `browser_research` | See and extract public web evidence | browser sandbox, OCR, page extraction |
| Sales Agent | `controlled_sales` | Prepare and later send compliant outreach | contact proof, email draft/send gates, CRM |
| Ops Agent | `ops_workspace` | Build operational docs and trackers | file exporter, tables, dashboards |
| Tool Scout Agent | `tool_scout` | Discover and benchmark useful tools/APIs | API cartographer, ToolBench |
| Self-Improvement Agent | `improvement_proposal` | Turn failures into patch proposals | trace reader, eval generator, diff proposal |
| Sidecar Agent | `permissioned_sidecar` | Operate local machine with explicit authority | fake sidecar, sanitizer, approval |

## 3. Target Repository Shape

This is not a command to create all files now. It is the target map.

```text
sentinel-control/
  apps/
    web/
      app/
        dashboard/
          missions/
          tools/
          capabilities/
          artifacts/
          reviews/
          escalations/
          traces/
          media/
          code/
  services/
    sentinel-core/
      sentinel/
        mission/
          authority.py
          runner.py
          planner.py
          registry.py
          scope_checker.py
          risk.py
          budget.py
          escalation.py
          kill_switch.py
          trace_timeline.py
          artifacts.py
          reviewer.py
          success.py
        missions/
          gtm/
          launch/
          research/
          brand/
          media/
          browser/
          code/
          sales/
          ops/
          tool_scout/
          self_improvement/
          sidecar/
        capabilities/
          manifests/
          registry.py
          policies.py
          scanner.py
          fake_harness.py
          tool_router.py
        tools/
          api_cartographer/
          tool_bench/
          tool_graph/
          web_search/
          browser_sandbox/
          ocr/
          vision/
          image_generation/
          image_editing/
          video_generation/
          video_editing/
          audio_transcription/
          repo_reader/
          patch_proposal/
          email_drafts/
          crm/
          sidecar_rpc/
        methods/
          registry.py
          evidence_ladder.py
          contradiction_mining.py
          red_blue_team.py
          bayesian_update.py
          premortem.py
          causal_map.py
          roi_tree.py
          opportunity_arbitrage.py
          systems_decomposition.py
        evidence/
          ledger.py
          verifier.py
          source_ranker.py
          citation_extractor.py
          cueidea_bridge.py
        memory/
          project_memory.py
          preference_memory.py
          outcome_memory.py
          poisoning_guard.py
        creation/
          brand_kit.py
          landing_assets.py
          social_assets.py
          pitch_deck.py
        security/
          policy_engine.py
          prompt_injection.py
          secret_filter.py
          path_policy.py
          network_policy.py
          outbound_policy.py
        evals/
          fake_browser/
          fake_email/
          fake_sidecar/
          fake_tool_catalog/
          prompt_injection/
          evidence_quality/
          media_quality/
          code_patch_safety/
  packages/
    prompts/
    shared-types/
    evals/
    tool-catalogs/
  data/
    generated_projects/
    traces/
    tool_registry/
    tool_bench/
    evidence_cache/
    media_cache/
    memory/
```

## 4. Module Responsibility Law

Generic kernel must never know mission-specific business filenames.

Good:

```text
MissionRunner calls registered planner.
GTM planner decides GTM artifact list.
Brand planner decides brand artifact list.
Code planner decides patch artifact list.
```

Bad:

```text
MissionRunner has if mission == gtm then write 05_OUTREACH_MESSAGES.md.
```

## 5. Thousands Of Files, But With Discipline

The final agent may eventually require hundreds or thousands of files because it has many capability packs.

But file count is not the goal.

The real goal is stable boundaries:

- core mission kernel;
- capability packs;
- tool intelligence;
- work methods;
- mission-specific agents;
- evaluators;
- security policies;
- UI surfaces.

Large codebase without these boundaries becomes noise.
