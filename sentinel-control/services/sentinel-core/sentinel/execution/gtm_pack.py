from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import re

from pydantic import BaseModel, ConfigDict, Field

from sentinel.decision.research_enrichment import EnrichedSignal, ResearchEnrichmentResult, enrich_research
from sentinel.decision.debate.verdict import DebateResult
from sentinel.shared.enums import ApprovalStatus, EvidenceType, RiskLevel
from sentinel.shared.models import AgentAction, EvidenceItem


class GTMPackSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str
    title: str
    content: str
    evidence_refs: list[str] = Field(default_factory=list)


class GTMPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    idea: str
    sections: list[GTMPackSection]
    evidence_refs: list[str] = Field(default_factory=list)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:64] or "sentinel-project"


def _evidence_summary(evidence: list[EvidenceItem]) -> str:
    if not evidence:
        return "No evidence attached yet."
    return "\n".join(f"- `{item.id}`: {item.summary}" for item in evidence[:8])


def _has_evidence_type(evidence: list[EvidenceItem], *types: EvidenceType) -> bool:
    return any(item.evidence_type in types for item in evidence)


def _has_proof_tier(evidence: list[EvidenceItem], tier: str) -> bool:
    return any(item.metadata.get("proof_tier") == tier for item in evidence)


def _evidence_gap(marker: str, message: str) -> str:
    return f"\n\n## Evidence gap\n\nEVIDENCE_GAP: {marker} - {message}"


def _signal_lines(signals: list[EnrichedSignal], empty: str = "- Unknown") -> str:
    if not signals:
        return empty
    return "\n".join(f"- {signal.label}: {signal.summary}" for signal in signals[:5])


def _signal_refs(signals: list[EnrichedSignal], fallback: list[str]) -> list[str]:
    refs: list[str] = []
    for signal in signals:
        for ref in signal.evidence_refs:
            if ref not in refs:
                refs.append(ref)
    return refs or fallback


def _first_label(signals: list[EnrichedSignal], fallback: str) -> str:
    return signals[0].label if signals else fallback


def _first_summary(signals: list[EnrichedSignal], fallback: str) -> str:
    return signals[0].summary if signals else fallback


def _section(filename: str, title: str, body: str, refs: list[str]) -> GTMPackSection:
    evidence_block = "\n\n## Evidence refs\n\n" + "\n".join(f"- `{ref}`" for ref in refs)
    return GTMPackSection(filename=filename, title=title, content=f"# {title}\n\n{body}{evidence_block}\n", evidence_refs=refs)


