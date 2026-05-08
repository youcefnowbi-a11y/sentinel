# Brain Eval And Certification

Date: 2026-04-28
Status: Core Brain Lock documentation

## Purpose

The brain must be measured with tests that prove invariants, not just happy-path
output creation.

Certification has four levels:

```text
unit tests
-> runtime trace certification
-> replay/final gate acceptance
-> execution-boundary primitive scan
```

## Current Test Surface

The core test suite covers:

- agent models;
- event bus;
- invariants;
- runtime;
- runtime certification;
- trace replay;
- final gate;
- tool selection;
- tool-call protocol;
- hypothesis verification;
- world model;
- effort router;
- repair loop;
- evidence chain;
- eval bench;
- artifact capture;
- controlled capability;
- execution posture;
- capability registry;
- mission kernel;
- mission risk/reviewer/success;
- GTM pack and quality.

## Eval Bench Doctrine

`SentinelEvalBench` exists to keep future capability work measurable. Every new
capability should add:

- fail-to-pass cases: the capability solves a gap that previously failed;
- pass-to-pass cases: existing brain invariants remain true;
- negative cases: forbidden actions remain blocked;
- repeated runs where relevant;
- fixture-driven tests before real runtime use.

## Brain Freeze Criteria

The brain can be considered frozen for module-harvest work only when:

- full sentinel-core tests pass;
- compile check passes;
- public API exports have no missing exports or duplicates;
- execution-boundary primitive scan shows no live shell/browser/email/payment/desktop
  execution in the certified core;
- `CoreFinalGate` accepts a clean local run;
- `CoreFinalGate` rejects forged or untraceable success;
- docs in this folder match current code behavior;
- no vendor runtime code is imported into production.

## Required Commands

Recommended local verification:

```powershell
python -m pytest sentinel-control\services\sentinel-core\tests -q
python -m compileall sentinel-control\services\sentinel-core\sentinel sentinel-control\services\sentinel-core\tests
rg -n -i "subprocess|os\.system|child_process|exec\(|eval\(|browser_submit|email_send|payment|credential|desktop" sentinel-control\services\sentinel-core\sentinel sentinel-control\services\sentinel-core\tests
```

The scan is a signal, not a proof by itself. Findings must be classified as:

- live executable primitive;
- blocklist/classifier/policy text;
- fixture/test case;
- documentation.

Only the first category blocks Brain Freeze.

## Review Standard

Before adding Browser, Sidecar, Channels, or Shell Sandbox, run a fresh review
on the exact boundary:

- what new authority is requested;
- what new side effects become possible;
- what dry-run exists;
- what receipt proves the result;
- what eval blocks abuse;
- what final-gate check must be added.
