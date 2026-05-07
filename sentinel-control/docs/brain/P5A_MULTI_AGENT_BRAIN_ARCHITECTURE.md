# P5A Multi-Agent Brain Architecture

Date: 2026-05-07
Status: Architecture audit

## Purpose

P5A defines the future Brain L4 architecture without implementing runtime
multi-agent execution. The architecture turns Sentinel from a single controlled
mission loop into an adaptive intelligence allocator.

## Target Flow

```text
MissionAuthorityEnvelope + user input + evidence refs
-> MissionEntropyEstimator
-> AgentCountController
-> FastBrain or SlowBrain route
-> AgentSocietyManager
-> MissionGlobalWorkspace
-> ResourcefulnessEngine / DebrouilleLane when blocked
-> specialists / debate / sparse MoA
-> Aggregator
-> BayesianBeliefState update
-> MissionRunner / controlled organs only if already authorized
-> CoreFinalGate
```

Authority stays outside the intelligence allocator.

## Core Modules

| Module | Purpose | Output |
| --- | --- | --- |
| MissionEntropyEstimator | Estimate mission uncertainty, breadth, evidence gap, impact, tool uncertainty, and parallelizability | `mission_entropy`, `domain_breadth`, `parallelizability`, `budget_pressure` |
| AgentCountController | Convert entropy and budget into bounded agent allocation | `recommended_agent_count`, `brain_mode`, `agent_budget` |
| AgentSocietyManager | Build a role-scoped society under the mission envelope | `AgentSocietyPlan` |
| MissionGlobalWorkspace | Maintain selected mission facts, beliefs, open questions, outputs, and broadcast slices | `WorkspaceSnapshot` |
| FastBrain / SlowBrain | Route low-entropy missions cheaply and high-entropy missions through deeper deliberation | `BrainRoute` |
| BayesianBeliefState | Track hypotheses as distributions, not only binary verdicts | `BeliefSet` |
| EpistemicActionEvaluator | Score actions by progress, information gain, risk, cost, and authority impact | `ActionValue` |
| ResourcefulnessEngine / DebrouilleLane | Search authorized alternatives before escalation | `ResourcefulnessDecision` |
| ToolSubstitutionPolicy | Replace a blocked or failed route with another already-authorized tool/path | `ToolSubstitutionDecision` |
| FallbackPlanner | Produce plan B/C/D inside the same mission envelope | `FallbackPlanSet` |
| PartialSuccessContract | Return useful bounded results when full success is impossible | `PartialSuccessReport` |
| AuthorityExtensionProposal | Request limited new authority without activating it | `AuthorityExtensionProposal` |
| Adaptive Debate / Sparse MoA | Trigger debate and layered synthesis only when uncertainty warrants it | `DebateResult` |
| SkillProcedureGraph | Store reusable know-how as procedures with preconditions and proof criteria | `SkillProcedureMatch` |
| BrainBench | Evaluate allocation, belief updates, debate triggers, cost, quality, and trace integrity | `BrainBenchReport` |

## Agent Society Contract

Every agent in a future society must have:

```text
role
mission_id
scope
allowed_tools
allowed_actions
context_budget
output_contract
evidence_required
timeout
authority_level
trace_refs
```

Specialist roles can include:

```text
PlannerAgent
ResearchAgent
VerifierAgent
SkepticAgent
CodeAgent
MathAgent
SecurityAgent
CostAgent
BrowserAgent
GTMStrategistAgent
AggregatorAgent
FinalJudgeAgent
```

These roles are cognitive roles. They do not create execution authority.

## Context Routing

The workspace follows this loop:

```text
select -> broadcast -> collect -> compress -> update -> rebroadcast
```

Agents receive only the context slice needed for their role:

```text
mission authority summary
task objective
relevant evidence refs
active beliefs
open questions assigned to the role
output schema
forbidden assumptions
```

Agents should return artifact references and structured outputs rather than
forcing all detail through the coordinator context.

## Sparse MoA Rule

Dense MoA fan-in can explode context cost. Sentinel L4 should use sparse fan-in:

```text
layer N agents produce outputs
workspace ranks outputs by relevance, evidence, novelty, contradiction
layer N+1 receives only top K outputs plus unresolved contradictions
aggregator receives compressed accepted/rejected summaries
```

Default v1 limits:

```text
max_layers = 2
max_fan_in_per_agent = 5
max_debate_rounds = 2
max_parallel_agents = governed by AgentCountController
```

## Debrouille Lane

The Debrouille Lane makes Sentinel tactically resourceful inside the mission
mandate:

```text
try allowed route
if blocked, search authorized alternatives
if still blocked, dry-run or replan inside authority
if authority is missing, create an AuthorityExtensionProposal
if impossible, return the best partial useful artifact
```

Debrouille levels:

| Level | Name | Behavior |
| --- | --- | --- |
| D0 | Obey | Follow the original plan exactly |
| D1 | Repair | Fix small failures in the same plan |
| D2 | Substitute | Use another already-authorized tool/path |
| D3 | Replan | Create a new plan inside the same mission envelope |
| D4 | Explore | Launch bounded agents, hypotheses, or routes inside budget |
| D5 | Propose Extension | Request limited new authority with scope, risk, expiry, and proof |

D5 is proposal-only. It never activates authority.

POWER mode means more initiative inside the mandate, never new permissions.

## Failure Modes To Design Against

```text
over-spawning for simple missions
duplicate agent work
context pollution
game-of-telephone loss
agent collusion around the same hallucination
unbounded debate
budget exhaustion
trace fan-in explosion
authority drift
aggregator accepting unsupported claims
fallback loop without progress
tool substitution that bypasses policy
partial success reported as full success
authority extension applied silently
```

## Runtime Boundary

P5A does not add:

```text
new browser powers
desktop control
external network mutation
email/channel send
credential access
payments
shell/process execution
production mutation
unrestricted agent spawning
```

All future implementation phases must enter through tests, trace events,
receipts, and CoreFinalGate checks.
