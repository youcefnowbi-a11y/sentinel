# CueIdea to Sentinel Evidence Contract

Sprint S1 proves the core product chain:

```text
CueIdea validation report
-> Sentinel evidence normalization
-> decision/debate layer
-> GTM pack
-> GTM quality score
-> Firewall review
-> safe local files/drafts
-> trace ledger
```

CueIdea/RedditPulse remains the evidence engine. Sentinel Control starts after validation: it normalizes evidence, decides with proof, generates a GTM operating pack, reviews actions through the firewall, and writes trace records.

## Mapping Contract

| CueIdea field | Sentinel target | Rule |
| --- | --- | --- |
| `validation_id`, `id`, `report.id` | `ValidationResult.validation_id` | Preserve the original CueIdea validation identifier when present. |
| `idea_text`, `idea`, `report.idea_text` | `ValidationResult.idea` | Preserve the validated idea text. |
| `report.executive_summary`, `report.summary`, `market_analysis.pain_description` | `ValidationResult.summary` | Preserve user-visible validation summary. |
| `market_analysis.evidence[]`, `market_analysis.pain_quotes[]`, `debate_evidence[]`, `evidence[]` | `EvidenceItem[]` | Import every usable evidence row. Do not hide weak/noisy rows. |
| `wtp_evidence[]`, `willingness_to_pay_evidence[]`, `pricing_strategy.evidence[]` | `EvidenceItem.evidence_type = wtp` or `pricing` | Paid intent must be explicit and countable. |
| `competitor_complaints[]`, competitor/alternative complaint rows | `EvidenceItem.evidence_type = competitor_complaint` | Competitor gaps are represented as competitor complaints plus raw metadata until a dedicated `competitor_gap` enum exists. |
| `directness_tier`, `proof_tier`, `evidence_taxonomy`, `directness`, `relevance` | `EvidenceItem.metadata.proof_tier` | Normalize into `direct`, `adjacent`, or `supporting`. |
| `confidence`, `score`, text labels like `high`, `medium`, `low` | `EvidenceItem.confidence` | Normalize to `0.0..1.0`. |
| `created_at`, `observed_at`, `scraped_at` | `EvidenceItem.freshness_score` | Convert recency into `0.0..1.0`. |
| `relevance_score`, `relevance` | `EvidenceItem.relevance_score` | Preserve explicit relevance; otherwise derive from proof tier. |
| `source`, `platform` | `EvidenceItem.source` | Preserve source or source identifier even when no URL exists. |
| `url`, `permalink` | `EvidenceItem.url` | Preserve source URL when available. |
| `quote`, `pain_quote` | `EvidenceItem.quote` | Preserve short supporting quote when available. |
| raw CueIdea row | `EvidenceItem.metadata.raw` | Keep original row for auditability. |

## Decision Rules

- Direct and adjacent evidence must remain distinguishable.
- WTP evidence is a build gate. Missing WTP blocks a `build` or `ready` outcome.
- Noisy evidence is downgraded through low confidence/supporting proof tier, not removed.
- Every generated GTM section must contain `evidence_refs` or an explicit `Evidence gap`.
- Weak sections must say `Evidence gap` instead of presenting certainty.
- CueIdea-backed runs are labeled `Evidence-backed`.
- Direct local runs without CueIdea evidence are labeled `Sandbox / hypothesis mode`.

## S2 Research Enrichment

After CueIdea import, Sentinel derives a deterministic `ResearchEnrichmentResult` from imported evidence only. This is not live browser research and does not add runtime power.

The enrichment layer extracts:

- competitor alternatives,
- manual workaround alternatives,
- ICP segments,
- reachable communities,
- objections,
- buying triggers,
- pricing/WTP hints,
- evidence gaps,
- recommended research questions.

The GTM Pack must use this enrichment to make ICP, competitor gap, outreach, landing copy, roadmap, watchlist, and prospect sources concrete. If enrichment cannot support a section, the section must show `Evidence gap`.

S2 quality gates:

- ICP must name a specific segment, not generic `founders`, `businesses`, `startups`, `creators`, or `users`.
- Competitor gap must name an alternative or show `Evidence gap`.
- Outreach must reference a real pain or buying trigger and remain draft-only.
- The 7-day roadmap must contain measurable actions.
- WTP must have explicit evidence or `Evidence gap`.
- Prospect sources must be specific communities/sources or marked unknown.

## Execution Rules

- File creation is limited to `data/generated_projects`.
- Outreach remains draft-only.
- `send_email`, `browser_submit_form`, `run_shell_command`, and `modify_code` remain disabled in v1.
- Every major step writes a trace event: CueIdea import, evidence record, decision, pack generation, firewall review, approval, and safe execution.

## S1 Acceptance

- Strong CueIdea fixture produces a ready or near-ready GTM pack.
- Weak/noisy fixture produces `needs_revision` or `research_more`, not a confident build.
- Missing WTP blocks build/ready.
- Generated files are evidence-referenced.
- Trace records exist for every major step.
- No risky execution capability is enabled.
