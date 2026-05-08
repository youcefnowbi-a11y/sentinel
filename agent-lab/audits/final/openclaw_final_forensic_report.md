# OpenClaw Final Forensic Report

Date: 2026-04-26
Vendor specimen: OpenClaw
Lab mode: source-only forensic reverse phase
Source path: `agent-lab/vendors/openclaw/source`
Source commit: `a2288c2b09e621f89a915960398f58e200b3b69d`

## Guardrails

This report is a forensic artifact, not an integration plan.

- No OpenClaw runtime was executed.
- No OpenClaw dependency install was performed.
- No skills, plugins, channels, browser, gateway, shell, desktop, or sidecar features were run.
- No real accounts, credentials, browser profile, or external services were connected.
- No vendor code is approved for Sentinel.
- All useful mechanisms below are classified as rewrite knowledge only.

## 1. Executive Summary

OpenClaw is not a simple chat assistant. It is a TypeScript/Node agent runtime with a gateway control plane, channel adapters, dynamic plugins, workspace skills, browser control, shell execution, memory search, sub-agents, mobile/node surfaces, and approval machinery. The project is valuable as a specimen because it shows what a high-power personal agent runtime tries to become: a live operator connected to chats, files, processes, browsers, and background services.

The real superpower is orchestration across surfaces: a prompt can route through a channel, enter an embedded agent loop, call tools, spawn sub-agents, use shell/browser/messaging, and send results back through the gateway. That same power is the core danger. The system has many high-impact surfaces: package install, dynamic module loading, plugin services, message send, browser CDP, shell/process spawning, credentials, webhook/gateway exposure, memory indexing, and persistent sub-agent state.

OpenClaw should not be integrated into Sentinel. Sentinel should learn from its patterns and rewrite a smaller, proof-first runtime:

- TAKE: gateway/control-plane shape, channel-adapter contract, approval UI pattern, memory hybrid-search math, source-only scanner mindset, fake-runtime benchmark approach.
- REWRITE: plugin loader, skill system, exec approval, browser control, messaging send, sub-agent orchestration, memory policy boundaries, cost/model fallback.
- AVOID: host install, unscanned marketplace/plugin installs, vendor runtime bridges, always-allow approvals, shell as a general tool, browser form submission, real channel outbound automation, config-driven background services without a Sentinel manifest.

Final vendor verdict:

- Best superpower: multi-surface execution runtime behind a gateway.
- Biggest weakness: powerful dynamic plugin/skill surfaces are too close to execution without Sentinel-grade evidence, simulation, policy, and trace boundaries.
- Biggest security risk: prompt/plugin/channel input can reach shell, browser, filesystem, messaging, or background services if policies are weak or misconfigured.
- Most valuable Sentinel rewrite: a permissioned action kernel that turns every tool/channel/browser/shell/plugin call into `evidence -> risk -> dry run -> approval -> execution -> trace`.
- Overall usefulness score: 8/10 as a lab specimen.
- Rewrite readiness score: 6/10. The primitives are clear, but runtime behavior remains unverified because this phase intentionally avoided running OpenClaw.

## 2. Source Inventory

| Field | Finding |
|---|---|
| Repo URL | `https://github.com/basetenlabs/openclaw-baseten.git` from local remote metadata |
| Commit | `a2288c2b09e621f89a915960398f58e200b3b69d` |
| Clone path | `agent-lab/vendors/openclaw/source` |
| Runtime | Node.js/TypeScript ESM |
| Package manager | pnpm declared by lock/workspace; root scripts use pnpm |
| Root package | `package.json` name `openclaw`, version `2026.2.1`, description "WhatsApp gateway CLI (Baileys web) with Pi RPC agent" at `package.json:1-4` |
| CLI entry | root bin `openclaw -> openclaw.mjs` at `package.json:8-10` |
| Workspaces | root, `ui`, `packages/*`, `extensions/*` in `pnpm-workspace.yaml` |
| Major source dirs | `src/agents`, `src/gateway`, `src/plugins`, `src/channels`, `src/browser`, `src/memory`, `src/security`, `extensions`, `skills` |
| Install scripts | `postinstall` invokes `node scripts/postinstall.js`; `prepack` builds code and UI at `package.json:119-120` |
| Runtime scripts | `start`, `dev`, `gateway:*`, `openclaw`, `openclaw:rpc`, `moltbot:rpc` at `package.json:92-103` and `package.json:115-126` |
| Docker/test scripts | many `test:docker:*`, `test:install:*`, `test:live` scripts at `package.json:129-145` |
| Native/high-risk deps | `node-pty`, Baileys, Slack, Line, Discord, Playwright, sqlite-vec, sharp, canvas, jiti at `package.json:153-204` |
| Generated/minified code | `package.json` publish list includes `dist/**`, but local checkout does not currently contain `dist` |
| Dynamic loaders | plugin loader uses `jiti` with TS/JS/JSON extensions at `src/plugins/loader.ts:208-217` |
| Dynamic installs | plugin install can run `npm pack` and `npm install --omit=dev --silent` at `src/plugins/install.ts:216-223` and `src/plugins/install.ts:411-417` |

## 3. Consolidated Prior Lab Evidence

### B1 Static Audit

B1 established that OpenClaw has the strongest runtime-power specimen in the lab: channel adapter pattern, gateway/control-plane, plugin API, approval UI, browser executor, shell executor, skills, and channel send. It also established the first Sentinel split:

- take the architectural ideas;
- rewrite the implementation boundaries;
- avoid vendor runtime linkage.

### B2 Dependency Audit

B2 showed that host install is a critical risk. The root package exposes high-impact scripts and dependencies:

- `postinstall` exists at `package.json:119`;
- root scripts include gateway, mobile, test-live, Docker, install tests, package/build, and UI install at `package.json:83-151`;
- the dependency set contains channel SDKs, browser control, native PTY, media/image processing, local vector search, and dynamic loader dependencies at `package.json:153-204`.

Sentinel implication: OpenClaw should remain clone/read-only. If any future runtime experiment is approved, it must be container-only with no host secrets, no real accounts, no real browser profile, and a disposable filesystem.

### B2.5 Scanner Consistency Lock

Canonical scanner output:

