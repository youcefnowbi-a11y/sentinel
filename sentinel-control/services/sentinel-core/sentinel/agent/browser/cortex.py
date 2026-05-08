from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any

from pydantic import Field

from sentinel.agent.events import AgentEventType
from sentinel.agent.evidence import (
    ContradictionRef,
    EvidenceChain,
    EvidenceClaim,
    EvidenceDecisionType,
    EvidenceRef,
    EvidenceSourceType,
    EvidenceVerdict,
)
from sentinel.agent.models import ReviewFinding
from sentinel.agent.phases import AgentPhase
from sentinel.shared.models import SentinelModel, new_id

if TYPE_CHECKING:
    from sentinel.agent.event_bus import EventBus
    from sentinel.agent.hypothesis import MissionHypothesis
    from sentinel.agent.models import AgentContext, AgentEvent


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


class BrowserCortexSourceKind(StrEnum):
    EVIDENCE = "browser_evidence"
    SNAPSHOT = "browser_snapshot"
    INTERACTION_PLAN = "browser_interaction_plan"
    INTERACTION_EXECUTION = "browser_interaction_execution"
    FORM_SUBMIT = "browser_v3_form_submit"
    DOWNLOAD_QUARANTINE = "browser_v3_download_quarantine"
    UPLOAD_AUTHORIZED = "browser_v3_upload_authorized"
    PRIVATE_SESSION = "browser_v3_private_session"
    LOGIN_AUTHORITY = "browser_v3_login_authority"
    COOKIE_STORAGE = "browser_v3_cookie_storage"
    JS_SANDBOX = "browser_v3_js_sandbox"
    HAR_BODY = "browser_v3_har_body"
    VERIFICATION = "browser_verification"
    LOOP_DETECTED = "browser_loop_detected"
    REJECTION = "browser_rejection"


class BrowserHypothesisEffect(StrEnum):
    CONFIRM = "confirm"
    WEAKEN = "weaken"
    NEEDS_ALTERNATIVE_EVIDENCE = "needs_alternative_evidence"
    NO_CHANGE = "no_change"


class BrowserActionRecommendationType(StrEnum):
    USE_AS_EVIDENCE = "use_as_evidence"
    SEEK_ALTERNATIVE_SOURCE = "seek_alternative_source"
    CREATE_INTERACTION_PLAN = "create_interaction_plan"
    TREAT_INTERACTION_AS_PROGRESS = "treat_interaction_as_progress"
    DO_NOT_USE_FOR_AUTHORITY = "do_not_use_for_authority"


class BrowserSourceConfidenceScore(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("bcscore"))
    mission_id: str
    source_trace_id: str
    source_kind: BrowserCortexSourceKind
    score: float = Field(ge=0.0, le=1.0)
    source_quality: float = Field(ge=0.0, le=1.0)
    citation_validity: float = Field(ge=0.0, le=1.0)
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    freshness: float = Field(ge=0.0, le=1.0)
    contradiction_status: float = Field(ge=0.0, le=1.0)
    prompt_injection_penalty: float = Field(ge=0.0, le=1.0)
    flags: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class BrowserHypothesisUpdate(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("bchyp"))
    mission_id: str
    hypothesis_id: str
    source_trace_id: str
    effect: BrowserHypothesisEffect
    confidence_delta: float
    confidence_after: float = Field(ge=0.0, le=1.0)
    reason: str
    evidence_refs: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class BrowserRepairDecision(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("bcrepair"))
    mission_id: str
    repair_needed: bool
    pressure: float = Field(ge=0.0, le=1.0)
    reason: str
    target_trace_id: str | None = None
    recommended_action: str
    trace_refs: list[str] = Field(default_factory=list)


class BrowserActionRecommendation(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("bcact"))
    mission_id: str
    recommendation: BrowserActionRecommendationType
    source_trace_id: str | None = None
    impact_score: float = Field(ge=0.0, le=1.0)
    reason: str
    evidence_refs: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class BrowserCortexInterpretation(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("bcortex"))
    mission_id: str
    browser_signal_count: int = Field(ge=0)
    source_scores: list[BrowserSourceConfidenceScore] = Field(default_factory=list)
    hypothesis_updates: list[BrowserHypothesisUpdate] = Field(default_factory=list)
    repair_decisions: list[BrowserRepairDecision] = Field(default_factory=list)
    action_recommendations: list[BrowserActionRecommendation] = Field(default_factory=list)
    review_findings: list[ReviewFinding] = Field(default_factory=list)
    evidence_chain: EvidenceChain | None = None
    trace_refs: list[str] = Field(default_factory=list)


