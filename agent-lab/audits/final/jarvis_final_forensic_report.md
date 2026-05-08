# JARVIS Final Forensic Report

Date: 2026-04-26
Vendor specimen: JARVIS
Lab mode: source-only forensic reverse phase
Source path: `agent-lab/vendors/jarvis/source`
Source commit: `7b66f0d3c77a4d050d56ff98b5723fd00b9fb937`

## Guardrails

This report is a forensic artifact, not an integration plan.

- No JARVIS runtime was executed.
- No dependency install was performed.
- No sidecar, daemon, browser, terminal, desktop automation, clipboard, screenshot, channels, workflows, OAuth setup, or account integrations were run.
- No real accounts, credentials, browser profiles, sidecar tokens, local desktop sessions, messages, or external services were connected.
- No vendor code is approved for Sentinel.
- All useful mechanisms below are classified as rewrite knowledge only.

## 1. Executive Summary

JARVIS is an always-on local/remote operator built around a Bun/TypeScript daemon and a Go sidecar. Its strongest axis is device and desktop authority: it can observe screen/clipboard/window state, route RPC calls to enrolled sidecars, operate browser sessions through Chrome DevTools Protocol, read and write files, run shell commands, control native desktop windows, trigger workflows, spawn sub-agents, and persist approvals and audit logs.

The real superpower is not the chat layer. It is the control plane around a machine: sidecar enrollment, capability declarations, WebSocket RPC, event scheduling, desktop awareness, authority levels, approval requests, deferred execution, and audit trails. That is valuable to Sentinel because a future Sentinel sidecar will need exactly this shape: explicit capability manifest, revocable enrollment, host action routing, UI/context capture, emergency stop, dry-run, approval, and trace.

The real danger is that JARVIS gives the agent host-level reach. Source inspection found terminal command execution, local and sidecar filesystem reads/writes, clipboard read/write, screenshot capture, Chrome DevTools browser control, arbitrary browser `Runtime.evaluate`, desktop click/type/key/app launch, workflow triggers, external-message templates, Google OAuth setup paths, proactive heartbeat execution, and awareness-driven auto-research. These are powerful mechanisms, but they are not acceptable as direct Sentinel runtime powers.

JARVIS should not be integrated into Sentinel. Sentinel should learn the mechanism classes and rewrite them under proof-first controls:

- TAKE: sidecar capability manifest vocabulary, sidecar enrollment/revocation idea, WebSocket RPC tracing, approval request lifecycle, emergency pause/kill, desktop/browser awareness as future context, screen-to-suggestion pipeline, persisted audit trail, workflow trigger taxonomy.
- REWRITE: PermissionedSidecar, ScreenContextSanitizer, DesktopActionRiskModel, BrowserSandbox, AuthorityPolicy, ApprovalGate, DeferredExecutor, SidecarEventLedger, WorkflowFirewall, SafeHeartbeat, CostAwareAwareness.
- AVOID: host shell execution, default all-capability sidecar config, substring-only command/path blocking, browser form submit/send flows, arbitrary CDP evaluation, clipboard/screenshot ingestion without redaction, prompt-level "banned tool" rules as security, auto-research from screen contents, workflow execution without firewall, sidecar admin config mutation without approval.

Final vendor verdict:

- Best superpower: the sidecar plus desktop-awareness control plane turns an agent into a machine operator.
- Biggest weakness: policy is mixed across numeric authority, role prompts, sidecar config, route checks, and app templates instead of one proof-backed firewall.
- Biggest security risk: a connected sidecar can expose terminal, filesystem, browser, desktop, clipboard, screenshot, and config mutation surfaces to the daemon.
- Most valuable Sentinel rewrite: `SentinelPermissionedSidecar + ScreenContextSanitizer + FirewallDeferredExecutor`, where every host action has manifest permissions, path/command allowlists, preview, approval, and trace.
- Overall usefulness score: 9/10 as a lab specimen.
- Rewrite readiness score: 7/10. The sidecar, authority, approval, awareness, and workflow mechanisms are source-visible enough to rewrite, but runtime behavior remains unverified because this phase intentionally avoided running JARVIS.

## 2. Source Inventory

| Field | Finding |
|---|---|
| Repo URL | `https://github.com/vierisid/jarvis` from local remote metadata |
| Commit | `7b66f0d3c77a4d050d56ff98b5723fd00b9fb937` |
| Clone path | `agent-lab/vendors/jarvis/source` |
| Clone size | Prior `audits/vendor_clone_checks.md` recorded `556` files / `5,481,611` bytes at this commit; current local measurement showed `523` filesystem files / `3,963,340` bytes and `509` `rg --files` entries, likely because of checkout/blobless differences |
| Runtime | Bun/TypeScript daemon plus Go sidecar |
| Package manager | `package.json`, `bun.lock`, and sidecar `go.mod` |
| Package name/version | `@usejarvis/brain`, version `0.4.0` at `package.json:2-3` |
| Main module | `src/daemon/index.ts` at `package.json:5` |
| CLI entrypoint | `bin/jarvis.ts` at `package.json:7-8` |
| Start scripts | `bun run src/daemon/index.ts` and hot dev daemon at `package.json:29-30` |
| Install-time scripts | `postinstall` runs `node scripts/ensure-bun.cjs` and `bun run copy:models`; `prepare` mutates git hooks path at `package.json:40-41` |
| Model copy script | `copy:models` copies wakeword/ONNX assets from `node_modules` into `ui/public` at `package.json:31` |
| Setup scripts | `setup`, `setup:google`, and environment generation scripts at `package.json:36-39` |
| Major TS dirs | `src/actions`, `src/agents`, `src/authority`, `src/awareness`, `src/comms`, `src/daemon`, `src/roles`, `src/sidecar`, `src/vault`, `src/workflows` |
| Sidecar source | Go sidecar in `sidecar/*.go`, including `client.go`, `handlers.go`, `browser.go`, `desktop_windows.go`, `observers.go`, `config.go`, and platform files |
| Role prompts | YAML roles under `roles/*.yaml` and `roles/specialists/*.yaml` |
| Web app templates | Slack and WhatsApp browser-operation templates under `webapp-templates/*.yaml` |
| Generated/minified code | Not deeply audited; no runtime build was executed |
| Dynamic loading | Daemon imports services conditionally, loads role YAML from multiple paths, loads webapp templates, routes sidecar RPC methods by registered capability, and workflow triggers execute stored workflow definitions |

## 3. Consolidated Prior Lab Evidence

The existing G3 artifacts established the first JARVIS split:

- `audits/jarvis_static_audit.md`
- `audits/jarvis_sidecar_map.md`
- `audits/jarvis_desktop_awareness_map.md`
- `audits/jarvis_permission_map.md`
- `audits/jarvis_failure_modes.md`
- `sentinel_integration_notes/jarvis_to_sentinel.md`

Those artifacts correctly identified JARVIS as the strongest specimen for daemon/sidecar/desktop awareness and authority gating, not as a runtime to integrate. This final report consolidates that layer and adds deeper source-path mapping for agent loop, prompts, authority, sidecar RPC, browser, desktop, awareness, workflows, memory, math, side effects, and failure modes.

## 4. Architecture Map

### 4.1 Daemon Bootstrap

Source paths:

- `src/daemon/index.ts`
- `src/daemon/agent-service.ts`
- `src/daemon/background-agent-service.ts`
- `src/daemon/ws-service.ts`
- `src/daemon/channel-service.ts`
- `src/daemon/observer-service.ts`
- `src/daemon/event-reactor.ts`

Mechanism:

- `src/daemon/index.ts` wires the long-running system: config, database, LLM providers, WebSocket service, channel service, authority engine, approval manager, audit trail, deferred executor, agent service, background agent, awareness service, sidecar manager, workflow engine, goal service, and heartbeat loop.
- Authority components are created at `src/daemon/index.ts:372-382`, injected into the orchestrator at `src/daemon/index.ts:409-411`, and injected into `AgentService` for prompt context at `src/daemon/index.ts:422`.
- The daemon auto-builds UI assets if `ui/dist/index.html` is missing by spawning `bun run build:ui` at `src/daemon/index.ts:448-462`.
- Awareness service startup and sidecar-event routing are wired at `src/daemon/index.ts:547-704`.
- Workflow engine startup and auto-suggest wiring are at `src/daemon/index.ts:786-835`.
- Sidecar routing for local tools is enabled at `src/daemon/index.ts:927`.