- scanner version: `0.2.0`;
- ruleset: `2026-04-24.b2.5`;
- source commit: `a2288c2b09e621f89a915960398f58e200b3b69d`;
- total items: `83`;
- plugins/root-script items: `31`;
- skills: `52`;
- risk counts: `critical=52`, `high=29`, `medium=2`;
- Sentinel decisions: `blocked=52`, `needs_review=29`, `draft_only_tool=2`;
- common patterns: `network_api_access=66`, `external_binary_requirement=53`, `env_secret_or_config_reference=37`, `filesystem_access=26`, `external_message_send=22`, `browser_control=16`, `shell_execution=10`.

Sentinel implication: "plugin/skill scanner" is not only internal tooling. It is a future product capability.

### B3 Fake Runtime Benchmarks

B3 fake benchmark results:

- fixtures: `9`;
- failures: `0`;
- decisions: `blocked=9`;
- risk counts: `critical=2`, `high=7`.

Blocked fixtures included prompt injection, external-send request, browser form submit, filesystem traversal, memory/policy override, plugin `sendMessage`, 1Password access, package install, and persistent policy override.

Sentinel implication: fake-only benchmark harness is the right evaluation shape before runtime power is allowed.

## 4. Architecture Map

### 4.1 Agent Loop

Primary source paths:

- `src/agents/pi-embedded-runner.ts`
- `src/agents/pi-embedded-runner/run.ts`
- `src/agents/pi-embedded-runner/run/attempt.ts`
- `src/agents/pi-embedded-subscribe.ts`

Core mechanism:

- `runEmbeddedPiAgent` is the outer run wrapper at `src/agents/pi-embedded-runner/run.ts:71-73`.
- It serializes work through session/global lanes at `src/agents/pi-embedded-runner/run.ts:74-91`.
- It resolves workspace/model/provider/auth profile, then loops attempts at `src/agents/pi-embedded-runner/run.ts:306-315`.
- `runEmbeddedAttempt` creates the effective workspace, resolves sandbox context, loads skills, builds tools, subscribes to events, and returns messages/tool metadata at `src/agents/pi-embedded-runner/run/attempt.ts:138-240` and `src/agents/pi-embedded-runner/run/attempt.ts:612-650`.

Inputs:

- user prompt, session key, message channel/provider, workspace dir, model/provider, config, skills snapshot, images, execution overrides, extra system prompt.

Outputs:

- assistant payloads, metadata, usage, system prompt report, pending tool calls, last tool error, messaging send metadata.

Side effects:

- creates workspace directories at `src/agents/pi-embedded-runner/run.ts:310`;
- changes process working directory during an attempt at `src/agents/pi-embedded-runner/run/attempt.ts:164-165`;
- may load skills and apply skill env overrides at `src/agents/pi-embedded-runner/run/attempt.ts:167-186`;
- builds high-power tools including exec/message/browser/session tools at `src/agents/pi-embedded-runner/run/attempt.ts:207-240`;
- records auth profile health and use at `src/agents/pi-embedded-runner/run.ts:650-661`.

Control flow:

```text
enqueue session/global lane
-> resolve model/auth/context
-> pick auth profile
-> run attempt
-> if context overflow, compact and retry
-> if unsupported thinking, downgrade and retry
-> if auth/rate-limit/timeout, rotate profile or fail over
-> return payloads + usage + trace-ish metadata
```

Sentinel rewrite:

Sentinel's loop should be narrower:

```text
see -> verify -> reason -> debate -> plan -> simulate -> approve -> execute -> trace -> learn
```

Unlike OpenClaw, Sentinel should not build execution tools directly into a general assistant loop. It should require a typed `DecisionPlan` and a firewall action review before any executor receives control.

### 4.2 Prompt and Instruction System

Primary source:

- `src/agents/system-prompt.ts`

Mechanism:

- The runtime builds a system prompt identifying the model as "a personal assistant running inside OpenClaw" at `src/agents/system-prompt.ts:362-369`.
- It injects a tool availability section at `src/agents/system-prompt.ts:370-391`.
- It instructs sub-agent use for longer tasks at `src/agents/system-prompt.ts:392`.
- It embeds safety text at `src/agents/system-prompt.ts:72-79`.
- It injects messaging rules and warns not to use `exec/curl` for provider messaging at `src/agents/system-prompt.ts:109-120`.
- It lists core tool semantics including `exec`, `browser`, `message`, `gateway`, `sessions_spawn`, and `nodes` at `src/agents/system-prompt.ts:217-244`.
- It includes self-update guidance only for explicit user requests at `src/agents/system-prompt.ts:413-420`.
- It loads project context files and gives `SOUL.md` persona influence unless higher priority instructions override it at `src/agents/system-prompt.ts:535-551`.

Risk:

Project-context and skill prompt injection are structurally close to tool availability. OpenClaw has safety wording, but Sentinel should treat all project docs, skill docs, scraped pages, emails, channel messages, and memory entries as untrusted evidence or context, never as policy.

Sentinel rewrite:

- Separate policy prompt from task prompt.
- Keep tool policy outside model-writable context.
- Add an evidence ledger instead of free-form context dominance.
- Require prompt segments to carry trust labels: `system_policy`, `user_goal`, `trusted_config`, `untrusted_external`, `retrieved_memory`, `tool_result`.

### 4.3 Skills

Primary sources:

- `skills/**/SKILL.md`
- `src/agents/skills/workspace.ts`
- `src/agents/skills-install.ts`
- `src/agents/system-prompt.ts`

Mechanism:

- Workspace skill entries are loaded from bundled, extra, managed, workspace, and plugin skill directories with precedence logic at `src/agents/skills/workspace.ts:100-188`.
- Skills can be compiled into the model prompt through `buildWorkspaceSkillsPrompt` at `src/agents/skills/workspace.ts:228-253`.
- Skills can expose command specs and tool-dispatch commands at `src/agents/skills/workspace.ts:334-438`.
- Skill installation supports brew/node/go/uv/download command construction at `src/agents/skills-install.ts:94-147`.
- Downloaded skill archives can be extracted via `unzip` or `tar xf` at `src/agents/skills-install.ts:202-225`.

Side effects:

- prompts/instructions enter model context;
- env overrides can be applied from skill snapshots;
- install flow can download files and run local commands.

Risk:

The scanner showed 52 skill items and classified high-risk patterns across shell, binaries, secrets, filesystem, network, browser, and messaging. Skills are not just documentation; in a runtime like OpenClaw they become behavior-shaping execution affordances.

Sentinel rewrite:

Skills must become declarative manifests:

```text
skill_id
version
declared_permissions
declared_inputs
declared_outputs
install_free=true for v1
network=false by default
shell=false by default
outbound_action=false by default
evidence_requirements
eval_cases
trace_fields
```

