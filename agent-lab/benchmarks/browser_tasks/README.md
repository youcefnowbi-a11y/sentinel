# Browser Tasks

Browser automation benchmark work is now organized around Browser Fluency:
whether the agent can operate a browser smoothly across lifecycle, navigation,
visual perception, state, forms, files, network diagnostics, research, safety,
and repair.

Primary catalog:

```text
browser_fluency_missions.json
```

Current catalog:

```text
12 groups
72 missions
levels F0-F5
```

Current runner profiles:

```text
first_subset = P4H-R critical subset, 42 executed missions
hardened_full = P4H-S full corpus, 72 executed missions, 18 partial missions
depth_hardened = P4H-T depth corpus, 72 target-met contract fixtures
```

Current live runner:

```text
browser_fluency_live_runner.py = P4H-U live self-hosted fixture runner
12 representative missions
30 runs per mission
360 total local HTTP iterations
--scope full = P4H-V full live self-hosted fixture runner
72 missions
30 runs per mission
2160 total local HTTP iterations
```

Current visual runner:

```text
browser_visual_engine_runner.py = P4H-W real browser-engine visual fixture runner
6 BF-VIS missions
30 runs per mission
180 total Playwright read-only fixture iterations
OCR fallback only, never authority
```

Current operator runners:

```text
browser_operator_trial_runner.py = P4H-Y operator trial
6 missions
30 runs per mission

browser_operator_hardening_runner.py = P4H-Z hardening trial
8 missions
30 runs per mission

browser_operator_cross_class_runner.py = P4H-AA V3 ActionEngine routing
10 missions
30 runs per mission
routes existing Browser V3 classes through ActionEngine

browser_operator_long_horizon_runner.py = P4H-AB long-horizon operator trial
10 missions
30 runs per mission
read -> act -> verify -> repair -> continue flows through ActionEngine

browser_operator_live_long_horizon_runner.py = P4H-AC live long-horizon operator harness
10 missions
30 runs per mission
self-hosted live pages -> ActionEngine -> V3 receipts -> FinalGate

browser_operator_open_web_like_hardening_runner.py = P4H-AD open-web-like hardening harness
10 missions
30 runs per mission
messy pages, weak DOM/AX, overlays, dynamic state, network repair, visual tempo cache
```

Allowed for benchmark fixtures:

- open/close public contexts;
- navigate allowed public URLs;
- read and cite public test pages;
- capture screenshots/crops/zoom artifacts;
- use OCR stubs or isolated OCR fixtures;
- use fixture cookies/storage/sessions;
- submit safe fixture forms only under authority;
- download quarantine fixtures;
- upload certified Sentinel artifacts;
- capture redacted HAR/body fixtures;
- test prompt-injection and stale-ref denial;
- test repair/loop/cognitive signals.

Blocked for now:

- submitting non-fixture forms;
- logging into real accounts;
- using the user's real browser profile;
- saving passwords or raw cookies;
- bypassing CAPTCHA/bot walls;
- payment or destructive external actions;
- host browser profile access.
