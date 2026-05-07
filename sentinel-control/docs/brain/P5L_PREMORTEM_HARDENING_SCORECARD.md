# P5L Pre-Mortem Hardening Scorecard

Date: 2026-05-07
Status: Implemented

## Targeted Test Result

```text
test files =
  sentinel-control/services/sentinel-core/tests/test_agent_brain_l4_integrated_review.py
  sentinel-control/services/sentinel-core/tests/test_agent_brain_l4_premortem_fixtures.py
tests = 23
passed = 23
```

Command verified:

```bash
python -m pytest tests/test_agent_brain_l4_integrated_review.py tests/test_agent_brain_l4_premortem_fixtures.py -v --tb=short
```

## Final Verification

```text
targeted full P5 suite with P5L = 102 passed
full sentinel-core regression = 618 passed
```

Commands verified:

```bash
python -m pytest tests/test_agent_mission_entropy.py tests/test_agent_count_controller.py tests/test_agent_society_manager.py tests/test_agent_global_workspace.py tests/test_agent_bayesian_belief_state.py tests/test_agent_adaptive_debate.py tests/test_agent_epistemic_action.py tests/test_agent_resourcefulness_engine.py tests/test_agent_skill_procedure_graph.py tests/test_agent_brainbench.py tests/test_agent_brain_l4_integrated_review.py tests/test_agent_brain_l4_premortem_fixtures.py -v --tb=short
python -m pytest tests -v --tb=short
```

## Fixture Coverage

| Fixture | Result | Hardening |
| --- | --- | --- |
| 1. Over-agenting simple mission | pass | Fast route remains 1 agent |
| 2. Under-agenting complex mission | pass | High route remains 8-20 agents |
| 3. Unverified claim accepted as fact | pass | WorkspaceFact rejects unverified accepted facts |
| 4. Rejected claim reintroduced as fact | pass | Workspace replay guard preserved |
| 5. Fake high-confidence weak evidence | pass | BrainBench negative_case detects miss |
| 6. Contradiction ignored | pass | Belief variance widens |
| 7. Debate unnecessary on low entropy | pass | Debate remains off |
| 8. Debate missing on high-impact contradiction | pass | Debate triggers |
| 9. Unsafe high-information action executable | pass | Authority impact blocks executability |
| 10. Substitution bypasses authority | pass | Unauthorized substitution remains rejected |
| 11. Authority proposal silently activated | pass | Proposal construction rejects activation |
| 12. Partial success mislabeled full success | pass | PartialSuccessReport rejects full_success |
| 13. Skill executes despite missing authority | pass | Skill match blocks execution recommendation |
| 14. BrainBench happy-path overfit | pass | negative_case category added |
| 15. Capital profit guarantee not flagged | pass | capital_claim category flags guarantee |
| 16. Dynamic spend change without signal refs | pass | WorkspaceSignal and BrainBench require refs |
| 17. Trivial mission slow route | pass | Low route stays FastBrain |
| 18. Dirty workspace broadcast leaks context | pass | Broadcast slice remains minimized |
| 19. Role without first-principles purpose | pass | AgentSociety validation rejects role |
| 20. P5 trace missing or forged | pass | EventBus/BrainBench reject trace failure |

## Boundary Metrics

```text
new external powers = 0
new browser powers = 0
new payment runtime = 0
new trading runtime = 0
new account creation runtime = 0
new credential access = 0
new authority expansion = 0
```

## Decision

All P5L pre-mortem fixtures are hardened and locked.
