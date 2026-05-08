# G12 Mission Authority Kernel Verdict

Date: 2026-04-26
Mode: deep-research synthesis and implementation doctrine
Runtime status: no risky runtime enabled

## 0. Local Sources Reviewed

Deep research sources:

- `deep-research-report (1).md:3` states the UX verdict: neither global Full Access nor permission popups, but bounded delegation by mission.
- `deep-research-report (1).md:7` defines the authority envelope as mission, authorized systems, authorized data, authorized actions, duration, and limits.
- `deep-research-report (1).md:31` defines Power Mode as autonomous execution under mandate, not Full Access.
- `deep-research-report (1).md:41` to `deep-research-report (1).md:55` define mission creation, Authority Preview, Mission Control, escalation, timeline, and kill switch UX.
- `deep-research-report (1)cc.md:5` states the market verdict: winning agents take a clear mandate, advance for minutes or hours, self-check, and escalate only for sensitive, irreversible, external, costly, or out-of-scope actions.
- `deep-research-report (1)cc.md:7` recommends permission by mission with risk-class escalation.
- `deep-research-report (1)cc.md:56` defines mission-level permission as the best product pattern.
- `deep-research-report (1)cc.md:117` to `deep-research-report (1)cc.md:145` list the concrete features: Mission Passport, action lattice, disposable workspaces, reviewer, rollback, budget, and responsibility ledger.
- `Designing Autonomous Agent Mission Authority.md:1` is a single-line architecture export that defines the Mission Authority Envelope, autonomy engine, classifiers, risk scoring, kill switches, action ledger, budget controller, domain rules, and phased rollout.
- `debat.md:1008` to `debat.md:1296` introduced Power Mode as future scoped authority.

Existing Sentinel sources:

- `agent-lab/audits/SENTINEL_POWER_MODE_SPEC.md` defines Power Mode as future scoped authority.
- `agent-lab/audits/final/g11_debate_verdict_aggressive_control.md` defines aggressive control and the tempo router.
- `agent-lab/audits/final/g10_sentinel_architecture.md` keeps risky runtime disabled.

## 1. NEXUS Verdict

The three deep research reports are stronger than G11.

G11 corrected the product from fear-based control to aggressive control. That was right, but still too action-centered.

The new primitive is not:

```text
Power Mode
```

The new primitive is:

```text
Mission Authority Envelope
```

Power Mode becomes one authority level inside mission authority. It is not the organizing concept.

The correct doctrine:

```text
Permission once for the mission.
Autonomy inside the mission.
Escalation only at the boundary.
```

This is the missing bridge between "wow" and "control." The user should not approve every step. The user delegates a mission with objective, scope, duration, budget, risk appetite, allowed systems, allowed actions, forbidden actions, and escalation triggers. Sentinel then works fast inside that envelope.

## 2. What GPT Got Right

GPT's answer is directionally correct:

- permission per action is too slow;
- global Full Access is too vague;
- tool-level permission is too coarse;
- mission-scoped autonomy is the right product and architecture layer;
- v1 should use deterministic classifiers, not train neural risk models first;
- GTM remains the wedge, but Mission Authority is the platform primitive;
- G12 should become Mission Authority Kernel, not just Core Kernel.

The key upgrade is the phrase:

```text
Mission first. Action lattice second.
```

That sentence should govern G12 implementation.

## 3. What GPT Still Understates

GPT's proposed G12 is good, but it misses five hard requirements.

### 3.1 Mission authority must be typed before it is intelligent

The first kernel should not depend on advanced model judgment. The Mission Authority Envelope must be a strict data contract with enum-based fields, deterministic checks, and explicit hard blocks.

Neural classifiers can come later. The kernel must work before the model is trusted.

### 3.2 Mission authority is not only permissions

A mission also needs:

- success criteria;
- expected artifacts;
- stop conditions;
- rollback preference;
- owner and user accountability;
- budget route;
- review route;
- trace scope;
- evidence requirements.

Without success criteria and artifacts, the mission becomes a broad permission bag.

### 3.3 Reviewer must be first-class

The market report explicitly points to executor plus reviewer plus policy engine. Sentinel should encode this from G12:

```text
Planner proposes.
Executor works.
Reviewer checks.
Policy routes.
Trace records.
```

The reviewer does not need to block every action. It can audit batches, sample outputs, verify evidence, and trigger escalation when drift appears.

### 3.4 Mission authority must separate autonomy from compute depth

The UX report is right: autonomy level and model effort are different controls.

- Safe/Operator/Power/Autonomous = authority level.
- Quick/Standard/Deep = reasoning and cost level.

Mixing these will confuse pricing, UX, and policy.

### 3.5 Power Mode should not be implemented before Mission Control exists

Power without Mission Control is invisible authority. The user needs:

- live mandate;
- timeline;
- active scope;
- current step;
- cost used;
- stop;
- revoke;
- rollback where possible;
- escalations pending.

Power Mode must wait until Mission Control exists, even as a fake harness.

## 4. Council Debate

