# P4H-AD Browser Operator Open-Web-Like Hardening

Date: 2026-05-01
Status: Implemented

## Goal

P4H-AD hardens the browser operator against open-web-like page conditions
without adding new powers.

The executable runner is:

```text
agent-lab/benchmarks/browser_tasks/browser_operator_open_web_like_hardening_runner.py
```

## What Changed

P4H-AC proved live long-horizon operation on self-hosted pages.
P4H-AD makes those pages harder:

```text
messy duplicated targets
weak DOM/AX targets
covered targets / overlays
dynamic state after action
network failures and repair
same-origin redirect revalidation
deep scroll targets
visual prompt injection / OCR contradiction
cookie/HAR no-leak checks
end-to-end open-web-like pack
```

## Visual Tempo Hardening

P4H-AC showed that the rendered visual verifier is the main latency pressure.
P4H-AD adds a targeted visual verifier cache:

```text
first visual proof = cold rendered screenshot/crop/zoom verifier
same static visual fixture = cached proof hash reuse
cache does not grant authority
runtime ref binding remains required
```

The cache reduces repeated visual verifier latency while preserving the rule:

```text
visible != understood != actionable != authorized
```

## Operator Path

P4H-AD keeps the same central path:

```text
self-hosted live observation
-> PerceptionFrame / SceneActionCandidate
-> CompiledMissionPolicy
-> ActionEnvelope
-> BrowserControlledCapabilityRunner
-> Browser V3 executor
-> receipt / event
-> CoreFinalGate
```

## Mission Groups

```text
BF-OPENWEB-001 messy duplicate context -> submit
BF-OPENWEB-002 weak DOM/AX -> visual binding -> action
BF-OPENWEB-003 overlay covered target -> repair
BF-OPENWEB-004 dynamic state -> after-action verification
BF-OPENWEB-005 network failure -> alternative path
BF-OPENWEB-006 redirect -> revalidate -> submit
BF-OPENWEB-007 deep scroll -> budget pressure
BF-OPENWEB-008 visual injection -> OCR denial -> runtime ref required
BF-OPENWEB-009 cookie/HAR -> no raw leak
BF-OPENWEB-010 end-to-end open-web-like final pack
```

## Boundary

P4H-AD does not add:

```text
new Browser V3 authority classes
desktop runtime
OS mouse/keyboard
real account login
real user browser profile access
non-fixture external submit
open-web supremacy claim
real peer runtime comparison
```

It is a harder self-hosted corpus, not an external web campaign.
