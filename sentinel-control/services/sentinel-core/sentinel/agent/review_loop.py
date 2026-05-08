from __future__ import annotations

from sentinel.agent.hypothesis import HypothesisStatus, HypothesisVerificationResult, MissionHypothesis, VerificationTestResult
from sentinel.agent.models import AgentContext, CapabilityNeed, ReviewFinding, ToolSelectionResult, WorkerResult
from sentinel.mission.models import MissionPlan


class ReviewLoop:
    def review_tool_selection(
        self,
        capabilities: list[CapabilityNeed],
        tool_selection: ToolSelectionResult,
    ) -> list[ReviewFinding]:
        findings: list[ReviewFinding] = []
        required_unavailable = [
            need.name
            for need in capabilities
            if need.required and need.name in set(tool_selection.missing_capabilities)
        ]
        if required_unavailable:
            findings.append(
                ReviewFinding(
                    code="required_tool_unavailable",
                    severity="critical",
                    message=f"Required capabilities have no selectable approved tool: {', '.join(sorted(required_unavailable))}.",
                    trace_refs=tool_selection.trace_refs,
                )
            )
        return findings

    def review_hypotheses(self, hypothesis_result: HypothesisVerificationResult) -> list[ReviewFinding]:
        findings: list[ReviewFinding] = []
        invalid_verified = [
            hypothesis.id
            for hypothesis in hypothesis_result.verified_hypotheses
            if hypothesis.status != HypothesisStatus.VERIFIED
        ]
        if invalid_verified:
            findings.append(
                ReviewFinding(
                    code="unverified_hypothesis_promoted",
                    severity="critical",
                    message=f"Hypotheses were promoted without verified status: {', '.join(sorted(invalid_verified))}.",
                    trace_refs=hypothesis_result.trace_refs,
                )
            )
        verified_test_ids = {
            test.hypothesis_id
            for test in hypothesis_result.verification_tests
            if test.result == VerificationTestResult.PASS
        }
        missing_positive_tests = [
            hypothesis.id
            for hypothesis in hypothesis_result.verified_hypotheses
            if hypothesis.id not in verified_test_ids
        ]
        if missing_positive_tests:
            findings.append(
                ReviewFinding(
                    code="verified_hypothesis_without_positive_test",
                    severity="critical",
                    message=f"Verified hypotheses must have at least one passing verification test: {', '.join(sorted(missing_positive_tests))}.",
                    trace_refs=hypothesis_result.trace_refs,
                )
            )
        return findings

    def review_plan(
        self,
        context: AgentContext,
        plan: MissionPlan,
        capabilities: list[CapabilityNeed],
        tool_selection: ToolSelectionResult | None = None,
        verified_hypotheses: list[MissionHypothesis] | None = None,
    ) -> list[ReviewFinding]:
        findings: list[ReviewFinding] = []
        if not plan.steps:
            findings.append(ReviewFinding(code="empty_plan", severity="critical", message="Mission plan has no steps."))
        missing_required = [need.name for need in capabilities if need.required and not need.available]
        if missing_required:
            findings.append(
                ReviewFinding(
                    code="missing_required_capability",
                    severity="critical",
                    message=f"Required capabilities are missing: {', '.join(sorted(missing_required))}.",
                )
            )
        if tool_selection is not None:
            selected_tools = set(tool_selection.selected_tools)
            unselected_plan_tools = sorted({step.action.tool for step in plan.steps if step.action.tool not in selected_tools})
            if unselected_plan_tools:
                findings.append(
                    ReviewFinding(
                        code="plan_uses_unselected_tool",
                        severity="critical",
                        message=f"Plan references tools not selected by the agent firewall: {', '.join(unselected_plan_tools)}.",
                        trace_refs=tool_selection.trace_refs,
                    )
                )
        if verified_hypotheses is not None:
            leaked_hypotheses = [hypothesis.id for hypothesis in verified_hypotheses if hypothesis.status != HypothesisStatus.VERIFIED]
            if leaked_hypotheses:
                findings.append(
                    ReviewFinding(
                        code="plan_received_unverified_hypothesis",
                        severity="critical",
                        message=f"Planner received hypotheses that were not verified: {', '.join(sorted(leaked_hypotheses))}.",
                    )
                )
            verified_ids = [hypothesis.id for hypothesis in verified_hypotheses if hypothesis.status == HypothesisStatus.VERIFIED]
            if verified_ids:
                expected_refs = {f"hypothesis:{hypothesis_id}" for hypothesis_id in verified_ids}
                missing_ref_steps = [
                    step.id
                    for step in plan.steps
                    if not expected_refs.issubset(set(step.action.evidence_refs))
                    or not expected_refs.issubset(set(step.required_evidence_refs))
                ]
                if missing_ref_steps:
                    findings.append(
                        ReviewFinding(
                            code="plan_missing_verified_hypothesis_refs",
                            severity="critical",
                            message=(
                                "Plan steps are missing required verified hypothesis evidence refs: "
                                f"{', '.join(sorted(missing_ref_steps))}."
                            ),
                        )
                    )
                missing_payload_steps = []
                for step in plan.steps:
                    payload = step.action.input.get("verified_hypotheses")
                    payload_ids = {str(item.get("id")) for item in payload if isinstance(item, dict)} if isinstance(payload, list) else set()
                    if not set(verified_ids).issubset(payload_ids):
                        missing_payload_steps.append(step.id)
                if missing_payload_steps:
                    findings.append(
                        ReviewFinding(
                            code="plan_missing_verified_hypothesis_payload",
                            severity="critical",
                            message=(
                                "Plan steps are missing verified hypothesis payloads: "
                                f"{', '.join(sorted(missing_payload_steps))}."
                            ),
                        )
                    )
        return findings

    def review_worker_result(self, result: WorkerResult) -> list[ReviewFinding]:
        if result.mission_result is None:
            return [ReviewFinding(code="missing_mission_result", severity="critical", message="Worker did not return a mission result.")]
        if not result.mission_result.success:
            return [ReviewFinding(code="mission_runner_failed", severity="high", message="MissionRunner reported failure.")]
        return []