### Conflict 1: Full Access vs Mission Authority

NOVA position:

- Full Access creates the wow.

AXIOM position:

- Full Access creates an undefined blast radius.

Ruling:

- Mission Authority wins. The product keeps the wow by allowing autonomy inside a mandate, not by granting global power.

Final position:

```text
No global Full Access.
Use Mission Authority Envelope with scoped systems, tools, data, actions, duration, budget, and escalation triggers.
```

### Conflict 2: Safety vs Agentic Feeling

SECURITY position:

- More approval reduces risk.

SIGNAL position:

- More approval reduces the feeling that an agent is working.

Ruling:

- SIGNAL wins inside the mission. SECURITY wins at the boundary.

Final position:

```text
Inside scope: auto-execute green actions.
At boundary: escalate.
Outside scope or forbidden: block.
```

### Conflict 3: Neural Classifiers Now vs Deterministic Kernel First

CIPHER position:

- Compact classifiers are the future and can make routing fast.

AXIOM position:

- v1 needs deterministic behavior, testability, and trace data before training.

Ruling:

- AXIOM wins for G12. CIPHER wins for G15+.

Final position:

```text
G12 uses deterministic classifiers.
Neural action classifiers become a later upgrade trained on traces.
```

### Conflict 4: GTM Wedge vs Platform Primitive

FORGE position:

- Sentinel must stay sellable as GTM Operator.

NOVA position:

- Mission Authority can become the platform.

Ruling:

- Both are correct.

Final position:

```text
Sell the first mission: find first customers.
Build the platform primitive: Mission Authority Kernel.
```

### Conflict 5: Disposable Workspace Now vs Later

CIPHER position:

- The market report says disposable workspaces are key.

NEXUS position:

- G12 can model the workspace boundary, but should not build real browser, shell, or sidecar runtime yet.

Ruling:

- G12 creates workspace contracts and path limits, not full sandbox runtime.

Final position:

```text
Generated-project workspace now.
Disposable browser/shell/sidecar workspaces later.
```

## 5. Corrected G12 Scope

G12 should not be "Core Kernel" only. It should be:

```text
G12 - Mission Authority Kernel
```

Build the foundation that lets Sentinel execute a safe GTM mission end to end without micro-approval.

Required modules:

1. MissionAuthorityEnvelope.
2. MissionState.
3. MissionAction.
4. EscalationRequest.
5. MissionTraceEvent.
6. MissionPlanner v0.
7. AutonomyEngine v0.
8. Deterministic action classifiers.
9. MissionBudgetController.
10. MissionKillSwitch.
11. MissionTraceTimeline.
12. SafeMissionExecutors.

## 6. Routing Model

The G11 tempo router remains valid, but it is now mission-aware.

```text
green  -> in-scope, reversible, local, non-sensitive -> auto_execute
amber  -> in-scope, low externality, recoverable -> log_and_continue or light preview
red    -> in-scope but external, irreversible, sensitive, costly, or low confidence -> escalate
black  -> forbidden, out of runtime boundary, or system invariant breach -> block
```

Every route must answer:

- Is this inside the mission?
- Is the tool allowed?
- Is the action allowed?
- Is the data allowed?
- Is the target allowed?
- Is it reversible?
- Does it touch an external party or system?
- Is it sensitive?
- Is it within budget?
- Is confidence high enough?

## 7. Risk Formula v0

The architecture report proposes a conceptually stronger formula with intent divergence, sensitivity, externality, and reversibility/loss magnitude.

For G12, use a deterministic v0:

```text
risk_score =
  25 * out_of_scope
+ 20 * forbidden_or_unknown_tool
+ 15 * externality
+ 15 * irreversibility
+ 10 * sensitivity
+ 10 * cost_pressure
+  5 * low_confidence
```

Routing:

```text
0-30   -> auto_execute
31-55  -> log_and_continue or light preview
56-80  -> escalate
81-100 -> block
```

Hard overrides:

- forbidden action blocks;
- expired mission blocks;
- revoked mission blocks;
- path traversal blocks;
- shell blocks now;
- real browser submit blocks now;
- real external send blocks now unless future scope is explicitly implemented;
- credential access blocks now;
- payment blocks now;
- production mutation blocks now.

## 8. G12 Acceptance

G12 is accepted only if:

- a local GTM mission can run end to end without micro-approvals;
- all generated artifacts stay under `sentinel-control/data/generated_projects`;
- outreach is draft-only;
- external send escalates or blocks;
- shell and browser submit block even if the mission mode is Power;
- every route writes a MissionTraceEvent;
- every escalation explains why it is asking now;
- stop/revoke prevents further queued actions;
- budget and max action limits are enforced;
- mission authority is separate from model effort/cost depth.

## 9. Final Product Sentence

```text
Give Sentinel a mission, not a list of clicks.
```

## 10. North Star

Sentinel becomes the mission operating system for AI agents: users delegate bounded outcomes, Sentinel acts aggressively inside the mandate, and the system escalates only when the boundary is crossed.
