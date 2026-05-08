# P4C-S Live Adapter Corpus

Date: 2026-04-29
Status: Implemented

## Corpus Groups

P4C-S defines nine measured groups:

| Group | Purpose |
| --- | --- |
| public_evidence_interaction | evidence plus limited interaction proof |
| form_submit | governed public commit with post-action proof |
| download_quarantine | bounded file capture into quarantine |
| upload_authorized | upload from Sentinel-captured artifact only |
| private_login_cookie | private session, account-id login, cookie/storage summary, close |
| js_no_network | runtime network-attempt rejection |
| har_redaction | bounded HAR/body capture with redaction proof |
| cross_class_flow | private session to login to cookie summary to HAR to close |
| failure_denials | stale ref, prompt-injection ref, cross-origin result, credential leak attempt |

## Runtime Character

The corpus mixes deterministic local adapters and Playwright-backed local live
fixtures:

- public interaction, form submit, download, and upload use bounded local
  backends to keep the measurement stable;
- private/login/cookie/HAR and JS no-network paths use the P4C-H.3 local
  Playwright-backed harness;
- no public internet target is required;
- no new Browser V3 authority class is created.

## Why This Is Enough For P4C-S

P4C-S is a measured readiness gate, not a public benchmark claim.

The corpus proves that Browser V3 authority classes can be exercised together
through EvalBench with repeated runs and stable signatures.

## What Still Needs External Benchmarking

External browser supremacy still requires:

- a larger live site corpus;
- repeated cross-class missions across heterogeneous pages;
- external failure injection;
- comparison against a peer browser agent using the same task definitions.