Inputs:

- YAML config, roles, sidecar tokens/connections, UI clients, channel messages, sidecar events, workflow triggers, heartbeat interval, LLM provider config, user chat.

Outputs:

- Agent responses, tool calls, approval requests, audit records, WebSocket events, sidecar RPCs, workflow executions, proactive suggestions, voice/TTS output, channel broadcasts.

Side effects:

- Starts long-running services, binds HTTP/WebSocket APIs, persists database rows, can spawn UI build process, can trigger browser/desktop/terminal/filesystem side effects through registered tools.

Sentinel rewrite:

- Sentinel must split "daemon lifecycle" from "execution authority". The runtime may start services, but all host-impacting operations should pass through one Sentinel Firewall service with deterministic policy, dry-run preview, approval, and trace.

### 4.2 Agent Loop and Tool Dispatch

Source paths:

- `src/agents/orchestrator.ts`
- `src/agents/sub-agent-runner.ts`
- `src/actions/tools/registry.ts`
- `src/actions/tools/delegate.ts`
- `src/actions/tools/agents.ts`
- `src/daemon/agent-service.ts`

Mechanism:

- `ToolRegistry` registers named tools, validates parameter types, and executes by name at `src/actions/tools/registry.ts:25-67`.
- The primary orchestrator gates every tool call in `executeTool` at `src/agents/orchestrator.ts:498-559`, using emergency state, `getActionForTool`, `AuthorityEngine.checkAuthority`, audit logging, approval request creation, and normal registry execution.
- Sub-agents use the same registry but are denied outright for governed actions requiring approval at `src/agents/sub-agent-runner.ts:98-146`.
- Agent roles become instances with authority bounds, allowed tools, denied tools, spawn capability, and memory scope in `src/agents/agent.ts:27-80`.
- Delegation checks parent spawn authority in `src/agents/delegation.ts:36-42`.
- `AgentService` loads role YAML, registers tools, registers delegate/manage-agent tools, builds system prompts, and routes user messages at `src/daemon/agent-service.ts:137-217` and `src/daemon/agent-service.ts:251-280`.

Inputs:

- User prompt, role definition, tool calls from LLM, tool registry, authority policy, temporary grants, approval manager.

Outputs:

- Tool result strings or multimodal content blocks, approval request IDs, denial messages, audit rows.

Side effects:

- Tools can call local shell, filesystem, browser, desktop, clipboard, screenshot, workflows, documents, goals, channels, or sidecar RPC depending on registry configuration.

Sentinel rewrite:

- The loop shape is useful, but Sentinel should not allow tools to be executable objects directly behind an LLM call. Sentinel should use a two-phase `propose_action -> dry_run -> approve -> execute` contract, with action objects persisted before execution.

### 4.3 Authority, Approval, Deferred Execution, and Audit

Source paths:

- `src/roles/authority.ts`
- `src/authority/engine.ts`
- `src/authority/tool-action-map.ts`
- `src/authority/approval.ts`
- `src/authority/deferred-executor.ts`
- `src/authority/audit.ts`
- `src/authority/emergency.ts`

Mechanism:

- Action categories include read/write/delete data, send message/email, execute command, install software, make payment, modify settings, spawn/terminate agent, access browser, and control app at `src/roles/authority.ts:4-8`.
- Numeric authority requirements are defined at `src/roles/authority.ts:22-36`: read is level 1, write/send is 3, execute/browser/desktop is 5, send email/install is 7, delete/payment/settings/terminate is 9, and spawn agent is level 1.
- `AuthorityEngine.checkAuthority` evaluates temporary grants, overrides, context rules, numeric authority level, then governed-category approval at `src/authority/engine.ts:71-164`.
- Effective level is `Math.max(agentAuthorityLevel, default_level)` at `src/authority/engine.ts:147`, which can raise low-authority agents if the global default is high.
- Context rules support `time_range`, `tool_name`, and `always` at `src/authority/engine.ts:25` and `src/authority/engine.ts:272-291`.
- Tool-to-action mapping covers terminal, filesystem, browser, desktop, delegation, content, tasks, and productivity, but unknown tools default to `read_data` at `src/authority/tool-action-map.ts:64-73`.
- `ApprovalManager.createRequest` persists pending approval rows at `src/authority/approval.ts:35-69`.
- `approve` and `deny` only update pending requests at `src/authority/approval.ts:97-118`.
- `markExecuted` sets a request to executed at `src/authority/approval.ts:129-134`.
- `DeferredExecutor.executeApproved` checks approved status, executes through the registry, marks executed, logs audit, and records learner decisions at `src/authority/deferred-executor.ts:38-87`.
- `AuditTrail.log` inserts action category, decision, approval id, execution flag, timing, and timestamp at `src/authority/audit.ts:42-66`.
- `EmergencyController` supports normal, paused, and killed states; `canExecute` only allows normal at `src/authority/emergency.ts:37`.

Inputs:

- Agent authority level, role id, tool name/category, action category, temporary grants, policy config, approval decisions.

Outputs:

- Allowed/denied/approval-required decisions, persisted approval requests, audit rows, denial strings.

Side effects:

- Approved actions are executed by registry; emergency state is persisted to config in daemon startup callback.

Failure risk:

- Defaulting unknown tools to `read_data` is fail-open for unmapped capabilities.
- `Math.max(agentAuthorityLevel, default_level)` can elevate agents through configuration.
- Prompt-level role approval lists can diverge from actual authority policy.
- Approval requests do not include Sentinel-style evidence, risk score, dry-run preview, or expected external impact.

Sentinel rewrite:

- Replace numeric authority alone with explicit policy per tool/action, including risk level, required evidence, dry-run schema, approval actor, allowed path/domain/account, rate limits, and trace requirements. Unknown actions must be blocked, not downgraded to read.

### 4.4 Sidecar Enrollment and RPC Control Plane

Source paths:

- `src/sidecar/types.ts`
- `src/sidecar/manager.ts`
- `src/sidecar/protocol.ts`
- `src/sidecar/connection.ts`
- `src/sidecar/validator.ts`
- `src/sidecar/scheduler.ts`
- `src/sidecar/rpc.ts`
- `sidecar/types.go`
- `sidecar/client.go`
- `sidecar/config.go`
- `sidecar/main.go`

Mechanism:

- Capabilities are declared as `terminal`, `filesystem`, `desktop`, `browser`, `clipboard`, `screenshot`, `system_info`, and `awareness` in both TS and Go at `src/sidecar/types.ts:8-16` and `sidecar/types.go:7-14`.
- Sidecar config includes terminal blocked commands/default shell/timeout, filesystem blocked paths/max file size, browser CDP/profile, and awareness polling thresholds at `src/sidecar/types.ts:91-96`.
- Manager uses ES256 signing, PEM key storage, JWK export, and JWT validation at `src/sidecar/manager.ts:28`, `src/sidecar/manager.ts:166-217`, and `src/sidecar/manager.ts:397-402`.
- Enrollment validates sidecar name, creates id/token id, builds WebSocket/JWKS URLs, signs JWT claims, and inserts sidecar record at `src/sidecar/manager.ts:230-280`.
- `registerConnection`, `updateCapabilities`, and `dispatchRPC` manage connected sidecars and RPC dispatch at `src/sidecar/manager.ts:347-503`.
- Go sidecar default config enables terminal, filesystem, clipboard, screenshot, system info, awareness, desktop, and browser capabilities by default at `sidecar/config.go:25-45`.
- Go sidecar stores config at `~/.jarvis-sidecar/config.yaml`, returns defaults when absent, and writes config with `0644` permissions at `sidecar/config.go:50-96`.
- Go client decodes JWT payload, runs preflight, connects to the brain WebSocket with `Authorization: Bearer`, sends registration, starts observers, and handles RPC requests in goroutines at `sidecar/client.go`.

