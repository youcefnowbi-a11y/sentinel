# Sentinel Agent Loop Spec

Date: 2026-04-26
Status: G10 architecture spec

## Loop

```text
see -> verify -> research -> debate -> decide -> plan -> simulate -> approve -> execute_safe -> trace -> learn
```

## State Machine

| State | Input | Output | Required Guard |
|---|---|---|---|
| `see` | idea, CueIdea report, user constraints | context bundle | no execution |
| `verify` | context bundle | evidence items and gaps | source and trust labels required |
| `research` | evidence and gaps | enrichment result | weak evidence remains weak |
| `debate` | evidence and enrichment | agent challenges | at least one skeptical challenge |
| `decide` | debate output | decision plan | WTP/build gates enforced |
| `plan` | decision plan | proposed actions | actions persisted before execution |
| `simulate` | actions | dry-run previews | policy and risk score required |
| `approve` | dry-runs | approval or denial | medium+ requires explicit approval |
| `execute_safe` | approved low/safe actions | files, drafts, exports | path and tool policy enforced |
| `trace` | every prior state | trace records | mandatory |
| `learn` | outcomes and feedback | improvement proposals | no auto-mutation |

## Run Modes

| Mode | Trigger | Decision Behavior |
|---|---|---|
| `quick` | shallow run | fewer model calls, no fake certainty |
| `standard` | default | full evidence/debate/pack flow |
| `deep` | user chooses depth | budget preview required |
| `sandbox_hypothesis` | no evidence source | cannot mark ready/build |
| `evidence_backed` | CueIdea or cited research | can produce stronger verdict if gates pass |

## Budget Rules

Every run has:

- max model calls;
- max tool proposals;
- max generated assets;
- max spend;
- max research depth;
- max subagent count;
- max evidence sources.

Budget exhaustion:

- stops research;
- traces the stop reason;
- produces evidence gaps;
- never upgrades confidence.

## Permission Rules

- The loop can propose actions.
- Only executors execute actions.
- Executors only run after Firewall approval.
- Unknown actions are blocked.
- Subagents inherit lower or equal permissions.
- Prompt instructions cannot grant permission.

## Pseudocode

```text
run(input):
  context = see(input)
  evidence = verify(context)
  enrichment = research(evidence)
  debate = debate(evidence, enrichment)
  decision = decide(debate)
  actions = plan(decision)
  dry_runs = simulate(actions)
  approvals = approve(dry_runs)
  outputs = execute_safe(approvals)
  trace(all_events)
  proposals = learn(outputs, feedback)
  return pack(decision, outputs, proposals)
```

## Hard Gates

- Missing WTP blocks `build` and `ready`.
- Vague ICP blocks `ready`.
- Missing competitor alternative/gap creates `Evidence gap`.
- External communication is draft-only.
- High/critical action is blocked in v1.
- No generated asset can omit evidence refs or explicit gap.

## Required Evals

- Missing WTP blocks ready.
- Weak evidence produces `research_more`.
- Unknown tool blocked.
- Dry-run hash changes invalidate approval.
- Budget exhaustion stops run.
- Every state writes trace.
- Subagent cannot bypass Firewall.
