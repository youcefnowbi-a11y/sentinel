from __future__ import annotations

from sentinel.agent.models import CapabilityNeed, LearningProposal, ReviewFinding


class LearningLoop:
    def propose(
        self,
        *,
        review_findings: list[ReviewFinding],
        missing_capabilities: list[CapabilityNeed],
        mission_failed: bool = False,
    ) -> list[LearningProposal]:
        proposals: list[LearningProposal] = []
        for need in missing_capabilities:
            proposals.append(
                LearningProposal(
                    observed_failure=f"Capability `{need.name}` is missing.",
                    proposed_change=f"Consider adding a manifest and tests for `{need.name}` in a later capability phase.",
                    risk="medium" if need.required else "low",
                    tests_needed=[f"test_{need.name}_is_declared_before_execution"],
                )
            )
        if mission_failed or review_findings:
            proposals.append(
                LearningProposal(
                    observed_failure="Agent review found mission issues.",
                    proposed_change="Inspect review findings and add a bounded repair rule if the issue is recurrent.",
                    risk="low",
                    tests_needed=["test_agent_review_issue_creates_learning_proposal"],
                )
            )
        return proposals
