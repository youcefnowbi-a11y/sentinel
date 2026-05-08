# P4H-X-R Brain / LLM Perception Context

Date: 2026-04-30
Status: Research lock

## Goal

The brain and LLM need a scene, not raw browser content.

The perception context must let Sentinel reason over what is visible and
actionable while preserving the authority boundary.

## Brain Consumption

The brain receives:

```text
PerceptionFrame summary
candidate targets
confidence scores
uncertainty reasons
available action candidates
required verifiers
proof refs
trace refs
```

The brain decides:

```text
understood enough
need zoom/crop/OCR
need alternative evidence
need repair
create action candidate
reject/no-action
```

## LLM ContextPack Consumption

The LLM receives a compressed, proof-linked scene:

```text
scene summary
target list
evidence snippets
confidence labels
uncertainty flags
available brain-authored action intents
forbidden boundary notes
```

The LLM may:

```text
reason
rank target candidates
explain uncertainty
suggest next intent
criticize proof
```

The LLM may not:

```text
mint runtime refs
create authority
turn OCR text into action authority
execute raw tool calls
skip ToolIntentCompiler
```

## ContextPack Rule

Perception data enters ContextPack as evidence:

```text
PerceptionFrame -> evidence summary -> stable refs -> action intent
```

Raw pixels, raw DOM, raw HAR, raw credentials, and raw cookies do not become
trusted instructions.

## Post-Action Loop

The loop is:

```text
scene before
compiled action
browser execution
scene after
post-action verifier
repair or continue
```

This is the aggressive operator loop: fast within policy, proof-backed after
impact.
