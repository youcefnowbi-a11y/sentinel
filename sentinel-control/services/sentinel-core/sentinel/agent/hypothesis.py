from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import Field

from sentinel.agent.events import AgentEventType
from sentinel.shared.enums import MissionType
from sentinel.shared.models import SentinelModel, new_id

if TYPE_CHECKING:
    from sentinel.agent.event_bus import EventBus
    from sentinel.agent.models import AgentContext


class HypothesisStatus(StrEnum):
    PROPOSED = "proposed"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_EVIDENCE = "needs_evidence"


class VerificationTestResult(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


class MissionHypothesis(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("hyp"))
    mission_id: str
    statement: str
    source: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    evidence_refs: list[str] = Field(default_factory=list)
    counterexamples: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class VerificationTest(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("vtest"))
    mission_id: str
    hypothesis_id: str
    method: str
    input_refs: list[str] = Field(default_factory=list)
    expected_signal: str
    result: VerificationTestResult
    notes: str
    evidence_refs: list[str] = Field(default_factory=list)
    counterexamples: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class AdversarialFinding(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("adv"))
    mission_id: str
    hypothesis_id: str | None = None
    target_artifact: str = "hypothesis"
    attack_type: str
    finding: str
    severity: str
    suggested_repair: str
    trace_refs: list[str] = Field(default_factory=list)


class HypothesisVerificationResult(SentinelModel):
    hypotheses: list[MissionHypothesis] = Field(default_factory=list)
    verification_tests: list[VerificationTest] = Field(default_factory=list)
    adversarial_findings: list[AdversarialFinding] = Field(default_factory=list)
    verified_hypotheses: list[MissionHypothesis] = Field(default_factory=list)
    rejected_hypotheses: list[MissionHypothesis] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class HypothesisGenerator:
    def generate(self, context: AgentContext) -> list[MissionHypothesis]:
        mission_type = context.mission.mission_type
        source = "deterministic_p1d_generator"
        if mission_type == MissionType.GTM:
            statements = [
                "The target customer has a painful and urgent launch problem.",
                "A focused launch pack is more immediately valuable than a broad dashboard.",
                "Draft-only outreach is safer than sending outbound messages in the current mission scope.",
            ]
        elif mission_type == MissionType.RESEARCH_SUMMARY:
            statements = [
                "The mission can produce useful output from provided evidence references.",
                "Unverified public-web research should remain a future capability, not a runtime dependency.",
            ]
        else:
            statements = ["The mission should stay in decomposition mode until stronger evidence is available."]

        provided = context.user_input.get("hypotheses", [])
        if isinstance(provided, list):
            statements.extend(str(item) for item in provided if str(item).strip())

        return [
            MissionHypothesis(
                mission_id=context.mission.id,
                statement=statement,
                source=source,
                evidence_refs=list(context.evidence_refs),
            )
            for statement in dict.fromkeys(statements)
        ]


class VerificationEngine:
    def verify(self, context: AgentContext, hypotheses: list[MissionHypothesis]) -> tuple[list[MissionHypothesis], list[VerificationTest]]:
        verified: list[MissionHypothesis] = []
        tests: list[VerificationTest] = []
        for hypothesis in hypotheses:
            local_tests = [
                self._evidence_presence_test(context, hypothesis),
                self._scope_consistency_test(context, hypothesis),
            ]
            tests.extend(local_tests)
            pass_count = len([test for test in local_tests if test.result == VerificationTestResult.PASS])
            fail_count = len([test for test in local_tests if test.result == VerificationTestResult.FAIL])
            confidence = min(1.0, max(0.0, hypothesis.confidence + (0.2 * pass_count) - (0.35 * fail_count)))
            if fail_count:
                status = HypothesisStatus.REJECTED
            elif pass_count == len(local_tests) and confidence >= 0.8:
                status = HypothesisStatus.VERIFIED
            else:
                status = HypothesisStatus.NEEDS_EVIDENCE
            verified.append(hypothesis.model_copy(update={"confidence": confidence, "status": status}))
        return verified, tests

    @staticmethod
    def _evidence_presence_test(context: AgentContext, hypothesis: MissionHypothesis) -> VerificationTest:
        evidence_refs = list(dict.fromkeys([*hypothesis.evidence_refs, *context.evidence_refs]))
        if evidence_refs:
            return VerificationTest(
                mission_id=context.mission.id,
                hypothesis_id=hypothesis.id,
                method="evidence_presence",
                input_refs=evidence_refs,
                expected_signal="At least one evidence reference exists before hypothesis promotion.",
                result=VerificationTestResult.PASS,
                notes="Evidence references are present. P1D does not inspect live sources.",
                evidence_refs=evidence_refs,
            )
        return VerificationTest(
            mission_id=context.mission.id,
            hypothesis_id=hypothesis.id,
            method="evidence_presence",
            expected_signal="At least one evidence reference exists before hypothesis promotion.",
            result=VerificationTestResult.INCONCLUSIVE,
            notes="No evidence references are available, so the hypothesis cannot be verified in P1D.",
        )

    @staticmethod
    def _scope_consistency_test(context: AgentContext, hypothesis: MissionHypothesis) -> VerificationTest:
        forbidden = [action for action in context.mission.forbidden_actions if action and action.lower() in hypothesis.statement.lower()]
        if forbidden:
            return VerificationTest(
                mission_id=context.mission.id,
                hypothesis_id=hypothesis.id,
                method="scope_consistency",
                expected_signal="Hypothesis does not rely on forbidden mission actions.",
                result=VerificationTestResult.FAIL,
                notes=f"Hypothesis references forbidden actions: {', '.join(sorted(forbidden))}.",
                counterexamples=forbidden,
            )
        return VerificationTest(
            mission_id=context.mission.id,
            hypothesis_id=hypothesis.id,
            method="scope_consistency",
            expected_signal="Hypothesis does not rely on forbidden mission actions.",
            result=VerificationTestResult.PASS,
            notes="No forbidden mission action was referenced.",
        )


class AdversarialReviewer:
    ABSOLUTE_TERMS = ("guaranteed", "everyone", "always", "no competitor", "zero risk", "cannot fail")

    def review(self, context: AgentContext, hypotheses: list[MissionHypothesis]) -> tuple[list[MissionHypothesis], list[AdversarialFinding]]:
        reviewed: list[MissionHypothesis] = []
        findings: list[AdversarialFinding] = []
        for hypothesis in hypotheses:
            attacks = self._attack(context, hypothesis)
            findings.extend(attacks)
            if attacks and any(finding.severity in {"high", "critical"} for finding in attacks):
                hypothesis = hypothesis.model_copy(
                    update={
                        "status": HypothesisStatus.REJECTED,
                        "confidence": min(hypothesis.confidence, 0.2),
                        "counterexamples": [*hypothesis.counterexamples, *[finding.finding for finding in attacks]],
                    }
                )
            reviewed.append(hypothesis)
        return reviewed, findings

    def _attack(self, context: AgentContext, hypothesis: MissionHypothesis) -> list[AdversarialFinding]:
        statement = hypothesis.statement.lower()
        findings: list[AdversarialFinding] = []
        for term in self.ABSOLUTE_TERMS:
            if term in statement:
                findings.append(
                    AdversarialFinding(
                        mission_id=context.mission.id,
                        hypothesis_id=hypothesis.id,
                        attack_type="absolute_claim",
                        finding=f"Hypothesis contains overconfident absolute claim `{term}`.",
                        severity="high",
                        suggested_repair="Rewrite as a bounded assumption and require supporting evidence.",
                    )
                )
        return findings


class HypothesisVerifier:
    def __init__(
        self,
        *,
        generator: HypothesisGenerator | None = None,
        verifier: VerificationEngine | None = None,
        reviewer: AdversarialReviewer | None = None,
    ) -> None:
        self.generator = generator or HypothesisGenerator()
        self.verifier = verifier or VerificationEngine()
        self.reviewer = reviewer or AdversarialReviewer()

    def run(self, context: AgentContext, *, event_bus: EventBus) -> HypothesisVerificationResult:
        proposed = self.generator.generate(context)
        generated_event = event_bus.append(
            AgentEventType.HYPOTHESES_GENERATED,
            "Mission hypotheses generated for internal verification.",
            payload={"hypotheses": [{"id": item.id, "statement": item.statement} for item in proposed]},
        )
        proposed = [item.model_copy(update={"trace_refs": [generated_event.id]}) for item in proposed]

        verified, tests = self.verifier.verify(context, proposed)
        verified_event = event_bus.append(
            AgentEventType.HYPOTHESES_VERIFIED,
            "Mission hypotheses verified against local evidence and scope checks.",
            payload={
                "tests": [{"id": test.id, "hypothesis_id": test.hypothesis_id, "result": test.result} for test in tests],
                "verified": [item.id for item in verified if item.status == HypothesisStatus.VERIFIED],
            },
            trace_refs=[generated_event.id],
        )
        verified = [item.model_copy(update={"trace_refs": [*item.trace_refs, verified_event.id]}) for item in verified]
        tests = [test.model_copy(update={"trace_refs": [verified_event.id]}) for test in tests]

        reviewed, findings = self.reviewer.review(context, verified)
        reviewed_event = event_bus.append(
            AgentEventType.HYPOTHESES_REVIEWED,
            "Mission hypotheses reviewed adversarially before planning.",
            payload={
                "findings": [{"id": finding.id, "hypothesis_id": finding.hypothesis_id, "severity": finding.severity} for finding in findings],
                "verified": [item.id for item in reviewed if item.status == HypothesisStatus.VERIFIED],
                "rejected": [item.id for item in reviewed if item.status == HypothesisStatus.REJECTED],
            },
            trace_refs=[generated_event.id, verified_event.id],
        )
        reviewed = [item.model_copy(update={"trace_refs": [*item.trace_refs, reviewed_event.id]}) for item in reviewed]
        findings = [finding.model_copy(update={"trace_refs": [reviewed_event.id]}) for finding in findings]

        return HypothesisVerificationResult(
            hypotheses=reviewed,
            verification_tests=tests,
            adversarial_findings=findings,
            verified_hypotheses=[item for item in reviewed if item.status == HypothesisStatus.VERIFIED],
            rejected_hypotheses=[item for item in reviewed if item.status == HypothesisStatus.REJECTED],
            trace_refs=[generated_event.id, verified_event.id, reviewed_event.id],
        )
