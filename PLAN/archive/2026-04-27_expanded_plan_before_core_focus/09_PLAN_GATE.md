# 09 Plan Gate

Date: 2026-04-26

## Purpose

This gate prevents Sentinel from drifting into implementation without knowing what it is becoming.

## Gate Questions

Before coding next:

1. Are we building a Mission OS, not a single-purpose generator?
2. Is GTM a first mission type, not the full product?
3. Does every new capability enter through manifest, policy, fake benchmark, trace, and reviewer?
4. Do we have a Tool Intelligence path, not only fixed tools?
5. Do we have a Work Method Library path, not only prompts?
6. Do we have a capability roadmap for vision, media, browser, code, outbound, sidecar, and memory?
7. Do we keep vendor agents as specimens, not integrations?
8. Do we block leaked credentials and unsafe runtime power?
9. Do we know the next implementation phase?
10. Do we have a concrete agent runtime loop, not only layers around an agent?

## Gate Verdict Criteria

Pass if:

- `PLAN/` is accepted as the construction contract;
- next implementation phase is chosen from the roadmap;
- no direct browser/email/shell/desktop/vendor bridge is added early;
- the next phase increases platform power, not only GTM output.

Fail if:

- next work adds random tools without a registry;
- next work adds UI without capability semantics;
- next work adds browser/email/shell without fake harness and policy;
- next work treats public API catalogs as trusted tools instead of candidates;
- next work makes Sentinel a generic assistant.
- next work adds capabilities before an executable agent runtime exists.

## Recommended Next Implementation

After plan approval:

```text
P1A: Agent Core Runtime Skeleton
P1B: Capability Manifest And Tool Registry
```

Why:

- P1A defines the actual agent loop: context, orientation, method selection, tool needs, planning, worker coordination, review, success, learning.
- It is the missing layer between Mission OS and future power.
- It prepares browser, media, APIs, code, sidecar, and outbound safely.
- It prevents "tool sprawl".
- It turns public API catalogs into governed candidates.

## P1A Acceptance

P1A is accepted only when:

- an actual `sentinel/agent/` runtime exists;
- the agent can initialize from a mission envelope;
- the agent can build context;
- the agent can select methods;
- the agent can express needed capabilities;
- the agent can route a safe mission through the existing Mission OS;
- the agent reports missing tools instead of inventing them;
- the agent cannot expand authority from memory/tool output.

## P1B Acceptance

P1B is accepted only when:

- unknown tools cannot execute;
- every tool has manifest;
- every manifest declares side effects;
- every capability maps to mission scope;
- fake tools can be routed through mission authority;
- black-zone actions stay blocked;
- tests pass.
