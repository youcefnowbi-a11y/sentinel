# Browser V1 Roadmap

Date: 2026-05-01
Status: Browser V1/V2 certified, Browser V2.5 locked, P4H-AE runtime integration locked, P4G-R rechecked with Docker but real peer command still missing

## Phase Map

| Phase | Goal | Runtime Power | Status |
| --- | --- | --- | --- |
| P3A.0 | Public URL guard and browser evidence contracts. | No browser, no fetch. | Done |
| P3A.1 | Fake evidence adapter with injected page source. | No browser, no fetch. | Done |
| P3A.2 | Trace, receipt, artifact capture, event catalog. | No browser, no fetch. | Done |
| P3A.3 | Fake eval dataset for positive and negative browser cases. | No browser, no fetch. | Done |
| P3A.4 | Controlled live public HTTP read-only fetch. | Public GET only. | Done |
| P3B.0 | Rendered snapshot contract with injected renderer. | No live browser. | Done |
| P3B.1 | Screenshot/snapshot artifact capture contract. | No live browser. | Done |
| P3B.2 | Live rendered browser backend read-only. | Public rendered page only. | Done |
| P3B.3 | Citation extraction from real rendered pages. | Read-only evidence only. | Done |
| P3B.4 | AgentRuntime integration through ToolRegistry/RiskRouter. | Governed browser evidence capability. | Done |
| P3B.5 | Browser final gate and exhaustive review. | Certified Browser V1. | Done |
| P3C | Public URL/fetch guard hardening. | Public evidence only. | Done |
| P3D | Evidence quality and readable extraction. | Public evidence only. | Done |
| P3E | Structural snapshot, refs, screenshot metadata. | Public evidence only. | Done |
| P3F | Network/diagnostic observability ledger. | Public evidence only. | Done |
| P3G | Interaction dry-run planning. | No-op plan only. | Done |
| P3H | Limited real interaction gate. | Plan-bound public browser state interaction. | Done |
| P3I | Public tabs / stateless lifecycle. | Public session/tab lifecycle ledger. | Done |
| P3J | PDF, element screenshot, screenshot normalization. | Proof-bound artifact expansion. | Done |
| P3K | Browser reliability, pool, lifecycle supervisor. | Stateless lease, health, retry, and FinalGate proof. | Done |
| P3N | Browser final review. | Browser V2 certification. | Done |
| P3O | Browser formal review gate. | Logic/code/algorithm/math lock before Browser 2.5/V3. | Done |
| P3X | Browser-cortex integration. | Brain consumes browser evidence/actions. | Done |
| P3Y | Browser-LLM cortex integration. | LLM ContextPack and ToolIntentCompiler contracts. | Done |
| P4A | Browser V2.5 perception, grounding, public multi-tab, verifier, and loop detector. | Public/stateless advanced browser operator layer. | Done |
| P4A-R | Browser V2.5 readiness review before V3 authority classes. | Consumption map and P4B authority class plan. | Done |
| P4B-0 | Browser V3 authority kernel. | Shared V3 grant/request/receipt/FinalGate contract. | Done |
| P4B-1 | Form submit/post/send/publish authority. | Governed public form commit from certified plan. | Done |
| P4B-2 | Download quarantine authority. | Bounded public file capture into quarantine artifact. | Done |
| P4B-3 | Upload authorized authority. | Governed upload of certified Sentinel artifacts only. | Done |
| P4B-4 | Private session authority. | Per-mission private session with destroy proof. | Done |
| P4B-5 | Login authority. | Account-id login inside private session with credential redaction. | Done |
| P4B-6 | Cookie/storage contracts. | Redacted session-bound storage summary or scoped clear. | Done |
| P4B-7 | Sandboxed JS evaluate. | Script-hash allowlisted no-network JS result artifact. | Done |
| P4B-8 | HAR/body capture. | Bounded redacted network body diagnostics. | Done |
| P4B-9 / P4C | Browser V3 supremacy review. | Integrated V3 logic/code/algorithm/math/failure/comparison lock. | Done |
| P4C-H.1 | Browser V3 backend-reality and EvalBench metric hardening. | No new powers; backend-result validation and multi-run metrics. | Done |
| P4C-H.2 | Browser V3 fixture backend bench and multi-run proof. | No new powers; profile lifecycle fixture and Browser V3 EvalBench case. | Done |
| P4C-H.3 | Live Browser V3 adapter harness. | No new powers; Playwright/vault-style fixture proof and 10-run EvalBench. | Done |
| P4C-S | Browser V3 measured supremacy gate. | EvalBench corpus with measured local Browser V3 results. | Done |
| P4D | Browser grand review and benchmark research. | No new powers; code/logic/algorithm/Brain/LLM/OpenClaw/benchmark review. | Done |
| P4D-H | Browser scientific hardening. | No new powers; stronger statistics, V3 cognition mapping, adversarial corpora, external benchmark prep. | Done |
| P4E | Self-hosted browser benchmark campaign. | No new powers; WebArena-style, VisualWebArena-style, BrowseComp-style, 30-run scorecard, and peer protocol. | Done |
| P4F | Peer browser benchmark campaign. | No new powers; lab-isolated protocol, profiled peer baseline, same corpus, timeout, scoring, and run_count. | Done |
| P4G | External/open-web browser benchmark campaign. | No new powers; neutral result schema, Sentinel 30-run export, and recorded peer-runtime block. | Done, inconclusive |
| P4G-R | Approved containerized peer runtime run. | No new powers; source/lockfile/package hashes recorded, neutral non-execution rows emitted, no host fallback. | Done, blocked |
| P4H | Browser Fluency mission corpus. | No new powers; define Sentinel-owned mission list for lifecycle, URL, vision/OCR, cookies, forms, files, research, safety, and repair. | Done, draft |
| P4H-R | Browser Fluency runner and first scorecard. | No new powers; 42 critical subset missions executed as contract fixtures and F0-F5 group levels reported. | Done, partial |
| P4H-S | Browser Fluency hardening and full 72-mission scorecard. | No new powers; 72 missions executed, all groups >= F3, state group F4, 18 partial missions remain. | Done, partial |
| P4H-T | Browser Fluency depth hardening. | No new powers; 72 missions target-met in contract fixtures, zero partial missions remain. | Done, contract-ready |
| P4H-U | Live/self-hosted Browser Fluency verification. | No new powers; 12 representative groups, 30 runs per group, 360 live local iterations. | Done, representative live-pass |
| P4H-V | Full live/self-hosted Browser Fluency verification. | No new powers; 72 missions, 30 runs per mission, 2160 live local iterations. | Done, full live-pass |
| P4H-W-R | Real browser-engine visual/OCR research lock. | No new powers; reject OCR-only design and define hybrid visual perception architecture. | Done |
| P4H-W | Real browser-engine visual/OCR harness. | No new powers; 6 visual missions, 30 runs each, 180 Playwright read-only fixture iterations. | Done, local visual-pass |
| P4H-X-R | Aggressive operator doctrine and Perception/Action research lock. | No new powers; lock Power-first/Mission-governed/Proof-backed doctrine, CompiledMissionPolicy, and browser-only v0 direction. | Done |
| P4H-X | PerceptionEngine v0 + ActionEngine v0 browser backend. | Browser backend only; map browser observations to scene/action candidates and existing governed runners. | Done |
| P4H-Y | Browser Operator Trial. | No new powers; prove PerceptionEngine/ActionEngine can observe, ground, act, verify, repair, and deny. | Done |
| P4H-Z | Browser Operator Hardening. | No new powers; ambiguity, repair, budget pressure, and negative action paths. | Done |
| P4H-AA | Browser V3 ActionEngine Routing. | No new powers; route existing Browser V3 authority classes through ActionEngine. | Done |
| P4H-AB | Browser Operator Long-Horizon Mission Trial. | No new powers; 10 longer mixed missions through ActionEngine. | Done |
| P4H-AC | Browser Operator Live Long-Horizon Harness. | No new powers; live self-hosted pages feed long-horizon ActionEngine/V3 flows. | Done |
| P4H-AD | Browser Operator Open-Web-Like Breadth and Visual Tempo Hardening. | No new powers; harder live self-hosted pages, weak DOM/AX, dynamic state, ambiguity, and visual latency pressure. | Done |
| P4H-AE | Browser Runtime Integration Gate. | No new powers; connect proven browser operator route to Sentinel mission runtime path. | Done |
| P4H-AF | Browser Runtime Mini-Corpus Integration. | No new powers; execute multiple P4H-AD-style runtime tasks through AgentRuntime/MissionRunner. | Next |
| P4G-R2 | Real peer container execution after Docker/Podman is available. | No new powers; execute real peer runtime in throwaway lab container and import only neutral JSONL results. | Docker available; blocked by missing approved peer command |

