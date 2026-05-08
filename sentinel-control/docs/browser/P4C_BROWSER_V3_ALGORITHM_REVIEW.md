# P4C Browser V3 Algorithm Review

Date: 2026-04-29
Status: Completed

## Core Algorithms

## 1. Authority Selection

Input:

```text
MissionAuthorityEnvelope.browser_v3_authority_grants
CanonicalToolCall.action
authority_grant_id
```

Output:

```text
grant found -> delegated token set
grant missing -> browser_v3_authority_grant_missing
```

P4C verdict: sound for P4B-1 through P4B-8.

## 2. Compiler Delegation

The compiler allows browser V3 tokens only when the matching class grant exists.
P4C added a second layer: delegated tokens do not permit raw sensitive values.

P4C verdict: improved and acceptable.

## 3. Provenance Binding

Runtime refs are checked against `ContextPack.browser_stable_refs`, page hash,
and snapshot hash.

P4C verdict: acceptable for ref-bound classes. Future CDP-native refs should
extend this same binding model.

## 4. FinalGate Class Contracts

Every V3 class has a class-specific proof algorithm:

- validate class identity;
- validate grant/context/compiled intent fields;
- validate artifact hash references;
- validate class-specific invariants;
- validate before/action/after ordering where applicable.

P4C verdict: strong.

## 5. Redaction and Bounds

Cookie/storage, HAR/body, and login contracts reject raw value exposure and
missing redaction metadata.

P4C verdict: architecturally strong; adversarial runtime fixtures still needed.

## Algorithm Verdict

The P4B algorithms are internally consistent. The weakest remaining point is not
algorithm shape; it is runtime proof depth for real browser backends.
