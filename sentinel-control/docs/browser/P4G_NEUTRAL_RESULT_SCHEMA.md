# P4G Neutral Result Schema

Date: 2026-04-30
Status: Complete

## Schema Version

```text
p4g.neutral_result.v1
```

## Required Fields

```text
schema_version
campaign_id
generated_at
runtime_id
runtime_kind
task_group
execution_status
run_count
same_task_corpus
same_timeout
same_scoring
product_vendor_runtime_imported
binary_success
mission_success_score
trace_quality
proof_completeness
source_quality
interaction_correctness
side_effect_containment
authority_violation_rate
artifact_leakage_rate
latency_ms_p50
latency_ms_p95
step_count_p50
step_count_p95
unstable_iterations
wilson_lower
wilson_upper
failure_category
blocked_reason
```

## Execution Status Values

```text
executed
blocked_not_executed
failed
not_configured
```

## Product Boundary

The neutral schema is the only data Sentinel product code should consume from a
peer runtime campaign. It must not contain raw credentials, raw cookies, raw
storage, raw HAR bodies, or vendor runtime objects.
