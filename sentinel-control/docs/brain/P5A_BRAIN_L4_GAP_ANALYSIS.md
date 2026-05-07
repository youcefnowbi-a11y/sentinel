# P5A Brain L4 Gap Analysis

Date: 2026-05-07
Status: Architecture audit

## Verdict

Sentinel has a strong L3 brain: authority, planning, controlled execution,
trace, repair, evidence, replay, and FinalGate. It is not yet an L4 brain.

The L4 gap is not "make one agent smarter." The gap is adaptive intelligence
allocation:

```text
mission -> estimate uncertainty and breadth -> allocate the right agent society
-> route context -> update beliefs -> aggregate -> certify
```

## Current Strengths

The current brain already has the pieces that make L4 possible:

```text
MissionAuthorityEnvelope = source of authority
AgentRuntime = cognitive controller
MissionRunner = controlled worker execution
ToolSelector / CapabilitySelector = tool and capability policy
HypothesisVerifier = deterministic hypothesis generation and attack
WorldModel / ObjectiveFunctionV2 = basic progress and epistemic scoring
EffortRouter = bounded effort route
CognitiveRepairLoop = bounded repair
EventBus / TraceReplay / CoreFinalGate = proof and certification
```

This is the right base. The brain was built as a certifiable spine before
external organs were expanded.

## L4 Missing Capabilities

| Area | Current State | L4 Gap |
| --- | --- | --- |
| Agent allocation | Worker path is effectively single-worker | Decide 1, 3-5, 8-20, 20-100 agents from entropy, budget, and parallelizability |
| Effort routing | Scalar effort level, `max_parallel_workers = 1` | FastBrain/SlowBrain plus an AgentCountController |
| Workspace | Context is built and compressed | Versioned MissionGlobalWorkspace with selected broadcasts |
| Beliefs | Hypotheses are verified/rejected with confidence | BayesianBeliefState with probability, variance, support, contradiction |
| Debate | Adversarial review exists inside hypothesis verifier | Adaptive debate only when uncertainty or impact warrants it |
| MoA | No layered agent synthesis | Sparse Mixture-of-Agents with fan-in limits and aggregator contracts |
| Action value | Epistemic value exists as a field | Information-gain-aware action selection |
| Resourcefulness | Repair exists, but fallback strategy is not a first-class lane | Debrouille Lane for repair, substitution, replan, exploration, partial success, and authority extension proposal |
| Skills | Capabilities/tools exist | SkillProcedureGraph for reusable know-how under authority |
| Evaluation | Core/browser tests exist | BrainBench for allocation, belief, debate, cost, and trace quality |

## Non-Negotiable Boundary

```text
Brain decides intelligence allocation.
MissionAuthorityEnvelope still decides authority.
```

No Brain module may grant:

```text
new tools
new browser actions
new external systems
new paths
credentials
payments
production mutation
desktop control
channel sending
```

The Brain can recommend more cognition. It cannot expand authority.

## Debrouille Gap

Sentinel must not become passive just because its authority boundary is strict.
The missing product behavior is controlled resourcefulness:

```text
strict on boundaries
flexible on strategies
aggressive on authorized alternatives
transparent when blocked
```

The future ResourcefulnessEngine / DebrouilleLane must handle:

```text
D0 Obey              follow the original plan
D1 Repair            fix small failures in the same plan
D2 Substitute        use another already-authorized tool/path
D3 Replan            create a new plan inside the same envelope
D4 Explore           launch bounded agents/hypotheses/routes inside budget
D5 Propose Extension request limited new authority without activating it
```

D5 proposes only. It does not grant, activate, or execute new authority.

## Scaling Doctrine

Agent count must be earned by mission uncertainty and parallel structure.

| Entropy/Breadth | Agent Policy |
| --- | --- |
| low entropy | 1 agent |
| medium entropy | 3-5 agents |
| high entropy | 8-20 agents |
| very high entropy | 20-100 agents |
| extreme swarm | disabled by default |

Extreme swarm mode requires:

```text
explicit mission budget
parallelizability proof
context fan-out/fan-in limits
trace aggregation plan
cost ceiling
timeout ceiling
CoreFinalGate acceptance criteria
```

P5A does not authorize a 1000-agent mode.

## Conclusion

Sentinel L3 is a controlled mission brain. Sentinel L4 must become a
metacognitive brain: it measures uncertainty, chooses the right society of
agents, tries authorized alternatives when blocked, learns what evidence
matters, and stops when proof is sufficient.