Inputs:

- Enrollment token, sidecar config, capability list, sidecar events, RPC requests, WebSocket frames.

Outputs:

- Registered connection, capability updates, RPC results/progress, sidecar events, binary frames, observer streams.

Side effects:

- Remote host actions through RPC; persisted sidecar config and keys; observer data sent to daemon.

Sentinel rewrite:

- Sentinel sidecars should be deny-by-default. Enrollment must require explicit user approval per capability, scoped workspace roots, redaction profile, token expiry, revocation, device attestation where possible, and immutable capability manifests. Admin config mutation must itself be a high-risk action.

### 4.5 Sidecar Protocol, Scheduling, and Validation

Source paths:

- `src/sidecar/protocol.ts`
- `src/sidecar/rpc.ts`
- `src/sidecar/connection.ts`
- `src/sidecar/validator.ts`
- `src/sidecar/scheduler.ts`

Mechanism:

- RPC states are `pending`, `detached`, `completed`, `failed`, `timed_out`, and `cancelled` at `src/sidecar/protocol.ts:8`.
- Event priorities are `critical`, `high`, `normal`, and `low` at `src/sidecar/protocol.ts:11`.
- Default RPC timeouts are initial `30_000` ms and max detached `300_000` ms at `src/sidecar/protocol.ts:82`.
- `RPCTracker.dispatch` resolves quickly if a result arrives before initial timeout; otherwise it transitions to detached and later calls detached callbacks or times out at `src/sidecar/rpc.ts:39-97`.
- Connection heartbeat uses `30_000` ms interval and closes after `3` missed pongs at `src/sidecar/connection.ts:13-14` and `src/sidecar/connection.ts:119-134`.
- JSON frames are capped at 1 MB, binary frames at 50 MB, inline binary threshold is 256 KB, and binary refs are 36-byte UUIDs at `src/sidecar/validator.ts:10-13`.
- Validator strips dangerous object keys `__proto__`, `constructor`, and `prototype` at `src/sidecar/validator.ts`.
- Scheduler queues events per sidecar, sorts by priority, and drains one round-robin pass every 50 ms at `src/sidecar/scheduler.ts:29-90`.

Inputs:

- RPC requests, sidecar events, binary frames, priorities, timeout config.

Outputs:

- Dispatched events, detached notifications, completed/failed/timed-out RPC state.

Side effects:

- Prevents one sidecar queue from monopolizing event processing; does not by itself sanitize sensitive payload semantics.

Sentinel rewrite:

- Keep the event scheduler concept, but bind every event/RPC to a trace id, policy decision, sanitized payload classification, cost/latency metadata, and privacy redaction result.

### 4.6 Terminal, Filesystem, Clipboard, Screenshot, and Admin RPC Handlers

Source paths:

- `sidecar/handlers.go`
- `src/actions/tools/builtin.ts`
- `src/actions/terminal/executor.ts`
- `src/actions/tools/sidecar-route.ts`
- `src/actions/tools/local-tools-guard.ts`

Mechanism:

- Go handler registry registers terminal, filesystem, clipboard, screenshot, system info, desktop, browser, and always registers admin `get_config` and `update_config` at `sidecar/handlers.go:15-64`.
- `run_command` executes a command string using platform shell (`/C` or `-c`) through `exec.CommandContext` at `sidecar/handlers.go:107-109`.
- Filesystem reads and writes use `os.ReadFile`, `os.MkdirAll`, and `os.WriteFile` at `sidecar/handlers.go:148-191`.
- Blocked path enforcement resolves paths and uses prefix matching at `sidecar/handlers.go:137-141`.
- Screenshot capture writes a temp PNG, reads it, and returns base64 data at `sidecar/handlers.go:238-276`.
- TS built-in tools expose local or sidecar-routed `run_command`, `read_file`, `write_file`, `list_directory`, `get_clipboard`, `set_clipboard`, `capture_screen`, `get_system_info`, browser tools, and sidecar list at `src/actions/tools/builtin.ts`.
- `--no-local-tools` flips a module-level flag and requires target sidecar for local tools at `src/actions/tools/local-tools-guard.ts:7-20`.
- `routeToSidecar` resolves sidecars by id/name/substring, auto-selects a single capable sidecar, checks connected state and capability availability, then dispatches RPC at `src/actions/tools/sidecar-route.ts:29-166`.

Inputs:

- Command strings, file paths/content, clipboard content, screenshot requests, sidecar target/capability.

Outputs:

- stdout/stderr/exit code, file content, directory listing, clipboard content, base64 screenshots, sidecar status.

Side effects:

- Arbitrary host shell command execution, host file read/write, clipboard mutation, screen capture, sidecar config mutation.

Failure risk:

- Command blocking is substring-based and configuration defaults to empty blocked command list.
- Path blocking is prefix-based, not an allow-root model.
- Admin config update is always registered by the Go sidecar handler registry.

Sentinel rewrite:

- No host shell in Sentinel v1. Future sidecar command execution must use declared command templates, workspace-root allowlists, no raw shell, no implicit cwd, dry-run preview, and explicit user approval. File access must be allow-root plus canonical path containment, not blocked prefixes.

### 4.7 Browser Control

Source paths:

- `sidecar/browser.go`
- `src/actions/tools/builtin.ts`
- `src/actions/browser/session.ts`
- `src/actions/browser/chrome-launcher.ts`
- `webapp-templates/slack.yaml`
- `webapp-templates/whatsapp.yaml`

Mechanism:

- Go sidecar CDP client connects to Chrome on `localhost:<port>/json`, finds a page websocket, and sends CDP JSON commands at `sidecar/browser.go`.
- Browser navigate calls `Page.navigate`, waits 1 second, then returns a snapshot at `sidecar/browser.go:192-213`.
- Browser click uses `Runtime.evaluate` to find interactive elements and call `el.click()` at `sidecar/browser.go:240-263`.
- Browser type sets focus/value, dispatches events, or sends key events; if `submit` is true, it sends Enter at `sidecar/browser.go:275-328`.
- Browser screenshot uses `Page.captureScreenshot` with quality 80 at `sidecar/browser.go:340-347`.
- Browser scroll maps `amount * 100` pixels at `sidecar/browser.go:378-397`.
- Browser evaluate executes arbitrary `Runtime.evaluate` expressions at `sidecar/browser.go:409-421`.
- Snapshot returns URL/title, body text truncated to 5000 characters, up to 200 interactive elements, and element text truncated to 100 chars at `sidecar/browser.go:435-477`.
- Slack template explicitly instructs message send via `desktop_press_keys("ctrl,enter")` at `webapp-templates/slack.yaml:186-191`.
- WhatsApp template explicitly instructs sending via `browser_type` with `submit:true` at `webapp-templates/whatsapp.yaml:88-92`.

Inputs:

- URL, element id, text, submit flag, scroll direction/amount, arbitrary JS expression, app-specific prompt templates.

Outputs:

- Browser snapshots, screenshots, page interaction results, message send effects if used against real web apps.

Side effects:

- Navigation, clicks, typing, form submit/send, arbitrary JS execution, file upload, external messages.

Failure risk:

- App templates ban tools by instruction, not by enforceable policy.
- `browser_evaluate` is a direct arbitrary code execution surface inside the browser context.
- Message sending is deliberately optimized in templates, which is useful but high-risk.

Sentinel rewrite:

- Browser must start read-only. Later write interactions require sandbox profile, no real accounts by default, intent classification, DOM diff preview, no form submit without explicit user approval, and per-domain policy. Arbitrary evaluate should be blocked except for signed, audited, deterministic extraction snippets.

### 4.8 Desktop Control and Desktop Awareness

Source paths:

- `src/actions/tools/desktop.ts`
- `sidecar/desktop_windows.go`
- `sidecar/desktop_darwin.go`
- `sidecar/desktop_linux.go`
- `sidecar/platform_windows.go`
- `sidecar/platform_linux.go`
- `sidecar/platform_darwin.go`
- `sidecar/observers.go`

Mechanism:

- TS desktop tools expose `desktop_list_windows`, `desktop_snapshot`, `desktop_click`, `desktop_type`, `desktop_press_keys`, `desktop_launch_app`, `desktop_screenshot`, `desktop_focus_window`, and `desktop_find_element` at `src/actions/tools/desktop.ts:269-615`.
- Each desktop tool can route to a sidecar target or execute local desktop controller logic at `src/actions/tools/desktop.ts`.
- Windows sidecar lists windows, snapshots UI Automation trees, clicks elements, types text, sends keys, launches apps, focuses windows, and finds elements at `sidecar/desktop_windows.go:17-305`.
- Windows typing and hotkeys use `System.Windows.Forms.SendKeys` at `sidecar/desktop_windows.go:154-187`.
- Windows app launch uses `Start-Process` at `sidecar/desktop_windows.go:205-222`.
- Platform files implement clipboard, screenshot, default shell, browser launch, and active-window capture for Windows/macOS/Linux.
- `ClipboardObserver` polls clipboard every 2000 ms and emits raw clipboard content on change at `sidecar/observers.go:17-75`.
- `ScreenObserver` captures screen at awareness interval, computes sampled pixel diff, and emits binary screen captures when change exceeds threshold at `sidecar/observers.go:98-200`.
- `WindowObserver` polls active window and emits `context_changed` and `idle_detected` events at `sidecar/observers.go:238-327`.

Inputs:

- Window PIDs, element IDs, UI Automation trees, key strings, app executable path, screen/clipboard/window state.

Outputs:

- Window lists, UI trees, clicked/typed/keyed actions, launched processes, screenshots, clipboard events, screen capture events.

Side effects:

- Native app control, arbitrary keystrokes, process launch, data capture from screen and clipboard.

Sentinel rewrite:

- Desktop sidecar is a later-stage product, not v1. It needs a `ScreenContextSanitizer`, secret/PII redaction, app allowlists, active-window proof, command preview, no hidden keystrokes, and a human-visible approval surface for every click/type/launch outside low-risk read-only observation.

### 4.9 Awareness, OCR, Struggle Detection, and Proactive Reaction

Source paths:

- `src/awareness/service.ts`
- `src/awareness/ocr-engine.ts`
- `src/awareness/context-tracker.ts`
- `src/awareness/struggle-detector.ts`
- `src/awareness/intelligence.ts`
- `src/awareness/suggestion-engine.ts`
- `src/daemon/event-reactor.ts`
- `sidecar/observers.go`

Mechanism:

- `AwarenessService` wires OCR, context tracker, intelligence, suggestion engine, and retention cleanup at `src/awareness/service.ts:47-115`.
- Worst-case cloud vision cost estimate uses captures per hour capped by cloud vision cooldown and multiplies vision calls by 1400 tokens at `src/awareness/service.ts:152-175`.
- Screen capture handling runs OCR, context tracking, event classification, key-moment retention, optional cloud escalation, and suggestion evaluation at `src/awareness/service.ts:409-485`.
- Context tracker emits `stuck_detected` when same-window duration exceeds configured threshold and screen text is unchanged at `src/awareness/context-tracker.ts:128-145`.
- Context tracker emits struggle events with `compositeScore`, signal list, app category, and duration at `src/awareness/context-tracker.ts:159-169`.
- Struggle detector uses a 30-snapshot max, 3.5-minute window, 8-minimum-snapshot threshold, 120-second grace, 180-second cooldown, and weighted composite score at `src/awareness/struggle-detector.ts:35-153`.
- Signal weights are trial/error 0.30, undo/revert 0.25, repeated output 0.25, low progress 0.20; threshold is 0.5 at `src/awareness/struggle-detector.ts:42-55` and `src/awareness/struggle-detector.ts:119-125`.
- Intelligence escalates screenshots to LLM vision for errors, stuck states, significant context changes, or empty OCR at `src/awareness/intelligence.ts:35-55`.
- Suggestion engine rate-limits errors to 15 seconds and stuck suggestions to 60 seconds at `src/awareness/suggestion-engine.ts:21-25`.
- Event reactor converts critical/high events to synthetic agent messages with cooldown/dedup and queueing at `src/daemon/event-reactor.ts:38-139`.
- Daemon auto-researches detected errors and high-score code/terminal struggles at `src/daemon/index.ts:596-675`.

Inputs:

- OCR text, screenshots, active window metadata, idle events, cloud analysis, app category, recent patterns.

Outputs:

- Observations, key-moment captures, context/stuck/error/struggle events, proactive suggestions, synthetic agent messages, auto-research tasks.

Side effects:

- LLM calls on screenshot-derived content, voice notifications, channel broadcasts, background research, possible tool execution through proactive agent path.

Failure risk:

- Screen and clipboard are untrusted and sensitive. They can contain secrets and prompt injection.
- Auto-research from visible error text can leak private code or terminal data to cloud models/search.
- Proactive reactions use agent service with tools, so context observation can become action.

Sentinel rewrite:

- Sentinel can learn the sensing pipeline, but all raw screen/clipboard data must be treated as untrusted evidence. Add local redaction before LLM, never let screen text become policy, require user opt-in per app/window, and make proactive suggestions draft-only until approved.

### 4.10 Workflows and Triggers

Source paths:

- `src/workflows/engine.ts`
- `src/workflows/triggers/manager.ts`
- `src/workflows/triggers/cron.ts`
- `src/workflows/triggers/webhook.ts`
- `src/workflows/triggers/poller.ts`
- `src/workflows/triggers/observer-bridge.ts`
- `src/workflows/triggers/screen-condition.ts`
- `src/workflows/auto-suggest.ts`
- `src/workflows/nodes/actions/send-message.ts`
- `src/workflows/nodes/actions/code-execution.ts`

Mechanism:

- Trigger manager supports cron, webhook, polling, file/clipboard/screen observer triggers, and executes workflows through the engine at `src/workflows/triggers/manager.ts:5-35`, `src/workflows/triggers/manager.ts:190-281`.
- Cron parser supports five-field expressions and schedules callbacks at `src/workflows/triggers/cron.ts:2-4` and `src/workflows/triggers/cron.ts:224-227`.
- Webhooks validate optional HMAC-SHA256 signatures using `X-Jarvis-Signature` at `src/workflows/triggers/webhook.ts:2-35` and `src/workflows/triggers/webhook.ts:101-116`.
- Poller requires interval at least 1000 ms and performs outbound HTTP fetch jobs at `src/workflows/triggers/poller.ts:70-98`.
- Screen condition evaluator asks an LLM to answer yes/no from OCR text and screen state at `src/workflows/triggers/screen-condition.ts:144-179`.
- Auto-suggest stores up to 500 awareness patterns, waits for at least 10 patterns, analyzes every 5 minutes, detects 5 app switches or 3 app errors, and uses confidence formulas such as `Math.min(count / 20, 0.9)` and `Math.min(count / 10, 0.85)` at `src/workflows/auto-suggest.ts:30-177`.

Inputs:

- Workflow definitions, triggers, webhook requests, poll URLs, screen/OCR events, LLM screen decisions, pattern buffers.

Outputs:

- Workflow executions, generated suggestions, callbacks, external HTTP fetches, send-message/code-execution node effects.

Side effects:

- Scheduled actions, inbound webhook-to-execution path, outbound polling, screen-triggered automation, possible messaging and code execution nodes.

Sentinel rewrite:

- Workflow automation is a later Sentinel layer. It must compile workflows into action plans, run risk simulation, block high-impact nodes by default, require signed triggers for inbound, and mark screen/clipboard/poll/webhook data as untrusted inputs.

### 4.11 Prompt and Instruction Pipeline

Source paths:

- `src/roles/prompt-builder.ts`
- `src/roles/types.ts`
- `src/roles/*.yaml`
- `src/daemon/agent-service.ts`
- `src/daemon/background-agent-service.ts`
- `src/authority/engine.ts`
- `webapp-templates/*.yaml`

Mechanism:

