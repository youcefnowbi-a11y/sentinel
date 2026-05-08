from __future__ import annotations

from pathlib import PurePosixPath

from sentinel.mission.models import MissionAction, MissionAuthorityEnvelope, MissionPlan, MissionPlanStep
from sentinel.mission.safe_executors import mission_slug
from sentinel.shared.enums import ConfidenceLevel, ExternalityLevel, ReversibilityLevel, SensitivityLevel


class ResearchSummaryMissionPlanner:
    def create_plan(
        self,
        envelope: MissionAuthorityEnvelope,
        *,
        idea: str | None = None,
        evidence_refs: list[str] | None = None,
    ) -> MissionPlan:
        refs = evidence_refs or ["mission_input"]
        project_path = str(PurePosixPath("data/generated_projects") / mission_slug(envelope.mission_title))
        topic = idea or envelope.mission_objective
        summary = (
            "# Research Summary\n\n"
            f"Topic: {topic}\n\n"
            "This dummy mission proves the Mission Authority Kernel can run a non-GTM mission type through the same registry, "
            "autonomy engine, executors, artifact index, reviewer, success evaluator, and trace timeline.\n\n"
            "## Evidence refs\n\n"
            + "\n".join(f"- `{ref}`" for ref in refs)
            + "\n"
        )

        folder = MissionAction(
            mission_id=envelope.id,
            action_type="create_project_folder",
            tool="safe_file_writer",
            intent="Create research summary workspace.",
            target=project_path,
            input={"path": project_path},
            expected_output="Project folder created.",
            reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
            externality=ExternalityLevel.INTERNAL_LOCAL,
            sensitivity=SensitivityLevel.INTERNAL,
            confidence=ConfidenceLevel.HIGH,
            evidence_refs=refs,
        )
        write_summary = MissionAction(
            mission_id=envelope.id,
            action_type="create_markdown_file",
            tool="safe_file_writer",
            intent="Write a minimal research summary.",
            target=project_path,
            input={
                "filename": "RESEARCH_SUMMARY.md",
                "artifact_type": "research_summary",
                "content": summary,
            },
            expected_output="Research summary markdown created.",
            reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
            externality=ExternalityLevel.INTERNAL_LOCAL,
            sensitivity=SensitivityLevel.INTERNAL,
            confidence=ConfidenceLevel.HIGH,
            evidence_refs=refs,
        )

        return MissionPlan(
            mission_id=envelope.id,
            steps=[
                MissionPlanStep(id="prepare_workspace", action=folder, expected_artifact="."),
                MissionPlanStep(
                    id="write_research_summary",
                    depends_on=["prepare_workspace"],
                    action=write_summary,
                    expected_artifact="RESEARCH_SUMMARY.md",
                    required_evidence_refs=refs,
                ),
            ],
        )
