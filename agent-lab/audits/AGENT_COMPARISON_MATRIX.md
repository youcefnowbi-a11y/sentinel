# Agent Comparison Matrix

Date: 2026-04-26
Mode: source-only forensic comparison.

| Vendor | Commit | Core strength | Source-backed mechanism | High-risk surface | Sentinel rewrite |
| --- | --- | --- | --- | --- | --- |
| OpenClaw | `a2288c2b09e621f89a915960398f58e200b3b69d` | Runtime, channels, skills, gateway, approval UI patterns | Canonical scanner: `agent-lab/audits/openclaw_scanner_report.json`; static audit: `agent-lab/audits/openclaw_static_audit.md` | 83 scanned items; 52 blocked, 29 needs review, 2 draft-only in B2.5 scanner | Keep scanner/policy ideas. Do not bridge runtime. |
| Hermes Agent | `35c57cc46b88710a98c4d43107b87b4ab828e3eb` | Memory, skills, delegation, prompt composition, tool hooks | `AIAgent` init and budgets (`run_agent.py:844-946`), memory setup (`run_agent.py:1596-1704`), skill prompt index (`prompt_builder.py:621-708`), dispatcher hooks (`model_tools.py:498-630`) | Memory/plugin injection, external providers, skill auto-maintenance, messaging extras, Google Workspace skill install path | Rewrite memory and skills as permissioned, scanned, non-policy context. |
| OpenJarvis | `484d0f090b127a9b8a00f02d64c35428cb7be706` | Local-first routing, hardware-aware model choice, learning metrics, skill import | `recommend_engine`, `recommend_model`, `estimated_download_gb` (`core/config.py:209-300`), learning weights (`core/config.py:667-675`), `AgentConfigEvolver` (`learning/agents/agent_evolver.py:52-223`) | Skill import/sync from remote sources, direct skill run, learned config mutation, many channel extras | Rewrite CostRouter and SkillImporter with budget caps, sandbox scan, and approval gates. |
| JARVIS | `7b66f0d3c77a4d050d56ff98b5723fd00b9fb937` | Daemon, authority model, approval lifecycle, sidecar, desktop/browser awareness | `AuthorityEngine.checkAuthority` (`authority/engine.ts:61-175`), `ApprovalManager` (`authority/approval.ts:31-196`), sidecar JWT/enrollment (`sidecar/manager.ts:28-277`), sidecar RPC (`sidecar/handlers.go:15-67`) | Terminal shell, browser submit, desktop control, screenshots, clipboard, sidecar config mutation, token handling | Rewrite PermissionedSidecar and AuthorityGate with critical-action hard blocks and explicit user approval. |

## Cross-Agent Pattern Synthesis

| Pattern | Vendors showing it | Forensic conclusion | Sentinel target |
| --- | --- | --- | --- |
| Prompt/context assembly | Hermes, JARVIS | Both inject contextual memory/profile/role data into prompts. Hermes scans project context for injection; JARVIS labels user profile as untrusted (`roles/prompt-builder.ts:149-157`). | Sentinel prompt compiler must label every context block by trust level and source. |
| Memory as behavior substrate | Hermes, JARVIS | Durable memory is powerful but can poison future sessions if interpreted as instructions. | Memory is context only; policy lives in signed config. |
| Skills/plugins | OpenClaw, Hermes, OpenJarvis | Skills create leverage and supply-chain risk. | Skills require manifest, static scan, sandbox eval, risk class, approval, trace. |
| Channels/external messaging | OpenClaw, Hermes, OpenJarvis, JARVIS | Channel sends create reputation, privacy, and compliance risk. | Outbound communication is draft-only until approval and compliance gates exist. |
| Browser/desktop control | OpenClaw, JARVIS | App-specific templates make agents useful but can send or submit real-world actions. | Browser is read-only first; submit/send/publish are critical actions. |
| Local/cloud/cost routing | Hermes, OpenJarvis | Cost control is an architecture concern, not a UI afterthought. | Budget per run; route by risk, evidence depth, model capability, and spend cap. |

## Current Ranking For Sentinel Rewrites

1. Now: CueIdea-backed evidence normalization, GTM pack quality, trace ledger, firewall, skill scanner.
2. Next: CostRouter, memory context with source/trust labels, plugin manifest scanner.
3. Later: read-only browser sandbox, permissioned sidecar, channel adapters.
4. Avoid for now: shell execution, browser submit, real outbound messages, desktop automation, vendor bridges.
