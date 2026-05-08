# Brain Review Matrix

Date: 2026-04-28
Status: Core Brain Lock documentation

This matrix is the code-review checklist before starting module harvest.

| Area | Source | Invariant | Tests / Gate | Main Impact Concern |
| --- | --- | --- | --- | --- |
| Runtime orchestration | `sentinel/agent/runtime.py` | Runtime follows phase order and terminates with trace. | `test_agent_runtime.py`, final gate. | Hidden bypass or untraceable terminal state. |
| Context | `context_builder.py`, `context_compressor.py` | Context cannot expand authority; compression preserves refs. | runtime/invariant tests. | Memory or input becoming policy. |
| State | `state.py`, `models.py` | State stays mission-scoped and bounded. | replay/final gate tests. | State drift from trace. |
| EventBus | `event_bus.py`, `events.py` | Append-only hash-chain, monotonic sequence/logical time. | `test_agent_event_bus.py`, certification. | Tampered or reordered trace accepted. |
| Replay | `replay.py` | Replay reconstructs result snapshot. | `test_agent_trace_replay.py`, final gate. | Result cannot be audited. |
| Audit | `audit.py` | Certification matches trace truth. | runtime certification tests. | False certified run. |
| Mission authority | `sentinel/mission/models.py` | Envelope is the only authority source. | mission kernel tests. | Authority expansion from context. |
| Tool selection | `tool_selector.py`, `capability_selector.py` | Unknown/candidate/blocked tools do not execute. | `test_agent_tool_selection.py`, final gate. | Hallucinated tool becomes executable. |
| Tool-call protocol | `tool_call_protocol.py` | Ambiguous/malformed calls are rejected or canonicalized with trace. | `test_agent_tool_call_protocol.py`. | Parser recovery becomes outside-authority execution. |
| Browser URL contract | `agent/browser/url_guard.py`, `agent/browser/models.py` | Public URL classification is pure and does not fetch, navigate, or resolve DNS implicitly. | `test_agent_browser_url_guard.py`, execution-boundary primitive scan. | Read-only browser groundwork accidentally becomes network/browser authority. |
| Browser evidence adapter | `agent/browser/evidence_adapter.py` | Browser evidence requires URL decision, artifact capture, receipt, and trace before acceptance. | `test_agent_browser_evidence_adapter.py`, `browser_capability_receipts` final gate. | Page text becomes trusted evidence without provenance or prompt-injection flags. |
| Browser live fetch | `agent/browser/live_fetch.py` | Live fetch is public GET only, no redirects, no cookies, no JS, no browser control. | `test_agent_browser_live_fetch.py`, isolated network primitive scan. | HTTP fetch expands into full browser/session behavior too early. |
| Browser rendered snapshot | `agent/browser/rendered_snapshot.py` | Rendered snapshot requires URL decision, unchanged final URL, artifact capture, citations, screenshot receipt, network ledger, and trace. | `test_agent_browser_rendered_snapshot.py`, `browser_capability_receipts` final gate. | Rendered browser output bypasses URL policy, citation bounds, diagnostics proof, or artifact proof. |
| Browser artifact quality | `agent/browser/screenshot.py`, `agent/browser/pdf.py`, `agent/browser/rendered_snapshot.py` | Screenshot/PDF/element artifacts are bounded, metadata-rich, receipt-bound, and FinalGate-verifiable. | `test_agent_browser_artifact_quality.py`, `browser_capability_receipts` final gate. | Rich browser artifacts become unbounded files or unverified media blobs. |
| Browser observability | `agent/browser/observability.py` | Network/diagnostic ledger is bounded, hash-bound, and FinalGate-verifiable. | `test_agent_browser_rendered_snapshot.py`, `test_agent_browser_runtime_integration.py`, `browser_capability_receipts` final gate. | Browser diagnostics become unverifiable logs instead of proof. |
| Browser interaction dry-run | `agent/browser/interaction_dry_run.py` | Interaction plans are no-op, snapshot/page-hash bound, stable-ref verified, and FinalGate-verifiable. | `test_agent_browser_interaction_dry_run.py`, `browser_interaction_dry_run_contract` final gate. | Action planning becomes browser state mutation before authority is granted. |
| Browser limited interaction | `agent/browser/interaction_execution.py`, `agent/browser/playwright_interaction_backend.py` | Real browser interaction requires certified plan, valid before snapshot, same-origin result, post-action artifacts, receipt, and FinalGate proof. | `test_agent_browser_interaction_execution.py`, `browser_interaction_execution_contract` final gate. | Browser operator power executes without plan, stale refs, receipt, or authority. |
| Browser public lifecycle | `agent/browser/public_lifecycle.py` | Public sessions/tabs are stateless, URL-policy-bound, ordered, receipt-backed, and FinalGate-verifiable. | `test_agent_browser_public_lifecycle.py`, `browser_public_lifecycle_contract` final gate. | Tab/session state becomes hidden private browser authority. |
| Browser reliability supervisor | `agent/browser/supervisor.py` | Public browser leases, health checks, retries, releases, and rejections are stateless, bounded, ordered, and FinalGate-verifiable. | `test_agent_browser_reliability_supervisor.py`, `browser_reliability_supervisor_contract` final gate. | Backend health or retry machinery becomes hidden permission or unbounded loop. |
| Browser rendered backend | `agent/browser/playwright_renderer.py` | Real browser rendering uses fresh context, JavaScript disabled, no downloads, no storage, blocked subresources, and bounded diagnostics. | `test_agent_browser_playwright_renderer.py`, Browser V1 review. | Browser backend becomes interactive/session-capable before policy integration. |
| Browser runtime integration | `agent/browser/controlled_runner.py`, `agent/runtime.py` | Agent can use browser only through canonical tool call, mission authority, registry policy, URL guard, artifact capture, and receipt. | `test_agent_browser_runtime_integration.py`, `CoreFinalGate`. | Browser becomes an undeclared side channel outside MissionAuthority. |
| Controlled capability | `controlled_capability.py` | Only approved local reversible artifacts execute. | `test_agent_controlled_capability.py`, receipt gate. | Direct tool calls bypass worker/policy. |
| Mission execution | `mission/runner.py`, `worker_coordinator.py` | `MissionRunner` executes plan; cognition remains in `AgentRuntime`. | mission runner/runtime tests. | Execution layer starts making cognitive decisions. |
| Local executors | `mission/safe_executors.py` | Writes stay under generated-project boundary. | mission/execution tests, project scope gate. | Path escape or production mutation. |
| Risk routing | `mission/risk.py` | Posture adjusts thresholds but never authority. | risk/posture tests, final gate. | POWER becomes permission. |
| Posture | `execution_posture.py`, `mission/posture.py` | Aggressiveness only inside granted local/reversible scope. | execution posture tests. | User mode silently grants high-impact tools. |
| Hypothesis | `hypothesis.py` | Only verified hypotheses influence plan. | `test_agent_hypothesis.py`, evidence gate. | Speculation enters execution. |
| World model | `world_model.py` | Scores actions; does not execute them. | `test_agent_world_model.py`. | Score is mistaken for permission. |
| Effort router | `effort_router.py` | Cost/risk/uncertainty route effort only. | `test_agent_effort_router.py`. | Effort expansion becomes authority expansion. |
| Repair | `repair_loop.py` | Repair is bounded and trace-bound. | `test_agent_repair_loop.py`. | Infinite retry or authority creep. |
| Evidence | `evidence.py` | Major decisions produce trace-bound evidence chains. | `test_agent_evidence_chain.py`, final gate. | "Done" without proof. |
| Artifact capture | `artifact_capture.py`, `mission/artifacts.py` | Artifacts have hashes, receipts, rollback metadata. | artifact tests, final gate. | File exists but cannot be proven. |
| Learning | `learning_loop.py` | Learning is proposal-only and human-approved. | final gate, learning tests. | Self-mutation or hidden policy update. |
| Eval bench | `eval_bench.py` | New capabilities require F2P/P2P/negative evals. | `test_agent_eval_bench.py`. | Demo works but reliability regresses. |
| Final gate | `final_gate.py` | Success requires trace, replay, evidence, receipts, scope, budget. | `test_agent_core_final_gate.py`. | Invalid result accepted. |

## Brain Lock Findings To Record

During review, record each finding as:

```text
module:
finding:
severity:
invariant affected:
test coverage:
required fix:
```

No future module harvest should begin if a critical finding affects authority,
trace, replay, receipts, risk routing, or final gate.
