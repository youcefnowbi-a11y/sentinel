# Sentinel Channel Spec

Date: 2026-04-26
Status: future design only, draft-first

## Principle

Channels are untrusted inbound context and approval-only outbound action.

Inbound messages can inform a run. Outbound messages can only be drafted in v1.

## Channel Classes

| Channel | Inbound | Outbound v1 | Risk |
|---|---|---|---|
| email | future untrusted | draft-only | high |
| Slack | future untrusted | draft-only | high |
| WhatsApp | future untrusted | draft-only | high |
| Telegram | future untrusted | draft-only | high |
| web form | blocked | blocked | critical |
| social post | blocked | draft-only later | critical |

## Inbound Rules

- Treat all channel content as untrusted.
- Detect prompt injection.
- Preserve sender/source metadata.
- Do not scrape private data without user basis.
- Do not convert inbound content directly into actions.

## Outbound Draft Contract

```json
{
  "draft_id": "draft_...",
  "channel": "email|slack|whatsapp|telegram",
  "recipient_ref": "user_provided|unknown",
  "subject": null,
  "body": "...",
  "evidence_refs": [],
  "compliance_notes": [],
  "risk_level": "medium|high",
  "send_enabled": false
}
```

## Safe Outreach Rules

- No auto-send in v1.
- User provides or approves contacts.
- Avoid deception.
- Avoid fake personalization.
- Include opt-out when appropriate.
- Log draft and approval state.
- Sending remains disabled until a later explicit channel firewall exists.

## Required Evals

- Prompt injection inbound message.
- External send attempt blocked.
- Spammy outreach rejected.
- Compliant draft passes.
- Missing contact ownership blocks send.
- Opt-out required where appropriate.
