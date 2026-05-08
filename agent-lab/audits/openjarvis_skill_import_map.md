# OpenJarvis Skill Import Map

Date: 2026-04-26

## CLI Surfaces

Source: `agent-lab/vendors/openjarvis/source/src/openjarvis/cli/skill_cmd.py:162-245`, `:258-349`.

Mechanisms:

- Resolver selection supports `hermes`, `openclaw`, and `github` sources.
- GitHub source requires `--url`.
- Install command creates a resolver, parser, translator, and importer.
- `--with-scripts` imports a skill's `scripts/` directory.
- Sync bulk-imports from configured sources.

Risk:

- Imports from vendor ecosystems and remote GitHub sources.
- `scripts/` are explicitly marked security-sensitive in CLI help.
- Prompt-only skills can still inject policy or unsafe instructions.

Sentinel rewrite:

- `SkillImportRequest` is draft/review only.
- Source is pinned to commit.
- Scanner runs before any install.
- `scripts/` stay in quarantine.
- Imported skill cannot appear in prompt index until accepted.

## Importer Mechanics

Source: `agent-lab/vendors/openjarvis/source/src/openjarvis/skills/importer.py:7-43`, `:62-139`, `:171-192`.

Mechanism:

- Converts resolved vendor skill to OpenJarvis skill.
- Writes `SKILL.md`.
- Copies always-allowed subdirectories.
- Copies `scripts/` only if `with_scripts=True`.
- Writes `.source` metadata including origin and `scripts_imported`.

Sentinel rewrite:

```text
ResolvedSkill
-> SkillScanReport
-> Quarantine
-> User review
-> Sandbox tests
-> Approved SkillManifest
-> SkillIndexCompiler
```

## Loader And Security

Source:

- `agent-lab/vendors/openjarvis/source/src/openjarvis/skills/security.py:11-55`.
- `agent-lab/vendors/openjarvis/source/src/openjarvis/skills/loader.py:109-143`.

Observed mechanisms:

- Dangerous capabilities include shell execution, network listen, filesystem write.
- Loader can verify signatures when given a public key and signature.
- Loader checks for prompt injection in skill steps.

Sentinel rewrite:

- Capability declarations are mandatory, not optional.
- Signature validation is required for promoted skills.
- Prompt-injection scanner covers markdown body, metadata, steps, scripts, and linked files.

## Required Tests

- GitHub skill with script is quarantined.
- Prompt-only skill with policy override is blocked.
- Skill declaring filesystem write maps to high risk.
- Skill source metadata is preserved in trace.
- Skill cannot be run directly from CLI equivalent without firewall approval.