### 4.4 Plugin System

Primary sources:

- `src/plugins/manifest.ts`
- `src/plugins/loader.ts`
- `src/plugins/registry.ts`
- `src/plugins/runtime/index.ts`
- `src/plugins/install.ts`
- `src/plugins/update.ts`

Mechanism:

- Plugin manifests use `openclaw.plugin.json` and support id, config schema, kind, channels, providers, skills, name, description, version, and UI hints at `src/plugins/manifest.ts:6-20`.
- The loader uses `jiti` to load TS/JS/JSON plugin entry files at runtime at `src/plugins/loader.ts:208-217` and imports candidate modules at `src/plugins/loader.ts:294`.
- The registry allows plugins to register tools, hooks, typed hooks, channels, providers, gateway methods, HTTP handlers/routes, CLI registrars, services, and commands at `src/plugins/registry.ts:146-514`.
- The runtime object exposes config write, system command helpers, media, TTS, memory tools, channel send/probe/monitor methods, WhatsApp login, Slack send, Telegram send, Signal send, iMessage send, Line push, and more at `src/plugins/runtime/index.ts:165-330`.
- Plugin install protects target directory traversal at `src/plugins/install.ts:99-115`, but still copies packages and runs `npm install --omit=dev --silent` when dependencies exist at `src/plugins/install.ts:193-223`.
- NPM plugin install can run `npm pack <spec>` in a temp dir at `src/plugins/install.ts:411-417`.
- Update logic can install/sync NPM plugins at `src/plugins/update.ts:140-310` and `src/plugins/update.ts:313-430`.

Side effects:

- dynamic module execution;
- config writes;
- HTTP/gateway method expansion;
- background services;
- outbound channel actions;
- package installation;
- access to state/config/workspace.

Risk:

The plugin system is the largest attack surface. Even with config allow/deny mechanisms, the runtime grants plugin authors hooks into agent lifecycle, gateway, HTTP, commands, services, channels, and tools. This is incompatible with Sentinel v1 unless reduced to a static, scanned, sandboxed manifest model.

Sentinel rewrite:

- No dynamic plugin execution in v1.
- No `jiti`/runtime TS loader for user plugins.
- No package install in host workspace.
- Plugin scanner runs before any registration.
- Plugin registration is data-only until approved.
- Background services require a separate sidecar manifest and explicit user approval.

### 4.5 Gateway and Control Plane

Primary sources:

- `src/gateway/server.impl.ts`
- `src/gateway/server-http.ts`
- `src/gateway/auth.ts`
- `src/gateway/tools-invoke-http.ts`
- `src/gateway/server-methods-list.ts`
- `src/gateway/server-methods/exec-approval.ts`

Mechanism:

- Gateway startup validates config, auto-enables plugins, initializes sub-agent registry, loads gateway plugins, builds gateway methods, and starts sidecars at `src/gateway/server.impl.ts:185-237` and `src/gateway/server.impl.ts:500-510`.
- Plugin gateway handlers are merged with exec approval handlers into `extraHandlers` at `src/gateway/server.impl.ts:439-442`.
- HTTP request routing handles hooks, `/tools/invoke`, Slack, plugin HTTP handlers, OpenResponses/OpenAI-compatible HTTP, canvas, Control UI, and fallback 404 at `src/gateway/server-http.ts:236-318`.
- Gateway auth can use token/password or Tailscale mode at `src/gateway/auth.ts:199-221`.
- `assertGatewayAuthConfigured` rejects missing token/password unless Tailscale is allowed at `src/gateway/auth.ts:224-235`.
- `authorizeGatewayConnect` accepts verified Tailscale, token, or password using timing-safe compare at `src/gateway/auth.ts:238-290`; the low-level `safeEqual` is at `src/gateway/auth.ts:35-40`.
- `/tools/invoke` requires POST and gateway auth, then constructs tools and filters by policy at `src/gateway/tools-invoke-http.ts:108-155` and `src/gateway/tools-invoke-http.ts:213-283`.

Risk:

The gateway is the right architectural shape, but it centralizes many powerful surfaces. Plugin HTTP handlers and tool invocation in the same server are especially sensitive. Misconfigured auth or reverse proxy exposure can convert local control into remote control.

Sentinel rewrite:

Sentinel should keep a gateway/control-plane, but split:

- read-only inspection API;
- action proposal API;
- approval API;
- execution API;
- audit log API.

High-impact action execution should be a separate capability behind policy and trace gates, not a generic plugin/gateway expansion point.

### 4.6 Shell / Process Execution and Approval

Primary sources:

- `src/agents/bash-tools.exec.ts`
- `src/infra/exec-approvals.ts`
- `src/gateway/server-methods/exec-approval.ts`
- `ui/src/ui/views/exec-approval.ts`

Mechanism:

- The exec tool accepts command, workdir, env, yield/background, timeout, PTY, elevated mode, host, security, ask, and node parameters at `src/agents/bash-tools.exec.ts:195-241`.
- Host env validation blocks many loader/path injection variables at `src/agents/bash-tools.exec.ts:59-107`.
- Default constants include output caps, approval timeout, request timeout, notice, and slug length at `src/agents/bash-tools.exec.ts:108-126`.
- `runExecProcess` can spawn Docker exec, PTY via `@lydell/node-pty`, or shell fallback process execution at `src/agents/bash-tools.exec.ts:421-798`.
- Elevated mode can become `full`, which sets full security and disables ask in the normalized path at `src/agents/bash-tools.exec.ts:865-949`.
- Gateway approval requests are sent as `exec.approval.request` and resolved by `exec.approval.resolve` at `src/gateway/server-methods/exec-approval.ts:13-137`.
- Shell allowlist evaluation splits command chains and checks segments at `src/infra/exec-approvals.ts:1149-1236`.
- Approval is required when ask is always, or ask-on-miss with allowlist/security mismatch at `src/infra/exec-approvals.ts:1238-1249`.
- The UI approval prompt shows command metadata and offers `Allow once`, `Always allow`, and `Deny` at `ui/src/ui/views/exec-approval.ts:25-89`.

Risk:

This is a mature surface compared with many agent runtimes, but it still grants the model a shell-shaped tool. `Allow always` is productive but dangerous. Policy-by-command-analysis is brittle against shell quoting, interpreter tricks, package managers, env injection, file traversal, and generated scripts.

Sentinel rewrite:

Sentinel v1 should keep shell execution disabled. Later, shell should be replaced with typed executors:

- `create_project_folder`
- `create_markdown_file`
- `export_json`
- `prepare_email_draft`
- `run_test_in_sandbox` only after explicit plan

If shell ever returns, it must require:

```text
declared command intent
static command AST parse
deny by default
no wildcard allow-always
ephemeral sandbox
no secrets in env
path scope
dry-run preview
explicit approval
full trace
```

### 4.7 Browser Control

Primary sources:

- `src/browser/chrome.ts`
- `src/browser/server.ts`
- `src/browser/profiles.ts`
- `src/browser/pw-ai.ts`

Mechanism:

- Browser profiles live under OpenClaw config state at `CONFIG_DIR/browser/<profile>/user-data` via `resolveOpenClawUserDataDir` at `src/browser/chrome.ts:62-64`.
- `launchOpenClawChrome` refuses remote-profile local launches, ensures a CDP port is available, resolves Chrome-like browser executable, creates user-data dir, and spawns the browser with remote debugging and profile flags at `src/browser/chrome.ts:163-227`.
- The browser control server binds Express JSON endpoints to `127.0.0.1:<controlPort>` when enabled at `src/browser/server.ts:15-68`.
- Profile names and CDP ports are bounded by regex, length, and the `18800-18899` range at `src/browser/profiles.ts:1-45`.
- `pw-ai.ts` re-exports Playwright actions including navigate, click, fill, evaluate, screenshots, storage state, cookies, geolocation, credentials, tracing, and downloads at `src/browser/pw-ai.ts:14-60`.

Risk:

Browser control is an extremely high-impact capability. Even dedicated profiles and localhost binding do not remove risks: form submission, logged-in sessions, cookies, credential fields, downloads/uploads, prompt injection from webpages, and silent state mutation.

Sentinel rewrite:

Browser v1 should be absent. Later browser should be:

- sandbox profile only;
- read-only first;
- no form submit;
- no credential field fill;
- no file upload/download without approval;
- DOM content treated as untrusted external content;
- screenshot/cookie/storage redaction;
- dry-run DOM action preview;
- full trace with target URL, selector, risk class, evidence refs.

### 4.8 Channels and Messaging

Primary sources:

- `src/channels/plugins/types.plugin.ts`
- `src/gateway/server-channels.ts`
- `extensions/slack/src/channel.ts`
- `extensions/whatsapp/src/channel.ts`
- `src/gateway/server-methods/send.ts`
- `src/plugins/runtime/index.ts`

Mechanism:

- `ChannelPlugin` supports metadata, capabilities, config, setup/pairing/security/groups/mentions/outbound/status/gateway/auth/elevated/commands/streaming/threading/messaging/action/heartbeat/agentTools fields at `src/channels/plugins/types.plugin.ts:48-84`.
- Gateway channel manager starts/stops configured channel account runtimes through plugin gateway lifecycle hooks at `src/gateway/server-channels.ts:63-230`.
- Slack plugin config requires bot/app token for configuration and warns about open group policy/no allowlist at `extensions/slack/src/channel.ts:119-170`.
- WhatsApp plugin uses web auth state and warns about open group policy/no allowlist at `extensions/whatsapp/src/channel.ts:101-156`.
- Plugin runtime exposes many channel send/probe/monitor functions at `src/plugins/runtime/index.ts:260-330`.
- The prompt tells the assistant that normal replies route to the source channel and `sessions_send` handles cross-session messaging at `src/agents/system-prompt.ts:109-120`.

Risk:

Inbound channels are untrusted input. Outbound channels are real-world actions. The combination creates a classic prompt-injection-to-external-action path if a malicious inbound message convinces the agent to send, invite, click, post, or reveal.

Sentinel rewrite:

Sentinel v1 should generate outreach drafts only. Real channel send must remain disabled until:

- contact ownership is documented;
- message purpose is evidence-backed;
- opt-out/compliance policy is satisfied;
- human approval exists;
- rate limit exists;
- trace includes source, target, draft, approval, and delivery result.

### 4.9 Memory

Primary sources:

- `src/memory/manager.ts`
- `src/memory/manager-search.ts`
- `src/memory/hybrid.ts`
- `src/memory/internal.ts`
- `src/agents/memory-search.ts`
- `src/plugins/runtime/index.ts`

Mechanism:

- Memory search can index memory and session sources, then search by vector and/or keyword.
- Memory config resolves defaults and clamps scores/weights/candidate multiplier at `src/agents/memory-search.ts:210-278`.
- Search computes candidates as `min(200, max(1, floor(maxResults * candidateMultiplier)))` at `src/memory/manager.ts:288-294`.
- Vector search uses `score = 1 - row.dist` for sqlite vector results or cosine similarity fallback at `src/memory/manager-search.ts:55-90`.
- Keyword search uses SQLite FTS `bm25` and maps rank to score at `src/memory/manager-search.ts:145-182`.
- `bm25RankToScore(rank)` computes `1 / (1 + max(0, rank))` at `src/memory/hybrid.ts:36-39`.
- Hybrid merge computes `score = vectorWeight * vectorScore + textWeight * textScore` and sorts descending at `src/memory/hybrid.ts:102-114`.
- Cosine similarity computes dot product over the shared vector length and returns 0 for empty/zero norm vectors at `src/memory/internal.ts:258-275`.

Risk:

This is useful math, but memory can become policy if inserted into prompts without trust boundaries. Session memory and external channel history can carry prompt injection, stale facts, user preference poisoning, or accidental secrets.

Sentinel rewrite:

Sentinel should take the scoring ideas but enforce memory roles:

- `facts`: can support decisions with evidence refs;
- `preferences`: can affect formatting/UX only;
- `project_context`: can influence pack specifics;
- `outcomes`: can tune future scoring;
- `policy`: cannot be written by memory;
- `secrets`: never indexed;
- `untrusted_memory`: never executes or overrides policy.

### 4.10 Model Routing and Cost/Fallback

Primary sources:

- `src/agents/model-selection.ts`
- `src/agents/model-fallback.ts`
- `src/agents/auth-profiles/order.ts`
- `src/agents/context-window-guard.ts`
- `src/agents/usage.ts`

Mechanism:

- Context window defaults are `hardMin=16000`, `warnBelow=32000`, default tokens `200000` at `src/agents/context-window-guard.ts:3-4` and `src/agents/defaults.ts:6`.
- `resolveContextWindowInfo` chooses config model context, model metadata, or default, then caps by `agents.defaults.contextTokens` at `src/agents/context-window-guard.ts:21-50`.
- `evaluateContextWindowGuard` warns below threshold and blocks below hard minimum at `src/agents/context-window-guard.ts:57-73`.
- `resolveFallbackCandidates` adds primary model, configured fallbacks, and default primary while respecting an allowlist at `src/agents/model-fallback.ts:147-220`.
- `runWithModelFallback` skips providers where all auth profiles are in cooldown, catches failover errors, records attempts, and throws a summary if all fail at `src/agents/model-fallback.ts:223-332`.
- Auth profile ordering favors available profiles, then type score (`oauth=0`, `token=1`, `api_key=2`, other=3), then oldest `lastUsed`, with cooldown profiles appended at `src/agents/auth-profiles/order.ts:163-210`.

Risk:

There is fallback and usage tracking, but not a full business budget router. The cost risk is not just API price; it is uncontrolled retry, long context, image/media payloads, batch embeddings, tool loops, and sub-agent ping-pong.

Sentinel rewrite:

Sentinel CostRouter should be explicit:

```text
budget_per_run
max_model_attempts
max_tool_calls
max_research_sources
max_subagents
max_context_tokens
estimated_cost_before_run
actual_cost_after_run
fallback_reason_trace
stop_when_budget_exceeded
```

### 4.11 Sub-agents and Delegation

Primary sources:

- `src/agents/tools/sessions-spawn-tool.ts`
- `src/agents/tools/sessions-send-tool.a2a.ts`
- `src/agents/subagent-registry.ts`

Mechanism:

- `sessions_spawn` accepts task, label, target agent, model, thinking level, timeout, cleanup policy at `src/agents/tools/sessions-spawn-tool.ts:26-36`.
- It rejects spawning from sub-agent sessions at `src/agents/tools/sessions-spawn-tool.ts:121-127`.
- It calls the gateway `agent` method with a child session key, `lane=AGENT_LANE_SUBAGENT`, extra system prompt, timeout, and delivery disabled at `src/agents/tools/sessions-spawn-tool.ts:217-247`.
- It registers sub-agent runs for later result announcement/cleanup at `src/agents/tools/sessions-spawn-tool.ts:262-280`.
- Agent-to-agent send can perform ping-pong turns up to `maxPingPongTurns` at `src/agents/tools/sessions-send-tool.a2a.ts:60-96`.
- Sub-agent registry persists run records, resumes pending cleanup after restart, and runs a sweeper every 60 seconds at `src/agents/subagent-registry.ts:12-31` and `src/agents/subagent-registry.ts:92-180`.

Risk:

Delegation is powerful but can multiply costs, amplify prompt injection, preserve stale tasks, and obscure why an action happened.

Sentinel rewrite:

Sentinel may use sub-agents later only as bounded roles in the decision layer:

- research;
- competitor analysis;
- WTP extraction;
- skeptic challenge;
- GTM drafting.

No sub-agent should directly execute high-impact actions. Every sub-agent output must become evidence, critique, or draft, not authority.

### 4.12 Security Helpers

Primary sources:

- `src/security/external-content.ts`
- `src/security/audit.ts`
- `src/security/fix.ts`
- `src/infra/fs-safe.ts`
- `src/infra/exec-approvals.ts`

Mechanism:

- External content helper states that external source content must not be directly interpolated into system prompts or treated as trusted instructions at `src/security/external-content.ts:1-9`.
- Suspicious patterns include ignore-previous-instructions, system override, `exec command=`, `elevated=true`, `rm -rf`, delete-all, and role marker patterns at `src/security/external-content.ts:15-28`.
- Wrapped external content receives explicit untrusted boundaries and warning text at `src/security/external-content.ts:53-64` and `src/security/external-content.ts:177-201`.
- Security audit flags missing gateway auth on loopback with Control UI as critical at `src/security/audit.ts:300-309`.
- It flags Tailscale Funnel exposure as critical at `src/security/audit.ts:312-319`.
- It flags disabled redaction and elevated allowlist wildcards at `src/security/audit.ts:412-455`.
- Audit aggregation includes gateway, browser, logging, elevated, hooks, secrets, model hygiene, exposure, filesystem, plugins, and channels at `src/security/audit.ts:920-963`.

Risk:

OpenClaw includes many good security checks, but they are checks around a large runtime. Sentinel should invert the model: make dangerous capabilities impossible by default, not merely audited after configuration.

Sentinel rewrite:

Security helpers become mandatory gates:

```text
untrusted content wrapper
prompt injection score
secret leak scan
source trust label
action risk score
policy decision
dry-run preview
approval record
trace record
post-action audit
```

## 5. Algorithm and Math Audit

| Mechanism | Source | Formula / pseudocode | Assumptions | Failure risk | Sentinel rewrite |
|---|---|---|---|---|---|
| Context guard | `src/agents/context-window-guard.ts:3-73`, used by `src/agents/pi-embedded-runner/run.ts:113-137` | `warn = tokens > 0 && tokens < warnBelow`; `block = tokens > 0 && tokens < hardMin`; defaults `warnBelow=32000`, `hardMin=16000` | Context window metadata is accurate | Wrong model metadata can over/under-block; large contexts increase cost | Keep hard model capability gates and add per-run cost/context budget |
| Model fallback | `src/agents/model-fallback.ts:147-332` | candidates = primary + configured fallbacks + default primary; skip if all profiles in cooldown; retry only failover errors | Provider errors are classifiable; fallback list is safe | Cost explosion or degraded model silently changes quality | Require max attempts, explicit fallback trace, and pack confidence downgrade |
| Auth profile ordering | `src/agents/auth-profiles/order.ts:163-210` | available first; score `oauth=0`, `token=1`, `api_key=2`, other=3; sort by type then oldest `lastUsed`; cooldown last | Rotating credentials improves reliability | Can hide rate-limit/cost/account abuse under rotation | Sentinel v1 should avoid account rotation; later route by budget and explicit account scope |
| Memory vector score | `src/memory/manager-search.ts:55-90`, `src/memory/internal.ts:258-275` | SQLite vector score `1 - dist`; fallback cosine similarity `dot/(||a||*||b||)` | Embedding space matches retrieval goal | Poisoned/stale memory can outrank reliable evidence | Use memory only as support, never as proof or policy |
| Keyword score | `src/memory/hybrid.ts:36-39`, `src/memory/manager-search.ts:145-182` | `textScore = 1 / (1 + max(0, bm25Rank))` | BM25 rank maps cleanly to [0,1]-like score | Keyword stuffing can boost adversarial memory | Weight by source trust and freshness |
| Hybrid memory merge | `src/memory/hybrid.ts:41-114`, `src/agents/memory-search.ts:238-245` | normalized weights; `score = vectorWeight*vectorScore + textWeight*textScore`; sort descending | Vector and BM25 scores are comparable | Combined score lacks source-trust multiplier | Sentinel evidence score should include confidence, freshness, relevance, source trust, directness |
| Search candidate cap | `src/memory/manager.ts:288-317` | candidates = `min(200, max(1, floor(maxResults*candidateMultiplier)))` | 200 candidates enough | Misses long-tail evidence; too many candidates cost more | Make candidate count tied to run depth and budget |
| Exec allowlist decision | `src/infra/exec-approvals.ts:1149-1249` | split shell chains; require approval if ask always or allowlist miss/analysis fail | Shell segmentation catches dangerous commands | Shell parsing is hard; interpreter tricks bypass intent | Replace shell with typed executors; shell later only in sandbox |
| Plugin install path guard | `src/plugins/install.ts:99-115` | resolve target; reject relative path escaping base | Path traversal is the main install path risk | Safe path does not make package code safe | Keep path guard but require signature/scanner/sandbox/no install v1 |
| Sub-agent ping-pong | `src/agents/tools/sessions-send-tool.a2a.ts:60-96` | loop `turn=1..maxPingPongTurns`; alternate requester/target sessions | Bounded debate improves answer | Bounded loops can still compound cost/confusion | Use fixed debate roles with strict output schema and cost caps |

