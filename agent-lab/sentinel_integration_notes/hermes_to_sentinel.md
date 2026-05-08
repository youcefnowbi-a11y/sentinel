# Hermes To Sentinel Rewrite Notes

Date: 2026-04-26
Rule: rewrite, do not integrate.

## What Sentinel Should Learn

1. Persistent memory is valuable when it stores stable facts, preferences, and outcomes.
2. Skill indexes are useful when they are compact and conditionally loaded.
3. Tool hook points are necessary for observability and policy.
4. Delegation needs explicit budgets and approval propagation.
5. Prompt injection scanning must happen before context enters prompts.

## What Sentinel Must Not Copy

- Hermes runtime.
- Hermes skills.
- Hermes memory provider plugins.
- Hermes Google Workspace setup.
- Hermes tool dispatcher.
- Hermes gateway/channel code.

## Sentinel Rewrites

| Hermes mechanism | Rewrite |
| --- | --- |
| `MemoryStore` file-backed durable memory | `SentinelMemoryStore` with typed records, scope, trust, expiry, and no policy directives |
| `MemoryManager` external provider | `MemoryProviderManifest` with scanner, provenance, and no secret access by default |
| `build_skills_system_prompt` | `SkillIndexCompiler` from scanned manifests only |
| `_scan_context_content` | `ContextTrustScanner` over files, web evidence, memory, and skills |
| `model_tools` hooks | `FirewallDispatchPipeline` with fail-closed policy and traceable transforms |
| `delegate_task` | `SubagentPlan` with parent permission inheritance and trace tree |

## Firewall Implications

- Memory write: medium risk if durable; high if contains credentials, policies, or external identity data.
- Skill activation: medium by default; high/critical if scripts, shell, browser, network, or secrets appear.
- Delegation: medium; high if child can access external tools.
- Google Workspace: high/critical; disabled until dedicated product plan.

## Trace Requirements

- `memory.read`
- `memory.write`
- `context.scan`
- `skill.scan`
- `skill.index.compile`
- `skill.invoke.proposed`
- `subagent.spawn.proposed`
- `tool.firewall.precheck`
- `tool.firewall.result`

## Required Evals

- Prompt injection in project context.
- Memory-as-policy attempt.
- Skill script execution attempt.
- OAuth scope expansion attempt.
- Subagent tool-permission bypass.
- Tool hook policy-failure fail-closed behavior.
