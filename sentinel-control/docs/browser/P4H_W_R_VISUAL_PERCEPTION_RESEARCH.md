# P4H-W-R Visual Perception Research

Date: 2026-04-30
Status: Research locked

## Question

Should Sentinel implement P4H-W as a simple OCR/screenshot harness?

## Verdict

No.

Modern browser/computer-use agents do not become strong by adding OCR alone.
The useful pattern is hybrid:

```text
rendered screenshot
+ UI/DOM/AX structure
+ coordinate/action grounding
+ crop/zoom/refinement
+ post-action screenshot verification
+ safety and prompt-injection gating
```

OCR is only one fallback channel, mainly for text trapped inside images or PDFs.

## Research Signals

### VisualWebArena

VisualWebArena exists because many web tasks require visual grounding, not just
text extraction. It extends WebArena-style self-hosted task environments with
visual and textual requirements.

Sentinel decision:

```text
P4H-W must test visually grounded tasks, not only OCR text extraction.
```

### WebVoyager

WebVoyager-style agents use screenshots plus auxiliary text/element metadata and
emit browser actions. Reported failure modes include navigation limits and
visual grounding errors.

Sentinel decision:

```text
visual perception must be evaluated together with action grounding and recovery.
```

### OpenAI CUA / Operator Pattern

OpenAI's computer-use model pattern is screen, mouse, and keyboard. The loop is:

```text
observe screenshot
choose action
execute action
capture new screenshot
repeat
```

Sentinel decision:

```text
P4H-W must include screenshot-after-action verification.
```

### Anthropic Computer Use Pattern

Anthropic's computer use tool also centers on screenshots and mouse/keyboard
control, with the host loop sending environment state back after actions.

Sentinel decision:

```text
visual state is an observation stream, not authority.
```

### OSWorld / GUI Grounding

OSWorld and GUI-grounding research show that the hard problem is not just
seeing pixels. The hard part is grounding instructions to the correct UI element
and completing workflows robustly.

Sentinel decision:

```text
P4H-W must score grounding correctness, not just OCR accuracy.
```

## Implication For Sentinel

P4H-W should not be:

```text
take screenshot
run OCR
call it visual perception
```

P4H-W should be:

```text
real browser screenshot
-> DOM/AX/UIObservation overlay
-> crop/zoom target regions
-> optional OCR for image text
-> visual grounding score
-> post-action screenshot verifier
-> evidence receipt + FinalGate boundary
```

## Research Sources

- VisualWebArena, ACL 2024: https://aclanthology.org/2024.acl-long.50/
- WebVoyager paper entry: https://arxiv.org/abs/2401.13919
- OpenAI Computer-Using Agent: https://openai.com/index/computer-using-agent/
- OpenAI Computer Use API guide: https://platform.openai.com/docs/guides/tools-computer-use
- Anthropic Computer Use docs: https://docs.anthropic.com/en/docs/build-with-claude/computer-use
- OSWorld benchmark: https://os-world.github.io/
- SeeClick / GUI grounding: https://aclanthology.org/2024.acl-long.505/
