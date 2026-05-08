# P4H-X-R Aggressive Operator Doctrine

Date: 2026-04-30
Status: Research lock

## Doctrine

Sentinel must become a powerful operator, not an audit room.

```text
Power-first.
Mission-governed.
Proof-backed.
```

This replaces defensive language with operator language.

## Vocabulary Shift

| Old wording | New wording |
| --- | --- |
| safe action | granted action |
| dangerous action | impactful / irreversible / external action |
| blocked action | out-of-scope action |
| risky action | higher-authority action |

The classification axes are:

```text
authority
impact
reversibility
externality
blast radius
mission scope
credentialed state
uncertainty
```

## Operating Rule

```text
Inside compiled mission policy: execute fast.
At boundary: escalate or reject.
After impact: verify automatically.
On failure: repair automatically.
```

This is not unrestricted execution. The point is to remove repeated
micro-friction after a mission has already granted the relevant authority.

## What Stays

```text
MissionAuthorityEnvelope
ToolRegistry
ToolIntentCompiler
Controlled runners
receipts
trace
FinalGate
mission boundaries
```

## What Changes

The default posture changes from:

```text
ask whether a capability is safe at every step
```

to:

```text
compile mission authority once
execute decisively inside it
verify and repair continuously
stop sharply at boundaries
```

## Source Alignment

- OpenAI Computer Use and Anthropic Computer Use both center the loop around
  screen state, action, and updated screen state. Sentinel should adopt that
  tempo, but keep its mission authority layer.
- OWASP agent guidance reinforces tool scoping, explicit permission boundaries,
  logging, and sensitive-tool handling. Sentinel should make those boundaries
  compiled and fast, not conversational friction.
- NIST AI RMF frames governance as a lifecycle function. Sentinel should embed
  that in mission policy rather than retrofit it after execution.

References:

```text
OpenAI Computer Use: https://platform.openai.com/docs/guides/tools-computer-use
Anthropic Computer Use: https://docs.anthropic.com/en/docs/build-with-claude/computer-use
OWASP AI Agent Security: https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
```

## Final Rule

```text
Sentinel is not constrained by fear.
Sentinel is constrained by mission law.
```
