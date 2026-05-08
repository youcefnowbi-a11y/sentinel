# SENTINAL Core Audit - 2026-04-26

## Scope

Repository cloned from `https://github.com/Gameminde/SENTINAL` into `C:\Users\youcefcheriet\sentinal`.

Audit order requested:

1. `RedditPulse/` as the current CueIdea product and evidence engine.
2. `sentinel-control/` as the new Sentinel Control product layer.

This is a core-understanding audit, not a feature implementation pass.

## Core Thesis

The project is not simply a Reddit scraper and not a generic agent dashboard.

The real product architecture is:

```text
Idea
  -> CueIdea evidence and market validation
  -> Sentinel evidence normalization
  -> decision/debate layer
  -> GTM pack
  -> risk/firewall review
  -> approval
  -> local safe execution
  -> trace log
```

CueIdea/RedditPulse is the evidence engine. Sentinel Control is the decision, GTM, approval, execution-safety, and traceability layer on top.

## Live Product Check

`https://cueidea.me` was reachable during this audit on 2026-04-26. The public site presents CueIdea as "startup demand before you build" and shows public signal coverage across Reddit, Hacker News, Product Hunt, Indie Hackers, GitHub Issues, review complaints, and hiring signals.

This matters for Sentinel: CueIdea is not a speculative input. It is already a live evidence product. Sentinel should treat CueIdea as the first external information substrate for agentic business decisions.

## Repository Map

| Area | Role | Current Status |
| --- | --- | --- |
| `RedditPulse/` | Existing CueIdea market intelligence and validation app | Real product code, Python engine, Next.js app, tests, migrations, docs |
| `sentinel-control/` | New Sentinel Control product | Working local prototype with CueIdea import, GTM pack generation, firewall, traces, evals |
| `agent-lab/` | Research-only external agent runtime lab | Audit/reference material only; should not feed vendor code directly into production |

## Product Baseline From The Active Plan

The active product lock is:

```text
Sentinel Control
  = AgentOps Firewall + Business Decision Agent

Public wedge:
  Sentinel GTM Operator

Long-term moat:
  AgentOps Firewall
```

The system should not become a generic assistant, an OpenClaw clone, or a broad automation runtime. It should become a controlled business operator that only acts after proof, risk scoring, simulation, approval, and trace logging.

### Product Role Split

| Layer | Owns | Must Not Own |
| --- | --- | --- |
| CueIdea | market signals, validation, WTP, competitors, trends, reports, credibility, AI debate | risky execution, external actions, filesystem writes, agent runtime policy |
| Sentinel GTM Operator | decision package, ICP, positioning, landing copy, outreach drafts, interview script, prospect sources, 7-day plan | raw market scraping as the main job, auto-send, browser submit, shell, code edits |
| AgentOps Firewall | action policy, risk score, dry-run preview, approval, trace, blocked capability map | market validation, business copy generation |
| Agent Lab | study unsafe agent runtimes, extract patterns, build safe fake benchmarks | production execution, vendor runtime bridging, account connection |

### Operating Law

Every future feature must answer one of two questions:

1. Does this improve the GTM Operator's ability to turn evidence into first-customer action?
2. Does this improve the Firewall's ability to control, simulate, approve, and trace agent actions?

If the answer is no, the feature is out of scope for v1.

## Audit 1 - RedditPulse / CueIdea

### What It Is

CueIdea is the market-demand discovery and validation system. Its job is to turn messy public market signals into decision-grade evidence for startup ideas.

The product surfaces are:

- `Radar`: discovers public opportunities.
- `Validate`: decides whether a specific idea has enough proof.
- `Reports`: explains and preserves the evidence.
- `Following` / digest / watchlist: keeps decisions alive over time.

### Runtime Shape

Important working zones:

- `RedditPulse/app/`: Next.js app, auth, API routes, dashboard, report UI, admin surfaces.
- `RedditPulse/app/src/app/api/validate/route.ts`: authenticated validation entry point.
- `RedditPulse/app/src/lib/queue.ts`: pg-boss queue and Python worker bridge.
- `RedditPulse/validate_idea.py`: main Python validation pipeline.
- `RedditPulse/engine/`: scrapers, model gateway, scoring, credibility, multi-brain debate, validation depth.
- `RedditPulse/migrations/`: Supabase schema evolution.
- `RedditPulse/tests/`: Python tests for pipeline, AI gateway, and market editorial logic.

### Verified Flow

The validation path is:

1. User submits an idea through `/api/validate`.
2. Server checks auth, active AI config, provider health, durable rate limit, premium depth access, and runtime pause state.
3. A row is inserted into `idea_validations`.
4. `enqueueValidationJob` sends a pg-boss job.
5. Worker writes a temporary JSON config and spawns `python validate_idea.py --config-file`.
6. Python decomposes the idea, scrapes sources, filters evidence, performs intelligence passes, runs debate, builds a report, and writes back to Supabase.
7. The status endpoint enriches the validation with evidence/trust/decision-pack data and returns diagnostics.

### Strong Points

- The product has a strong trust model: direct evidence, adjacent evidence, inference, WTP, competitor signals, freshness, and source breadth are treated as separate concepts.
- The validation system is more valuable than the generic market feed. Docs correctly say market rows are not all "ideas"; only validation should support strong build/pivot/kill decisions.
- Queue design is pragmatic: web request returns quickly, worker handles long-running Python, status endpoint reports stale/failed queue states.
- RedditPulse has meaningful tests. `python -m pytest tests` passed: 44 tests.
- The code has already moved away from raw prompt-output trust toward contracts such as `evidence.ts`, `decision-pack.ts`, `validation-depth.py`, and report guardrails.

### Weak Points / Risks

1. Top-level pytest is brittle.
   - Running `python -m pytest` from `RedditPulse/` fails because `run_validation_test.py` tries to open ignored local `app/.env.local` during collection.
   - The committed `tests/` suite passes, but the root test entry point is not clean for fresh clones.

2. The product still has two mental models competing.
   - Older docs and some code call it RedditPulse, current brand calls it CueIdea.
   - Some older docs frame the product as "Reddit 24/7"; newer runtime and docs clearly make it multi-source market validation.

3. Report-schema drift is still a central risk.
   - Existing docs record historical mismatches between Python report keys and frontend rendering.
   - Current code has many fallback chains, which prevents hard failure but can hide backend/frontend contract drift.

4. Validation is powerful but heavy.
   - `validate_idea.py` is a very large orchestration file, mixing scraping, filtering, quality rules, prompt construction, debate, report shaping, persistence, and guardrails.
   - This makes it hard to reason about one failure mode without reading a broad region of the file.

5. Some fallback behavior can make output look more complete than the evidence.
   - The system has explicit warnings and direct/adjacent/supporting proof tiers, which is good.
   - The remaining risk is UI presentation: fallback summaries and heuristic copy must keep looking visibly weaker than direct proof.

### CueIdea Core Verdict

CueIdea's real defensible core is not "find startup ideas from Reddit." It is:

```text
Turn public buyer pain, competitor weakness, WTP hints, and market timing into an evidence-backed validation decision.
```

The strongest product surface is `Validate`, not the feed. The feed is discovery/context; validation is the decision engine.

### CueIdea As Sentinel Information Substrate

CueIdea already has the hardest part of the product: real market context. Sentinel should not spend early cycles rebuilding this.

What CueIdea contributes to Sentinel:

- observed pain and complaint signals;
- source coverage and freshness context;
- competitor and alternative context;
- WTP and pricing signals;
- report-grade synthesis;
- credibility, evidence, and proof-tier logic;
- user-facing validation reports that can be imported into Sentinel.

What Sentinel must add on top:

- decision normalization into `build / pivot / niche_down / kill / research_more`;
- GTM asset generation;
- action proposal;
- risk scoring and policy;
- dry-run preview;
- approval workflow;
- local file/draft execution;
- trace ledger and future learning loop.

The product risk is dilution. If Sentinel starts acting like another CueIdea screen, it loses its reason to exist. Sentinel must be the layer after validation: the layer that turns proof into a controlled operating plan.

### CueIdea Contract Risks To Resolve

1. `report` schema drift can silently weaken Sentinel imports.
   - CueIdea has rich JSON, but the frontend and Sentinel adapters rely on key fallbacks.
   - The next integration test should use real CueIdea report fixtures and assert that critical fields survive normalization.

2. Evidence tiers need a shared vocabulary.
   - CueIdea uses direct/adjacent/supporting style proof.
   - Sentinel uses `EvidenceItem.evidence_type`, `confidence`, `freshness_score`, and `relevance_score`.
   - These need one shared mapping table.

3. WTP must remain a hard gate.
   - The active plan correctly says no `build` verdict without WTP.
   - Sentinel's deterministic debate layer already enforces this partly, but imported CueIdea verdicts should also be checked before pack readiness.

4. Public market feed rows should not become automatic GTM packs.
   - A market row is discovery context.
   - A validation report is decision context.
   - Sentinel should prefer validation imports over raw opportunity-card imports.

## Audit 2 - Sentinel Control

### What It Is

