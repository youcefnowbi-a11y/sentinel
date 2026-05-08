# Hermes Memory Map

Date: 2026-04-26

## Built-In Memory

Source paths:

- `agent-lab/vendors/hermes-agent/source/run_agent.py:1596-1617`
- `agent-lab/vendors/hermes-agent/source/tools/memory_tool.py:105-124`
- `agent-lab/vendors/hermes-agent/source/tools/memory_tool.py:222-263`
- `agent-lab/vendors/hermes-agent/source/tools/memory_tool.py:363-367`

Mechanism:

- `AIAgent` reads config flags `memory_enabled`, `user_profile_enabled`, `nudge_interval`.
- If enabled, it constructs `MemoryStore` with character limits and loads from disk.
- Memory files are loaded into a frozen system prompt snapshot at session start.
- Mid-session writes update disk immediately but do not affect the current system prompt snapshot.

Data input:

- User/assistant content sent to memory tool.
- Target: memory or user profile.

Data output:

- Prompt memory block.
- Durable disk entries.

Side effect:

- Writes to Hermes home memory files.

Risk:

- Memory persists across sessions and can shape future behavior.

Sentinel rewrite:

- Store memory as typed records: `fact`, `preference`, `project_context`, `outcome`, `rejected_suggestion`.
- Disallow memory entries that are imperative instructions or policy.
- Add `source_run_id`, `created_by`, `confidence`, `scope`, and `expires_at`.

## Memory Threat Pattern Checks

Source: `agent-lab/vendors/hermes-agent/source/tools/memory_tool.py:73-100`.

Mechanism:

- Checks for secret exfiltration patterns and known injection strings.
- Blocks memory entries that match threat patterns.

Sentinel rewrite:

- Extend to secret scanner, PII classifier, prompt-injection classifier, and schema validation.
- Store blocked entry hash and reason, not the raw secret.

## External Memory Providers

Source paths:

- `agent-lab/vendors/hermes-agent/source/run_agent.py:1621-1704`
- `agent-lab/vendors/hermes-agent/source/agent/memory_manager.py:84-145`
- `agent-lab/vendors/hermes-agent/source/plugins/memory/__init__.py:1-19`, `:122-180`, `:184-254`

Mechanism:

- Config selects `memory.provider`.
- Provider is loaded from bundled or user plugin dirs.
- Only one external provider is allowed at a time.
- Provider schemas are injected into the tool surface.
- Provider lifecycle receives turn start/end, prefetch, sync, compression, and memory write notifications.

Data input:

- Query text, session ID, platform, user/chat identity, session title, provider config.

Data output:

- Prompt blocks, prefetch context, memory tool schemas.

Side effect:

- Provider-specific network or disk behavior depending on plugin.

Risk:

- External provider can return untrusted context that affects prompts.
- Provider tool schemas expand the callable tool surface.

Sentinel rewrite:

- External memory providers require:
  - manifest;
  - no secret access by default;
  - source trust label;
  - per-record provenance;
  - retrieval scoring and citation;
  - blocked policy override language.

## Retrieval And Scoring

Verified source fact:

- The built-in memory path is character-limited and file-backed.
- External provider scoring depends on individual provider implementation; a full provider-by-provider scoring audit remains pending.

Sentinel rewrite:

- Built-in retrieval must return `MemoryHit` objects with:
  - `id`;
  - `source`;
  - `scope`;
  - `confidence`;
  - `recency_score`;
  - `relevance_score`;
  - `trust_level`;
  - `used_in_prompt`.

## Eval Requirements

- Memory injection cannot override Firewall policy.
- Secret-looking memory write is blocked/redacted.
- External provider context is labeled untrusted unless verified.
- A stale memory cannot turn a sandbox run into an evidence-backed run.