## Completion Criteria

Browser V1 is complete only when:

- live public read-only fetch is governed by `PublicUrlGuard`;
- rendered browser reads are read-only and sessionless;
- every accepted page creates trace, evidence, artifact, and receipt;
- every rejected page creates trace with a clear reason;
- fake evals and live-read evals pass;
- prompt injection is detected and visible in receipts;
- rendered snapshots include network/diagnostic ledger metadata;
- interaction dry-run plans bind to snapshot hash, page hash, and stable refs;
- limited real interactions require a certified dry-run plan, same-origin result,
  post-action recapture, receipt, and FinalGate proof;
- public session/tab lifecycle is stateless, URL-policy-bound, and FinalGate
  verifiable;
- rendered artifacts include screenshot normalization proof and optional
  PDF/element screenshots bound to receipts and FinalGate checks;
- browser reliability supervision proves stateless leases, bounded retries,
  health checks, and release ordering;
- Browser V2 formal lock proves logic, code, algorithm, math, failure-mode, and
  eval scorecard readiness before Browser 2.5/V3;
- Browser-Cortex integration maps browser outputs to source confidence,
  hypothesis deltas, repair signals, action recommendations, and evidence
  chains;
- final gate rejects forged browser success;
- final gate rejects forged interaction plans and any real browser interaction event in P3G;
- final gate rejects forged, stale, or unplanned P3H interaction execution;
- execution-boundary primitive scan is clean for non-delegated surfaces;
- product docs remain Sentinel-native.

