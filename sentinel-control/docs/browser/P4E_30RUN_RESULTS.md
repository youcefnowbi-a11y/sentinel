# P4E 30-Run Results

Date: 2026-04-30
Status: Complete

## Summary

```text
verdict = browser_ready_for_peer_campaign
mission_success_score = 1.0
trace_quality = 1.0
proof_completeness = 1.0
artifact_leakage_rate = 0.0
authority_violation_rate = 0.0
run_count_per_group = 30
confidence_interval_method = wilson_score_95
```

## Scorecard

| Task group | Family | Runs | Success | Wilson lower | Wilson upper | Latency p50 ms | Latency p95 ms | Steps p50 | Steps p95 | Unstable |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `form_workflow` | `web_arena_style` | 30 | 1.0 | 0.8865 | 1.0 | 15.894 | 17.751 | 6.0 | 6.0 | [] |
| `search_navigation` | `web_arena_style` | 30 | 1.0 | 0.8865 | 1.0 | 6.680 | 9.246 | 6.0 | 6.0 | [] |
| `multi_page_task` | `web_arena_style` | 30 | 1.0 | 0.8865 | 1.0 | 7.611 | 11.799 | 7.0 | 7.0 | [] |
| `download_quarantine` | `v3_authority` | 30 | 1.0 | 0.8865 | 1.0 | 13.745 | 64.172 | 5.0 | 5.0 | [] |
| `upload_authorized` | `v3_authority` | 30 | 1.0 | 0.8865 | 1.0 | 21.555 | 42.643 | 7.0 | 7.0 | [] |
| `login_fixture` | `v3_authority` | 30 | 1.0 | 0.8865 | 1.0 | 36.650 | 55.223 | 15.0 | 15.0 | [] |
| `cookie_storage_redaction` | `v3_authority` | 30 | 1.0 | 0.8865 | 1.0 | 40.176 | 66.855 | 15.0 | 15.0 | [] |
| `js_no_network_rejection` | `adversarial_denial` | 30 | 1.0 | 0.8865 | 1.0 | 10.950 | 26.202 | 3.0 | 3.0 | [] |
| `har_body_redaction` | `v3_authority` | 30 | 1.0 | 0.8865 | 1.0 | 20.687 | 58.929 | 4.0 | 4.0 | [] |
| `visual_grounding` | `visual_grounding` | 30 | 1.0 | 0.8865 | 1.0 | 10.745 | 26.892 | 3.0 | 3.0 | [] |
| `research_browsing_citations` | `research_browsing` | 30 | 1.0 | 0.8865 | 1.0 | 6.893 | 11.147 | 3.0 | 3.0 | [] |
| `cross_class_authority_flow` | `v3_authority` | 30 | 1.0 | 0.8865 | 1.0 | 52.654 | 77.594 | 18.0 | 18.0 | [] |
| `failure_denials` | `adversarial_denial` | 30 | 1.0 | 0.8865 | 1.0 | 19.785 | 27.580 | 13.0 | 13.0 | [] |

## Interpretation

The result is strong enough to move from self-hosted benchmark to peer-runner
comparison.

The Wilson lower bound remains the important scientific guard: 30/30 observed
success is not treated as a true 100% guarantee.

## Boundary

This is still self-hosted. It proves benchmark readiness, not open-web
supremacy.