@dataclass
class GTMPackGenerator:
    output_root: str = "data/generated_projects"

    def generate(
        self,
        idea: str,
        debate: DebateResult,
        evidence: list[EvidenceItem],
        enrichment: ResearchEnrichmentResult | None = None,
    ) -> GTMPack:
        refs = debate.evidence_refs or [item.id for item in evidence[:5]]
        enrichment = enrichment or enrich_research(evidence)
        has_wtp = _has_evidence_type(evidence, EvidenceType.WTP, EvidenceType.PRICING)
        has_competitor = _has_evidence_type(evidence, EvidenceType.COMPETITOR_COMPLAINT)
        has_direct = _has_proof_tier(evidence, "direct")
        icp_refs = _signal_refs(enrichment.icp_segments, refs)
        competitor_refs = _signal_refs(enrichment.competitors, refs)
        community_refs = _signal_refs(enrichment.communities, refs)
        trigger_refs = _signal_refs(enrichment.buying_triggers, refs)
        pricing_refs = _signal_refs(enrichment.pricing_hints, refs)

        verdict_body = f"Decision: **{debate.decision.value}**\n\n{debate.skeptical_challenge}"
        if not has_direct:
            verdict_body += _evidence_gap("direct_proof", "Direct CueIdea evidence is missing; keep this run in research_more or sandbox mode.")

        primary_icp = _first_label(enrichment.icp_segments, "Unknown ICP")
        pain_trigger = _first_summary(enrichment.buying_triggers, "No buying trigger extracted yet.")
        community = _first_label(enrichment.communities, "Unknown prospect source")
        competitor = _first_label(enrichment.competitors, "Unknown alternative")
        pricing_hint = _first_summary(enrichment.pricing_hints, "No pricing or WTP hint imported.")

        icp_body = (
            f"Primary segment: {primary_icp}\n\n"
            f"Why this segment: {pain_trigger}\n\n"
            f"Reachability: start from {community} and verify 10 reachable prospects before build."
        )
        if "icp" in enrichment.evidence_gaps:
            icp_body += _evidence_gap("icp", enrichment.evidence_gaps["icp"])

        competitor_body = (
            f"Primary alternative: {competitor}\n\n"
            f"Concrete wedge: {_first_summary(enrichment.competitors, debate.recommended_wedge)}\n\n"
            f"Manual/workaround alternatives:\n{_signal_lines(enrichment.alternatives)}"
        )
        if not has_competitor:
            competitor_body += _evidence_gap("competitor_gap", enrichment.evidence_gaps.get("competitor_gap", "No competitor complaint or gap evidence was imported; do not claim differentiation yet."))

        outreach_body = (
            f"Draft only. Open with the observed pain: {pain_trigger}\n\n"
            f"Ask {primary_icp} for a 10 minute discovery conversation about {idea}. "
            "Reference only verified public evidence, avoid false personalization, and include opt-out language such as: Reply stop if not relevant."
        )

        landing_body = (
            f"Headline: Stop {pain_trigger.lower()}\n\n"
            f"Subheadline: For {primary_icp} who need a focused fix for {idea} without switching blindly from {competitor}.\n\n"
            "CTA: Join the 7-day validation pilot."
        )

        roadmap_body = (
            f"Day 1: extract 10 prospects from {community} and log source URLs.\n"
            f"Day 2: interview 5 {primary_icp} about the pain trigger and current workaround.\n"
            "Day 3: compare 3 alternatives and write the narrow competitor gap.\n"
            "Day 4: test 2 landing headlines tied to the strongest direct pain quote.\n"
            "Day 5: ask 5 prospects for a paid pilot or exact budget range.\n"
            "Day 6: summarize top 3 objections and update positioning.\n"
            "Day 7: decide build / pivot / niche_down / kill using WTP, ICP reachability, and competitor gap evidence."
        )

        watchlist_body = (
            f"Competitors:\n{_signal_lines(enrichment.competitors)}\n\n"
            f"Communities/prospect sources:\n{_signal_lines(enrichment.communities)}\n\n"
            f"Objections:\n{_signal_lines(enrichment.objections)}\n\n"
            f"Research questions:\n" + "\n".join(f"- {question}" for question in enrichment.recommended_research_questions)
        )
        if "communities" in enrichment.evidence_gaps:
            watchlist_body += _evidence_gap("communities", enrichment.evidence_gaps["communities"])

        prospect_sources_body = (
            f"Primary source: {community}\n\n"
            f"Specific sources:\n{_signal_lines(enrichment.communities)}"
        )
        if "communities" in enrichment.evidence_gaps:
            prospect_sources_body += _evidence_gap("communities", enrichment.evidence_gaps["communities"])

        decision_rules_body = (
            f"Pricing/WTP signal: {pricing_hint}\n\n"
            "Kill if no direct pain after 5 interviews. Pivot if pain exists but WTP stays weak. "
            "Build only if WTP, reachable ICP, and a concrete competitor gap are proven."
        )
        if not has_wtp:
            decision_rules_body += _evidence_gap("wtp", enrichment.evidence_gaps.get("wtp", "CueIdea did not provide paid-intent, pricing, budget, or willingness-to-pay evidence."))

        sections = [
            _section("00_VERDICT.md", "Executive Verdict", verdict_body, refs),
            _section("01_EVIDENCE.md", "Evidence", _evidence_summary(evidence), refs),
            _section("02_ICP.md", "ICP", icp_body, icp_refs),
            _section("03_COMPETITOR_GAPS.md", "Competitor Gaps", competitor_body, competitor_refs),
            _section("04_LANDING_PAGE_COPY.md", "Landing Page Copy", landing_body, trigger_refs),
            _section("05_OUTREACH_MESSAGES.md", "Outreach Messages", outreach_body, trigger_refs),
            _section("06_INTERVIEW_SCRIPT.md", "Interview Script", "Ask about current workaround, cost of the pain, existing alternatives, urgency, and willingness to pay.", refs),
            _section("07_7_DAY_ROADMAP.md", "7-Day Validation Roadmap", roadmap_body, refs),
            _section("08_WATCHLIST.md", "Watchlist", watchlist_body, refs),
            _section("09_DECISION_RULES.md", "Decision Rules", decision_rules_body, pricing_refs),
            _section("10_PROSPECT_SOURCES.md", "Prospect Sources", prospect_sources_body, community_refs),
        ]
        return GTMPack(slug=slugify(idea), idea=idea, sections=sections, evidence_refs=refs)

    def actions_for_pack(self, pack: GTMPack) -> list[AgentAction]:
        base = str(PurePosixPath(self.output_root) / pack.slug)
        actions = [
            AgentAction(
                tool="create_folder",
                intent="Create generated project folder for GTM Pack",
                input={"path": base},
                expected_output="Project folder exists",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                evidence_refs=pack.evidence_refs,
                approval_status=ApprovalStatus.NOT_REQUIRED,
            )
        ]
        for section in pack.sections:
            actions.append(AgentAction(
                tool="create_file",
                intent=f"Write {section.title} GTM Pack section",
                input={"path": str(PurePosixPath(base) / section.filename), "content": section.content},
                expected_output=f"{section.filename} created",
                risk_level=RiskLevel.LOW,
                requires_approval=False,
                evidence_refs=section.evidence_refs,
                approval_status=ApprovalStatus.NOT_REQUIRED,
            ))
        actions.append(AgentAction(
            tool="prepare_email_draft",
            intent="Prepare outreach draft for user approval",
            input={
                "subject": f"Quick question about {pack.idea}",
                "body": "Draft only: I am validating a focused workflow problem and would value your perspective. Reply stop if not relevant.",
            },
            expected_output="Email draft object, not sent",
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
            evidence_refs=pack.evidence_refs,
            approval_status=ApprovalStatus.PENDING,
        ))
        return actions
