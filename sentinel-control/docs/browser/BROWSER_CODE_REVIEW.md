# Browser Code Review

Date: 2026-04-29
Status: Passed with improvement backlog

## Reviewed Modules

| Module | Role | Code Verdict |
| --- | --- | --- |
| `models.py` | Typed contracts. | Strong, but large. Future split may help readability. |
| `url_guard.py` | Public URL policy. | Clear pure-policy module. |
| `live_fetch.py` | Controlled GET fetcher. | Strong boundaries; pinned HTTPS path deserves broader live corpus tests. |
| `evidence_adapter.py` | Fetch-to-evidence adapter. | Correct proof chain; module is dense and should be monitored. |
| `extraction.py` | Readable extraction. | Good heuristic layer; not full DOM/readability engine. |
| `rendered_snapshot.py` | Rendered snapshot adapter. | Strong receipt logic; artifact paths are predictable and scoped. |
| `accessibility_snapshot.py` | Role snapshot and refs. | Deterministic; CDP-native tree is a future upgrade. |
| `observability.py` | Network ledger hashing. | Small and clean. |
| `interaction_dry_run.py` | Plan generation. | Strong hash/ref binding. |
| `interaction_execution.py` | Limited execution gate. | Correct validation; large enough to justify future split if expanded. |
| `playwright_renderer.py` | Read-only rendered backend. | Clear public/fresh-context boundary. |
| `playwright_interaction_backend.py` | Limited backend action. | Bounded current scope; do not expand casually. |
| `public_lifecycle.py` | Stateless lifecycle ledger. | Clear in-memory state and FinalGate-compatible events. |
| `supervisor.py` | Reliability supervisor. | Correct contract layer; not a real persistent pool yet. |
| `screenshot.py` / `pdf.py` | Artifact metadata. | Small and focused. |
| `controlled_runner.py` | Runtime bridge. | Correct authority/policy boundary. |
| `fake_eval.py` | Deterministic browser evals. | Useful V2 coverage; needs more mission-level evals. |

## Code Strengths

- Browser code is split into policy, adapters, backend, artifacts, lifecycle,
  supervisor, and FinalGate checks.
- Runtime browser use goes through canonical tool call, registry policy, and
  controlled runner.
- Artifacts are not accepted by implication; they are captured with hashes.
- FinalGate has browser-specific forged-output checks.
- Product code contains no vendor runtime import.

## Code Concerns

| Concern | Severity | Required Action |
| --- | --- | --- |
| `models.py` is becoming a broad schema hub. | Medium | Split when Browser 2.5 adds private/session classes. |
| `final_gate.py` browser checks are long. | Medium | Consider browser-specific validator modules before V3. |
| Source confidence is heuristic. | Medium | P3X adds the first Browser-Cortex model; calibrate further with mission evals. |
| `supervisor.py` is a contract, not a real pool. | Low | Keep documented until real persistent pool is implemented. |
| Screenshot normalization depends on injected normalizer. | Low | Decide packaging/dependency when product needs native transcode. |

## Blockers Found

No Browser V2 lock blocker was found in this review.

## Verdict

Code is acceptable for Browser V2 lock. Expansion to Browser 2.5/V3 should begin
with refactoring seams for private authority classes and browser-specific
FinalGate validators.