- Role schema includes responsibilities, autonomous actions, approval-required actions, heartbeat instructions, sub-roles, tools, and authority level at `src/roles/types.ts:27-35`.
- `buildSystemPrompt` builds sections from role name/description, responsibilities, autonomous actions, approval-required actions, task acknowledgment rule, heartbeat instructions, tools, authority rules, webapp-specific instructions, and active goal context at `src/roles/prompt-builder.ts:24-135` and `src/roles/prompt-builder.ts:210`.
- Authority rules are converted into prompt text by `AuthorityEngine.describeRulesForAgent` at `src/authority/engine.ts:180-190`.
- `AgentService.buildFullSystemPrompt` retrieves vault/context/goals and app-specific instructions before sending messages at `src/daemon/agent-service.ts:464-477` and `src/daemon/agent-service.ts:562-569`.
- Background heartbeat prompt tells the agent to execute due commitments and perform queued research using browser/tools at `src/daemon/background-agent-service.ts:243-298`.
- Personal assistant role explicitly lists terminal, browser, file management, and browsing in autonomous actions, and heartbeat instruction says overdue commitments should be executed with tools at `roles/personal-assistant.yaml:71-266`.
- CEO/founder role has authority level 9 and tools including browser, terminal, email, calendar, file-ops, and app-control at `roles/ceo-founder.yaml:36-144`.
- System admin role has authority level 9 and autonomous actions including permission adjustment and routine system operations at `roles/system-admin.yaml:13-76`.
- Slack/WhatsApp templates are highly operational instructions for message sending and app navigation at `webapp-templates/slack.yaml` and `webapp-templates/whatsapp.yaml`.

Inputs:

- Role YAML, runtime context, authority text, vault/context retrieval, webapp template matches, goals, heartbeat events.

Outputs:

- System prompts and app-specific instructions used by the LLM.

Failure risk:

- Prompt instructions can grant apparent behavioral permission that diverges from real policy.
- Webapp templates include "banned tools" instructions, but security must be enforced by code policy.
- Heartbeat prompts push autonomous execution, which is incompatible with Sentinel v1 safety.

Sentinel rewrite:

- Sentinel prompts should be policy-descriptive, not policy-authoritative. The firewall must be the authority. Role instructions can propose actions, but cannot bypass risk classification, dry-run, approval, or trace.

### 4.12 Memory and Vault

Source paths:

- `src/vault/schema.ts`
- `src/vault/retrieval.ts`
- `src/vault/vectors.ts`
- `src/vault/entities.ts`
- `src/vault/facts.ts`
- `src/vault/relationships.ts`
- `src/vault/goals.ts`
- `src/vault/observations.ts`
- `src/vault/awareness.ts`
- `src/vault/user-profile.ts`

Mechanism:

- Vault schema includes entities, facts, relationships, vectors, observations, awareness captures, goals, workflow data, documents, settings, and other persistent tables.
- Retrieval extracts search terms by stopword filtering, searches entity names, limits to 10 entities, fetches facts and relationships, and formats prompt context at `src/vault/retrieval.ts:16-172`.
- Goal context renders active goals with scores and limit 15 at `src/vault/retrieval.ts:202-247`.
- Vector storage stores Float32 embeddings as SQLite BLOBs at `src/vault/vectors.ts:22-57`.
- `findSimilar` is currently a stub returning an empty array, with TODO for sqlite-vec/HNSW at `src/vault/vectors.ts:64-80`.
- Goal score updates clamp score to `[0, 1]` and log score progress at `src/vault/goals.ts:205-218`.

Inputs:

- User messages, entities/facts/relationships, awareness observations, goals, embeddings.

Outputs:

- Prompt context, goal context, persisted memory, scores, observations.

Failure risk:

- Memory retrieval is mostly lexical and can inject stale/untrusted data into prompts.
- Vector search is not active in this source snapshot despite schema support.
- Awareness-derived memory can contain sensitive screen/clipboard content.

Sentinel rewrite:

- Memory should be typed as facts, preferences, project context, outcomes, and evidence. It must never be policy. Retrieval needs source, confidence, freshness, sensitivity, and trust level on every injected memory.

## 5. Algorithm and Math Audit

| Mechanism | Source | Formula / Logic | Failure Risk | Sentinel Rewrite |
|---|---|---|---|---|
| Authority thresholds | `src/roles/authority.ts:22-36` | read=1, write/send=3, execute/browser/desktop=5, email/install=7, delete/payment/settings/terminate=9, spawn=1 | Numeric levels hide action-specific risk and evidence requirements | Policy matrix per action with risk, evidence, actor, allowed resources, and approval |
| Effective authority | `src/authority/engine.ts:147` | `effectiveLevel = Math.max(agentAuthorityLevel, default_level)` | Global default can raise agents | Never elevate by default; use minimum of role and policy cap unless explicit grant |
| Authority decision order | `src/authority/engine.ts:71-164` | grants -> overrides -> context rules -> numeric level -> governed approval | Temporary grants and overrides can bypass expected approval | Time-boxed signed grants with trace, reason, scope, and revocation |
| Unknown tool fallback | `src/authority/tool-action-map.ts:64-73` | Explicit map, category map, else `read_data` | New dangerous tools may be misclassified as low risk | Unknown action = blocked until policy is added |
| Approval expiration | `src/authority/approval.ts:186-191` | `created_at < Date.now() - maxAgeMs` for pending requests | Approval lifecycle not tied to evidence/dry-run validity | Expire preview hashes and evidence snapshots together |
| RPC timeouts | `src/sidecar/protocol.ts:82`, `src/sidecar/rpc.ts:39-97` | 30s initial, 300s max detached | Detached tasks can complete after user attention moves away | Detached task must have trace status, cancel, and post-completion approval boundary |
| Sidecar heartbeat | `src/sidecar/connection.ts:13-14` | 30s ping, close after 3 missed pongs | Availability-only, not capability trust | Add capability health and policy sync hash |
| Event validation size caps | `src/sidecar/validator.ts:10-13` | 1MB JSON, 50MB binary, 256KB inline, 36B UUID ref | Size safety does not sanitize secrets | Add privacy classification and redaction before persistence/LLM |
| Event scheduler | `src/sidecar/scheduler.ts:29-90` | 50ms interval, priority sort, one round-robin pass | Critical event storm still possible | Per-source/event rate limits, trace ids, budget caps |
| Sidecar default capabilities | `sidecar/config.go:25-45` | Enables terminal/filesystem/clipboard/screenshot/system_info/awareness/desktop/browser by default | Too much authority by default | Deny-by-default, explicit capability consent |
| Terminal timeout | `sidecar/config.go:31-35`, `sidecar/handlers.go:107-109` | Default 30000ms, shell executes command string | Raw shell injection and host mutation | No raw shell; signed command templates only |
| Filesystem max size | `sidecar/config.go:35-36` | Default read max 100KB | Path access is still broad | Workspace-root allowlists and sensitivity scanning |
| Path blocking | `sidecar/handlers.go:137-141` | canonical path startsWith blocked prefix | Prefix logic can be brittle; blocklist is not a sandbox | Allowlist root containment with path normalization |
| Browser snapshot caps | `sidecar/browser.go:435-477` | text 5000 chars, 200 elements, element text 100 chars | May omit critical security context or include sensitive data | DOM extraction policy per domain plus redaction |
| Browser scroll | `sidecar/browser.go:378-397` | pixels = amount * 100 | Minor | Safe if read-only; write actions need approval |
| Browser submit | `sidecar/browser.go:275-328` | submit flag sends Enter key events | Can submit forms/send messages | No submit in v1; explicit preview and user approval later |
| Screen change diff | `sidecar/observers.go:188-200` | sample every 100 bytes; changed/total | Pixel diff ignores semantic sensitivity | Add local redaction and app/window allowlists |
| Awareness cost estimate | `src/awareness/service.ts:152-175` | min(captures/hr, cooldown cap) * 1400 tokens | Worst-case only; privacy not represented | Cost + privacy budget per run/app |
| Struggle score | `src/awareness/struggle-detector.ts:42-55`, `:119-125` | .30 trial/error + .25 undo + .25 repeated output + .20 low progress; threshold .5 | Behavior inference may be wrong and invasive | Treat as suggestion signal only, never action permission |
| Struggle windows | `src/awareness/struggle-detector.ts:35-40` | 30 snapshots, 3.5 min, min 8 snapshots | Timing assumptions may not generalize | Make thresholds user-visible and app-scoped |
| Suggestion rate limits | `src/awareness/suggestion-engine.ts:21-25` | error 15s, stuck 60s | Still can become noisy or leak context | User-configured privacy and notification budgets |
| Event reactor cooldown | `src/daemon/event-reactor.ts:13-27`, `:182-195` | per-type max and global max 15 per 10 min | Converts untrusted events into agent messages | Events are evidence, not instructions; no tool execution without firewall |
| Workflow auto-suggest | `src/workflows/auto-suggest.ts:30-177` | 500 pattern buffer, 5 min analysis cooldown, count thresholds, count/20 and count/10 confidence caps | Pattern suggestions may overfit sensitive behavior | User-visible candidate workflow with no auto-enable |
| Polling interval | `src/workflows/triggers/poller.ts:70-98` | interval must be >=1000ms | External polling can leak or overload | Domain allowlist, rate limit, trace, approval |
| Vault retrieval | `src/vault/retrieval.ts:16-172` | stopword terms -> entity LIKE search -> max 10 profiles | Lexical/stale memory injection | Source/confidence/freshness/sensitivity-scored memory |
| Goal score clamp | `src/vault/goals.ts:205-218` | clamp score to [0,1] and log progress | Goal score can be modified by system source | Goal updates require user evidence and trace |
| Vector search | `src/vault/vectors.ts:64-80` | Stub returns `[]` | Semantic memory absent despite schema | Implement audited vector retrieval later, not as policy |

