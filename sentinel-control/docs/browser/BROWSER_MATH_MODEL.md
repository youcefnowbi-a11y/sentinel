# Browser Math Model

Date: 2026-04-29
Status: P3O formal model accepted

## State Definition

Let browser state at step `t` be:

```text
B_t = {
  U_t,  # URL policy decisions
  E_t,  # evidence items and artifacts
  S_t,  # rendered snapshots and refs
  P_t,  # interaction plans
  X_t,  # executed limited interactions
  L_t,  # public lifecycle state
  R_t   # reliability supervisor state
}
```

Accepted browser output must satisfy:

```text
Accepted(output) =>
  trace(output)
  AND authority(output)
  AND receipt(output)
  AND final_gate(output)
```

## Validity Functions

### URL Validity

```text
V_url(u) = scheme_ok * host_public * dns_public * domain_scope * redirect_ok
```

Accepted public browser evidence requires:

```text
V_url(u) = 1
```

### Evidence Strength

```text
E_strength =
  0.30 * source_quality
+ 0.20 * citation_validity
+ 0.20 * extraction_confidence
+ 0.15 * freshness
+ 0.15 * contradiction_status
```

Browser V2 computes the required observables, and P3X maps them into
browser-cortex source confidence, evidence chains, hypothesis deltas, repair
signals, and action recommendations. P3Y defines how the LLM consumes the same
fields through ContextPack.

### Ref Validity

```text
V_ref(ref, page, snapshot) =
  ref_exists(ref)
  AND page_sha256_current == page_sha256_plan
  AND snapshot_sha256_current == snapshot_sha256_plan
```

Accepted interaction requires:

```text
V_ref = 1
```

### Plan Validity

```text
V_plan =
  hash(plan_without_hash) == plan_sha256
  AND dry_run_only == true
  AND all(required_refs exist)
  AND no non_delegated_intent
```

### Execution Validity

```text
V_exec =
  V_plan
  AND before_hash_match
  AND same_origin(before_url, after_url)
  AND post_action_snapshot_exists
  AND receipt_exists
  AND FinalGate_accepts
```

### Retry Bound

```text
0 <= attempts < max_attempts <= 5
```

Retry is valid only if:

```text
retryable(reason) AND attempt_number < max_attempts
```

## Impact Classes

| Impact Class | Browser V2 Example | Status |
| --- | --- | --- |
| Observation | URL classify, fetch, render, snapshot. | Delegated in V2. |
| Local page state | hover, fill/type/select before submit. | Delegated only from certified plan. |
| Navigation wait | wait for URL/text/selector. | Delegated only from certified plan. |
| External mutation | submit/post/send/publish. | Not delegated in V2; delegated only in V3 P4B-1 through `browser_form_submit` authority. |
| Private session | cookies/storage/login/private profile. | Not delegated in V2. |
| File transfer | upload/download. | Not delegated in V2; public download quarantine is delegated only in V3 P4B-2 with `promoted=false`, and public upload is delegated only in V3 P4B-3 from certified Sentinel artifacts. |
| Private browser state | sessions/login/cookies/storage. | Delegated only in V3 P4B-4 through P4B-6 with per-mission session proof, account-id login, and redacted storage contracts. |
| Script and network diagnostics | JS/HAR/body capture. | Delegated only in V3 P4B-7/P4B-8 with script-hash allowlist, no-network JS, redaction, and bounded artifacts. |
| Browser scripting | arbitrary JS/evaluate. | Not delegated in V2. |

## Lock Theorem

If all V2 invariants hold, then no accepted Browser V2 run can create successful
browser output without:

```text
MissionAuthority + ToolRegistry + EventBus + Receipt + FinalGate
```

The theorem is operational, not mathematical proof over all possible programs.
It is enforced by tests, typed models, event contracts, and FinalGate checks.

## Verdict

The Browser V2 math model is coherent. P3X connects `E_strength`,
`source_quality`, `prompt_flags`, `V_plan`, and `V_exec` to mission reasoning.
P3Y now defines the LLM-facing reasoning contract.