class BrowserEvidenceInterpreter:
    """Maps browser output into cognitive signals.

    P3X is deterministic. It does not fetch pages, open browser sessions, call an
    LLM, or create authority. It reads browser trace events already produced by
    Browser V2 and converts them into evidence strength, hypothesis deltas,
    repair pressure, and action recommendations.
    """

    ACCEPTED_EVENTS = {
        AgentEventType.BROWSER_EVIDENCE_COLLECTED,
        AgentEventType.BROWSER_SNAPSHOT_CAPTURED,
        AgentEventType.BROWSER_INTERACTION_PLAN_CREATED,
        AgentEventType.BROWSER_INTERACTION_EXECUTED,
        AgentEventType.BROWSER_FORM_SUBMIT_EXECUTED,
        AgentEventType.BROWSER_DOWNLOAD_QUARANTINED,
        AgentEventType.BROWSER_UPLOAD_AUTHORIZED_EXECUTED,
        AgentEventType.BROWSER_PRIVATE_SESSION_STARTED,
        AgentEventType.BROWSER_PRIVATE_SESSION_CLOSED,
        AgentEventType.BROWSER_LOGIN_AUTHORITY_EXECUTED,
        AgentEventType.BROWSER_COOKIE_STORAGE_CONTRACT_APPLIED,
        AgentEventType.BROWSER_JS_EVALUATE_SANDBOXED_EXECUTED,
        AgentEventType.BROWSER_HAR_BODY_CAPTURED,
        AgentEventType.BROWSER_VERIFICATION_COMPLETED,
    }
    REJECTION_EVENTS = {
        AgentEventType.BROWSER_EVIDENCE_REJECTED,
        AgentEventType.BROWSER_SNAPSHOT_REJECTED,
        AgentEventType.BROWSER_INTERACTION_REJECTED,
        AgentEventType.BROWSER_PUBLIC_LIFECYCLE_REJECTED,
        AgentEventType.BROWSER_SUPERVISOR_REJECTED,
        AgentEventType.BROWSER_FORM_SUBMIT_REJECTED,
        AgentEventType.BROWSER_DOWNLOAD_REJECTED,
        AgentEventType.BROWSER_UPLOAD_AUTHORIZED_REJECTED,
        AgentEventType.BROWSER_PRIVATE_SESSION_REJECTED,
        AgentEventType.BROWSER_LOGIN_AUTHORITY_REJECTED,
        AgentEventType.BROWSER_COOKIE_STORAGE_CONTRACT_REJECTED,
        AgentEventType.BROWSER_JS_EVALUATE_SANDBOXED_REJECTED,
        AgentEventType.BROWSER_HAR_BODY_CAPTURE_REJECTED,
        AgentEventType.BROWSER_LOOP_DETECTED,
    }

    def interpret(
        self,
        context: AgentContext,
        trace: list[AgentEvent] | tuple[AgentEvent, ...],
        *,
        hypotheses: list[MissionHypothesis] | None = None,
        event_bus: EventBus | None = None,
    ) -> BrowserCortexInterpretation:
        browser_events = [event for event in trace if event.event_type in self.ACCEPTED_EVENTS or event.event_type in self.REJECTION_EVENTS]
        scores = [self._score_event(context, event) for event in browser_events]
        hypothesis_updates = self._hypothesis_updates(context, hypotheses or [], browser_events, scores)
        repairs = self._repair_decisions(context, browser_events, scores)
        recommendations = self._action_recommendations(context, browser_events, scores)
        review_findings = self._review_findings(context, repairs, scores)
        interpretation = BrowserCortexInterpretation(
            mission_id=context.mission.id,
            browser_signal_count=len(browser_events),
            source_scores=scores,
            hypothesis_updates=hypothesis_updates,
            repair_decisions=repairs,
            action_recommendations=recommendations,
            review_findings=review_findings,
            evidence_chain=self._evidence_chain(context, browser_events, scores, hypothesis_updates, repairs),
            trace_refs=[event.id for event in browser_events],
        )
        if event_bus is None or not browser_events:
            return interpretation

        event = event_bus.append(
            AgentEventType.BROWSER_CORTEX_INTERPRETED,
            "Browser outputs interpreted into cognitive evidence signals.",
            phase_before=AgentPhase.EXECUTING,
            phase_after=AgentPhase.EXECUTING,
            payload={
                "interpretation_id": interpretation.id,
                "browser_signal_count": interpretation.browser_signal_count,
                "source_score_ids": [score.id for score in scores],
                "hypothesis_update_ids": [update.id for update in hypothesis_updates],
                "repair_decision_ids": [decision.id for decision in repairs],
                "action_recommendation_ids": [item.id for item in recommendations],
                "review_finding_codes": [finding.code for finding in review_findings],
                "evidence_chain_id": interpretation.evidence_chain.id if interpretation.evidence_chain else None,
            },
            trace_refs=interpretation.trace_refs,
        )
        chain = interpretation.evidence_chain
        if chain is not None:
            chain_event = event_bus.append(
                AgentEventType.EVIDENCE_CHAIN_BUILT,
                "Evidence chain built for browser cortex interpretation.",
                phase_before=AgentPhase.EXECUTING,
                phase_after=AgentPhase.EXECUTING,
                payload={
                    "chain_id": chain.id,
                    "decision_type": chain.decision_type,
                    "claim_id": chain.claim.id,
                    "verdict": chain.verdict,
                    "confidence": chain.confidence,
                    "evidence_ref_ids": [ref.id for ref in chain.evidence],
                    "contradiction_ids": [ref.id for ref in chain.contradictions],
                },
                trace_refs=[*interpretation.trace_refs, event.id],
            )
            chain = chain.model_copy(update={"trace_refs": [*chain.trace_refs, event.id, chain_event.id]})
        return interpretation.model_copy(update={"trace_refs": [*interpretation.trace_refs, event.id], "evidence_chain": chain})

    def _score_event(self, context: AgentContext, event: AgentEvent) -> BrowserSourceConfidenceScore:
        payload = event.payload
        kind = self._source_kind(event)
        flags = sorted(set([*self._list(payload.get("source_quality_flags")), *self._list(payload.get("prompt_injection_flags"))]))
        prompt_flags = self._list(payload.get("prompt_injection_flags"))
        source_quality = self._source_quality(flags)
        citation_validity = self._citation_validity(kind, payload)
        extraction_confidence = self._extraction_confidence(kind, payload)
        freshness = 0.75 if event.event_type in self.ACCEPTED_EVENTS else 0.25
        if self._is_successful_protective_rejection(event):
            freshness = 0.80
        contradiction_status = self._contradiction_status(kind, payload)
        prompt_penalty = min(0.45, 0.18 * len(prompt_flags))
        score = _clamp01(
            (0.30 * source_quality)
            + (0.20 * citation_validity)
            + (0.20 * extraction_confidence)
            + (0.15 * freshness)
            + (0.15 * contradiction_status)
            - prompt_penalty
        )
        reasons = self._score_reasons(kind, payload, flags, score)
        if prompt_flags:
            score = min(score, 0.45)
            reasons.append("prompt_injection_content_is_evidence_only")
        if event.event_type in self.REJECTION_EVENTS and not self._is_successful_protective_rejection(event):
            score = min(score, 0.20)
            reasons.append("browser_output_rejected_before_acceptance")
        if self._is_successful_protective_rejection(event):
            score = max(score, 0.62)
            reasons.append("protective_browser_rejection_is_security_signal")
        return BrowserSourceConfidenceScore(
            mission_id=context.mission.id,
            source_trace_id=event.id,
            source_kind=kind,
            score=round(score, 6),
            source_quality=round(source_quality, 6),
            citation_validity=round(citation_validity, 6),
            extraction_confidence=round(extraction_confidence, 6),
            freshness=round(freshness, 6),
            contradiction_status=round(contradiction_status, 6),
            prompt_injection_penalty=round(prompt_penalty, 6),
            flags=flags,
            reasons=reasons,
            trace_refs=[event.id],
        )

    def _hypothesis_updates(
        self,
        context: AgentContext,
        hypotheses: list[MissionHypothesis],
        events: list[AgentEvent],
        scores: list[BrowserSourceConfidenceScore],
    ) -> list[BrowserHypothesisUpdate]:
        updates: list[BrowserHypothesisUpdate] = []
        score_by_trace = {score.source_trace_id: score for score in scores}
        for event in events:
            score = score_by_trace[event.id]
            matched = [hypothesis for hypothesis in hypotheses if self._hypothesis_matches_event(hypothesis, event)]
            for hypothesis in matched:
                if score.score >= 0.72:
                    effect = BrowserHypothesisEffect.CONFIRM
                    delta = 0.15
                    reason = "browser_source_supports_linked_hypothesis"
                elif score.score <= 0.35:
                    effect = BrowserHypothesisEffect.NEEDS_ALTERNATIVE_EVIDENCE
                    delta = -0.12
                    reason = "browser_source_too_weak_for_hypothesis_promotion"
                else:
                    effect = BrowserHypothesisEffect.WEAKEN
                    delta = -0.05
                    reason = "browser_source_inconclusive_for_linked_hypothesis"
                updates.append(
                    BrowserHypothesisUpdate(
                        mission_id=context.mission.id,
                        hypothesis_id=hypothesis.id,
                        source_trace_id=event.id,
                        effect=effect,
                        confidence_delta=round(delta, 6),
                        confidence_after=round(_clamp01(hypothesis.confidence + delta), 6),
                        reason=reason,
                        evidence_refs=self._event_refs(event),
                        trace_refs=[event.id, *hypothesis.trace_refs],
                    )
                )
        return updates

    def _repair_decisions(
        self,
        context: AgentContext,
        events: list[AgentEvent],
        scores: list[BrowserSourceConfidenceScore],
    ) -> list[BrowserRepairDecision]:
        decisions: list[BrowserRepairDecision] = []
        for event, score in zip(events, scores, strict=True):
            payload = event.payload
            if event.event_type in self.REJECTION_EVENTS:
                if self._is_successful_protective_rejection(event):
                    decisions.append(
                        BrowserRepairDecision(
                            mission_id=context.mission.id,
                            repair_needed=True,
                            pressure=0.60,
                            reason="browser_js_network_attempt_blocked",
                            target_trace_id=event.id,
                            recommended_action="keep_js_rejected_and_review_script_or_use_non_js_path",
                            trace_refs=[event.id],
                        )
                    )
                    continue
                if event.event_type == AgentEventType.BROWSER_LOOP_DETECTED:
                    decisions.append(
                        BrowserRepairDecision(
                            mission_id=context.mission.id,
                            repair_needed=True,
                            pressure=0.75,
                            reason="browser_loop_detected",
                            target_trace_id=event.id,
                            recommended_action="change_strategy_or_stop_repeating_browser_action",
                            trace_refs=[event.id],
                        )
                    )
                    continue
                decisions.append(
                    BrowserRepairDecision(
                        mission_id=context.mission.id,
                        repair_needed=True,
                        pressure=0.70,
                        reason=f"browser_output_rejected:{payload.get('reason', 'unknown')}",
                        target_trace_id=event.id,
                        recommended_action="seek_alternative_public_source_or_recapture",
                        trace_refs=[event.id],
                    )
                )
                continue
            if score.score <= 0.35:
                decisions.append(
                    BrowserRepairDecision(
                        mission_id=context.mission.id,
                        repair_needed=True,
                        pressure=0.55,
                        reason="browser_source_confidence_low",
                        target_trace_id=event.id,
                        recommended_action="seek_alternative_public_source",
                        trace_refs=[event.id],
                    )
                )
                continue
            if self._list(payload.get("prompt_injection_flags")):
                decisions.append(
                    BrowserRepairDecision(
                        mission_id=context.mission.id,
                        repair_needed=True,
                        pressure=0.45,
                        reason="browser_prompt_injection_flags_limit_confidence",
                        target_trace_id=event.id,
                        recommended_action="summarize_as_untrusted_evidence_and_cross_check",
                        trace_refs=[event.id],
                    )
                )
        if not decisions and events:
            best_score = max((score.score for score in scores), default=0.0)
            decisions.append(
                BrowserRepairDecision(
                    mission_id=context.mission.id,
                    repair_needed=False,
                    pressure=round(max(0.0, 0.30 - best_score), 6),
                    reason="browser_sources_sufficient_for_current_scope",
                    target_trace_id=max(scores, key=lambda item: item.score).source_trace_id,
                    recommended_action="use_browser_evidence_in_reasoning",
                    trace_refs=[score.source_trace_id for score in scores],
                )
            )
        return decisions

    def _action_recommendations(
        self,
        context: AgentContext,
        events: list[AgentEvent],
        scores: list[BrowserSourceConfidenceScore],
    ) -> list[BrowserActionRecommendation]:
        if not events:
            return [
                BrowserActionRecommendation(
                    mission_id=context.mission.id,
                    recommendation=BrowserActionRecommendationType.CREATE_INTERACTION_PLAN
                    if "public_web" in context.mission.allowed_systems
                    else BrowserActionRecommendationType.DO_NOT_USE_FOR_AUTHORITY,
                    impact_score=0.20,
                    reason="no_browser_output_available_for_reasoning",
                )
            ]

        recommendations: list[BrowserActionRecommendation] = []
        for event, score in zip(events, scores, strict=True):
            if event.event_type == AgentEventType.BROWSER_FORM_SUBMIT_EXECUTED and score.score >= 0.50:
                rec = BrowserActionRecommendationType.TREAT_INTERACTION_AS_PROGRESS
                reason = "browser_v3_form_submit_finalgate_eligible_progress_signal"
                impact = 0.78
            elif event.event_type == AgentEventType.BROWSER_DOWNLOAD_QUARANTINED:
                rec = BrowserActionRecommendationType.USE_AS_EVIDENCE
                reason = "download_quarantine_artifact_available_not_promoted_trust"
                impact = 0.45
            elif event.event_type == AgentEventType.BROWSER_UPLOAD_AUTHORIZED_EXECUTED:
                rec = BrowserActionRecommendationType.TREAT_INTERACTION_AS_PROGRESS
                reason = "authorized_upload_outbound_artifact_side_effect_completed"
                impact = 0.68
            elif event.event_type in {AgentEventType.BROWSER_PRIVATE_SESSION_STARTED, AgentEventType.BROWSER_PRIVATE_SESSION_CLOSED}:
                rec = BrowserActionRecommendationType.DO_NOT_USE_FOR_AUTHORITY
                reason = "private_session_is_scoped_runtime_state_not_evidence_truth"
                impact = 0.30
            elif event.event_type == AgentEventType.BROWSER_LOGIN_AUTHORITY_EXECUTED:
                rec = BrowserActionRecommendationType.TREAT_INTERACTION_AS_PROGRESS
                reason = "login_success_authenticated_state_no_credential_evidence"
                impact = 0.58
            elif event.event_type == AgentEventType.BROWSER_COOKIE_STORAGE_CONTRACT_APPLIED:
                rec = BrowserActionRecommendationType.DO_NOT_USE_FOR_AUTHORITY
                reason = "cookie_storage_summary_is_tainted_redacted_session_metadata"
                impact = 0.34
            elif event.event_type == AgentEventType.BROWSER_JS_EVALUATE_SANDBOXED_REJECTED and self._is_successful_protective_rejection(event):
                rec = BrowserActionRecommendationType.SEEK_ALTERNATIVE_SOURCE
                reason = "sandboxed_js_network_attempt_blocked_repair_signal"
                impact = 0.62
            elif event.event_type == AgentEventType.BROWSER_HAR_BODY_CAPTURED:
                rec = BrowserActionRecommendationType.USE_AS_EVIDENCE
                reason = "har_body_redacted_diagnostic_artifact_only"
                impact = 0.50
            elif event.event_type == AgentEventType.BROWSER_INTERACTION_EXECUTED and score.score >= 0.50:
                rec = BrowserActionRecommendationType.TREAT_INTERACTION_AS_PROGRESS
                reason = "limited_interaction_has_before_after_receipt"
                impact = 0.75
            elif score.score >= 0.72:
                rec = BrowserActionRecommendationType.USE_AS_EVIDENCE
                reason = "browser_source_confidence_high_enough_for_evidence_chain"
                impact = 0.65
            elif score.score <= 0.35:
                rec = BrowserActionRecommendationType.SEEK_ALTERNATIVE_SOURCE
                reason = "browser_source_confidence_low"
                impact = 0.55
            else:
                rec = BrowserActionRecommendationType.DO_NOT_USE_FOR_AUTHORITY
                reason = "browser_source_is_supporting_evidence_only"
                impact = 0.35
            recommendations.append(
                BrowserActionRecommendation(
                    mission_id=context.mission.id,
                    recommendation=rec,
                    source_trace_id=event.id,
                    impact_score=impact,
                    reason=reason,
                    evidence_refs=self._event_refs(event),
                    trace_refs=[event.id],
                )
            )
        return recommendations

    def _review_findings(
        self,
        context: AgentContext,
        repairs: list[BrowserRepairDecision],
        scores: list[BrowserSourceConfidenceScore],
    ) -> list[ReviewFinding]:
        findings: list[ReviewFinding] = []
        for repair in repairs:
            if not repair.repair_needed:
                continue
            severity = "high" if repair.pressure >= 0.65 else "medium"
            findings.append(
                ReviewFinding(
                    code=f"browser_cortex_{repair.reason.split(':', 1)[0]}",
                    severity=severity,
                    message=f"Browser cortex requires follow-up: {repair.recommended_action}.",
                    trace_refs=repair.trace_refs,
                )
            )
        for score in scores:
            if score.prompt_injection_penalty:
                findings.append(
                    ReviewFinding(
                        code="browser_cortex_prompt_injection_evidence_only",
                        severity="medium",
                        message="Browser page text contains instruction-like content and must remain evidence-only.",
                        trace_refs=score.trace_refs,
                    )
                )
        return list({finding.code: finding for finding in findings}.values())

    def _evidence_chain(
        self,
        context: AgentContext,
        events: list[AgentEvent],
        scores: list[BrowserSourceConfidenceScore],
        updates: list[BrowserHypothesisUpdate],
        repairs: list[BrowserRepairDecision],
    ) -> EvidenceChain | None:
        if not events:
            return None
        avg_score = sum(score.score for score in scores) / len(scores)
        repair_needed = any(item.repair_needed for item in repairs)
        if repair_needed and avg_score <= 0.35:
            verdict = EvidenceVerdict.INCONCLUSIVE
        elif repair_needed:
            verdict = EvidenceVerdict.SUPPORTED
        else:
            verdict = EvidenceVerdict.SUPPORTED if avg_score >= 0.50 else EvidenceVerdict.INCONCLUSIVE
        return EvidenceChain(
            mission_id=context.mission.id,
            decision_type=EvidenceDecisionType.BROWSER_CORTEX_INTERPRETATION,
            claim=EvidenceClaim(
                mission_id=context.mission.id,
                decision_type=EvidenceDecisionType.BROWSER_CORTEX_INTERPRETATION,
                subject="browser_cortex",
                statement="Browser outputs are interpreted as evidence signals, not as mission authority.",
                confidence=round(avg_score, 6),
            ),
            evidence=[
                EvidenceRef(
                    source_type=EvidenceSourceType.BROWSER_OUTPUT,
                    ref=event.id,
                    summary=f"{event.event_type.value} score={score.score}.",
                    confidence=score.score,
                    trace_refs=[event.id],
                )
                for event, score in zip(events, scores, strict=True)
            ],
            contradictions=[
                ContradictionRef(
                    ref=repair.target_trace_id or repair.id,
                    summary=repair.reason,
                    severity="high" if repair.pressure >= 0.65 else "medium",
                    trace_refs=repair.trace_refs,
                )
                for repair in repairs
                if repair.repair_needed
            ],
            verdict=verdict,
            confidence=round(avg_score, 6),
            trace_refs=[event.id for event in events],
        )

    @staticmethod
    def _source_kind(event: AgentEvent) -> BrowserCortexSourceKind:
        mapping = {
            AgentEventType.BROWSER_EVIDENCE_COLLECTED: BrowserCortexSourceKind.EVIDENCE,
            AgentEventType.BROWSER_SNAPSHOT_CAPTURED: BrowserCortexSourceKind.SNAPSHOT,
            AgentEventType.BROWSER_INTERACTION_PLAN_CREATED: BrowserCortexSourceKind.INTERACTION_PLAN,
            AgentEventType.BROWSER_INTERACTION_EXECUTED: BrowserCortexSourceKind.INTERACTION_EXECUTION,
            AgentEventType.BROWSER_FORM_SUBMIT_EXECUTED: BrowserCortexSourceKind.FORM_SUBMIT,
            AgentEventType.BROWSER_FORM_SUBMIT_REJECTED: BrowserCortexSourceKind.FORM_SUBMIT,
            AgentEventType.BROWSER_DOWNLOAD_QUARANTINED: BrowserCortexSourceKind.DOWNLOAD_QUARANTINE,
            AgentEventType.BROWSER_DOWNLOAD_REJECTED: BrowserCortexSourceKind.DOWNLOAD_QUARANTINE,
            AgentEventType.BROWSER_UPLOAD_AUTHORIZED_EXECUTED: BrowserCortexSourceKind.UPLOAD_AUTHORIZED,
            AgentEventType.BROWSER_UPLOAD_AUTHORIZED_REJECTED: BrowserCortexSourceKind.UPLOAD_AUTHORIZED,
            AgentEventType.BROWSER_PRIVATE_SESSION_STARTED: BrowserCortexSourceKind.PRIVATE_SESSION,
            AgentEventType.BROWSER_PRIVATE_SESSION_CLOSED: BrowserCortexSourceKind.PRIVATE_SESSION,
            AgentEventType.BROWSER_PRIVATE_SESSION_REJECTED: BrowserCortexSourceKind.PRIVATE_SESSION,
            AgentEventType.BROWSER_LOGIN_AUTHORITY_EXECUTED: BrowserCortexSourceKind.LOGIN_AUTHORITY,
            AgentEventType.BROWSER_LOGIN_AUTHORITY_REJECTED: BrowserCortexSourceKind.LOGIN_AUTHORITY,
            AgentEventType.BROWSER_COOKIE_STORAGE_CONTRACT_APPLIED: BrowserCortexSourceKind.COOKIE_STORAGE,
            AgentEventType.BROWSER_COOKIE_STORAGE_CONTRACT_REJECTED: BrowserCortexSourceKind.COOKIE_STORAGE,
            AgentEventType.BROWSER_JS_EVALUATE_SANDBOXED_EXECUTED: BrowserCortexSourceKind.JS_SANDBOX,
            AgentEventType.BROWSER_JS_EVALUATE_SANDBOXED_REJECTED: BrowserCortexSourceKind.JS_SANDBOX,
            AgentEventType.BROWSER_HAR_BODY_CAPTURED: BrowserCortexSourceKind.HAR_BODY,
            AgentEventType.BROWSER_HAR_BODY_CAPTURE_REJECTED: BrowserCortexSourceKind.HAR_BODY,
            AgentEventType.BROWSER_VERIFICATION_COMPLETED: BrowserCortexSourceKind.VERIFICATION,
            AgentEventType.BROWSER_LOOP_DETECTED: BrowserCortexSourceKind.LOOP_DETECTED,
        }
        return mapping.get(event.event_type, BrowserCortexSourceKind.REJECTION)

    @staticmethod
    def _source_quality(flags: list[str]) -> float:
        penalty_map = {
            "empty_extraction": 0.55,
            "thin_content": 0.25,
            "no_title": 0.10,
            "truncated": 0.10,
            "prompt_injection_detected": 0.35,
        }
        penalty = sum(penalty_map.get(flag, 0.06) for flag in flags)
        return _clamp01(1.0 - penalty)

    @staticmethod
    def _citation_validity(kind: BrowserCortexSourceKind, payload: dict[str, Any]) -> float:
        if isinstance(payload.get("citation_char_start"), int) and isinstance(payload.get("citation_char_end"), int):
            return 0.95
        if int(payload.get("citation_count") or 0) > 0:
            return 0.85
        if kind in {BrowserCortexSourceKind.HAR_BODY, BrowserCortexSourceKind.DOWNLOAD_QUARANTINE}:
            return 0.60 if payload.get("redaction_applied") is True or payload.get("artifact_id") else 0.30
        if kind in {BrowserCortexSourceKind.FORM_SUBMIT, BrowserCortexSourceKind.UPLOAD_AUTHORIZED, BrowserCortexSourceKind.LOGIN_AUTHORITY}:
            return 0.50 if payload.get("receipt_id") else 0.25
        if kind in {BrowserCortexSourceKind.PRIVATE_SESSION, BrowserCortexSourceKind.COOKIE_STORAGE, BrowserCortexSourceKind.JS_SANDBOX}:
            return 0.35
        if kind == BrowserCortexSourceKind.INTERACTION_EXECUTION:
            return 0.65
        if kind == BrowserCortexSourceKind.INTERACTION_PLAN:
            return 0.40
        if kind == BrowserCortexSourceKind.REJECTION:
            return 0.10
        return 0.45

    @staticmethod
    def _extraction_confidence(kind: BrowserCortexSourceKind, payload: dict[str, Any]) -> float:
        if kind == BrowserCortexSourceKind.SNAPSHOT:
            return 0.78
        if kind == BrowserCortexSourceKind.FORM_SUBMIT:
            return 0.82 if payload.get("receipt_id") and payload.get("post_submit_snapshot_artifact_id") else 0.42
        if kind == BrowserCortexSourceKind.DOWNLOAD_QUARANTINE:
            return 0.70 if payload.get("promoted") is False and payload.get("artifact_id") else 0.35
        if kind == BrowserCortexSourceKind.UPLOAD_AUTHORIZED:
            return 0.78 if payload.get("source_artifact_id") and payload.get("post_upload_snapshot_artifact_id") else 0.40
        if kind == BrowserCortexSourceKind.PRIVATE_SESSION:
            return 0.70 if payload.get("destroyed") is True or payload.get("created") is True else 0.35
        if kind == BrowserCortexSourceKind.LOGIN_AUTHORITY:
            return 0.72 if payload.get("login_success") is True and payload.get("account_id") else 0.30
        if kind == BrowserCortexSourceKind.COOKIE_STORAGE:
            return 0.58 if payload.get("redaction_applied") is True and payload.get("raw_value_exposed") is not True else 0.20
        if kind == BrowserCortexSourceKind.JS_SANDBOX:
            return 0.72 if payload.get("network_calls_blocked") is True or payload.get("reason") == "browser_js_evaluate_network_call_detected" else 0.45
        if kind == BrowserCortexSourceKind.HAR_BODY:
            return 0.72 if payload.get("redaction_applied") is True and payload.get("har_artifact_id") else 0.30
        if kind == BrowserCortexSourceKind.VERIFICATION:
            return 0.80 if payload.get("accepted", payload.get("verified", True)) is not False else 0.25
        if kind == BrowserCortexSourceKind.LOOP_DETECTED:
            return 0.20
        if kind == BrowserCortexSourceKind.INTERACTION_EXECUTION:
            return 0.82 if payload.get("same_origin") is True else 0.30
        if kind == BrowserCortexSourceKind.INTERACTION_PLAN:
            return 0.55
        if kind == BrowserCortexSourceKind.REJECTION:
            return 0.10
        strategy = str(payload.get("extraction_strategy") or "")
        return {
            "readability": 0.90,
            "simple_html": 0.78,
            "text_plain": 0.72,
            "json_text": 0.70,
            "fallback": 0.45,
        }.get(strategy, 0.65)

    @staticmethod
    def _contradiction_status(kind: BrowserCortexSourceKind, payload: dict[str, Any]) -> float:
        if kind == BrowserCortexSourceKind.REJECTION:
            return 0.10
        if kind == BrowserCortexSourceKind.LOOP_DETECTED:
            return 0.10
        failures = int(payload.get("network_failure_count") or 0)
        page_errors = int(payload.get("page_error_count") or 0)
        if failures or page_errors:
            return max(0.25, 0.75 - (0.10 * failures) - (0.15 * page_errors))
        return 0.85

    @staticmethod
    def _score_reasons(kind: BrowserCortexSourceKind, payload: dict[str, Any], flags: list[str], score: float) -> list[str]:
        reasons = [f"source_kind={kind.value}"]
        if flags:
            reasons.append(f"flags={','.join(flags)}")
        if payload.get("network_ledger_truncated"):
            reasons.append("network_ledger_truncated")
        if score >= 0.72:
            reasons.append("source_confidence_high")
        elif score <= 0.35:
            reasons.append("source_confidence_low")
        else:
            reasons.append("source_confidence_medium")
        return reasons

    @staticmethod
    def _hypothesis_matches_event(hypothesis: MissionHypothesis, event: AgentEvent) -> bool:
        refs = set(hypothesis.evidence_refs)
        event_refs = set(BrowserEvidenceInterpreter._event_refs(event))
        if refs & event_refs:
            return True
        statement_tokens = BrowserEvidenceInterpreter._tokens(hypothesis.statement)
        payload_text = " ".join(
            str(event.payload.get(key) or "")
            for key in ("title", "final_url", "reason", "evidence_item_id", "receipt_id", "artifact_id")
        )
        payload_tokens = BrowserEvidenceInterpreter._tokens(payload_text)
        return len(statement_tokens & payload_tokens) >= 2

    @staticmethod
    def _event_refs(event: AgentEvent) -> list[str]:
        refs = [event.id]
        for key in (
            "evidence_item_id",
            "receipt_id",
            "artifact_id",
            "snapshot_artifact_id",
            "screenshot_artifact_id",
            "plan_id",
            "plan_sha256",
            "final_url",
            "post_submit_snapshot_artifact_id",
            "post_upload_snapshot_artifact_id",
            "summary_artifact_id",
            "har_artifact_id",
            "result_artifact_id",
            "receipt_artifact_id",
            "source_artifact_id",
            "compiled_intent_trace_id",
            "authority_grant_id",
            "context_pack_id",
            "session_id",
            "profile_id",
            "account_id",
        ):
            value = event.payload.get(key)
            if value:
                refs.append(str(value))
        return list(dict.fromkeys(refs))

    @staticmethod
    def _is_successful_protective_rejection(event: AgentEvent) -> bool:
        return (
            event.event_type == AgentEventType.BROWSER_JS_EVALUATE_SANDBOXED_REJECTED
            and event.payload.get("reason") == "browser_js_evaluate_network_call_detected"
        )

    @staticmethod
    def _tokens(value: str) -> set[str]:
        separators = ".,:/?&=#-_()[]{}'\""
        normalized = value.lower()
        for separator in separators:
            normalized = normalized.replace(separator, " ")
        return {token for token in normalized.split() if len(token) >= 4}

    @staticmethod
    def _list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value if str(item)]
