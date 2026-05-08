# OpenJarvis To Sentinel Rewrite Notes

Date: 2026-04-26
Rule: rewrite, do not integrate.

## What Sentinel Should Learn

- Hardware-aware local routing can reduce cost and improve privacy.
- Reward weights should include accuracy, latency, cost, and efficiency.
- Skills from external ecosystems need import quarantine.
- Learned optimization should be trace-backed and reversible.

## What Sentinel Must Not Copy

- OpenJarvis CLI runtime.
- Skill importers/resolvers.
- Channel integrations.
- Browser or cloud runtime extras.
- Learning auto-write behavior.

## Sentinel CostRouter Rewrite

Source lesson:

- `recommend_engine`, `_available_memory_gb`, `recommend_model`, and `estimated_download_gb` provide a simple hardware-aware routing model (`agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:209-300`).

Sentinel design:

```text
input: run_mode, task_stage, risk_level, evidence_density, budget, latency_target, local_hardware
score candidates:
  quality_score
  cost_score
  latency_score
  privacy_score
  risk_fit_score
hard filters:
  budget cap
  policy-required model class
  data privacy boundary
output: selected route + rationale + fallback + trace
```

## Sentinel Skill Import Rewrite

Source lesson:

- OpenJarvis imports skills from Hermes/OpenClaw/GitHub and gates scripts with `with_scripts` (`agent-lab/vendors/openjarvis/source/src/openjarvis/cli/skill_cmd.py:162-245`; `skills/importer.py:128-135`).

Sentinel design:

- Import request creates a scan job only.
- No skill appears in the agent prompt until scan passes.
- Scripts are always quarantined.
- User sees permission diff and risk class.
- Scan report is hashed and stored.

## Sentinel Learning Rewrite

Source lesson:

- `AgentConfigEvolver` writes TOML configs from trace scoring (`agent-lab/vendors/openjarvis/source/src/openjarvis/learning/agents/agent_evolver.py:193-223`).

Sentinel design:

- `LearningObservation`.
- `ImprovementProposal`.
- `PatchSuggestion`.
- `TestsRequired`.
- Manual approval.

## Required Evals

- Cost budget cap.
- Wrong route fallback.
- Unscanned skill import blocked.
- Learning proposal cannot apply itself.
- Secret scanner hard-blocks high-risk exfil.