Current certification:

- full sentinel-core test suite passes;
- `CoreFinalGate` accepts governed Browser V1 runtime results;
- `CoreFinalGate` rejects browser results with forged registry policy traces;
- `CoreFinalGate` rejects browser snapshots with forged or missing network ledger metadata;
- `CoreFinalGate` rejects forged browser interaction dry-run plans;
- `CoreFinalGate` rejects forged browser interaction execution events;
- `CoreFinalGate` rejects forged public browser lifecycle events;
- `CoreFinalGate` rejects forged PDF and element screenshot browser artifacts;
- `CoreFinalGate` rejects forged browser reliability supervisor events;
- Browser V2 final certification is recorded in `BROWSER_V2_CERTIFICATION.md`;
- Browser V2 formal lock is recorded in `BROWSER_V2_FORMAL_REVIEW.md` and
  `BROWSER_V2_LOCK_VERDICT.md`;
- Browser-Cortex integration is recorded in
  `BROWSER_CORTEX_INTEGRATION_REPORT.md` and `P3X_LOCK_VERDICT.md`;
- Browser-LLM cortex integration is recorded in `BROWSER_LLM_ARCHITECTURE.md`,
  `BROWSER_LLM_CONTEXTPACK_SPEC.md`, `BROWSER_TOOL_INTENT_COMPILER_SPEC.md`,
  and `P3Y_LOCK_VERDICT.md`;