Sentinel Control is the new product layer that turns CueIdea evidence into a controlled GTM operating pack. It is not a generic autonomous agent.

The first wedge is `Sentinel GTM Operator`.

The long-term moat is `AgentOps Firewall`.

### Runtime Shape

Important working zones:

- `sentinel-control/apps/web/`: local Next.js dashboard and API routes.
- `sentinel-control/apps/web/lib/cueidea-import.ts`: read-only CueIdea report import and normalization for the web app.
- `sentinel-control/apps/web/lib/run-store.ts`: local run state, generated pack assets, approvals, Supabase sync.
- `sentinel-control/services/sentinel-core/sentinel/shared/`: typed models and enums.
- `sentinel-control/services/sentinel-core/sentinel/cueidea_bridge/`: Python bridge for normalizing CueIdea validation data into Sentinel evidence.
- `sentinel-control/services/sentinel-core/sentinel/decision/`: deterministic research/debate logic.
- `sentinel-control/services/sentinel-core/sentinel/execution/`: GTM pack, quality scoring, safe executors.
- `sentinel-control/services/sentinel-core/sentinel/firewall/`: policy, path allow-list, approval and risk scoring.
- `sentinel-control/packages/evals/`: safety and business-quality eval datasets.

### Verified Flow

The Sentinel flow is:

1. Create a local run directly, or import a CueIdea validation by ID / pasted JSON.
2. Normalize evidence rows into proof tiers and tags.
3. Build a run with evidence, actions, generated assets, watchlist items, cost estimate, GTM quality, and traces.
4. Generate a GTM pack locally.
5. Write files only under `data/generated_projects`.
6. Keep high-impact actions disabled or approval-gated.
7. Optionally sync Sentinel run tables to Supabase when env flags are enabled.

### Strong Points

- The product boundary is clear: proof-backed GTM output plus controlled execution.
- The security model is correctly conservative: shell, code modification, browser submission, email sending, and payment execution are disabled in v1.
- The firewall has a real path policy for file actions and unknown tools default to critical/blocked.
- The CueIdea bridge is read-only and can import by validation ID or pasted report JSON.
- The GTM pack quality layer is a good product move: it blocks vague ICP, missing WTP, weak competitor gaps, spammy outreach, and unrealistic roadmaps from being treated as ready.
- The trace model is treated as a first-class product feature, not just logs.

### Weak Points / Risks

1. Sentinel is still partly prototype/demo-state.
   - Direct local runs create placeholder evidence until CueIdea is connected.
   - Several dashboard surfaces still import `demo-data`.
   - Cost estimates are local estimates, not real provider accounting.

2. Research/debate is deterministic and shallow compared with CueIdea.
   - The Python `DebateOrchestrator` is useful as a guardrail, but it is rule-based counting logic, not real market research.
   - The next real upgrade should not be more UI; it should be better research, competitor, WTP, ICP, and evidence-gap extraction.

3. Auth defaults are safe for local development but unsafe for hosted mode if forgotten.
   - `.env.example` has `SENTINEL_REQUIRE_AUTH=false`.
   - Hosted staging must explicitly set `SENTINEL_REQUIRE_AUTH=true`.

4. Sentinel Python tests are one environment dependency short in this clone.
   - `python -m pytest` in `sentinel-core` produced 33 passed and 1 failure because `pytest-asyncio` is missing in the current environment.
   - The failed test is async bridge coverage, not a product assertion failure.

5. Supabase schema lacks visible RLS in the first migration.
   - The migration creates tables and indexes, but this audit pass did not find RLS policies in `001_sentinel_core.sql`.
   - If hosted Supabase sync is enabled, table-level access controls need a dedicated review before staging.

### Sentinel Core Verdict

Sentinel's real defensible core is:

```text
Turn evidence into an executable GTM package, while making every risky action reviewable, approvable, and traceable.
```

It should not become a general agent runtime yet. Its sharp product path is GTM Operator first, AgentOps Firewall as the compounding moat.

### Roadmap Alignment Matrix