## 6. Prompt and Skill Instruction Audit

| Prompt/instruction surface | Source | Purpose | Risk | Sentinel rewrite |
|---|---|---|---|---|
| Base identity | `src/agents/system-prompt.ts:362-369` | Agent identity and runtime context | Generic assistant identity invites broad task execution | Sentinel identity should be product-specific: GTM Operator + AgentOps Firewall |
| Tooling section | `src/agents/system-prompt.ts:370-391` | Lists available tools | Model learns broad tool affordance | Tool list should be computed from a policy-approved action plan |
| Safety section | `src/agents/system-prompt.ts:72-79` | No independent goals, no bypass safeguards | Good text, but text is not enforcement | Enforce with code-level policy gates |
| Messaging section | `src/agents/system-prompt.ts:109-120` | Normal and cross-session message behavior | Outbound messaging can become autonomous action | Draft-only in v1; send requires approval and compliance |
| Self-update | `src/agents/system-prompt.ts:413-420` | Allows config/update only on explicit request | Config write/restart is high impact | Sentinel self-improvement writes proposals, not code/config mutation |
| SOUL/project context | `src/agents/system-prompt.ts:535-551` | Injects project docs into prompt | Local docs can contain malicious or stale instructions | Project docs are evidence/context, never policy |
| Skills prompt | `src/agents/skills/workspace.ts:228-253` | Inserts skill instructions | Skills can smuggle tool instructions | Skills require scanner, manifest, trust label, and eval |
| External content wrapper | `src/security/external-content.ts:177-201` | Wraps untrusted content | Useful but optional unless all ingestion uses it | Mandatory wrapper for all channel/web/research input |

## 7. Runtime Side-Effect Map

| Side effect | Trigger | Source path | Risk | Existing mitigation | Sentinel mitigation | Eval required |
|---|---|---|---|---|---|---|
| Filesystem write | workspace creation, file tools, plugin install | `src/agents/pi-embedded-runner/run.ts:310`, `src/plugins/install.ts:193-223` | High | sandbox context, install path guard | write only under `data/generated_projects`; no vendor install | path traversal, outside-dir write |
| Shell/process | `exec` tool | `src/agents/bash-tools.exec.ts:421-798` | Critical | approvals, allowlist, env validation | disabled v1; typed executors only | shell blocked |
| PTY | `exec` with PTY | `src/agents/bash-tools.exec.ts:481-519` | Critical | fallback handling | disabled v1 | PTY unavailable/blocked |
| Browser CDP | browser tool/server | `src/browser/chrome.ts:163-227`, `src/browser/pw-ai.ts:14-60` | High/Critical | dedicated profile, localhost server | disabled v1; read-only sandbox later | form submit blocked |
| External messaging | channel send/message/sessions | `src/plugins/runtime/index.ts:260-330`, `src/agents/system-prompt.ts:109-120` | High | channel policy/allowlists | draft-only, approval, opt-out, trace | outbound send blocked |
| Gateway tool invoke | `/tools/invoke` | `src/gateway/tools-invoke-http.ts:108-155` | High | token/password/Tailscale auth | separate action proposal vs execution APIs | unauth rejected |
| Plugin HTTP routes | plugin registry | `src/plugins/registry.ts:287-326`, `src/gateway/server-http.ts:259-260` | High | registry diagnostics | no plugin HTTP handlers v1 | unscanned plugin route blocked |
| Plugin dynamic import | loader | `src/plugins/loader.ts:208-217`, `src/plugins/loader.ts:294` | Critical | config allow/deny | no dynamic user plugins v1 | dynamic loader detected |
| Package install | plugin/skill install | `src/plugins/install.ts:216-223`, `src/plugins/install.ts:411-417`, `src/agents/skills-install.ts:94-147` | Critical | path guard, timeout | no host install; container-only future | package install blocked |
| Memory write/index | memory manager | `src/memory/manager.ts:849-1188` | Medium/High | source filters, sync settings | no secrets; trust labels; memory cannot override policy | memory poisoning |
| Background service | plugin services | `src/plugins/services.ts:12-72` | High | stop handle | no background plugin service v1 | service registration blocked |
| Sub-agent persistence | sub-agent registry | `src/agents/subagent-registry.ts:12-180` | Medium/High | cleanup/archive | bounded decision roles only | runaway sub-agent blocked |

## 8. Security and Failure Autopsy

