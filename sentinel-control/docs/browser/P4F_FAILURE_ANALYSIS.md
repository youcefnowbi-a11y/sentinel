# P4F Failure Analysis

Date: 2026-04-30
Status: Complete

## Main Failure Classes

P4F separates failures into four categories:

```text
peer_governance_proof_gap
peer_sensitive_proof_gap
peer_policy_denial_gap
sentinel_raw_runtime_gap
```

## Findings

### 1. Governance / Proof Gap

The peer profile can complete many raw browser tasks, but it does not provide
Sentinel-equivalent authority chain proof:

```text
MissionAuthority -> ToolIntentCompiler -> executor -> receipt -> FinalGate
```

### 2. Sensitive Data Proof Gap

Login, cookie/storage, and HAR/body groups require proof that secrets were not
exposed. Sentinel scores strongly here because it has redaction contracts and
FinalGate checks. A peer browser runtime must prove this separately.

### 3. Policy Denial Gap

The failure-denial group is where governance matters most. A raw browser runtime
can be excellent at execution while weaker at rejecting stale refs, prompt
injection, cross-origin misuse, or unauthorized high-impact actions.

### 4. Sentinel Raw Runtime Gap

Sentinel still has an unproven raw-runtime gap:

```text
external site compatibility
large uncontrolled DOMs
long-horizon visual tasks
real account edge cases
remote-browser scale
vendor-grade debugging ergonomics
```

This is why P4F does not declare external supremacy.
