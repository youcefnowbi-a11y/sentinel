# P4C Browser V3 Supremacy Review

Date: 2026-04-29
Status: Completed with hardening queue

## Verdict

Browser V3 is locked as an authority architecture. P4B-0 through P4B-8 now form
one governed browser system:

```text
MissionAuthorityEnvelope
-> BrowserV3AuthorityGrant
-> ContextPack action intent
-> ToolIntentCompiler
-> ControlledRunner / class executor
-> EventBus event
-> artifact / receipt
-> CoreFinalGate
```

The review does not declare external benchmark supremacy yet. The V3 contracts
are strong, but several runtime paths still use injected backends in tests. The
next browser work should be backend-reality hardening and EvalBench multi-run,
not a new module and not new browser powers.

## Scope Reviewed

| Class | Status | P4C result |
| --- | --- | --- |
| P4B-0 V3 authority kernel | Done | Pass |
| P4B-1 form submit/post/send/publish | Done | Pass |
| P4B-2 download quarantine | Done | Pass |
| P4B-3 upload authorized | Done | Pass |
| P4B-4 private session | Done | Pass with backend-reality follow-up |
| P4B-5 login authority | Done | Pass with backend-reality follow-up |
| P4B-6 cookie/storage contracts | Done | Pass with redaction hardening |
| P4B-7 sandboxed JS evaluate | Done | Pass with no-network hardening queue |
| P4B-8 HAR/body capture | Done | Pass with adversarial redaction queue |

## Hardening Applied During P4C

P4C found a compiler-layer gap: after a valid V3 grant, the compiler delegated
tokens such as `login`, `cookie`, and `storage`, but did not explicitly reject
LLM-authored raw payload keys like `credential_value`, `cookie_value`, or
`raw_body`.

The compiler now rejects:

- raw credential fields in `browser_login_authority`;
- raw cookie/storage fields in `browser_cookie_storage_contract`;
- raw or unredacted body fields in `browser_har_body_capture`.

The new P4C test verifies login, cookie/storage, and HAR/body rejection at
compile time before execution.

## Supremacy Position

| Axis | Current Sentinel Browser V3 | Verdict |
| --- | --- | --- |
| Authority governance | Stronger than raw browser agents | Exceeds |
| Proof chain and receipts | Stronger than transcript logging | Exceeds |
| LLM boundary | ContextPack + compiler, not raw tool execution | Exceeds |
| Form submit class | Governed and certifiable | Strong |
| Upload/download classes | Artifact/quarantine bound | Strong |
| Private/login/cookie classes | Architecturally present | Needs real-backend stress |
| Sandboxed JS | Hash-allowlisted and no-network by contract | Needs adversarial runtime tests |
| HAR/body capture | Bounded/redacted by contract | Needs adversarial redaction tests |
| Raw live automation breadth | Not fully benchmarked | Not declared |

## Final Review Decision

Browser V3 authority architecture is accepted. Browser V3 external supremacy is
not declared until real backend tests and EvalBench multi-run prove these
classes under realistic browser conditions.
