from __future__ import annotations

import re
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field

from sentinel.shared.enums import EvidenceType
from sentinel.shared.models import EvidenceItem


class EnrichedSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    summary: str
    evidence_refs: list[str] = Field(default_factory=list)


class ResearchEnrichmentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    competitors: list[EnrichedSignal] = Field(default_factory=list)
    alternatives: list[EnrichedSignal] = Field(default_factory=list)
    icp_segments: list[EnrichedSignal] = Field(default_factory=list)
    communities: list[EnrichedSignal] = Field(default_factory=list)
    objections: list[EnrichedSignal] = Field(default_factory=list)
    buying_triggers: list[EnrichedSignal] = Field(default_factory=list)
    pricing_hints: list[EnrichedSignal] = Field(default_factory=list)
    evidence_gaps: dict[str, str] = Field(default_factory=dict)
    recommended_research_questions: list[str] = Field(default_factory=list)


GENERIC_SEGMENTS = {
    "businesses",
    "startups",
    "founders",
    "creators",
    "users",
    "teams",
    "companies",
}


ICP_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bfreelance (brand and web |brand |web )?designers?\b", "freelance designers"),
    (r"\bsolo design studios?\b", "solo design studios"),
    (r"\bsmall design agencies?\b", "small design agencies"),
    (r"\bagency owners?\b", "agency owners"),
    (r"\bindependent consultants?\b", "independent consultants"),
    (r"\bsolo consultants?\b", "solo consultants"),
    (r"\bcreator operators?\b", "creator operators"),
    (r"\bnewsletter creators?\b", "newsletter creators"),
    (r"\bfreelancers?\b", "freelancers"),
)

COMMUNITY_TOKENS = ("reddit", "subreddit", "forum", "discord", "slack", "community", "linkedin", "hn")
OBJECTION_TOKENS = ("too heavy", "too generic", "robotic", "awkward", "ignored", "privacy", "expensive", "trust", "not tied", "lack", "missing")
WORKAROUND_TOKENS = ("manual", "spreadsheet", "template", "checklist", "email", "docs", "project management", "pm tools", "client portal")
TRIGGER_TOKENS = ("would pay", "ready to pay", "budget", "late", "overdue", "launch delay", "missing", "manual", "hours", "awkward", "urgent")


def _raw(item: EvidenceItem) -> dict:
    value = item.metadata.get("raw")
    return value if isinstance(value, dict) else {}


def _text(*values: object) -> str:
    return " ".join(str(value or "").strip() for value in values if str(value or "").strip())


def _combined_text(item: EvidenceItem) -> str:
    raw = _raw(item)
    return _text(
        item.summary,
        item.quote,
        item.source,
        item.url,
        item.metadata.get("title"),
        raw.get("title"),
        raw.get("post_title"),
        raw.get("summary"),
        raw.get("quote"),
        raw.get("source"),
        raw.get("platform"),
        raw.get("subreddit"),
        raw.get("community"),
        raw.get("segment"),
        raw.get("icp_segment"),
    )


def _label_from(item: EvidenceItem, *keys: str, fallback: str | None = None) -> str:
    raw = _raw(item)
    for key in keys:
        value = raw.get(key)
        if value:
            return str(value).strip()
    return fallback or str(item.metadata.get("title") or item.source).strip()


def _append_unique(signals: list[EnrichedSignal], label: str, summary: str, evidence_ref: str) -> None:
    normalized = label.strip()
    if not normalized:
        return
    for signal in signals:
        if signal.label.lower() == normalized.lower():
            if evidence_ref not in signal.evidence_refs:
                signal.evidence_refs.append(evidence_ref)
            return
    signals.append(EnrichedSignal(label=normalized, summary=summary.strip(), evidence_refs=[evidence_ref]))


def _segment_is_specific(label: str) -> bool:
    normalized = re.sub(r"[^a-z0-9 ]+", " ", label.lower()).strip()
    if normalized in GENERIC_SEGMENTS:
        return False
    return len(normalized.split()) >= 2 or any(token in normalized for token in ("freelance", "agency", "consultant", "designer"))


def _infer_icp_segments(item: EvidenceItem) -> Iterable[str]:
    raw = _raw(item)
    for key in ("icp_segment", "segment", "customer_segment", "audience", "persona"):
        value = raw.get(key)
        if value:
            yield str(value)

    text = _combined_text(item).lower()
    for pattern, label in ICP_PATTERNS:
        if re.search(pattern, text):
            yield label


