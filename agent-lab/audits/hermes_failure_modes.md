# Hermes Failure Modes

Date: 2026-04-26

| Failure | Source evidence | Trigger | Impact | Sentinel prevention | Eval |
| --- | --- | --- | --- | --- | --- |
| Context prompt injection | `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:32-75`, `:1045-1085` | Local project context contains hostile instruction | Model obeys untrusted file | Context scanner plus trust labels | Malicious context fixture |
| Memory poisoning | `agent-lab/vendors/hermes-agent/source/tools/memory_tool.py:73-124`; `agent/memory_manager.py:159-180` | Bad memory/provider context enters prompt | Persistent behavior drift | Typed memory and no policy-in-memory | Memory override fixture |
| Skill prompt injection | `agent-lab/vendors/hermes-agent/source/agent/prompt_builder.py:621-708` | Malicious skill metadata appears in index | Unsafe behavior selection | Skill scanner and quarantine | Malicious skill fixture |
| Skill script execution | `agent-lab/vendors/hermes-agent/source/agent/skill_commands.py:137-202` | Skill points agent to scripts | Shell/process execution | Convert to proposed action only | Skill script no-execute eval |
| Runtime install | `skills/productivity/google-workspace/scripts/setup.py:95-120` | Skill setup installs packages | Supply-chain risk | No runtime install | Install command block eval |
| External account access | `skills/productivity/google-workspace/scripts/setup.py:45-56` | OAuth Google Workspace setup | Account data/send access | Least-privilege integration plan only | OAuth scope gate eval |
| Tool hook bypass | `model_tools.py:527-630` | Hook fails or transforms result | Policy/result integrity loss | Fail-closed policy hooks | Hook failure eval |
| Cost explosion | `run_agent.py:844-946`, `:2638-2708` | Long loop and cache miss | High API bill | Budget caps and cache telemetry | Budget/cost eval |
| Unsafe delegation | `tools/delegate_tool.py:55-107`, `run_agent.py:4706-4737` | Subagents auto-approve or multiply work | Tool/cost amplification | Permission inheritance and trace tree | Subagent bypass eval |

## Highest-Value Sentinel Rewrites

1. `SentinelMemory`: typed, scoped, non-policy memory.
2. `ContextTrustScanner`: project context and vendor skill prompt scanner.
3. `SkillScanner`: static scan before skill index.
4. `DelegationBudget`: parent/child budget and permission inheritance.
5. `ToolFirewallDispatcher`: policy hooks fail closed.