| Plan Phase | Repo Status | Audit Verdict |
| --- | --- | --- |
| Phase 0 Product/Safety Lock | Present in `docs/product/PRODUCT_SPEC.md`, `docs/mission-os/SECURITY_MODEL.md`, `docs/mission-os/FIREWALL_POLICIES.md` | Good. Keep non-goals strict. |
| Phase 1 Schemas + Trace Ledger | Present in `services/sentinel-core/sentinel/shared/` and `learning/trace_ledger.py` | Good baseline. Needs hosted persistence/RLS review. |
| Phase 2 Firewall v0 | Present in `sentinel/firewall/` with tests | Strongest technical differentiator. Keep expanding tests before adding powers. |
| Phase 3 CueIdea Bridge | Present in Python bridge and web import | Good start. Needs real fixture contract tests and shared mapping doc. |
| Phase 4 Research Agent | Skeleton present | Underpowered versus target. This is the next core product upgrade. |
| Phase 5 Debate Engine | Deterministic debate present | Useful guardrail, not yet a true multi-agent council. Evidence gates matter more than role labels. |
| Phase 6 GTM Pack Generator | Present | Useful, but current generated content is still template-heavy. Needs CueIdea-derived specificity. |
| Phase 7 Safe Execution v0 | Present for local files and draft email object | Correctly constrained. Do not add sending/browser/shell. |
| Phase 8 Web UI | Present across dashboard routes | Broad prototype. Some surfaces still use demo data. |
| Phase 9 Learning Layer | Present as safe proposal/memory layer | Correct safe pattern. No auto-mutation. |
| Phase 10 Standalone AgentOps Firewall | Not yet productized | Do later. First prove GTM Operator value. |

### Sentinel Product Risks To Watch

1. GTM output can become generic if it is not grounded in CueIdea evidence.
   - The GTM pack quality scorer helps, but generation must cite evidence, not only pass text heuristics.

2. Direct local runs may confuse users.
   - They use placeholders and hypotheses.
   - Product wording should label these as sandbox runs unless backed by CueIdea or live research.

3. The Firewall is a product moat only if it is strict.
   - Approval buttons are not enough.
   - The valuable object is a complete action record: intent, input, risk, evidence refs, dry-run, approval status, execution result, trace.

4. Research depth is the current product ceiling.
   - The dashboard is broad enough for now.
   - The next real product value comes from competitor discovery, pricing/WTP extraction, ICP/community reachability, objection extraction, and evidence-gap reporting.

## Integration Verdict

The two systems are coherent if they keep their jobs separate:

- CueIdea should continue owning evidence discovery, validation, report proof, WTP, competitors, and market timing.
- Sentinel should own evidence normalization, decision packaging, GTM asset generation, action policy, approvals, local execution, and traceability.
- Agent Lab should remain research-only until a specific runtime pattern is rewritten into Sentinel's safety model.

The strategic risk is trying to make Sentinel duplicate CueIdea's market engine. Sentinel should consume CueIdea evidence, not rebuild it.

## Agent Lab Current State

Agent Lab is the safety research track. Its purpose is to convert dangerous patterns from agent runtimes into Sentinel product requirements.

The current state in this clone:

- Sprint B2.5 artifacts exist.
- `agent-lab/audits/openclaw_scanner_report.json` and `.md` agree internally.
- Scanner consistency tests pass.
- The canonical scanner hash matches the current JSON.
- The OpenClaw source snapshot has been restored locally at `agent-lab/vendors/openclaw/source`.
- The source is checked out at commit `a2288c2b09e621f89a915960398f58e200b3b69d`.
- The scanner was rerun from that source on 2026-04-26.

This creates an important distinction:

```text
B2.5 artifact consistency: verified here.
B2.5 fresh source rerun from the restored OpenClaw snapshot: verified here.
```

The canonical B2.5 counts in the current artifact are:

| Metric | Value |
| --- | ---: |
| Total items | 83 |
| Plugins/root-script items | 31 |
| Skills | 52 |
| Critical risk | 52 |
| High risk | 29 |
| Medium risk | 2 |
| Blocked | 52 |
| Needs review | 29 |
| Draft-only tool | 2 |

The old contradictory count set should be treated as stale. The active count set is `52 blocked / 29 needs_review / 2 draft_only_tool`.

### B2.5 Audit Caveat

The scanner metadata now records the current local absolute source path:

```text
C:/Users/youcefcheriet/sentinal/agent-lab/vendors/openclaw/source
```

That is acceptable for local provenance, but it is still not portable. Before public Skill Scanner positioning, the scanner should support portable provenance:

- `source_path_relative`: `agent-lab/vendors/openclaw/source`;
- `source_present`: true/false;
- `source_snapshot_id`: commit or archive hash;
- `scan_reproducible_here`: true/false.

This is not cosmetic. AgentOps products sell auditability. A scanner report that cannot explain whether the source exists locally is weaker than Sentinel's own positioning.

### B3 Gate

B3 has now started as a fake-only benchmark harness:

```text
fake inbound message
  -> prompt injection detection
  -> policy mapping
  -> dry-run preview
  -> approval simulation
  -> trace record
```

Do not install OpenClaw. Do not run OpenClaw. Do not connect real accounts. Do not build an OpenClaw bridge.

