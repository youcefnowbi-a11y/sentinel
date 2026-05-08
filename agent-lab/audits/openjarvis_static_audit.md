# OpenJarvis Static Forensic Audit

Date: 2026-04-26
Mode: source-only, no install, no runtime.

## Source Inventory

| Field | Value |
| --- | --- |
| Repository | `https://github.com/open-jarvis/OpenJarvis` |
| Local source | `agent-lab/vendors/openjarvis/source` |
| Commit | `484d0f090b127a9b8a00f02d64c35428cb7be706` |
| Clone size | 1,774 files / 30,714,956 bytes |
| Runtime | Python package with optional Rust bridge, Tauri frontend, and Node channel/agent runners |
| Dependency manager | `pyproject.toml`, `uv.lock`, frontend `package.json` |
| Entrypoint | `jarvis = openjarvis.cli:main` (`agent-lab/vendors/openjarvis/source/pyproject.toml`) |
| Install/runtime status | Not installed, not run |

## Major Subsystems

| Subsystem | Source paths | Purpose | Sentinel lesson |
| --- | --- | --- | --- |
| Hardware/model routing | `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:209-300` | Select engine/model by GPU/RAM and model tier | Sentinel CostRouter needs hardware, budget, quality, and risk signals |
| Learning config | `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:545-675`, `:726-760` | Routing policy, SFT/GRPO, DSPy/GEPA, reward weights | Learning must be proposal-only in Sentinel |
| Memory config | `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:761-774` | SQLite backend, top-k, min score, token caps | Evidence/memory retrieval needs thresholds and trace |
| Security config | `agent-lab/vendors/openjarvis/source/src/openjarvis/core/config.py:1043-1064` | Capability policy, input/output scans, secret/PII scanner, audit | Sentinel should formalize these as hard gates |
| Skill import | `agent-lab/vendors/openjarvis/source/src/openjarvis/cli/skill_cmd.py:162-245`, `:258-349` | Install/sync skills from sources | Unscanned imports are blocked |
| Skill importer | `agent-lab/vendors/openjarvis/source/src/openjarvis/skills/importer.py:7-43`, `:62-139`, `:171-192` | Copy skill docs/supporting files; scripts only with opt-in | Good quarantine pattern, but Sentinel needs scanner before install |
| Agent evolution | `agent-lab/vendors/openjarvis/source/src/openjarvis/learning/agents/agent_evolver.py:52-223` | Analyze traces and write new TOML | Useful as improvement proposal only |

## Dependency And Optional Surface

- Optional extras cover local inference, cloud inference, memory backends, server, browser, channels, scheduler, security signing, WASM/Docker sandbox, dashboard, speech, and eval trackers.
- `pyproject.toml` force-includes Node packages under `_node_modules`: Claude Code runner and WhatsApp Baileys bridge.
- Channel extras include Telegram, Discord, Slack, Reddit, Gmail, Twilio, Twitter, Twitch, Matrix-like/XMPP, and others.

## Forensic Conclusion

OpenJarvis is most valuable to Sentinel for:

- budget-aware model choice;
- local-first hardware assumptions;
- reward-weighted learning metrics;
- skill import/sync threat model;
- capability/security config vocabulary.

It is not a runtime to integrate. Its skill import and learning systems are precisely the surfaces Sentinel must rewrite under scanner, approval, trace, and budget controls.

## Lab Notes

Commands run:

- Git source checks and file inventory.
- Targeted reads of `pyproject.toml`, `core/config.py`, `learning/agents/agent_evolver.py`, `cli/skill_cmd.py`, and `skills/*`.

Commands intentionally not run:

- `pip install`, `uv sync`, `jarvis`, `jarvis skill install`, `jarvis skill sync`, `jarvis model pull`, channel logins, dashboard/server, Tauri/frontend installs.

Next experiment:

- Build static extractor for OpenJarvis skill manifests, dangerous capabilities, and learning config writes.
