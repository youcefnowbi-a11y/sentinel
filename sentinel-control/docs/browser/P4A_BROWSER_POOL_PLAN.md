# P4A Browser Pool Plan

Status: implemented as public/stateless pool accounting

P4A adds `BrowserPublicPoolManager`, a warm-instance ledger for public browser work.

## Pool Contract

Each instance is recorded with:

- instance id
- backend kind
- status
- mission id
- lease id
- public/stateless boundary flags
- health notes

Each lease records:

- lease id
- mission id
- instance id
- purpose
- status
- trace refs

## Events

P4A emits:

- `BROWSER_ADVANCED_POOL_STARTED`
- `BROWSER_ADVANCED_POOL_LEASED`
- `BROWSER_ADVANCED_POOL_RELEASED`

## FinalGate

FinalGate rejects:

- invalid capacity;
- missing instance ids;
- duplicate lease ids;
- release for unknown lease;
- release with instance mismatch;
- stateful boundary flags.

## Boundary

This pool remains public/stateless. It does not persist cookies, storage, downloads, credentials, or private profiles.
