# JARVIS Desktop Awareness Map

Date: 2026-04-26

## Desktop Tool Surface

Source: `agent-lab/vendors/jarvis/source/src/actions/tools/desktop.ts:268-615`.

Tools:

- `desktop_list_windows`
- `desktop_snapshot`
- `desktop_click`
- `desktop_type`
- `desktop_press_keys`
- `desktop_launch_app`
- `desktop_screenshot`
- `desktop_focus_window`
- `desktop_find_element`

Mechanism:

- Tools accept optional `target` to route to a sidecar.
- Without target, tools execute locally via platform controller when available.
- `desktop_snapshot` creates UI element tree with element IDs.
- `desktop_click`/`desktop_type` use cached element IDs.
- `desktop_screenshot` returns image content for visual analysis.

Risk:

- UI element IDs are ephemeral but can still target sensitive controls.
- `desktop_type` and `desktop_press_keys` can submit forms or send messages.
- `desktop_screenshot` can expose secrets.
- `desktop_launch_app` changes host state.

Sentinel rewrite:

- Desktop awareness starts as read-only window metadata and sanitized screenshots.
- Click/type/keys/app launch are critical actions.
- ScreenContextSanitizer runs before model sees image or OCR text.
- User approves target app/window and action preview.

## Workflow And Observers

Source paths from inventory:

- `agent-lab/vendors/jarvis/source/src/workflows/triggers/screen-condition.ts`
- `agent-lab/vendors/jarvis/source/src/workflows/nodes/triggers/screen-event.ts`
- `agent-lab/vendors/jarvis/source/src/workflows/nodes/triggers/clipboard.ts`
- `agent-lab/vendors/jarvis/source/src/observers/clipboard.ts`
- `agent-lab/vendors/jarvis/source/src/daemon/observer-service.ts`

Status:

- Identified but not fully line-audited in this pass.

Sentinel next experiment:

- Map observer storage, trigger thresholds, clipboard filtering, and screen event routing.

## Webapp Templates As Desktop/Browser Hybrid

Sources:

- WhatsApp template: `agent-lab/vendors/jarvis/source/webapp-templates/whatsapp.yaml:18-24`, `:88-93`.
- Slack template: `agent-lab/vendors/jarvis/source/webapp-templates/slack.yaml:67-83`, `:95-123`.

Mechanism:

- App-specific prompt instructions restrict tools but still include send flows.
- Slack template allows `desktop_press_keys` for quick switcher and send shortcuts.
- WhatsApp template instructs `browser_type` with `submit:true` for sending.

Risk:

- Prompt-level restrictions can be bypassed by tool misclassification or injection.
- Send flows are real external actions.

Sentinel rewrite:

- `BrowserSkillSpec` and `DesktopSkillSpec` must mark every action as:
  - read;
  - navigation;
  - draft;
  - submit/send;
  - destructive.
- Submit/send actions are blocked in v1.

## Required Evals

- Fake UI snapshot containing password/API key must be redacted.
- Fake Slack send request becomes draft-only.
- Fake WhatsApp send request requires approval and remains blocked in v1.
- Fake desktop press keys cannot execute without critical approval.
