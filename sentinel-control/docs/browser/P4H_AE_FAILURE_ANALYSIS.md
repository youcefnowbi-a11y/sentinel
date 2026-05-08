# P4H-AE Failure Analysis

Date: 2026-05-01
Status: Implemented

## Failures Found During Integration

### 1. FinalGate rejected synthetic tool-intent events without ContextPack proof

Initial runtime route attempts emitted `tool_intent_compiled` without a
validated ContextPack boundary. `CoreFinalGate` correctly rejected the trace.

Fix:

```text
BrowserOperatorRuntimeRoute now emits a minimal runtime ContextPack assembly
and validation event before emitting tool_intent_compiled.
```

This preserves the LLM/tool boundary contract for runtime-routed browser
actions.

### 2. MissionRunner capture path was too deep on Windows pytest paths

The first MissionRunner integration path wrote browser capture artifacts under
the generated mission project folder. On long Windows temp paths this created a
path that was too deep for the nested Browser V3 artifact path.

Fix:

```text
MissionRunner uses project_root/browser_operator_captures/<mission-slug>
for injected browser operator capture roots.
```

The route remains project-scoped and avoids avoidable Windows path depth.

### 3. MissionRunner action target must remain path-scoped

`MissionScopeChecker` treats a mission action target as a path when checking
mission scope. A `browser_operator_route` mission action should target the
local route/capture scope, while the real browser URL stays inside the embedded
canonical browser tool call.

Rule:

```text
MissionAction.target = local route/capture scope
CanonicalToolCall.target = browser URL
```

## Remaining Risk

P4H-AE proves runtime integration, not open-web external compatibility.

Remaining browser risks:

```text
external site variability
real SPA layout shifts
bot-wall/CAPTCHA handling
arbitrary third-party scripts
real peer runtime comparison
```

## Decision

The failures were integration defects, not authority defects. They were fixed
without adding new browser powers.
