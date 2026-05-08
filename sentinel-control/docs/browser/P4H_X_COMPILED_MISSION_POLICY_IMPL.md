# P4H-X CompiledMissionPolicy Implementation

Date: 2026-04-30
Status: Implemented

## Goal

`CompiledMissionPolicy` converts `MissionAuthorityEnvelope` into a fast runtime
policy.

It does not expand authority. It compiles existing authority.

## Code

```text
sentinel.agent.action_engine.CompiledMissionPolicy
sentinel.agent.action_engine.CompiledMissionPolicyCompiler
```

## Compiled Fields

```text
mission_id
source_envelope_hash
policy_hash
allowed_action_classes
allowed_tools
allowed_domains
allowed_paths
allowed_backend_kinds
impact_budget
action_budget
max_steps
max_wall_clock_ms
confirmation_boundaries
forbidden_zones
required_receipt_types
required_verifier_types
credentialed_state_rules
externality_rules
trace_refs
```

## Browser v0 Behavior

If the mission grants browser actions, `allowed_backend_kinds` contains:

```text
browser
```

If no browser action is granted, no browser backend is granted.

## Required Proof

Browser actions compile required proof automatically:

```text
browser_receipt
browser_interaction_receipt
browser_post_action_verifier
```

The existing runner and FinalGate remain responsible for execution trace and
receipt certification.
