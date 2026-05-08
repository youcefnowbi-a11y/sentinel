# Browser Logic Review

Date: 2026-04-29
Status: Passed with explicit V2 limits

## State Machine

Browser V2 is composed of typed state transitions, not a free browser session.

```text
URL candidate
-> PublicUrlDecision
-> evidence/snapshot request
-> artifact capture
-> receipt
-> EventBus trace
-> FinalGate
```

For interaction:

```text
BrowserAccessibilitySnapshot
-> BrowserInteractionPlan
-> dry-run proof
-> BrowserInteractionExecutionRequest
-> before snapshot verification
-> limited backend action
-> post-action snapshot
-> receipt
-> FinalGate
```

For lifecycle:

```text
session_started
-> tab_opened
-> tab_navigated*
-> tab_closed
-> session_closed
```

For reliability:

```text
lease
-> health_check*
-> operation_retry*
-> release
```

## Transition Findings

| Transition | Deterministic? | Proof | Finding |
| --- | --- | --- | --- |
| URL -> decision | Yes | `BROWSER_URL_CLASSIFIED` | Pure policy output for a given resolver/redirect input. |
| decision -> evidence | Yes | evidence receipt and artifact | Accepted content requires URL decision, MIME, size, and optional connection proof. |
| rendered page -> snapshot | Yes | snapshot artifact and receipt | Final URL must remain policy-compatible; artifacts carry hashes. |
| snapshot -> plan | Yes | plan hash | Required refs must exist before plan acceptance. |
| plan -> execution | Yes | plan trace and before snapshot | Execution rejects stale snapshot/page hashes. |
| execution -> after state | Yes | after snapshot artifact | Accepted execution requires post-action artifact and receipt. |
| lifecycle session/tab | Yes | ordered events | FinalGate reconstructs active/closed state. |
| supervisor retry | Yes | bounded retry event | Retry event must be below max attempts. |

## Ref Validity

Refs are valid only in the context of:

- `snapshot_sha256`;
- `page_sha256`;
- role/name/nth metadata;
- plan hash;
- plan trace event.

Refs are not authority. They are structural coordinates. Authority comes from
MissionAuthority, ToolRegistry, and controlled runner policy.

## Logic Risks

| Risk | Current Mitigation | Residual |
| --- | --- | --- |
| Page changes after plan | Before snapshot/page hash check. | Dynamic pages can still drift after the backend begins execution. |
| Weak source text | Source quality flags and evidence gaps. | Brain must decide whether weak source is enough. |
| Multi-step action strategy | Plan steps are explicit. | No cognitive planner policy yet for complex page workflows. |
| Lifecycle and real backend mismatch | Public lifecycle ledger is proof-only. | Real persistent pool is not yet bound to lifecycle state. |

## Verdict

The logic is coherent for Browser V2. The main missing layer is not more browser
state. It is a cortex policy that decides how browser results change mission
beliefs and plans.
