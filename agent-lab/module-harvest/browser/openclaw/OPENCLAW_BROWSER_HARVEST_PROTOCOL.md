# OpenClaw Browser Harvest Protocol

Date: 2026-04-28
Status: static analysis only

## Objective

Extract browser engineering knowledge without importing browser authority.

The target Sentinel capability is read-only public web evidence:

```text
open public URL
extract title/text/links/citations
capture bounded artifacts
detect prompt injection
write EvidenceChain + receipt
```

## Hard Bans During Harvest

- No runtime launch.
- No browser opening.
- No dependency install.
- No credential use.
- No profile import.
- No cookies or sessions.
- No live page navigation.
- No external network request made by the harvest process.
- No copying vendor runtime into `sentinel-control`.

## Static Review Sequence

1. Source map browser-related files.
2. Identify entrypoints.
3. Map dependencies and lifecycle.
4. Map security controls.
5. Map tests worth adapting.
6. Classify files:
   - `copy_candidate`
   - `rewrite_required`
   - `adapter_only`
   - `test_pattern_only`
   - `docs_only`
   - `reject`
7. Draft Sentinel capability contract.
8. Build fake eval dataset before implementation.
9. Implement Sentinel-owned adapter later.

## Questions To Answer Before P3A

- What starts the browser service?
- What paths expose observe versus act?
- Which routes are read-only?
- Which routes mutate browser state?
- Where are SSRF and localhost guards implemented?
- How are snapshots represented?
- How are screenshots represented?
- How are downloads handled?
- How are profiles, storage, cookies, and auth separated?
- Which tests prove read-only behavior?
- Which tests prove blocked mutation?
- Which parts are too coupled to reuse?

## Sentinel Mapping

| Harvest Concept | Sentinel Destination |
| --- | --- |
| Browser command taxonomy | Capability manifest and action enums. |
| URL and SSRF guard logic | Mission scope and browser URL guard. |
| Snapshot schema | Evidence item and artifact capture schema. |
| Screenshot capture pattern | Future capture sandbox extension. |
| Browser tests | Fake evals and negative tests. |
| Vendor profile/session model | Reject for P3A; redesign under mission authority. |
| Browser action routes | Reject or dry-run only until separate authority exists. |

## Exit Criteria For Harvest

Harvest is complete only when these docs exist and are reviewed:

- browser tree;
- entrypoint map;
- dependency map;
- security map;
- test map;
- extraction matrix;
- Sentinel browser capability contract;
- fake eval dataset plan.