- Browser V2.5 P4A is recorded in `P4A_BROWSER_V25_ARCHITECTURE.md`,
  `P4A_UIOBSERVATION_MODEL.md`, and `P4A_LOCK_VERDICT.md`;
- Browser V2.5 readiness for P4B is recorded in `P4A_READINESS_REVIEW.md`,
  `P4A_CORTEX_LLM_CONSUMPTION_MAP.md`, and `P4B_AUTHORITY_CLASS_PLAN.md`;
- Browser V3 authority kernel and form submit authority are recorded in
  `P4B_BROWSER_V3_AUTHORITY_KERNEL.md`, `P4B_FORM_SUBMIT_AUTHORITY_SPEC.md`,
  and `P4B_FORM_SUBMIT_LOCK_VERDICT.md`;
- `CoreFinalGate` rejects forged or incomplete Browser V3 form-submit events;
- Browser V3 download quarantine is recorded in
  `P4B_DOWNLOAD_QUARANTINE_AUTHORITY_SPEC.md` and
  `P4B_DOWNLOAD_QUARANTINE_LOCK_VERDICT.md`;
- `CoreFinalGate` rejects forged or incomplete Browser V3 download-quarantine
  events;
- Browser V3 upload authorized is recorded in
  `P4B_UPLOAD_AUTHORIZED_AUTHORITY_SPEC.md` and
  `P4B_UPLOAD_AUTHORIZED_LOCK_VERDICT.md`;
- `CoreFinalGate` rejects forged or incomplete Browser V3 upload-authorized
  events;
- Browser V3 private session, login authority, cookie/storage contract,
  sandboxed JS evaluate, and HAR/body capture are recorded in their P4B specs
  and lock verdicts;
- `CoreFinalGate` rejects missing close proof, credential-bearing login payloads,
  unredacted storage/HAR outputs, sandboxed-JS network calls, and forged
  artifacts for P4B-4 through P4B-8;
- P4C Browser V3 supremacy review is recorded in
  `P4C_BROWSER_V3_SUPREMACY_REVIEW.md` and
  `P4C_BROWSER_V3_LOCK_VERDICT.md`;
- `ToolIntentCompiler` rejects raw credential, raw cookie/storage, and raw
  HAR/body payload fields in V3 LLM draft intents;
- P4C-H.1 backend-reality and EvalBench hardening is recorded in
  `P4C_H_BROWSER_V3_BACKEND_REALITY_HARDENING.md`,
  `P4C_H_EVALBENCH_MULTI_RUN_HARDENING.md`, and
  `P4C_H_LOCK_VERDICT.md`;
- P4C-H.2 fixture backend bench and multi-run proof is recorded in
  `P4C_H2_BROWSER_V3_FIXTURE_BACKEND_BENCH.md`,
  `P4C_H2_BROWSER_V3_EVALBENCH_PROOF.md`, and
  `P4C_H2_LOCK_VERDICT.md`;
- P4C-H.3 live adapter harness is recorded in
  `P4C_H3_LIVE_ADAPTER_HARNESS.md`,
  `P4C_H3_BROWSER_V3_LIVE_EVALBENCH.md`, and
  `P4C_H3_LOCK_VERDICT.md`;
- P4C-S measured supremacy gate is recorded in
  `P4C_S_BROWSER_V3_MEASURED_SUPREMACY_GATE.md`,
  `P4C_S_CROSS_CLASS_EVAL_MISSIONS.md`, and
  `P4C_S_LOCK_VERDICT.md`;
- P4D Browser Grand Review is recorded in `P4D_BROWSER_GRAND_REVIEW.md`,
  `P4D_BROWSER_CODE_REVIEW.md`, `P4D_BROWSER_LOGIC_REVIEW.md`,
  `P4D_BROWSER_ALGORITHM_REVIEW.md`,
  `P4D_BROWSER_BRAIN_LLM_INTEGRATION_REVIEW.md`,
  `P4D_OPENCLAW_BROWSER_FORENSIC_RESEARCH.md`,
  `P4D_BROWSER_BENCHMARK_RESEARCH.md`,
  `P4D_SENTINEL_BROWSER_EVALBENCH_SPEC.md`, and
  `P4D_BROWSER_SUPREMACY_DECISION.md`;