The initial B3 fixture set covers:

- fake Slack prompt injection;
- fake Telegram external-send request;
- fake plugin declaring `sendMessage`;
- fake skill requesting `npm install`;
- fake skill requesting 1Password access;
- fake browser task attempting form submit;
- fake filesystem path traversal;
- fake memory/policy override instruction.

Current B3 output:

```text
agent-lab/benchmarks/openclaw_fake_runtime/
  fake_channel_messages.jsonl
  fake_plugin_manifests/
  fake_skills/
  expected_results.json
  benchmark_runner.py
  reports/openclaw_fake_benchmark_report.md
```

The current report proves the initial Sentinel product rule: scan, score, preview, approve, trace before any action. Initial result: `9` fake fixtures, `0` failures, `9` blocked decisions.

## Priority Recommendations

1. Fix fresh-clone test commands.
   - Move or guard `RedditPulse/run_validation_test.py` so `python -m pytest` does not require ignored local env files.
   - Install/use `pytest-asyncio` for Sentinel or adjust test config so the async bridge test runs cleanly.

2. Make CueIdea-to-Sentinel the main route, not direct placeholder runs.
   - Direct Sentinel runs should be labeled as sandbox/hypothesis mode.
   - Real product runs should start from CueIdea validation imports until Sentinel has real research acquisition.

3. Promote an evidence contract as the cross-app API.
   - CueIdea already has `evidence.ts` and `evidence_contract.md`.
   - Sentinel has `EvidenceItem`.
   - The next integration step should be a shared field-level mapping document and tests against real CueIdea report fixtures.

4. Upgrade Sentinel research before adding more execution capability.
   - Improve competitor alternatives, WTP extraction, ICP/community reachability, objections, buying triggers, and evidence gaps.
   - Keep email sending, browser execution, shell, code edits, and payments disabled.

5. Review hosted Supabase security before staging.
   - Set `SENTINEL_REQUIRE_AUTH=true`.
   - Verify user scoping for all API routes.
   - Add/review RLS for Sentinel tables if they are exposed beyond service-role server paths.

6. Promote B2.5 portability before public scanner positioning.
   - Current B2.5 artifacts are consistent.
   - Fresh rerun from restored OpenClaw source is verified in this clone.
   - Add explicit portable reproducibility metadata before treating scanner reports as public audit artifacts.

7. Build B3 as fake benchmark infrastructure, not integration.
   - The next Agent Lab output should be controlled fixtures and expected results.
   - This will turn OpenClaw risk learning into Sentinel Skill Scanner requirements without touching real runtime powers.

## Verification

Commands run:

```powershell
git clone https://github.com/Gameminde/SENTINAL.git .
python -m pytest tests
python -m pytest
```

Results:

- Clone completed successfully.
- `https://cueidea.me` reachable on 2026-04-26 and presents CueIdea as a live public startup-opportunity intelligence product.
- `RedditPulse`: `python -m pytest tests` -> 44 passed.
- `RedditPulse`: top-level `python -m pytest` fails during collection because `run_validation_test.py` requires ignored `app/.env.local`.
- `sentinel-control/services/sentinel-core`: `python -m pytest` -> 33 passed, 1 failed due missing async pytest plugin (`pytest-asyncio`).
- `agent-lab/tools/openclaw_static_scanner`: `python -m unittest discover -s agent-lab\tools\openclaw_static_scanner\tests` -> 11 passed.
- `agent-lab/vendors/openclaw/source`: restored by cloning `https://github.com/basetenlabs/openclaw-baseten.git`.
- OpenClaw source checkout: `a2288c2b09e621f89a915960398f58e200b3b69d`.
- OpenClaw scanner rerun from source completed without installing dependencies or running OpenClaw.
- `agent-lab/audits/openclaw_scanner_report.json`: regenerated hash matches computed hash.
- Regenerated B2.5 scanner counts: `83` total, `52` blocked, `29` needs_review, `2` draft_only_tool.
- `agent-lab/benchmarks/openclaw_fake_runtime/benchmark_runner.py`: `9` fake fixtures, `0` failures.
- Frontend type/build checks were not run because neither app has `node_modules` installed in this fresh clone.

## Next Best Step

Before building new features, create a CueIdea-to-Sentinel integration contract test:

```text
real CueIdea report fixture
  -> normalized CueIdea import
  -> Sentinel evidence rows
  -> decision/GTM pack
  -> GTM quality score
  -> generated files
  -> trace records
```

That test would prove the heart of the product: evidence enters from CueIdea, and Sentinel turns it into a controlled, useful GTM operating package.
