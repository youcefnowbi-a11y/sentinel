# Sentinel Core Plan

Date: 2026-04-27
Status: core focus reset

## Decision

The expanded plan was too broad for the current stage.

We are not continuing with capability sprawl, browser, media, APIs, sidecar, or more product roadmap until the agent core is logically sound.

The old expanded files were moved to:

```text
PLAN/archive/2026-04-27_expanded_plan_before_core_focus/
```

They remain reference material only.

## Current Focus

Build the actual Sentinel agent core.

Not:

- more surface capabilities;
- more generic roadmap;
- more UI-first work;
- more tool catalog work.

Now:

```text
What is the agent?
How does it think?
What is its state?
How does it decide?
How does it perceive?
How does it choose actions?
How does it review itself?
How does it learn without mutating dangerously?
How does it connect mission authority to real execution?
```

## Canonical Core Docs

Read these first for the current phase:

1. `SPINE_01_CORE_ARCHITECTURE.md`
2. `SPINE_02_CORE_ROADMAP.md`

Supporting audit files:

3. `CORE_00_LOGIC_AUDIT.md`
4. `CORE_01_AGENT_ORGANISM_ARCHITECTURE.md`
5. `CORE_02_RUNTIME_STATE_MACHINE.md`
6. `CORE_03_IMPLEMENTATION_ROADMAP.md`
7. `CORE_04_REVIEW_BOARD.md`

## Current Verdict

G12B built a useful mission kernel.

But it is not yet a true agent. It is closer to:

```text
mission runner + authority router + local executor
```

The missing piece is:

```text
Agent Core Runtime =
identity + cognitive loop + working memory + world model + method selection
+ plan synthesis + action selection + worker coordination + review + learning proposal
```

## Next Implementation After This Audit

Only after this core plan is accepted:

```text
P1A: Agent Core Runtime Skeleton
```

No tool registry before the agent loop exists.