- P4D-H Browser scientific hardening is recorded in
  `P4D_H_EVALBENCH_STATS_HARDENING.md`,
  `P4D_H_BROWSER_V3_COGNITIVE_MAPPING.md`,
  `P4D_H_ADVERSARIAL_CORPUS.md`,
  `P4D_H_LOCAL_10RUN_SCORECARD.md`,
  `P4D_H_SELF_HOSTED_BENCHMARK_PLAN.md`, and
  `P4D_H_LOCK_VERDICT.md`;
- P4E self-hosted browser benchmark is recorded in
  `P4E_BROWSER_BENCHMARK_ARCHITECTURE.md`,
  `P4E_WEBARENA_STYLE_TASKS.md`,
  `P4E_VISUAL_GROUNDING_TASKS.md`,
  `P4E_RESEARCH_BROWSING_TASKS.md`,
  `P4E_BROWSER_SCORECARD_SCHEMA.md`,
  `P4E_30RUN_RESULTS.md`, and `P4E_LOCK_VERDICT.md`;
- P4F peer browser benchmark protocol is recorded in
  `P4F_PEER_BENCHMARK_PROTOCOL.md`,
  `P4F_OPENCLAW_LAB_RUNNER_PLAN.md`,
  `P4F_SHARED_TASK_CORPUS.md`,
  `P4F_SCORING_RULES.md`,
  `P4F_SENTINEL_VS_OPENCLAW_RESULTS.md`,
  `P4F_FAILURE_ANALYSIS.md`, and `P4F_BROWSER_SUPREMACY_VERDICT.md`;
- P4G external/open-web campaign harness is recorded in
  `P4G_OPEN_WEB_BENCHMARK_PROTOCOL.md`,
  `P4G_REAL_PEER_RUNTIME_RUNNER.md`,
  `P4G_NEUTRAL_RESULT_SCHEMA.md`,
  `P4G_SENTINEL_RESULTS.md`,
  `P4G_OPENCLAW_REAL_RESULTS.md`,
  `P4G_SENTINEL_VS_OPENCLAW_MEASURED_RESULTS.md`,
  `P4G_FAILURE_ANALYSIS.md`, and
  `P4G_BROWSER_FINAL_SUPREMACY_VERDICT.md`;
- P4G-R containerized peer runtime attempt is recorded in
  `P4G_R_CONTAINERIZED_PEER_RUNTIME_RUN.md`,
  `P4G_R_CONTAINER_POLICY.md`,
  `P4G_R_OPENCLAW_CONTAINER_RESULTS.md`, and
  `P4G_R_LOCK_VERDICT.md`;
- P4H Browser Fluency mission corpus is recorded in
  `P4H_BROWSER_FLUENCY_MISSION_RESEARCH.md`,
  `P4H_BROWSER_FLUENCY_MISSION_CATALOG.md`,
  `P4H_BROWSER_FLUENCY_SCORECARD.md`, and
  `P4H_BROWSER_FLUENCY_NEXT_PLAN.md`;
- P4H-R Browser Fluency runner and first scorecard are recorded in
  `P4H_R_BROWSER_FLUENCY_RUNNER.md`,
  `P4H_R_FIRST_SCORECARD.md`,
  `P4H_R_FAILURE_ANALYSIS.md`,
  `P4H_R_NEXT_HARDENING_PLAN.md`, and
  `P4H_R_LOCK_VERDICT.md`;
- P4H-S full Browser Fluency scorecard is recorded in
  `P4H_S_FULL_FLUENCY_SCORECARD.md`,
  `P4H_S_PARTIAL_MISSIONS.md`,
  `P4H_S_HARDENING_PLAN.md`, and
  `P4H_S_LOCK_VERDICT.md`;
