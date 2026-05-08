# Browser Failure Modes V2

Date: 2026-04-29
Status: Reviewed and bounded

## Failure Mode Matrix

| Failure Mode | Detection | Current Response | Residual |
| --- | --- | --- | --- |
| Private/internal URL | URL guard / DNS guard. | Reject before fetch/render. | Resolver or DNS environment quality still matters. |
| Redirect to outside-authority target | Per-hop revalidation. | Reject before next fetch. | Rendered backend redirect policy is stricter and still bounded. |
| MIME mismatch | Evidence adapter MIME gate. | Reject before artifact. | Server may mislabel; content sniffing is not full. |
| Compressed body too large | Compressed byte budget. | Reject before artifact. | Streaming semantic extraction not implemented. |
| Uncompressed body too large | Uncompressed byte budget. | Reject before artifact. | None for V2 scope. |
| Missing connection proof when required | Receipt/proof check. | Reject evidence. | Custom transports must provide proof or not be used for proof-required missions. |
| Weak extraction | Quality flags / evidence gap. | Mark weak or reject empty. | Brain must decide whether to search alternative sources. |
| Prompt-injection text | Pattern flags. | Mark untrusted in receipt. | LLM layer must treat content as evidence, not instruction. |
| Missing screenshot | Snapshot adapter check. | Reject when required. | Optional screenshot mode can still omit image by design. |
| Oversized screenshot | Metadata/normalization check. | Normalize via hook or reject. | Built-in transcode not packaged yet. |
| Stale interaction plan | Snapshot/page hash mismatch. | Reject execution. | Dynamic page can change during action window. |
| Unknown ref | Dry-run planner validation. | Reject plan. | Parser-backed refs may be less complete than browser-native refs. |
| Forged plan | Plan hash verification. | FinalGate reject. | None for V2 scope. |
| Forged post-action artifact | Artifact hash check. | FinalGate reject. | None for V2 scope. |
| Cross-origin action result | Same-origin check. | Reject execution. | Same-origin does not imply account/private authority. |
| Unbounded retry | Attempt/max check. | FinalGate reject. | Retry policy value not optimized yet. |
| Lifecycle forgery | FinalGate lifecycle reconstruction. | Reject unknown/stale session/tab state. | Real backend not yet pooled. |

## Highest Residual Risks

1. LLM-browser ambiguity: the LLM still needs rules for seeing page text as
   evidence, not authority.
2. Dynamic pages: hash checks catch stale before state but cannot fully model
   every DOM race after action starts.
3. Parser-backed refs: adequate for V2, weaker than browser-native accessibility.
4. Confidence scoring: currently operational, not yet mathematically calibrated.
5. Real pool gap: P3K is a supervisor contract, not a persistent browser pool.

## Required Mitigation Before Browser 2.5/V3

- Define LLM ContextPack treatment for browser evidence and page text.
- Add mission evals where browser evidence changes hypothesis confidence.
- Add evals for weak source -> alternative search.
- Add formal authority classes before private/session/file/script powers.

## Verdict

Failure modes are known, bounded, and documented for Browser V2. P3X handles the
brain-side browser ambiguity. The remaining residuals are LLM integration and
future-power issues, not Browser V2 lock blockers.