| Failure mode | How it can happen in OpenClaw | Source paths | Existing protection | Gap | Sentinel prevention | Required test |
|---|---|---|---|---|---|---|
| Prompt injection | inbound/web/external content enters prompt and suggests tool use | `src/security/external-content.ts:15-28`, `src/agents/system-prompt.ts:535-551` | suspicious patterns and wrapper | protection depends on consistent use | mandatory untrusted wrapper and policy separation | fake Slack/web injection |
| Malicious skill | `SKILL.md` or install metadata instructs command/network/secret actions | `src/agents/skills/workspace.ts:100-188`, `src/agents/skills-install.ts:94-225` | scanner in lab, some install guards | runtime skills can affect prompt/env | declarative skill manifest; no install v1 | malicious skill fixture |
| Malicious plugin | dynamic loaded module registers tools/routes/services | `src/plugins/loader.ts:208-294`, `src/plugins/registry.ts:146-514` | config allow/deny/diagnostics | dynamic code executes if allowed | static scanner + sandbox + no dynamic plugins v1 | plugin sendMessage fixture |
| Credential leakage | config/env/channel tokens, auth profiles, logs, tool summaries | `src/gateway/auth.ts:199-221`, `src/security/audit.ts:412-455` | redaction audit and config warnings | plugin/runtime may touch config and channel APIs | secret manager isolation; never index secrets | secret leak eval |
| Filesystem escape | file write/install paths or shell commands | `src/plugins/install.ts:99-115`, `src/agents/bash-tools.exec.ts:195-241` | path guard for plugin dir, exec approval | shell can do arbitrary FS | strict path scope and no shell v1 | `../` write fixture |
| Shell abuse | model or skill calls `exec` | `src/agents/bash-tools.exec.ts:800-1510` | allowlist/approval | shell analysis brittle; allow-always exists | disable shell; typed executors | shell blocked |
| Browser form submission | browser action fills/submits page | `src/browser/pw-ai.ts:14-60` | profile isolation | model can mutate real web state | browser disabled v1; later dry-run DOM plan | form submit fixture |
| Unauthorized external action | channels send replies/proactive messages | `src/plugins/runtime/index.ts:260-330` | channel allowlists/pairing | outbound still real action | draft-only and human approval | Telegram/send fixture |
| Memory poisoning | memory/session content retrieved into future runs | `src/memory/manager.ts:280-317`, `src/memory/hybrid.ts:102-114` | retrieval scoring | score lacks source trust/policy boundary | memory labels and no memory-as-policy | memory policy override fixture |
| Hallucinated decision | general assistant makes plan without evidence | `src/agents/system-prompt.ts:362-392` | no product evidence ledger | broad assistant orientation | DecisionPlan must cite EvidenceItem | fake evidence eval |
| Cost explosion | fallbacks, profile rotation, sub-agent ping-pong, memory embeddings | `src/agents/model-fallback.ts:223-332`, `src/agents/tools/sessions-send-tool.a2a.ts:60-96` | some cooldown and max turns | no business budget gate | CostRouter with hard caps | budget exhaustion eval |
| Unsafe self-improvement | update/config/gateway tools | `src/agents/system-prompt.ts:413-420`, `package.json:119-120` | explicit-request prompt | prompt text not enough | proposal-only self-improvement | config update blocked |
| Persistence abuse | plugin services, sub-agent registry, cron/wake | `src/plugins/services.ts:12-72`, `src/agents/subagent-registry.ts:92-180` | stop handles, cleanup | services can persist behavior | no background service v1 | background service fixture |
| Vendor lock-in | adopting runtime code/deps | `package.json:153-204`, `src/plugins/runtime/index.ts:165-330` | none relevant | dependency and architecture coupling | rewrite from first principles | no vendor import test |
| User trust collapse | action happens without clear proof/preview | cross-cutting | approval UI for exec only | other actions can be implicit | trace every decision/action | trace completeness eval |

## 9. Superpower Extraction

### Superpower 1: Gateway-Centered Runtime

- Source paths: `src/gateway/server.impl.ts`, `src/gateway/server-http.ts`, `src/gateway/server-methods-list.ts`
- Mechanism: central server loads config, plugins, channel methods, exec approval handlers, HTTP routes, websocket upgrades, sidecars.
- Why users care: one control plane can coordinate chat, tools, browser, channels, UI, and agents.
- Risk: gateway exposure turns local automation into remote automation.
- Sentinel rewrite: keep gateway, but split proposal/approval/execution/audit APIs and deny all high-impact actions by default.
- Firewall implication: every gateway execution method must map to a risk class.
- Trace requirement: request id, user/session, method, params hash, policy decision, approval id, result.
- Eval requirement: unauth tool invoke, unknown method, high-impact method without approval.
- Priority: now for internal architecture, later for dangerous methods.

### Superpower 2: Dynamic Plugin Ecosystem

- Source paths: `src/plugins/manifest.ts`, `src/plugins/loader.ts`, `src/plugins/registry.ts`, `src/plugins/runtime/index.ts`
- Mechanism: manifest discovery plus `jiti` dynamic loading and registry APIs for tools/hooks/channels/services/routes.
- Why users care: extensibility and rapid capability growth.
- Risk: untrusted code can register powerful actions.
- Sentinel rewrite: static Skill/Tool Manifest v0 with scanner and policy, no dynamic loading v1.
- Firewall implication: plugin permissions must be declared before load.
- Trace requirement: plugin id, version, manifest hash, scan result, permissions, approval.
- Eval requirement: malicious plugin declares `sendMessage`, shell, secrets, background service.
- Priority: later; scanner now.

### Superpower 3: Multi-Channel Adapter Pattern

- Source paths: `src/channels/plugins/types.plugin.ts`, `src/gateway/server-channels.ts`, `extensions/slack/src/channel.ts`, `extensions/whatsapp/src/channel.ts`
- Mechanism: channels declare capabilities, config, security, gateway lifecycle, outbound/messaging semantics.
- Why users care: one agent can operate across Slack, WhatsApp, Telegram, Discord, etc.
- Risk: inbound untrusted content and outbound real-world actions are coupled.
- Sentinel rewrite: ChannelAdapterManifest with inbound-only first; outbound draft-only; send disabled.
- Firewall implication: `contact_external_person` and `send_message` are high-impact actions.
- Trace requirement: source channel, sender trust, target, message draft, approval.
- Eval requirement: external-send injection, group allowlist bypass.
- Priority: later.

### Superpower 4: Exec Approval UX

- Source paths: `src/agents/bash-tools.exec.ts`, `src/infra/exec-approvals.ts`, `src/gateway/server-methods/exec-approval.ts`, `ui/src/ui/views/exec-approval.ts`
- Mechanism: shell command analysis, allowlist, approval request/resolve, UI prompt with allow once/always/deny.
- Why users care: high-power automation can pause for consent.
- Risk: consent fatigue and "Always allow" can turn into permanent overpermission.
- Sentinel rewrite: action preview approval, not shell approval; no `always allow` for high-impact classes.
- Firewall implication: approval records must bind action hash, user, expiry, and scope.
- Trace requirement: dry run, risk score, approval status, executed result.
- Eval requirement: blocked shell, stale approval replay, approval hash mismatch.
- Priority: now as UI pattern, not shell.