## 6. Prompt and Skill Instruction Audit

JARVIS has no single "skill marketplace" like OpenClaw, but it has several instruction and capability layers that function like skills:

| Instruction Layer | Source | Purpose | Risk | Sentinel Rewrite |
|---|---|---|---|---|
| Role YAML | `roles/*.yaml`, `roles/specialists/*.yaml` | Defines responsibilities, autonomous actions, approval-required actions, tools, authority level | Role text may overpromise autonomous authority | Role prompts may describe behavior but cannot authorize actions |
| Prompt builder | `src/roles/prompt-builder.ts:24-135` | Composes role, autonomy, approval, task acknowledgment, heartbeat, tools, authority, webapp instructions | Prompt composition blends policy, UX, and capability | Separate prompt context from policy engine |
| Authority prompt text | `src/authority/engine.ts:180-190` | Describes governed categories and current rules to the agent | Agent may interpret policy text creatively | Firewall decision objects, not free-text policy |
| Heartbeat prompt | `src/daemon/agent-service.ts:481-506`, `src/daemon/background-agent-service.ts:243-298` | Tells background agent to execute due commitments and research queues | Background autonomy can mutate external state | SafeHeartbeat: summarize/draft only unless approved |
| Personal assistant role | `roles/personal-assistant.yaml:71-266` | Broad assistant with browser, terminal, files, desktop, workflows | Too broad for v1 Sentinel | Split into least-privilege task roles |
| CEO/founder role | `roles/ceo-founder.yaml:36-144` | Business operator with authority level 9 and external communication tools | Strategic and external commitments | Sentinel GTM Operator drafts, never commits externally in v1 |
| System admin role | `roles/system-admin.yaml:13-76` | System operations and permission changes | High privilege host mutation | No sysadmin execution in Sentinel v1 |
| Slack template | `webapp-templates/slack.yaml:68-73`, `:186-191` | Operational browser/desktop sequence for Slack messages | Real outbound messages and fuzzy target matching | Draft-only channel actions until channel firewall exists |
| WhatsApp template | `webapp-templates/whatsapp.yaml:19-23`, `:88-92` | Operational browser sequence for WhatsApp sends | Real outbound messages via Enter submit | No real messaging; no browser submit in v1 |
| Screen condition prompt | `src/workflows/triggers/screen-condition.ts:144-179` | LLM yes/no classifier over OCR/screen state | Screen text is untrusted and sensitive | Local deterministic filters first; LLM classification only with sanitized input |
| Awareness intelligence prompts | `src/awareness/intelligence.ts:79-314` | Cloud vision analysis, delta, struggle and session prompts | Sends screen/OCR context to model | Redaction, app allowlist, cost/privacy budget, opt-in |

## 7. Runtime Side-Effect Map

| Side Effect | Trigger | Source Paths | Risk Level | Existing Mitigation | Gap | Sentinel Mitigation / Eval |
|---|---|---|---|---|---|---|
| Shell command | `run_command` local or sidecar | `src/actions/tools/builtin.ts:62-104`, `sidecar/handlers.go:107-109` | Critical | Authority level and optional blocked commands | Raw shell string; default blocklist empty | Block in v1; later signed command templates and command injection eval |
| File read | `read_file` | `src/actions/tools/builtin.ts:121-139`, `sidecar/handlers.go:148-166` | High | Authority mapping, max size, blocked paths | No allow-root/sensitivity policy | Workspace allowlist and sensitive-file scanner eval |
| File write | `write_file` | `src/actions/tools/builtin.ts:168-191`, `sidecar/handlers.go:174-191` | High | Authority mapping, blocked paths | Can create dirs/write anywhere not blocked | Data/generated-projects only in Sentinel v1 |
| Clipboard read/write | `get_clipboard`, `set_clipboard`, observer | `src/actions/tools/builtin.ts:330-377`, `sidecar/observers.go:17-75` | High | Capability gate | Raw content can include secrets | Redact, opt-in, no persistent raw clipboard |
| Screenshot | `capture_screen`, desktop screenshot, observer | `src/actions/tools/builtin.ts:384-398`, `src/actions/tools/desktop.ts:479-524`, `sidecar/observers.go:98-200` | High | Capability gate, size cap | Raw screen data to daemon/LLM | ScreenContextSanitizer and app allowlist |
| Browser navigate/click/type | Browser tools | `src/actions/tools/builtin.ts:537-790`, `sidecar/browser.go:192-421` | High | Authority category, app template instructions | Can submit forms/send messages | Browser read-only first; no submit |
| Browser arbitrary JS | `browser_evaluate` | `sidecar/browser.go:409-421` | Critical | Template says banned for some apps | Still a registered tool | Block in Sentinel except signed extractors |
| Desktop click/type/key/launch | Desktop tools | `src/actions/tools/desktop.ts:322-478`, `sidecar/desktop_windows.go:111-222` | Critical | Authority category | Host app control; keystroke injection | Desktop action approval and visible preview |
| External messaging via app templates | Slack/WhatsApp templates | `webapp-templates/slack.yaml`, `webapp-templates/whatsapp.yaml` | Critical | Prompt-level target confirmation | Can send real messages | Draft-only and contact approval |
| Sidecar admin mutation | `update_config` | `sidecar/handlers.go:63-64` | Critical | Always registered, no capability gate in registry | Can enable/alter capabilities | Admin config changes require separate signed approval |
| Workflow execution | Cron/webhook/poll/observer | `src/workflows/triggers/manager.ts:190-281` | High/Critical | Optional webhook HMAC | Trigger can execute high-impact nodes | Workflow compile-time policy and runtime approval |
| Outbound polling | Poll trigger | `src/workflows/triggers/poller.ts:70-98` | Medium/High | 1000ms min interval | Domain/data exfil risk | Domain allowlist and trace |
| Google/OAuth setup | Setup scripts and daemon OAuth | `package.json:39`, `src/daemon/index.ts:291-294` | High | User setup expected | Account access risk | Explicit OAuth scope review; no real accounts in lab |
| Proactive heartbeat execution | Heartbeat prompts | `roles/personal-assistant.yaml:95-266`, `src/daemon/agent-service.ts:481-506` | High | Authority and approvals | Background action without immediate user intent | SafeHeartbeat draft-only |
| Memory write | Vault/observations/goals | `src/vault/*`, `src/awareness/service.ts:349-356` | Medium/High | Schema and retention cleanup | Sensitive screen/context persistence | Sensitivity labels and deletion controls |

## 8. Security and Failure Autopsy

