# P4D Browser Logic Review

Date: 2026-04-29
Status: Complete

## Core Validity Model

A Browser V3 action is valid only if every factor is true:

```text
Valid_V3 = G * C * T * P * R * F
```

Where:

| Factor | Meaning |
| --- | --- |
| `G` | MissionAuthorityEnvelope contains an explicit Browser V3 grant for the class. |
| `C` | ContextPack exposes only brain-authored action intents inside authority. |
| `T` | ToolIntentCompiler canonicalizes and compiles the intent. |
| `P` | Provenance is bound: refs, snapshots, page hashes, session ids, artifacts. |
| `R` | Runtime emits a receipt and event with before/action/after proof. |
| `F` | CoreFinalGate certifies the class-specific contract. |

If any factor is false, the action must be rejected or treated as uncertified.

## Authority Chain

The intended chain is:

```text
MissionAuthorityEnvelope
-> BrowserV3AuthorityGrant
-> ContextPack action intent
-> ToolIntentCompiler
-> Controlled runner / executor
-> EventBus event
-> Receipt/artifact
-> CoreFinalGate
```

P4D confirms the chain is represented in code. The main risk is not missing
links; it is future drift as new classes and tests grow.

## Class Logic Table

| Class | Required proof | Current logic status | Remaining concern |
| --- | --- | --- | --- |
| form submit | plan, refs, pre snapshot, post snapshot, network ledger, same/cross-origin status | Strong | Needs more live form variants. |
| download quarantine | URL policy, MIME, byte limit, quarantine path, artifact hash, no promotion | Strong | Needs adversarial MIME/path corpus. |
| upload authorized | source artifact proof, plan/ref/snapshot proof, network ledger, post snapshot | Strong | Needs larger artifact-origin denial suite. |
| private session | profile/session ids, per-mission scope, storage hash, open/close order, destroy proof | Strong locally | Needs live profile reuse and crash cleanup campaign. |
| login authority | private-session binding, account id, plan, post-login snapshot, credential redaction | Strong locally | Needs exception-path leak corpus. |
| cookie/storage | private-session binding, redacted summary or scoped clear, no raw value exposure | Strong locally | Needs nested/raw export adversarial corpus. |
| sandboxed JS | script hash allowlist, no-network observation, timeout, result size, artifact | Strong locally | Needs broader network-attempt coverage. |
| HAR/body | bounds, MIME, redaction, artifact hash | Strong locally | Needs real header/body/form/nested redaction corpus. |

## Event Order Review

The expected order for accepted V3 actions is:

```text
ContextPack assembled/validated
Tool call canonicalized
Tool intent compiled
Optional URL/snapshot/plan artifact events
Browser V3 class event
FinalGate certification
```

FinalGate checks compiled intent presence and artifact order for the classes
where order matters. Private sessions also require close after open.

## Forgery Model

Forged browser success must fail if it lacks:

- accepted compiled intent trace;
- authority grant id;
- ContextPack id;
- class-correct receipt fields;
- required artifact references;
- hash-consistent plan/network/artifact;
- session open/close proof for session-bound powers.

The current FinalGate contracts cover these fields. The hardening task is to
expand forged-event tests per class so every required field has a negative
case.

## Logic Verdict

The V3 logic model is coherent.

The next risk is coverage depth, not architecture direction:

```text
model sound
local proof good
external/scientific proof pending
```
