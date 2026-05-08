# P4H-AF Lock Verdict

Date: 2026-05-07
Status: Locked

## Verdict

P4H-AF is accepted as full locked.

```text
runtime integrated browser mini-corpus = implemented
AgentRuntime mini-corpus route = implemented
MissionRunner mini-corpus route = implemented
CoreFinalGate mini-corpus proof = passing
new browser powers = none
```

## What Is Now Proven

P4H-AF proves that the P4H-AE browser runtime route can execute a bounded
multi-case browser corpus, not only one form-submit route.

The mini-corpus covers:

```text
messy duplicate context
weak DOM/AX target binding
dynamic post-action state
same-origin redirect revalidation
deep-scroll budget pressure
fabricated runtime-ref denial
action-budget denial
```

## What Passed

```text
targeted P4H-AF tests = 5 passed
neighbor regression tests = 84 passed
full sentinel-core tests = 516 passed
false_action_rate = 0.0
```

## Boundary

P4H-AF does not prove:

```text
open-web external success
real peer superiority
real account login
CAPTCHA/bot-wall handling
desktop/image/PDF/video runtime
new browser authority classes
```

It proves runtime-integrated breadth over the existing governed
`browser_form_submit` route.

## Decision

Browser runtime mini-corpus integration is locked.

Next phase is intentionally not started in this verdict.