| Failure Mode | How It Can Happen In JARVIS | Exact Source Paths | Existing Protection | Gap | Sentinel Prevention / Required Test |
|---|---|---|---|---|---|
| Prompt injection | Webpage, Slack, WhatsApp, screen OCR, clipboard, or vault memory enters prompts | `src/roles/prompt-builder.ts`, `src/awareness/service.ts`, `webapp-templates/*.yaml`, `src/vault/retrieval.ts` | Some tool bans in prompt templates | Untrusted text can influence tool use | Treat all observed content as data; prompt-injection eval with browser/OCR fixtures |
| Tool injection | New/unmapped tool defaults to read_data | `src/authority/tool-action-map.ts:64-73` | Category map | Fail-open default | Unknown tool blocked; static tool-policy test |
| Malicious sidecar | Enrolled sidecar can report capabilities/events and receive RPCs | `src/sidecar/manager.ts`, `src/sidecar/connection.ts`, `src/sidecar/validator.ts` | JWT validation and event validation | Device trust and event truth not verified | Device manifest, attestation, event trust labels |
| Credential leakage | Clipboard/screenshot/OCR/browser snapshot may capture secrets | `sidecar/observers.go`, `src/awareness/service.ts`, `sidecar/browser.go` | Size caps, retention cleanup | No semantic redaction before LLM/storage | Secret redaction eval on screenshots/clipboard/browser snapshots |
| Filesystem escape | File read/write outside intended workspace | `sidecar/handlers.go:137-191`, `src/actions/tools/builtin.ts:121-191` | Blocked paths and max size | No allow-root containment | Path traversal and sensitive file eval |
| Shell abuse | Agent runs raw command string through shell | `sidecar/handlers.go:107-109`, `src/actions/tools/builtin.ts:62-104` | Authority level 5, optional blocked commands | Shell is too broad | Block v1; command template eval later |
| Unauthorized external message | Browser templates send Slack/WhatsApp messages | `webapp-templates/slack.yaml:186-191`, `webapp-templates/whatsapp.yaml:88-92` | Prompt says confirm target | No legal/compliance/draft-only enforcement | No auto-send; outbound-message approval eval |
| Browser form submission | Browser type submit flag presses Enter | `sidecar/browser.go:321-328` | Authority access_browser | Submit bundled with type tool | Separate type and submit actions; block submit |
| Desktop overreach | Desktop tools click/type/launch apps | `src/actions/tools/desktop.ts`, `sidecar/desktop_windows.go` | Authority control_app level 5 | Host UI can mutate state invisibly | Human-visible preview and action capture |
| Memory poisoning | Vault/observations/roles/templates can influence prompts | `src/vault/retrieval.ts`, `src/roles/prompt-builder.ts`, `src/awareness/service.ts` | None sufficient | Memory may become hidden instruction | Memory cannot authorize; trust labels |
| Fake evidence | Screen/browser/vault claims may be stale or partial | `src/vault/retrieval.ts`, `sidecar/browser.go` | None | No evidence confidence model | Evidence ledger with source/freshness/confidence |
| Hallucinated decision | Agent can act from prompt context without proof gates | `src/agents/orchestrator.ts`, `src/daemon/agent-service.ts` | Authority only | No decision proof requirement | DecisionPlan must cite evidence |
| Cost explosion | Awareness cloud vision, heartbeat research, workflows, LLM loops | `src/awareness/service.ts:152-175`, `src/daemon/index.ts:596-675`, `src/daemon/agent-service.ts:481-506` | Some cooldowns | No unified budget ledger | CostRouter with per-run caps |
| Unsafe self-improvement | Workflow auto-suggest and roles push automation | `src/workflows/auto-suggest.ts`, `roles/*.yaml` | Suggestions only in some paths | Suggested workflows can become enabled automation | Improvement proposals only; no auto-enable |
| Persistence abuse | Daemon, sidecar config, workflows, settings, goals persist state | `src/daemon/index.ts`, `sidecar/config.go`, `src/vault/schema.ts` | Schema/persistence | Hard to audit behavior drift | Trace ledger and policy version hashes |
| Vendor lock-in | JARVIS-specific role/sidecar/workflow contracts | Many | None | Direct integration would inherit assumptions | Rewrite from principles, no vendor code |
| User trust collapse | Agent watches screen/clipboard and can act | `sidecar/observers.go`, `src/awareness/service.ts`, `src/actions/tools/desktop.ts` | Config and UI expected | Privacy and action boundaries not strong enough | Opt-in app scope, redaction, approval, trace viewer |

## 9. Superpower Extraction

### Superpower 1: Permissioned Sidecar Control Plane

- Source paths: `src/sidecar/manager.ts`, `src/sidecar/types.ts`, `src/sidecar/protocol.ts`, `src/sidecar/connection.ts`, `src/sidecar/rpc.ts`, `sidecar/client.go`, `sidecar/config.go`, `sidecar/handlers.go`.
- Mechanism: ES256 enrollment token, WebSocket connection, capability list, RPC dispatch, heartbeat, event scheduler, handler registry.
- Why users care: the agent can operate a real machine, not only chat.
- What makes it powerful: capability routing lets one daemon reach multiple hosts and execute terminal/filesystem/browser/desktop actions.
- What makes it risky: default sidecar config enables broad host capabilities; RPC handlers include raw shell, file write, browser evaluate, desktop control, and admin config update.
- Sentinel should learn: sidecar manifest, enrollment, revocation, event scheduling, detached RPC lifecycle.
- Sentinel must rewrite: deny-by-default permissioned sidecar with scoped capabilities, no raw shell, no broad filesystem, signed policy hash, and per-action trace.
- Firewall implication: every RPC method becomes a firewall action type.
- Trace requirement: enrollment, capability update, RPC request, dry-run, approval, result, and redaction hashes.
- Eval requirement: malicious sidecar, disabled capability, config mutation, path traversal, command injection, fake event.
- Priority: later, after GTM Operator and core firewall are stable.

### Superpower 2: Desktop Awareness and Screen Context

- Source paths: `sidecar/observers.go`, `src/awareness/service.ts`, `src/awareness/context-tracker.ts`, `src/awareness/struggle-detector.ts`, `src/awareness/intelligence.ts`.
- Mechanism: clipboard polling, screen capture diffing, active-window polling, OCR, context tracking, struggle scoring, cloud vision escalation, suggestions.
- Why users care: the agent can notice errors, stuck states, repeated behavior, and context shifts without the user explaining everything.
- What makes it powerful: it turns visual UI into event streams and proactive help.
- What makes it risky: screen/clipboard often contain secrets, private messages, code, customer data, and prompt injections.
- Sentinel should learn: event taxonomy, local OCR, key-moment retention, struggle signal scoring.
- Sentinel must rewrite: opt-in app/window capture, local redaction, no raw clipboard persistence, no cloud vision unless approved, no action from observed text.
- Firewall implication: screen/clipboard data is untrusted evidence, not instruction.
- Trace requirement: capture source, redaction result, sensitivity label, retention tier, model/cost if cloud.
- Eval requirement: secret-on-screen, clipboard-token, prompt-injection-OCR, false stuck detection.
- Priority: later.

### Superpower 3: Authority, Approval, Deferred Execution, and Audit

- Source paths: `src/authority/engine.ts`, `src/authority/approval.ts`, `src/authority/deferred-executor.ts`, `src/authority/audit.ts`, `src/agents/orchestrator.ts`.
- Mechanism: action categories, authority levels, governed categories, approval requests, user approval delivery, deferred registry execution, audit trail.
- Why users care: the agent can ask permission instead of blindly failing or acting.
- What makes it powerful: it separates proposed high-impact actions from immediate execution.
- What makes it risky: authority policy lacks evidence, dry-run preview, resource scoping, and default-blocking for unknowns.
- Sentinel should learn: persisted approval queue, deferred executor, emergency stop, audit stats.
- Sentinel must rewrite: risk-scored policy with evidence references, dry-run preview, approval actor, and trace.
- Firewall implication: this is the seed of Sentinel's AgentOps Firewall.
- Trace requirement: action object before execution, policy decision, preview, approval, final result.
- Eval requirement: approval bypass, unknown tool, expired approval, stale preview, denied action.
- Priority: now for Sentinel core.