- P4H-T Browser Fluency depth scorecard is recorded in
  `P4H_T_DEPTH_FLUENCY_SCORECARD.md`,
  `P4H_T_TARGET_MET_MISSIONS.md`,
  `P4H_T_REMAINING_REALITY_GAP.md`, and
  `P4H_T_LOCK_VERDICT.md`;
- P4H-U live self-hosted Browser Fluency scorecard is recorded in
  `P4H_U_LIVE_SELF_HOSTED_FLUENCY_RUNNER.md`,
  `P4H_U_30RUN_SCORECARD.md`,
  `P4H_U_FAILURE_ANALYSIS.md`,
  `P4H_U_REMAINING_GAP.md`, and
  `P4H_U_LOCK_VERDICT.md`;
- P4H-V full live self-hosted Browser Fluency scorecard is recorded in
  `P4H_V_FULL_LIVE_SELF_HOSTED_FLUENCY_RUNNER.md`,
  `P4H_V_72MISSION_30RUN_SCORECARD.md`,
  `P4H_V_FAILURE_ANALYSIS.md`,
  `P4H_V_REMAINING_GAP.md`, and
  `P4H_V_LOCK_VERDICT.md`;
- P4H-W-R visual perception research is recorded in
  `P4H_W_R_VISUAL_PERCEPTION_RESEARCH.md`,
  `P4H_W_R_SENTINEL_VISUAL_ARCHITECTURE.md`,
  `P4H_W_R_BENCHMARK_PLAN.md`, and
  `P4H_W_R_LOCK_VERDICT.md`;
- P4H-W real browser-engine visual harness is recorded in
  `P4H_W_REAL_VISUAL_HARNESS.md`,
  `P4H_W_VISUAL_OBSERVATION_MODEL.md`,
  `P4H_W_CROP_ZOOM_OCR_FALLBACK.md`,
  `P4H_W_VISUAL_GROUNDING_VERIFIER.md`,
  `P4H_W_30RUN_SCORECARD.md`, and
  `P4H_W_LOCK_VERDICT.md`;
- P4H-X-R aggressive operator doctrine and Perception/Action research lock is
  recorded in `P4H_X_R_AGGRESSIVE_OPERATOR_DOCTRINE.md`,
  `P4H_X_R_PERCEPTION_ACTION_ENGINE_RESEARCH.md`,
  `P4H_X_R_COMPILED_MISSION_POLICY.md`,
  `P4H_X_R_SCENE_MODEL_DECISION.md`,
  `P4H_X_R_PERCEPTION_TO_ACTION_LINK.md`,
  `P4H_X_R_BRAIN_LLM_PERCEPTION_CONTEXT.md`,
  `P4H_X_R_GUI_GROUNDING_BENCHMARK_RESEARCH.md`, and
  `P4H_X_R_LOCK_VERDICT.md`;
- P4H-X PerceptionEngine v0 + ActionEngine v0 code slice is recorded in
  `P4H_X_PERCEPTION_ENGINE_V0.md`, `P4H_X_ACTION_ENGINE_V0.md`,
  `P4H_X_COMPILED_MISSION_POLICY_IMPL.md`,
  `P4H_X_BROWSER_BACKEND_SLICE.md`, and `P4H_X_LOCK_VERDICT.md`;
- P4H-Y Browser Operator Trial is recorded in
  `P4H_Y_BROWSER_OPERATOR_TRIAL_RUNNER.md`,
  `P4H_Y_30RUN_OPERATOR_SCORECARD.md`, and `P4H_Y_LOCK_VERDICT.md`;
- P4H-Z Browser Operator Hardening is recorded in
  `P4H_Z_BROWSER_OPERATOR_HARDENING.md`,
  `P4H_Z_30RUN_OPERATOR_HARDENING_SCORECARD.md`,
  `P4H_Z_FAILURE_ANALYSIS.md`, and `P4H_Z_LOCK_VERDICT.md`;
- browser product docs contain no vendor-agent traces;
- execution-boundary primitive scan found no executable non-delegated primitive in the core.