### Superpower 5: Browser Profile and CDP Control

- Source paths: `src/browser/chrome.ts`, `src/browser/server.ts`, `src/browser/pw-ai.ts`
- Mechanism: launch dedicated browser profile with remote debugging and expose Playwright-like tools.
- Why users care: agent can use websites.
- Risk: logged-in sessions, form submission, cookie leakage, webpage prompt injection.
- Sentinel rewrite: read-only browser research sandbox after GTM quality is strong; form submit much later.
- Firewall implication: browser actions are medium/high/critical by action type.
- Trace requirement: URL, selector, screenshot hash, DOM action, approval.
- Eval requirement: browser form submit blocked, credential field detection.
- Priority: avoid now.

### Superpower 6: Hybrid Memory Search

- Source paths: `src/memory/manager.ts`, `src/memory/manager-search.ts`, `src/memory/hybrid.ts`, `src/memory/internal.ts`
- Mechanism: vector + BM25 merge with normalized weights.
- Why users care: cross-session recall and project continuity.
- Risk: poisoned memory can look relevant.
- Sentinel rewrite: evidence/memory split with source trust and no policy override.
- Firewall implication: memory can inform, never approve.
- Trace requirement: memory ids used, score, source, trust label.
- Eval requirement: memory policy override blocked.
- Priority: now for evidence retrieval, with restrictions.

### Superpower 7: Sub-Agent Delegation

- Source paths: `src/agents/tools/sessions-spawn-tool.ts`, `src/agents/tools/sessions-send-tool.a2a.ts`, `src/agents/subagent-registry.ts`
- Mechanism: spawn isolated child sessions and optionally run bounded ping-pong.
- Why users care: parallel/longer research and task decomposition.
- Risk: cost, confusion, untraceable conclusions, delegated execution.
- Sentinel rewrite: fixed debate roles only; no executor authority.
- Firewall implication: sub-agent output requires evidence_refs before action proposals.
- Trace requirement: role, task, input, output, cost, evidence refs.
- Eval requirement: sub-agent tries to send/execute and is blocked.
- Priority: later for debate, not runtime execution.

### Superpower 8: Security Audit and External Content Helpers

- Source paths: `src/security/audit.ts`, `src/security/external-content.ts`, `src/security/fix.ts`
- Mechanism: config security audit, hardening suggestions, prompt-injection pattern detection and untrusted content wrapper.
- Why users care: makes a powerful runtime more diagnosable.
- Risk: audit after capability is weaker than capability prevention.
- Sentinel rewrite: make these checks preconditions for action creation.
- Firewall implication: risk scanner feeds policy decision.
- Trace requirement: scanner version, findings, decision.
- Eval requirement: prompt injection, secrets, open gateway, wildcard allowlist.
- Priority: now.

## 10. TAKE / REWRITE / AVOID

### TAKE

- Gateway/control-plane concept, but only as a Sentinel-owned API boundary.
- Channel adapter vocabulary: capabilities, accounts, pairing, security policy, outbound status.
- Approval UI concept: show what will happen, why, risk, and decision controls.
- Hybrid memory retrieval formulas as a starting point.
- Scanner consistency lock pattern: version, timestamp, commit, ruleset, counts, JSON hash.
- Fake runtime benchmark approach before enabling real runtime power.
- External content wrapping and suspicious-pattern detection.

### REWRITE

- Agent loop around Sentinel's proof-first lifecycle, not a generic assistant loop.
- Plugin system as static manifests, not dynamic code loading.
- Skill system as scanned declarative capabilities, not arbitrary prompt/install content.
- Shell execution as typed safe executors; keep shell disabled until container-only plan.
- Browser system as read-only sandbox first; no form submit.
- Channel system as inbound untrusted plus outbound draft-only first.
- Memory as evidence/context, never policy.
- Model fallback as CostRouter with hard run budgets and trace.
- Sub-agents as bounded decision/debate roles, not execution delegates.
- Security audit as mandatory gate, not optional diagnostics.

### AVOID

- Host dependency install.
- `postinstall`/package-manager execution in Sentinel workspace.
- Runtime plugin loading from TS/JS/JSON with `jiti`.
- NPM plugin marketplace/install/update in v1.
- Real channel send/email send.
- Browser form submission or logged-in browser control.
- Desktop/node camera/screen controls.
- Shell/PTY execution.
- "Allow always" approvals for high-impact actions.
- Background plugin services.
- Vendor bridge or copied runtime modules.

## 11. Missing Blocks and Unknowns

Not audited or not verified in this final source-only pass:

- Live runtime behavior of the gateway, browser server, channel adapters, and exec approval UI.
- Actual behavior of every one of the 52 skills beyond scanner classification.
- Full source walk of every extension implementation; only representative and high-risk surfaces were inspected.
- Full UI code path for every approval/control screen.
- Runtime credential storage behavior under real onboarding.
- Actual browser sandbox isolation under a launched profile.
- Actual network calls made by all channel plugins.
- Full Docker/container behavior.
- Live model-provider request/response behavior.
- Performance/cost characteristics under real traffic.
- Whether all external content paths consistently call `wrapExternalContent`.
- Whether all plugin HTTP routes are authenticated consistently once registered.
- Whether all logs redact secrets in every tool/channel/plugin path.

These are intentionally unknown because this phase forbids install/runtime/account/browser execution.

## 12. Final Vendor Verdict

OpenClaw is the best current specimen for understanding agent runtime power. It demonstrates a real gateway-centered operator architecture with channels, plugins, shell, browser, memory, sub-agents, and approvals. It also demonstrates why Sentinel must not clone or integrate such a runtime before its own firewall, evidence, dry-run, approval, trace, and eval systems are complete.

The most important lesson is not "build more tools." The lesson is that every tool becomes a liability unless it is represented as a typed action with a risk class, evidence requirement, dry-run preview, approval state, execution boundary, and trace record.

Sentinel should therefore treat OpenClaw as a source of design pressure:

```text
OpenClaw shows the powers.
Agent Lab maps the failures.
Sentinel rewrites the powers as controlled capabilities.
```

Recommended next phase:

```text
G6 - Hermes Final Forensic Report
Focus: memory, learning, skill refinement, delegation, self-improvement boundaries.
No Sentinel runtime build until OpenClaw, Hermes, OpenJarvis, and JARVIS final reports are complete.
```
