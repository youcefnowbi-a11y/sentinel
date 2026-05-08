# Sentinel Mission UI Flow

Status: G12 product/UX spec
Runtime status: design only
Date: 2026-04-26

## 0. UX Doctrine

The user does not approve a list of clicks.

The user delegates a mission.

Sentinel acts inside that mission and escalates only at the boundary.

## 1. Mission Creation Flow

### Step 1: Mission Objective

Fields:

- mission title;
- mission objective;
- success criteria;
- expected artifacts;
- deadline or duration.

Example:

```text
Prepare the first-customer GTM package for this SaaS idea.
Success means: evidence summary, ICP, landing copy, outreach drafts, watchlist, and 7-day roadmap.
```

### Step 2: Scope

Use business verbs first, not raw technical permissions.

Systems:

- CueIdea report;
- public web;
- generated project folder;
- local draft workspace;
- later: CRM, email, browser sandbox, sidecar.

Actions:

- research;
- analyze;
- rank;
- draft;
- create files;
- update watchlist;
- prepare messages;
- export package.

Data:

- public;
- project documents;
- user-provided evidence;
- CueIdea evidence;
- later: approved contacts, CRM records, email metadata.

### Step 3: Limits

Fields:

- duration;
- max actions;
- max cost;
- max recipients;
- allowed paths;
- allowed domains;
- forbidden actions.

### Step 4: Autonomy Mode

Cards, not slider:

- Safe;
- Operator;
- Power;
- Autonomous.

Each card shows:

- works alone on;
- still asks for;
- cannot do;
- ideal for.

### Step 5: Effort Level

Separate from autonomy:

- Quick;
- Standard;
- Deep.

Meaning:

- effort controls reasoning depth, cost, and latency;
- autonomy controls authority to act.

### Step 6: Authority Preview

This is the launch contract.

It must show:

- mission objective;
- systems Sentinel can use;
- actions Sentinel can perform without asking;
- actions Sentinel will still ask for;
- actions Sentinel cannot do;
- duration and limits;
- stop / revoke / rollback behavior;
- estimated cost.

Recommended copy:

```text
Sentinel will operate autonomously inside this mission mandate.
It will act without asking for safe, reversible actions in this scope.
It will ask before external, irreversible, sensitive, costly, or out-of-scope actions.
```

### Step 7: Start Mission

Creates:

- MissionAuthorityEnvelope;
- MissionState;
- initial MissionTraceEvent;
- mission plan;
- budget reservation.

## 2. Mission Control Dashboard

Header:

- mission title;
- status;
- mode;
- effort level;
- time remaining;
- action count;
- cost used;
- Stop button;
- Revoke button.

Main panel:

- current step;
- completed steps;
- blocked steps;
- final artifacts;
- evidence gaps.

Timeline:

- action;
- target;
- result;
- impact;
- route;
- cost;
- undo/rollback if available.

Filters:

- read;
- create;
- change;
- draft;
- escalation;
- block;
- budget;
- error.

## 3. Escalation UI

Every escalation must answer four questions:

1. Why am I asking now?
2. What exactly will happen?
3. What is the impact?
4. What do you want to do?

Options:

- approve_once;
- allow_for_this_mission;
- deny;
- take_over.

Rules:

- escalation copy should be short;
- do not show chain of thought;
- show target, consequence, reversibility, and scope reason;
- `allow_for_this_mission` cannot grant black-zone actions.

## 4. Stop / Revoke / Rollback

Permanent controls:

- Pause;
- Stop now;
- Revoke mission authority.

Meanings:

- Pause: finish current safe step, then stop queue.
- Stop now: interrupt queued work immediately.
- Revoke: invalidate the authority envelope.

After stop:

- show what was done;
- show what remains pending;
- show what can be rolled back;
- allow resume only if mission authority is still valid.

## 5. Language Rules

Use:

- mission;
- mandate;
- scope;
- systems;
- actions;
- limits;
- stop;
- revoke;
- rollback;
- timeline;
- responsibility.

Avoid in primary UI:

- danger mode;
- unsafe;
- full access;
- root access;
- grant everything;
- critical risk for routine safe actions.

## 6. GTM Mission Example

Mission:

```text
Create a first-customer GTM package for an AI invoicing follow-up tool.
```

Allowed:

- use CueIdea report;
- use public research;
- create local generated project folder;
- create GTM markdown files;
- generate outreach drafts without sending;
- create watchlist.

Still asks for:

- sending any email;
- using real contact list;
- publishing landing page;
- connecting CRM;
- spending money.

Cannot do:

- shell execution;
- browser submit;
- desktop control;
- credential access;
- production code mutation.

## 7. Product Sentence

```text
Give Sentinel a mission, not a list of clicks.
```
