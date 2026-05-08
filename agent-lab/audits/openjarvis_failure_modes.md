# OpenJarvis Failure Modes

Date: 2026-04-26

| Failure | Source evidence | Trigger | Impact | Sentinel prevention | Eval |
| --- | --- | --- | --- | --- | --- |
| Cost/routing misclassification | `core/config.py:209-300` | Hardware string or memory estimate chooses wrong engine/model | Slow run, OOM, poor output | Observed telemetry, fallback, budget cap | Model route fallback eval |
| Learned config mutation | `learning/agents/agent_evolver.py:193-223` | Trace analysis writes agent TOML | Behavior drift | Proposal-only learning | No auto-mutation eval |
| Biased scoring | `learning/agents/agent_evolver.py:323-362` | Sparse/bad traces produce high score | Wrong agent/tool preference | Minimum sample and confidence gates | Low-sample eval |
| Skill import supply chain | `cli/skill_cmd.py:162-245`, `:258-349` | Import/sync from Hermes/OpenClaw/GitHub | Malicious prompt/script | Quarantine and scanner | Untrusted import eval |
| Script import risk | `skills/importer.py:128-135` | `with_scripts=True` copies scripts | Code execution path | Scripts disabled until sandbox | Script quarantine eval |
| Dangerous skill capability | `skills/security.py:11-55` | Skill requires shell/network/filesystem write | Host or network risk | Firewall risk class | Capability gate eval |
| Browser automation | `pyproject.toml` browser extra | Browser tool enabled | Form submit/external state change | Read-only browser first | Browser submit eval |
| Channel credentials | `pyproject.toml` channel extras | Real channel starts with credentials | External send/privacy risk | Draft-only channels | Fake channel send eval |
| Secret scanner bypass | `core/config.py:1051-1064` | Scan mode redacts/warns but tool proceeds | Secret leakage | Secret scan is hard gate for high-risk tools | Secret exfil eval |

## Sentinel Product Lessons

1. Cost routing is core infrastructure.
2. Skill import must be treated like package installation.
3. Learning can improve configuration, but only through reviewable proposals.
4. Security config must be enforced by code, not treated as advisory CLI settings.