### Superpower 4: Browser Operator with App Templates

- Source paths: `sidecar/browser.go`, `src/actions/tools/builtin.ts`, `webapp-templates/slack.yaml`, `webapp-templates/whatsapp.yaml`.
- Mechanism: CDP navigation, snapshot, element click/type, key submit, screenshot, arbitrary evaluate, app-specific operational playbooks.
- Why users care: the agent can operate web apps without dedicated APIs.
- What makes it powerful: templates encode real UI workflows, including Slack/WhatsApp navigation and sends.
- What makes it risky: browser actions can submit forms, send messages, upload files, expose accounts, or run arbitrary page JS.
- Sentinel should learn: app-specific UI playbooks as read-only guides.
- Sentinel must rewrite: BrowserSandbox with read-only first, no real accounts in lab, no submit, no send, no arbitrary evaluate.
- Firewall implication: each browser action needs domain/app risk policy.
- Trace requirement: URL/domain, DOM diff preview, target element, expected effect, screenshot/HTML hash.
- Eval requirement: fake browser form submit, external message send, prompt injection page, wrong-target message.
- Priority: later.

### Superpower 5: Workflow and Trigger Engine

- Source paths: `src/workflows/engine.ts`, `src/workflows/triggers/manager.ts`, `src/workflows/triggers/cron.ts`, `src/workflows/triggers/webhook.ts`, `src/workflows/triggers/poller.ts`, `src/workflows/auto-suggest.ts`.
- Mechanism: cron/webhook/poll/observer triggers, screen condition evaluation, auto-suggest from awareness patterns, execution engine.
- Why users care: repeated work can become automation.
- What makes it powerful: workflow triggers bridge external events, schedules, and observed desktop behavior.
- What makes it risky: triggers can fire without current user intent, and nodes can perform messaging/code execution.
- Sentinel should learn: trigger taxonomy and auto-suggest as draft workflow proposals.
- Sentinel must rewrite: workflow compiler that performs static policy scan before enabling.
- Firewall implication: workflow enablement is high-impact; every node must map to policy.
- Trace requirement: trigger source, payload hash, policy scan, run id, action list, approval state.
- Eval requirement: malicious webhook, poll exfiltration, screen-trigger injection, auto-enable block.
- Priority: later.

### Superpower 6: Role-Based Multi-Agent Operation

- Source paths: `roles/*.yaml`, `roles/specialists/*.yaml`, `src/agents/agent.ts`, `src/agents/delegation.ts`, `src/agents/sub-agent-runner.ts`, `src/roles/utils.ts`.
- Mechanism: roles define tools, authority, sub-roles, autonomous actions, heartbeat instructions; delegation spawns scoped sub-agents.
- Why users care: complex tasks can be split by specialist.
- What makes it powerful: different agents carry different tool scopes and communication styles.
- What makes it risky: role authority and prompt autonomy can drift into high-impact actions.
- Sentinel should learn: role-specific analysis/debate personas and least-privilege tool assignment.
- Sentinel must rewrite: sub-agents as planners/evaluators first, not executors.
- Firewall implication: sub-agent action proposals need the same policy as primary.
- Trace requirement: parent/child agent, assigned task, tool scope, budget, output, evidence refs.
- Eval requirement: sub-agent approval bypass, higher-authority spawn, delegated send/action.
- Priority: now for decision/debate; later for execution.

## 10. TAKE / REWRITE / AVOID

### TAKE

- Capability manifest vocabulary for sidecars: terminal, filesystem, desktop, browser, clipboard, screenshot, system info, awareness.
- Enrollment/revocation control-plane concept.
- RPC state model including pending/detached/completed/failed/timed-out/cancelled.
- Priority event scheduling and heartbeat liveness checks.
- Approval request lifecycle and deferred executor concept.
- Emergency pause/kill state.
- Audit trail rows for tool/action/decision/executed/timing.
- Screen/clipboard/window events as future context sources.
- Awareness struggle scoring as a suggestion signal.
- Workflow trigger taxonomy and auto-suggest concept.
- Role/sub-agent organization as a planning and research pattern.

### REWRITE

- PermissionedSidecar with deny-by-default capabilities.
- Sidecar admin config mutation as a high-risk approved action.
- Browser sandbox with read-only first and no submit/send.
- Desktop sidecar with visible previews, no hidden keystrokes, no silent launch.
- Filesystem access with workspace allowlists and path-containment proof.
- Authority engine as explicit policy matrix, not only numeric levels.
- ApprovalGate with evidence, dry-run preview, risk score, approver, and trace.
- ScreenContextSanitizer before storage or LLM use.
- SafeHeartbeat that can propose/draft but not execute high-impact actions.
- WorkflowFirewall that statically scans workflows before enabling.
- Memory retrieval with confidence/freshness/sensitivity, not memory-as-policy.

### AVOID

- Running JARVIS sidecar or daemon in Sentinel.
- Copying vendor sidecar code or browser/desktop handlers.
- Raw shell command execution.
- Default sidecar all-capability configuration.
- Blocklist-only command/path security.
- Arbitrary browser `Runtime.evaluate`.
- Browser submit/send/file upload with real accounts.
- Clipboard and screenshot ingestion without redaction and opt-in.
- Prompt-level "banned tools" as security controls.
- Background heartbeat execution of commitments.
- Workflow triggers that can execute without firewall.
- Role YAML authority as a security boundary.

## 11. Missing Blocks and Unknowns

Not audited in this pass:

- Runtime behavior of daemon, UI, sidecar, browser, desktop, workflow, and channel services.
- Actual database migration state under a running daemon.
- Exact WebSocket/API auth behavior in a live dashboard session.
- End-to-end approval UI behavior.
- Actual OS preflight behavior for Windows/macOS/Linux sidecar permissions.
- Whether `update_config` is reachable from normal agent tool paths without additional daemon-side gating.
- Exact local Chrome launch/profile behavior in real accounts.
- Full Google setup/OAuth scope behavior.
- Full workflow node catalog and every node side effect.
- Complete prompt content for every specialist role.
- Minified/generated UI bundles.
- Test suite behavior; no vendor tests were run.

Next experiment, still source-only unless explicitly approved:

- Build a deterministic JARVIS static scanner for sidecar RPC methods, desktop/browser tools, workflow nodes, role tools/authority, webapp templates, config mutation surfaces, OAuth/channel adapters, and prompt-injection sources.

## 12. Final Vendor Verdict

JARVIS is the best lab specimen for Sentinel's future PermissionedSidecar and desktop-awareness roadmap. It proves that users want agents that can observe and operate real machines, but it also proves why Sentinel cannot add those powers before a stronger firewall exists.

Best superpower:

- Machine-level agency through sidecar capabilities, desktop/browser control, awareness events, approvals, and audit.

Biggest weakness:

- Security authority is distributed across role YAML, numeric authority levels, context rules, app prompt templates, sidecar capability config, and tool route checks. That is too fragmented for an AgentOps product.

Biggest security risk:

- A connected sidecar can expose terminal, filesystem, browser, desktop, clipboard, screenshot, observer, and admin config mutation surfaces. If prompt injection or weak approval reaches those surfaces, the blast radius is the user's machine and accounts.

Most valuable Sentinel rewrite:

- `SentinelPermissionedSidecar + ScreenContextSanitizer + FirewallDeferredExecutor`.

What not to copy:

- Sidecar defaults, raw shell handlers, path blocklists, browser evaluate, browser submit, desktop keystroke execution, prompt-only tool bans, heartbeat execution, and real-message app templates.

Overall usefulness score:

- 9/10 as a sidecar/desktop-awareness specimen.

Rewrite readiness score:

- 7/10. The main mechanisms are source-visible and well enough mapped for Sentinel design, but live safety claims require fake-only benchmarks and later explicit sandbox experiments.

North star for Sentinel rewrite:

- Sentinel should eventually control machines, browsers, channels, and workflows only after it can prove what it saw, what it intends to do, what can go wrong, who approved it, and exactly what changed.
