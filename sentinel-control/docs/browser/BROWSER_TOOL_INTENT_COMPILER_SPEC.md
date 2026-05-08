# Browser Tool Intent Compiler Spec

Date: 2026-04-29
Status: P3Y-B implemented

## Purpose

`ToolIntentCompiler` converts LLM draft intent into a canonical tool call only
after deterministic checks. It extends `ToolCallProtocol`; it does not replace
it.

## Pipeline

```text
raw LLM draft
-> ToolCallProtocol canonicalization
-> ContextPack binding
-> schema and semantic checks
-> MissionAuthority checks
-> available-intent checks
-> browser power boundary checks
-> runtime ref provenance binding
-> prompt-injection source boundary
-> optional ToolRegistry policy decision
-> compiled intent event
```

## Required Bindings

Every compiled intent must include:

- `context_pack_id`;
- `context_pack_sha256`;
- canonical tool-call hash;
- compilation hash;
- provenance ref ids when refs are used;
- evidence refs when claims are used.

## Rejection Cases

- missing or mismatched ContextPack id/hash;
- tool outside mission authority;
- action outside mission authority;
- action not present in available ContextPack intents;
- fabricated runtime ref;
- stale page or snapshot hash;
- prompt-injection source used as action ref;
- submit/post/send/upload/download/login/private/session/storage/cookie/script powers;
- non-delegated side effects.

## Events

- `tool_intent_compiled`
- `tool_intent_compilation_rejected`

FinalGate requires compiled intents to reference a validated ContextPack and to
include canonical and compilation hashes.
