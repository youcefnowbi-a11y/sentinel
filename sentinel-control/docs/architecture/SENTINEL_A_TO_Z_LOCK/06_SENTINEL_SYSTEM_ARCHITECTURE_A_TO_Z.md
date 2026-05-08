# Sentinel System Architecture A To Z

## Layers

```text
L0 Evidence and forensic sources
L1 Mission Authority
L2 Brain L4 cognition
L3 Organ contracts
L4 Dry-run and simulation
L5 Sandboxed runtime
L6 Limited execution
L7 Product workflows
L8 Monitoring, replay, OrganBench
```

## Runtime Shape

```text
Mission request
-> AuthorityEnvelopeValidator
-> BrainRuntime
   -> MissionEntropyEstimator
   -> AgentCountController
   -> AgentSocietyManager
   -> MissionGlobalWorkspace
   -> BayesianBeliefState
   -> AdaptiveDebateRouter
   -> EpistemicActionEvaluator
   -> ResourcefulnessEngine
   -> SkillProcedureGraph
-> OrganRegistry
-> OrganPromotionGate
-> DryRunReceipt
-> Approval / SpecialAuthority if required
-> ExecutionReceipt
-> TraceReplay
-> FinalGate
-> BrainBench / OrganBench
```

## Product Principle

Sentinel does not become powerful by deleting dangerous capabilities. Sentinel
becomes powerful by controlling when, why, where, and how capabilities are used.

```text
Power is not bypass.
Power is governed capability.
```

