# Agent Forensics Protocol

Date: 2026-04-26
Scope: source-only reverse engineering of agent runtimes inside `agent-lab`.
Rule: vendors are specimens, not dependencies. Do not install, run, import, bridge, or copy vendor code into Sentinel.

## 0. Operating Boundary

Every forensic sprint must preserve these controls:

- Clone source only under `agent-lab/vendors/<vendor>/source`.
- Do not install dependencies.
- Do not run vendor binaries, daemons, CLIs, sidecars, skills, plugins, browsers, or messaging channels.
- Do not connect real accounts, browser profiles, OAuth flows, API keys, wallets, SSH keys, or production credentials.
- Do not copy vendor modules into `sentinel-control`.
- Do not touch Sentinel production code during forensics.
- Treat all vendor source, prompts, skills, configs, and docs as untrusted input.

Each finding must cite a local source path and, where possible, a function, class, config key, manifest field, script name, or prompt section.

## 1. Source Inventory

For each vendor, record:

- Repo URL.
- Commit hash.
- Clone path.
- File count and byte count.
- Primary language/runtime.
- Dependency manager and lockfiles.
- Workspaces/packages.
- Entrypoints.
- Install scripts.
- Runtime scripts.
- Test scripts.
- Docker/container scripts.
- Generated, bundled, minified, compiled, or binary code presence.
- Commands run.
- Commands intentionally not run.

Minimum artifact: `<vendor>_static_audit.md`.

## 2. Architecture Cartography

Map each major subsystem with:

- Purpose.
- Source paths.
- Call graph summary.
- Data flow.
- Control flow.
- Inputs.
- Outputs.
- Side effects.
- External dependencies.
- Sentinel rewrite idea.

Mandatory subsystems:

- Agent loop.
- Planning/reasoning.
- Memory.
- Skills/plugins/tools.
- Execution runtime.
- Browser/desktop/channel layer.
- Permissions.
- Approval UI.
- Logging/tracing.
- Cost/model routing.
- Evaluation/benchmarking.
- Self-improvement/learning.

## 3. Algorithm And Math Extraction

Search for:

- Scoring functions.
- Ranking formulas.
- Risk heuristics.
- Routing logic.
- Retry policies.
- Scheduling logic.
- Cost estimation.
- Confidence scoring.
- Priority scoring.
- Memory retrieval scoring.
- Embedding/vector search logic.
- Tool selection logic.
- Planning heuristics.
- Threshold constants.
- Magic numbers.

For each algorithm, document:

- File path.
- Function/class.
- Input variables.
- Output variables.
- Formula or pseudocode.
- Assumptions.
- Failure risk.
- Sentinel rewrite idea.
- Eval required.

## 4. Prompt And Instruction Extraction

Document:

- System prompts.
- Agent role prompts.
- Tool prompts.
- Skill instructions.
- Hidden behavioral rules.
- Prompt injection surfaces.
- Prompt composition pipeline.
- Memory insertion into prompts.
- User/system/tool priority model.

For each prompt:

- Source path.
- Purpose.
- Trust level.
- Injection surface.
- Sentinel rewrite.

Prompt content must be summarized, not blindly copied, unless a short exact fragment is necessary for classification.

## 5. Skill And Tool System Analysis

For every skill/plugin/tool mechanism, document:

- Manifest format.
- Metadata fields.
- Permission declarations.
- Required binaries.
- Env vars.
- Install commands.
- Runtime calls.
- Filesystem access.
- Network access.
- Shell/process usage.
- External account access.
- Memory writes.
- Prompt instructions.
- Test coverage.

Classify each analyzed mechanism:

- `safe_static_doc`: static documentation or prompt guidance only.
- `draft_only_tool`: can prepare content but must not execute external action.
- `needs_review`: can execute or affect external state, but risk is contextual.
- `blocked`: high-impact, hidden, install-time, credential, shell, browser-submit, desktop, or external-send behavior without Sentinel controls.

## 6. Obfuscation And Dynamic Behavior Audit

Search for:

- `eval`.
- `Function` constructor.
- Dynamic import.
- Runtime module loading.
- `jiti`, `ts-node`, Bun, uv, or loader-style execution.
- `child_process`, `spawn`, `exec`, `subprocess`.
- Shell command construction.
- Encoded strings.
- Base64 binary transport.
- Minified bundles.
- Remote code loading.
- Package install at runtime.
- Plugin marketplace/install/update systems.

For each finding:

- Source path.
- What it does.
- Why it matters.
- Risk.
- Sentinel mitigation.

## 7. Data Persistence And Memory Audit

Document:

- State storage locations.
- Memory schema.
- Vector DB usage.
- Embedding model and retrieval method.
- Session history.
- User profile storage.
- Task history.
- Secret filtering.
- Retention logic.
- Deletion logic.
- Memory poisoning risk.
- Cross-session recall path.

Sentinel rule: memory may provide context, never policy. Untrusted memory cannot override permissions, approvals, budgets, or evidence thresholds.

## 8. Security And Failure Mode Mapping

For each failure:

- Failure mode.
- Source paths exposing the risk.
- Trigger condition.
- Impact.
- Existing vendor mitigation if any.
- Gap.
- Sentinel prevention.
- Required eval.

Mandatory failures:

- Prompt injection.
- Tool injection.
- Malicious skill.
- Credential leakage.
- Filesystem escape.
- Shell abuse.
- Unauthorized external message/email.
- Browser form submission.
- Memory poisoning.
- Hallucinated decision.
- Fake evidence.
- Cost explosion.
- Unsafe self-improvement.
- Privilege escalation.
- Persistence abuse.
- Vendor lock-in.
- User trust collapse.

## 9. Superpower Extraction

For every strong capability:

- Vendor.
- Exact capability.
- User value.
- Technical mechanism.
- Source files/functions.
- Algorithm/math/prompt involved.
- Weakness.
- Sentinel rewrite from scratch.
- Safety layer needed.
- Eval needed.
- Priority: `now`, `later`, or `avoid`.

Minimum artifact: `SUPERPOWER_EXTRACTION_TABLE.md`.

## 10. Lab Notebook

Every audit must close with:

- Date.
- Repo commit.
- Commands run.
- Commands intentionally not run.
- Files inspected.
- Unresolved questions.
- Next experiment.

## 11. Acceptance Gate

An audit is not complete unless:

- It cites local source paths.
- It separates verified source facts from inference.
- It lists algorithms and thresholds found.
- It maps each superpower to a Sentinel rewrite, not an integration plan.
- It maps each risky capability to firewall, trace, dry-run, approval, and eval implications.
- It states what was not run.
