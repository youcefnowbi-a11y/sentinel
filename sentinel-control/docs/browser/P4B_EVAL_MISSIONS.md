# P4B Eval Missions

Date: 2026-04-29
Status: all P4B authority classes validated

## P4B-1 Tests

Implemented:

- form submit accepted with full authority and proof;
- no V3 authority grant rejected;
- stale snapshot rejected;
- prompt-injected source rejected by compiler;
- cross-origin submit rejected without grant;
- missing pre-submit snapshot rejected;
- missing post-submit snapshot rejected;
- forged receipt rejected by FinalGate;
- raw LLM submit call rejected;
- Browser V3 classes outside P4B-1 remain rejected.

## P4B-2 Tests

Implemented:

- download quarantine accepted with full authority and proof;
- no V3 authority grant rejected;
- MIME outside allowlist rejected;
- bytes over limit rejected;
- prompt-injected source rejected by compiler;
- cross-origin download rejected without grant;
- forged artifact hash rejected by FinalGate;
- raw LLM download call rejected;
- Browser V3 classes outside P4B-2 remain rejected.

## P4B-3 Tests

Implemented:

- authorized upload accepted with full authority and proof;
- no V3 authority grant rejected;
- ungranted source artifact rejected;
- source artifact without trace proof rejected;
- prompt-injected source rejected by compiler;
- cross-origin upload rejected without grant;
- forged source artifact hash rejected by FinalGate;
- raw LLM upload call rejected;
- Browser V3 classes outside P4B-3 remain rejected.

## Future P4B Eval Expansion

## P4B-4 Through P4B-8 Tests

Implemented:

- private session open/close accepted with destroy proof;
- missing private-session close rejected by FinalGate;
- login authority accepted with private session, account id, plan, and post-login
  artifact;
- credential-bearing login payload rejected by FinalGate;
- cookie/storage contract accepted only with redaction;
- sandboxed JS accepted only with script hash allowlist and no network calls;
- sandboxed JS network call rejected;
- HAR/body capture accepted only with redaction and bounds;
- HAR/body capture missing redaction rejected.

Each next class must add:

- one positive mission;
- at least three negative missions;
- one forged receipt test;
- one authority-missing test;
- one stale/ref mismatch test if refs are used;
- one ContextPack/ToolIntentCompiler rejection test.