def _extract_price_hints(text: str) -> list[str]:
    return re.findall(r"\$\s?\d+(?:\s?-\s?\$?\d+)?(?:\s?/(?:mo|month))?", text, flags=re.IGNORECASE)


def enrich_research(evidence: list[EvidenceItem]) -> ResearchEnrichmentResult:
    result = ResearchEnrichmentResult()

    for item in evidence:
        text = _combined_text(item)
        lowered = text.lower()
        raw = _raw(item)

        has_named_competitor = any(raw.get(key) for key in ("competitor", "name", "alternative"))
        has_competitor_language = "competitor" in lowered or "alternative" in lowered
        if item.evidence_type == EvidenceType.COMPETITOR_COMPLAINT or has_named_competitor or has_competitor_language:
            label = _label_from(item, "competitor", "name", "alternative", fallback=str(raw.get("source") or item.source))
            _append_unique(result.competitors, label, item.summary, item.id)

        if any(token in lowered for token in WORKAROUND_TOKENS) or item.evidence_type == EvidenceType.COMPETITOR_COMPLAINT:
            label = _label_from(item, "workaround", "alternative", "title", fallback="Manual workaround")
            _append_unique(result.alternatives, label, item.summary, item.id)

        for segment in _infer_icp_segments(item):
            _append_unique(result.icp_segments, segment, item.summary, item.id)

        if any(token in lowered for token in COMMUNITY_TOKENS):
            community = str(raw.get("subreddit") or raw.get("community") or raw.get("source") or item.source)
            if community.lower() == "reddit" and raw.get("subreddit"):
                community = f"r/{raw['subreddit']}"
            _append_unique(result.communities, community, item.summary, item.id)

        if any(token in lowered for token in OBJECTION_TOKENS):
            label = _label_from(item, "objection", "title", fallback="Objection signal")
            _append_unique(result.objections, label, item.summary, item.id)

        if item.evidence_type in {EvidenceType.PAIN, EvidenceType.WTP, EvidenceType.PRICING, EvidenceType.DIRECT_PROOF} or any(token in lowered for token in TRIGGER_TOKENS):
            label = _label_from(item, "buying_trigger", "title", fallback="Buying trigger")
            _append_unique(result.buying_triggers, label, item.summary, item.id)

        if item.evidence_type in {EvidenceType.WTP, EvidenceType.PRICING}:
            hints = _extract_price_hints(text)
            label = ", ".join(hints) if hints else "Pricing/WTP hint"
            _append_unique(result.pricing_hints, label, item.summary, item.id)

    has_direct = any(item.metadata.get("proof_tier") == "direct" for item in evidence)
    has_wtp = any(item.evidence_type in {EvidenceType.WTP, EvidenceType.PRICING} for item in evidence)
    has_competitor = bool(result.competitors)
    has_specific_icp = any(_segment_is_specific(signal.label) for signal in result.icp_segments)

    if not has_direct:
        result.evidence_gaps["direct_proof"] = "No direct CueIdea proof was imported."
    if not has_wtp:
        result.evidence_gaps["wtp"] = "No WTP, pricing, budget, or paid-intent evidence was imported."
    if not has_competitor:
        result.evidence_gaps["competitor_gap"] = "No competitor alternative or competitor complaint was imported."
    if not has_specific_icp:
        result.evidence_gaps["icp"] = "ICP is too broad or missing; name a reachable buyer segment."
    if not result.communities:
        result.evidence_gaps["communities"] = "No reachable community or prospect source was imported."
    if not result.buying_triggers:
        result.evidence_gaps["buying_triggers"] = "No concrete buying trigger was extracted."

    questions: list[str] = []
    if "wtp" in result.evidence_gaps:
        questions.append("Who has budget for this pain, and what exact price or paid pilot would they accept?")
    if "competitor_gap" in result.evidence_gaps:
        questions.append("Which current alternative is used today, and what repeated complaint creates the wedge?")
    if "icp" in result.evidence_gaps:
        questions.append("Which specific buyer segment repeats the pain and can be reached this week?")
    if "communities" in result.evidence_gaps:
        questions.append("Where can 10 reachable prospects be found without scraping private data?")
    if not questions:
        questions.append("What objection would prevent this ICP from joining a paid validation pilot this week?")
    result.recommended_research_questions = questions

    return result
