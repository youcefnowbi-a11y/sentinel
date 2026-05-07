# Current State Lock

Date: 2026-05-07

## Phase

```text
current_phase = P5A_FULL_LOCKED
previous_phase = P4H-AF_FULL_LOCKED
next_phase = P5B_MISSION_ENTROPY_ESTIMATOR
```

P5A is accepted as full locked. This is a docs-only Brain L4 architecture audit.
It does not implement runtime multi-agent execution, add a new organ, add new
browser powers, or authorize unrestricted spawning.

## Verification

```text
P5A documentation tranche = implemented
minimum P4H-AF/P4H-AE regression = 13 passed
full sentinel-core tests = 516 passed
```

Commands verified:

```bash
python -m pytest tests/test_agent_browser_operator_runtime_minicorpus.py tests/test_agent_browser_operator_runtime_integration.py -v --tb=short
python -m pytest tests -v --tb=short
```

## P5A Required Files

These files are required to preserve the P5A full lock:

```text
sentinel-control/docs/brain/P5A_BRAIN_L4_GAP_ANALYSIS.md
sentinel-control/docs/brain/P5A_MULTI_AGENT_BRAIN_ARCHITECTURE.md
sentinel-control/docs/brain/P5A_SCIENCE_TO_SENTINEL_BRAIN_MAP.md
sentinel-control/docs/brain/P5A_BRAIN_L4_ROADMAP.md
sentinel-control/docs/brain/P5A_LOCK_VERDICT.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## P5A Locked Doctrine

```text
Brain decides intelligence allocation.
MissionAuthorityEnvelope still decides authority.
```

P5A defines these future Brain L4 modules:

```text
MissionEntropyEstimator
AgentCountController
AgentSocietyManager
MissionGlobalWorkspace
FastBrain / SlowBrain routing
BayesianBeliefState
EpistemicActionEvaluator
ResourcefulnessEngine / DebrouilleLane
ToolSubstitutionPolicy
FallbackPlanner
PartialSuccessContract
AuthorityExtensionProposal
Adaptive Debate / Sparse MoA
SkillProcedureGraph
BrainBench
```

## Debrouille Lane Lock

Sentinel must be controlled, but not passive.

```text
Authority is fixed.
Strategy is flexible.
POWER means more initiative inside the mandate, not new permissions.
If blocked, try allowed alternatives before escalating.
If authority is insufficient, create an AuthorityExtensionProposal.
Partial success must be explicit and evidence-linked.
```

Debrouille levels:

```text
D0 Obey
D1 Repair
D2 Substitute
D3 Replan
D4 Explore
D5 Propose Extension
```

D5 proposes only. It does not grant, activate, or execute new authority.

## Agent Scaling Policy

```text
low entropy      -> 1 agent
medium entropy   -> 3-5 agents
high entropy     -> 8-20 agents
very high        -> 20-100 agents
extreme swarm    -> disabled by default
```

No 1000-agent mode is authorized by P5A. Extreme swarm requires explicit budget,
parallelizability proof, trace fan-in, context compression, timeout, and
FinalGate acceptance criteria before any future implementation.

## P4H-AF Required Files

These files remain required to preserve the P4H-AF full lock that P5A builds on:

```text
sentinel-control/services/sentinel-core/tests/test_agent_browser_operator_runtime_minicorpus.py
sentinel-control/docs/browser/P4H_AF_RUNTIME_MINICORPUS.md
sentinel-control/docs/browser/P4H_AF_RUNTIME_SCORECARD.md
sentinel-control/docs/browser/P4H_AF_LOCK_VERDICT.md
```

## P4H-AE Required Files

These files remain required to preserve the P4H-AE runtime route foundation:

```text
sentinel-control/services/sentinel-core/sentinel/agent/capability_selector.py
sentinel-control/services/sentinel-core/sentinel/agent/tool_selector.py
sentinel-control/services/sentinel-core/sentinel/agent/final_gate.py
sentinel-control/services/sentinel-core/tests/test_agent_browser_operator_runtime_integration.py
sentinel-control/docs/browser/P4H_AE_LOCK_VERDICT.md
sentinel-control/docs/browser/P4H_AE_RUNTIME_SCORECARD.md
```

## Git Synchronization Snapshot

The repository still has a broad dirty working tree outside this P5A tranche,
including pre-existing modified `RedditPulse`, `agent-lab`, web app, docs, and
core files. Those unrelated changes were not reverted.

P5A files currently expected to be newly tracked or updated until the next Git
commit step:

```text
sentinel-control/docs/brain/P5A_BRAIN_L4_GAP_ANALYSIS.md
sentinel-control/docs/brain/P5A_MULTI_AGENT_BRAIN_ARCHITECTURE.md
sentinel-control/docs/brain/P5A_SCIENCE_TO_SENTINEL_BRAIN_MAP.md
sentinel-control/docs/brain/P5A_BRAIN_L4_ROADMAP.md
sentinel-control/docs/brain/P5A_LOCK_VERDICT.md
sentinel-control/docs/CURRENT_STATE_LOCK.md
```

## Boundary

Do not start P5B in this pass.

Do not start the next organ.

Do not add new browser powers.

Do not implement runtime multi-agent execution from P5A alone.

Do not silently expand authority. Resourcefulness is allowed only inside the
MissionAuthorityEnvelope; missing authority must become a proposal.
