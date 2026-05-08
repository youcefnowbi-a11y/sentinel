# P4H-X ActionEngine v0

Date: 2026-04-30
Status: Implemented

## Goal

P4H-X adds a small action engine that prepares browser actions from scene
targets without creating a new browser power.

```text
PerceptionFrame
-> SceneActionCandidate
-> CompiledMissionPolicy
-> ActionEnvelope
-> existing browser runner
-> post-action verifier
```

## Code

```text
sentinel.agent.action_engine
```

## Boundaries

ActionEngine v0 does not click, type, submit, evaluate JS, control desktop, or
open new browser authority by itself.

It only:

1. checks that a scene target is visible, understood, actionable, and bound to a
   browser runtime ref;
2. checks that the action class and tool are inside `CompiledMissionPolicy`;
3. creates an `ActionEnvelope`;
4. dispatches the envelope's `CanonicalToolCall` to an existing browser runner;
5. delegates post-action checks to `BrowserPostActionVerifier`.

## Rejection Conditions

ActionEngine rejects:

```text
backend_not_active
browser_backend_not_granted
perception_target_not_found
target_not_visible
target_not_understood
target_not_actionable
target_runtime_ref_missing
candidate_ref_mismatch
target_action_class_not_supported
action_class_out_of_scope
action_class_forbidden
tool_out_of_scope
canonical_call_action_mismatch
canonical_call_tool_mismatch
canonical_call_ref_mismatch
target_domain_out_of_scope
```

## Execution Tempo

Inside compiled mission policy, the action decision is a fast lookup.

At the boundary, the action is rejected as:

```text
out_of_scope
higher_authority
invalid
```

No runtime action is attempted after a rejected preparation.
