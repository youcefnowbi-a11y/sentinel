# P4H-X-R Perception/Action Engine Research

Date: 2026-04-30
Status: Research lock

## Research Question

Should P4H-W remain a Browser visual harness, or become the prototype for a
general perception/action system?

Verdict:

```text
P4H-W is the prototype.
P4H-X code should create PerceptionEngine v0 + ActionEngine v0.
Browser remains the only active backend for v0.
```

## Architecture Target

```text
MissionAuthorityEnvelope
-> CompiledMissionPolicy
-> PerceptionEngine
-> SceneGraph / PerceptionFrame
-> Brain decision
-> ActionEngine
-> Browser backend
-> PostActionVerifier
-> Evidence / Receipt / FinalGate
```

## Why This Is Needed

Browser-only visual hardening would create a strong browser but not a coherent
agent sensory system. Desktop, image, PDF, and video work would later recreate
the same ideas:

```text
screenshot
crop
OCR
target grounding
action candidate
post-action verification
repair
```

So P4H-X should lift the browser visual path into a reusable perception/action
contract while keeping runtime execution limited to the browser backend.

## Research Signals

| Source | Signal for Sentinel |
| --- | --- |
| OpenAI Computer Use | Computer-use agents operate through repeated screenshot/action loops. |
| Anthropic Computer Use | Tooling exposes screen, mouse, keyboard, and isolated environment control. |
| VisualWebArena | Web agents need visually grounded task evaluation, not only DOM reasoning. |
| OSWorld | Real computer workflows require execution-based evaluation. |
| SeeClick / ScreenSpot | GUI grounding is a central bottleneck for visual agents. |
| ScreenSpot-Pro | High-resolution professional UIs expose small-target and complex-layout weakness. |
| UI-E2I / UI-I2E | Existing GUI benchmarks can overestimate agents by using large elements and explicit instructions. |

## Source References

```text
OpenAI Computer Use: https://platform.openai.com/docs/guides/tools-computer-use
OpenAI CUA overview: https://openai.com/index/computer-using-agent/
Anthropic Computer Use: https://docs.anthropic.com/en/docs/build-with-claude/computer-use
VisualWebArena: https://aclanthology.org/2024.acl-long.50/
OSWorld: https://os-world.github.io/
SeeClick / ScreenSpot: https://arxiv.org/abs/2401.10935
ScreenSpot-Pro: https://arxiv.org/abs/2504.07981
UI-E2I / UI-I2E: https://www.microsoft.com/en-us/research/articles/ui-e2i-synth-realistic-and-challenging-ui-grounding-benchmark-for-computer-use-agents/
OWASP AI Agent Security: https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
```

## Decision

P4H-X code should not be another browser-only benchmark pass. It should be the
first implementation of a general architecture:

```text
perception -> action candidate -> compiled mission policy -> action -> verifier
```

Runtime remains browser-only until the kernel proves itself.
