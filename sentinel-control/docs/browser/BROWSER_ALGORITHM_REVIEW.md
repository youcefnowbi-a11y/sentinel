# Browser Algorithm Review

Date: 2026-04-29
Status: Passed with known bounded limits

## Algorithm Matrix

| Algorithm | Current Method | Strength | Limit |
| --- | --- | --- | --- |
| URL normalization | `urlparse`, IDNA host normalization, scheme/domain checks. | Deterministic policy decision. | No advanced homograph scoring. |
| Private/internal target rejection | IP parsing, private/loopback/internal checks, DNS result rejection. | Strong public boundary. | Depends on resolver input quality. |
| Redirect revalidation | Adapter follows redirect responses and re-runs URL guard per hop. | Prevents redirect-to-private acceptance. | Redirect strategy is fetch/evidence scoped. |
| Connection proof | Optional pinned fetch path and `BrowserConnectionProof`. | Gives socket-level evidence in default path. | Mock/custom transports cannot prove socket pinning. |
| MIME gate | Allowlist by normalized content type. | Prevents non-content artifacts from becoming evidence. | MIME truth depends on server headers. |
| Size budget | Compressed and uncompressed byte accounting. | Prevents expansion/body overrun. | Does not yet model streaming semantic chunks. |
| Readable extraction | Heuristic article/main preference, script/style ignore, fallback modes. | Good V2 extraction. | Not full DOM readability. |
| Citation offsets | Bounded snippet offsets from extracted text. | Traceable quote proof. | Does not prove semantic truth. |
| Prompt flags | Pattern-based untrusted content markers. | Visible in receipts. | Not complete adversarial classifier. |
| Role refs | Parser-backed role/name/nth refs. | Deterministic stable refs per page hash. | Not CDP-native accessibility tree. |
| Snapshot hash | SHA-256 of snapshot text. | Stable tamper proof. | Hash proves bytes, not semantic correctness. |
| Page hash | SHA-256 of HTML/text basis. | Binds refs to page content. | Dynamic pages can change between capture and action. |
| Ledger hash | Canonical JSON SHA-256. | Strong consistency proof. | Ledger is metadata-only, not full HAR body proof. |
| Interaction plan hash | Canonical JSON SHA-256 without hash field. | Prevents plan tampering. | Plan quality still depends on planner/reasoner. |
| Same-origin check | URL origin tuple comparison. | Blocks cross-origin result in P3H. | Does not model same-site/private account semantics. |
| Retry bound | Max attempts with retryable reasons. | Prevents infinite loop. | Retry policy not yet optimized by mission value. |

## Strongest Algorithms

1. Plan hash + snapshot/page hash binding.
2. FinalGate browser forged-output rejection.
3. Per-hop redirect revalidation.
4. Canonical network ledger hashing.
5. Artifact receipt hash binding.

## Weakest Algorithms

1. Source quality scoring is still heuristic.
2. Role snapshot is parser-backed, not browser-native accessibility.
3. Screenshot normalization uses injected transcode hook.
4. Browser retry policy is deterministic but not value-optimized.
5. Browser evidence confidence is not yet integrated with mission hypotheses.

## Algorithmic Verdict

Browser V2 algorithms are robust enough for public mission-governed evidence and
limited public interaction. P3X now defines how the brain consumes browser
uncertainty. Browser 2.5/V3 should upgrade algorithms only after P3Y defines
how the LLM consumes browser uncertainty.
