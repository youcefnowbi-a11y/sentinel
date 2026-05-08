# Evidence, Receipts, Artifact Capture, And Final Gate

Date: 2026-04-28
Status: Core Brain Lock documentation

## Evidence Chain

`EvidenceChainBuilder` turns important cognitive decisions into explicit
evidence chains.

Current chain types include:

- tool selection;
- hypothesis verdict;
- plan creation;
- repair decision;
- success evaluation;
- learning proposal.

Evidence chains prevent silent leaps from "the agent thinks so" to "the agent
is allowed to act".

## Hypotheses And Evidence

Hypotheses are not planning facts until verified. The current flow:

```text
generate hypotheses
-> run verification tests
-> run adversarial review
-> produce findings
-> only verified hypotheses enter planning
```

This follows the core rule that planning receives survived beliefs, not raw
speculation.

## Artifact Capture

`ArtifactCaptureSandbox` and mission artifact indexing record local outputs as
artifacts. Captured artifacts are not just paths; they carry metadata needed for
audit and rollback.

Controlled local capabilities can create Markdown or JSON artifacts only inside
approved generated-project paths. Rejections must also be trace-bound.

## Receipts

Every controlled execution that creates a useful artifact must create a receipt.

A receipt binds:

- mission id;
- artifact id;
- artifact type;
- artifact path;
- artifact hash;
- size;
- action id when available;
- reversibility;
- rollback strategy;
- scope;
- trace refs.

Receipts are the proof that "done" corresponds to a concrete artifact.

## Rollback Metadata

Rollback metadata currently records created files/folders and receipt data. It
does not perform unverified automatic deletion. Rollback remains a controlled,
auditable follow-up action.

## Core Final Gate

`CoreFinalGate` is the certification boundary before capability expansion.

It checks:

- trace presence;
- trace mission consistency;
- runtime certification;
- state replay;
- phase contract;
- tool policy decision trace binding;
- selected tools policy eligibility;
- non-selected tools staying out;
- learning human approval requirement;
- mission trace integrity;
- mission result consistency;
- mission results archive;
- global action budget;
- active plan matching mission trace;
- evidence chains trace binding;
- success event contract;
- success evidence contract;
- success artifact contract;
- artifact paths being relative;
- execution posture matching authority;
- mission risk route decisions;
- controlled capability receipts;
- mission artifact receipts;
- optional project scope boundary.

## Success Contract

For a successful run, the final gate expects:

- terminal phase agrees with success flag;
- required success events exist;
- required evidence chain types exist;
- mission result and mission trace are consistent;
- artifacts and receipts are trace-bound;
- plan and mission trace agree;
- budget and action limits hold.

If a result cannot pass the final gate, it should not be considered certified
even if it created files.
