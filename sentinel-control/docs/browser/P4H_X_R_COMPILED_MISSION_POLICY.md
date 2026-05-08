# P4H-X-R Compiled Mission Policy

Date: 2026-04-30
Status: Research lock

## Goal

`CompiledMissionPolicy` is the mechanism that makes Sentinel faster without
making it uncontrolled.

It converts mission authority into runtime-ready execution boundaries.

```text
MissionAuthorityEnvelope -> CompiledMissionPolicy
```

## Why It Exists

The current architecture repeatedly asks policy questions at many stages. That
is correct for certification, but it can become too slow for a strong operator.

Compiled policy keeps the same authority but turns it into fast lookups:

```text
allowed now
requires higher authority
out of scope
requires verifier
requires receipt
requires confirmation
```

## Required Fields

```text
mission_id
policy_id
policy_hash
source_envelope_hash
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

## Execution Semantics

Inside the policy:

```text
execute fast
record receipts
verify post-action
repair automatically when allowed
```

At the boundary:

```text
reject or escalate
do not improvise authority
do not let page/model/OCR expand scope
```

## Relationship To Existing Components

| Component | Role |
| --- | --- |
| `MissionAuthorityEnvelope` | Source of authority. |
| `ToolRegistry` | Catalog and tool eligibility. |
| `ToolIntentCompiler` | Converts draft intent into canonical executable intent. |
| `CompiledMissionPolicy` | Fast execution envelope derived from mission authority. |
| `ActionEngine` | Executes only inside the compiled policy. |
| `FinalGate` | Certifies execution trace, receipts, and verifier chain. |

## Non-Goals

```text
No authority expansion.
No bypass of ToolIntentCompiler.
No replacement of FinalGate.
No retroactive permission.
No policy learned from web content or model output.
```
