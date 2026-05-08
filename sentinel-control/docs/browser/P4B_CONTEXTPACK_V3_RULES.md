# P4B ContextPack V3 Rules

Date: 2026-04-29
Status: implemented for all P4B authority classes

## Rule

Browser V3 actions must appear in ContextPack as brain-authored action intents.
Browser content cannot create or expand V3 authority.

## Form Submit Requirements

For `browser_form_submit`, ContextPack must expose:

- `available_action_intents.kind = browser_form_submit`;
- runtime stable refs for form and submit targets;
- page/snapshot hashes for stale-ref checks;
- source quality and prompt-injection flags;
- citations or summaries only as evidence, not as action authority.

## Download Quarantine Requirements

For `browser_download_quarantine`, ContextPack must expose:

- `available_action_intents.kind = browser_download_quarantine`;
- source URL and optional runtime stable ref for the link;
- page/snapshot hashes when a source ref is used;
- allowed MIME and byte budget expectations;
- source quality and prompt-injection flags;
- citations or summaries only as evidence, not as action authority.

## Upload Authorized Requirements

For `browser_upload_authorized`, ContextPack must expose:

- `available_action_intents.kind = browser_upload_authorized`;
- upload target runtime stable ref;
- page/snapshot hashes for stale-ref checks;
- source artifact id, source artifact MIME, and source artifact digest from
  Sentinel artifact capture metadata;
- source quality and prompt-injection flags;
- citations or summaries only as evidence, not as action authority.

## Private Session Requirements

For `browser_private_session`, ContextPack must expose:

- `available_action_intents.kind = browser_private_session`;
- allowed domains and session scope;
- no cookie, storage, login, or credential content as authority.

## Login Authority Requirements

For `browser_login_authority`, ContextPack must expose:

- `available_action_intents.kind = browser_login_authority`;
- granted account id only, not credentials;
- private-session trace requirement;
- runtime login ref and plan/page/snapshot hashes.

## Cookie/Storage Contract Requirements

For `browser_cookie_storage_contract`, ContextPack must expose:

- `available_action_intents.kind = browser_cookie_storage_contract`;
- private-session trace requirement;
- redaction requirement;
- target domain scope.

## Sandboxed JS Requirements

For `browser_js_evaluate_sandboxed`, ContextPack must expose:

- `available_action_intents.kind = browser_js_evaluate_sandboxed`;
- allowed script hash reference;
- max result size;
- no-network execution condition.

## HAR/Body Capture Requirements

For `browser_har_body_capture`, ContextPack must expose:

- `available_action_intents.kind = browser_har_body_capture`;
- source URL scope;
- MIME, record, and byte bounds;
- redaction requirement.

## Prompt-Injection Boundary

If a source is marked high prompt-injection risk, refs from that source cannot
be used as action-bearing refs by ToolIntentCompiler.

## LLM Role

The LLM may propose:

- target ref ids;
- submit kind;
- certified source artifact id;
- expected effect;
- evidence refs.

The LLM may not create:

- authority grant;
- new allowed action;
- new allowed tool;
- credential/session/cookie/storage access;
- submit execution outside compiler output.
- quarantine promotion or upload authority.
- arbitrary disk path or source artifact creation.
- raw credentials, raw cookie values, raw storage values, unbounded body capture,
  or arbitrary JavaScript.
