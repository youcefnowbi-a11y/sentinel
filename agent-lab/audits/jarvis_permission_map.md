# JARVIS Permission Map

Date: 2026-04-26

## Action Categories

Source: `agent-lab/vendors/jarvis/source/src/roles/authority.ts:3-45`.

Categories:

- `read_data`
- `write_data`
- `delete_data`
- `send_message`
- `send_email`
- `execute_command`
- `install_software`
- `make_payment`
- `modify_settings`
- `spawn_agent`
- `terminate_agent`
- `access_browser`
- `control_app`

Authority levels:

- level 1 read.
- level 3 write/send message.
- level 5 execute command/browser/app control.
- level 7 send email/install.
- level 9 payment/settings/delete/terminate.
- spawn agent is listed as level 1.

Risk:

- Numeric authority is too coarse for Sentinel.
- Payload matters: reading a public file is not equal to reading `.env`; browser navigate is not equal to form submit.

Sentinel rewrite:

- Risk class is action + payload + data + external effect.
- Role authority cannot override critical-action approvals.

## Authority Decision Order

Source: `agent-lab/vendors/jarvis/source/src/authority/engine.ts:1-10`, `:61-175`.

Order:

1. Temporary grants.
2. Per-action overrides.
3. Context rules.
4. Numeric level check.
5. Governed category approval check.

Risk:

- Temporary grants and overrides can become escalation paths.
- Governed categories are configurable and may omit high-impact actions.

Sentinel rewrite:

- Permission decisions use immutable policy version per run.
- Temporary grants have TTL, scope, and parent trace.
- Critical actions are always approval-required or disabled in v1.

## Approval Lifecycle

Source: `agent-lab/vendors/jarvis/source/src/authority/approval.ts:31-196`.

States:

- pending.
- approved.
- denied.
- expired.
- executed.

Stored fields:

- agent ID/name.
- tool name and JSON args.
- action category.
- urgency.
- reason/context.
- status and decision metadata.
- execution result.

Sentinel rewrite:

- Add risk score, evidence refs, dry-run preview, policy version, approver ID, expiration, and one-time nonce.

## Audit Trail

Source: `agent-lab/vendors/jarvis/source/src/authority/audit.ts:23-158`.

Stored fields:

- agent ID/name.
- tool name.
- action category.
- authority decision.
- approval ID.
- executed boolean.
- execution time.

Sentinel rewrite:

- Trace Ledger includes:
  - input snapshot;
  - decision plan;
  - proposed action;
  - dry-run;
  - approval result;
  - raw execution result;
  - transformed result;
  - evidence refs.

## Required Tests

- Temporary grant cannot permit critical action.
- Approval cannot be reused after execution.
- Expired approval blocks execution.
- Action category cannot downgrade path/secret/browser-submit risk.
- Unknown tool defaults to blocked or review, not read_data.
