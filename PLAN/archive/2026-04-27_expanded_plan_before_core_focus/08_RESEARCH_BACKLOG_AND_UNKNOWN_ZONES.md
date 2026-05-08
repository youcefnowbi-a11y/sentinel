# 08 Research Backlog And Unknown Zones

Date: 2026-04-26

## 1. Why This Exists

We do not want to build a reduced agent and discover too late that whole capability zones were missing.

This backlog names the unexplored or under-explored zones that can lift Sentinel beyond ordinary agents.

## 2. Tool Universe

Research:

- public API catalogs;
- MCP servers;
- Postman collections;
- RapidAPI-like marketplaces;
- government data portals;
- science/open-data portals;
- finance/market data APIs;
- ecommerce/review/app store datasets;
- jobs/hiring APIs;
- social/community sources;
- security intelligence sources.

Questions:

- What tools are no-auth and safe?
- Which tools require official free tier?
- Which categories are useful for GTM and launch?
- Which tools are stale or unreliable?
- Which tools can be composed into opportunity signals?

## 3. Cross-Domain Signal Arbitrage

Underused combinations:

- jobs + reviews + funding + regulations;
- app store complaints + pricing pages + Reddit/CueIdea;
- GitHub issues + enterprise hiring + compliance;
- weather + logistics + ecommerce;
- patents + hiring + product launches;
- public tenders + regulations + vendor pricing.

Goal:

Find opportunities before they become obvious.

## 4. Browser And Internet Understanding

Sentinel needs operational understanding of:

- DNS/URLs;
- HTTP methods;
- auth/cookies/sessions;
- robots and terms constraints;
- browser state;
- DOM vs screenshot;
- forms;
- rate limits;
- pagination;
- anti-bot behavior;
- prompt injection in web content.

Research output:

- BrowserSandbox spec;
- WebEvidenceExtractor spec;
- BrowserRiskPolicy.

## 5. Computer And OS Understanding

Sentinel needs operational understanding of:

- filesystems;
- processes;
- environment variables;
- shells;
- permissions;
- symlinks;
- registry on Windows;
- services/daemons;
- package managers;
- local network.

Research output:

- HostActionRiskModel;
- ShellSandbox spec;
- FileSystemBoundary spec.

## 6. Electronics And Hardware Understanding

Future sidecar/device work needs:

- camera/screen capture constraints;
- microphone/audio capture;
- local compute limits;
- GPU/CPU tradeoffs;
- device buses and sensors;
- latency/energy constraints;
- privacy around raw signals.

Research output:

- SidecarHardwareAwareness spec;
- DeviceCapabilityManifest.

## 7. LLM And AI Systems Understanding

Sentinel needs:

- model routing;
- context compression;
- hallucination checks;
- tool-call validation;
- prompt injection defense;
- multimodal model selection;
- image/video generation limits;
- eval-driven improvement;
- cost/latency/quality tradeoffs.

Research output:

- CostRouter spec;
- ModelCapabilityRegistry;
- PromptInjectionEvalSet;
- MultimodalCapabilityPolicy.

## 8. Media And Creative Production

Research:

- OCR engines;
- image generation/editing providers;
- video generation/editing providers;
- transcription;
- subtitles;
- asset provenance;
- brand consistency scoring;
- image-to-copy workflows;
- video-to-launch-asset workflows.

Research output:

- MediaArtifactSchema;
- BrandConsistencyReviewer;
- VisualAssetPolicy.

## 9. Code Intelligence

Research:

- repo mapping;
- call graph extraction;
- dependency scanning;
- test discovery;
- patch generation;
- sandbox test execution;
- secret detection;
- coding agent benchmarks.

Research output:

- CodeMissionSpec;
- PatchProposalProtocol;
- CodeSandboxPolicy.

## 10. Work Methods Not Yet Implemented

Priority methods:

- contradiction mining;
- premortem;
- Bayesian update;
- cross-domain opportunity arbitrage;
- causal map;
- ROI tree;
- red team / blue team;
- evidence ladder;
- systems decomposition;
- mission-to-tool compiler.

## 11. Product Unknowns

Still needs decision:

- Is the first paid product GTM Pack, Launch Pack, or Tool Scanner?
- Should Tool Intelligence be internal first or public product?
- Which media generation provider is acceptable?
- Which browser automation stack will be used?
- What data storage model for traces and tools?
- How much of Agent Lab becomes public-facing security product?
- What is the first user-visible "wow" demo?

## 12. Research Rule

Every future research pass must output:

- what was inspected;
- source paths or URLs;
- what is verified;
- what is inferred;
- what is unknown;
- what Sentinel should rewrite;
- what Sentinel must avoid;
- implementation gate.
