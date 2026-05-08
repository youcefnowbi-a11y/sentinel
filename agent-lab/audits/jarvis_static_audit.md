# JARVIS Static Forensic Audit

Date: 2026-04-26
Mode: source-only, no install, no runtime.

## Source Inventory

| Field | Value |
| --- | --- |
| Repository | `https://github.com/vierisid/jarvis` |
| Local source | `agent-lab/vendors/jarvis/source` |
| Commit | `7b66f0d3c77a4d050d56ff98b5723fd00b9fb937` |
| Clone size | 556 files / 5,481,611 bytes |
| Runtime | Bun/TypeScript daemon plus Go sidecar |
| Dependency manager | `package.json`, `bun.lock`, `sidecar/go.mod` |
| Entrypoints | `bin/jarvis.ts`, `src/daemon/index.ts`, sidecar Go binary |
| Install/runtime status | Not installed, not run |

## Install-Time And Runtime Scripts

- `package.json` exposes `start`, `dev`, `setup`, `test`, `setup:google`, `postinstall`, `prepare`, and UI build scripts.
- `postinstall` runs `node scripts/ensure-bun.cjs` and attempts `bun run copy:models` (`agent-lab/vendors/jarvis/source/package.json`).
- `install.sh` can install dependencies and set up CLI paths; it was not run.
- `Dockerfile` runs `bun install --frozen-lockfile`; Docker was not run.

## Core Subsystems

| Subsystem | Source paths | Purpose | Sentinel lesson |
| --- | --- | --- | --- |
| Authority model | `agent-lab/vendors/jarvis/source/src/roles/authority.ts:3-45`; `src/authority/engine.ts:61-175` | Map action categories to authority levels and approval decisions | Sentinel needs risk-based policy independent of role level |
| Approval lifecycle | `src/authority/approval.ts:31-196` | Persist pending/approved/denied/expired/executed approval requests | Sentinel approval records need dry-run, evidence refs, risk score |
| Audit trail | `src/authority/audit.ts:23-158` | Log tool decision, action category, execution, timing | Sentinel Trace Ledger should include raw and transformed outputs |
| Sidecar enrollment | `src/sidecar/manager.ts:28-277`, `:395-455` | ES256 keys, JWT token enrollment, WS connect/register | Sentinel sidecar must be capability-scoped and revocable |
| Sidecar capabilities | `src/sidecar/types.ts:7-14`; `sidecar/handlers.go:15-67` | Terminal, filesystem, desktop, browser, clipboard, screenshot RPCs | High-impact powers require manifest, sandbox, approval |
| Desktop tools | `src/actions/tools/desktop.ts:268-615` | Window list, snapshot, click/type/keys/app launch/screenshot | Desktop actions are critical until sanitizer/approval exists |
| Terminal | `src/actions/terminal/executor.ts:16-67`; `sidecar/handlers.go:71-133` | Shell command execution with timeout | Sentinel v1 blocks shell |
| Webapp templates | `webapp-templates/whatsapp.yaml:18-24`; `webapp-templates/slack.yaml:67-83` | App-specific browser/desktop action recipes | Browser agents need dry-run and submit/send gates |
| Vault/memory | `src/vault/retrieval.ts:47-149`; `src/vault/schema.ts`; `src/vault/vectors.ts:64-81` | Knowledge graph retrieval and vector table placeholder | Sentinel memory needs provenance and trust labels |

## Forensic Conclusion

JARVIS is the strongest specimen for sidecar, daemon, authority, and desktop/browser awareness. It is also the clearest proof that these powers must not enter Sentinel until risk scoring, approval, sandboxing, trace, and evals are mature.

## Lab Notes

Commands run:

- Git source checks and file inventory.
- Targeted reads of authority, approval, sidecar, terminal, desktop, vault, and webapp template files.

Commands intentionally not run:

- `bun install`, `bun run start`, `jarvis`, `jarvis-sidecar`, `install.sh`, Docker build/run, Google setup, browser/desktop/terminal tools.

Next experiment:

- Build sidecar capability fixture scanner and fake sidecar benchmark; no real sidecar.
