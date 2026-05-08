from __future__ import annotations

from pathlib import PurePosixPath

from sentinel.mission.models import MissionAction, MissionAuthorityEnvelope, MissionPlan, MissionPlanStep
from sentinel.mission.safe_executors import mission_slug
from sentinel.shared.enums import ConfidenceLevel, ExternalityLevel, ReversibilityLevel, SensitivityLevel


class GTMMissionPlanner:
    def create_plan(
        self,
        envelope: MissionAuthorityEnvelope,
        *,
        idea: str | None = None,
        evidence_refs: list[str] | None = None,
    ) -> MissionPlan:
        refs = evidence_refs or ["mission_input"]
        project_path = str(PurePosixPath("data/generated_projects") / mission_slug(envelope.mission_title))
        idea_text = idea or envelope.mission_objective

        actions = {
            "prepare_workspace": MissionAction(
                mission_id=envelope.id,
                action_type="create_project_folder",
                tool="safe_file_writer",
                intent="Create mission workspace under generated_projects.",
                target=project_path,
                input={"path": project_path},
                expected_output="Project folder created.",
                reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
                externality=ExternalityLevel.INTERNAL_LOCAL,
                sensitivity=SensitivityLevel.INTERNAL,
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=refs,
            ),
            "generate_evidence_pack": MissionAction(
                mission_id=envelope.id,
                action_type="generate_gtm_pack",
                tool="safe_file_writer",
                intent="Generate core GTM verdict, evidence, ICP, and competitor gap files.",
                target=project_path,
                input={"idea": idea_text},
                expected_output="Core GTM markdown files created.",
                reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
                externality=ExternalityLevel.INTERNAL_LOCAL,
                sensitivity=SensitivityLevel.INTERNAL,
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=refs,
            ),
            "generate_landing_copy": MissionAction(
                mission_id=envelope.id,
                action_type="generate_landing_copy",
                tool="safe_file_writer",
                intent="Generate landing page copy tied to the mission.",
                target=project_path,
                input={"idea": idea_text},
                expected_output="Landing page copy created.",
                reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
                externality=ExternalityLevel.INTERNAL_LOCAL,
                sensitivity=SensitivityLevel.INTERNAL,
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=refs,
            ),
            "generate_outreach_drafts": MissionAction(
                mission_id=envelope.id,
                action_type="generate_outreach_drafts_without_sending",
                tool="safe_file_writer",
                intent="Generate outreach drafts without sending.",
                target=project_path,
                input={"idea": idea_text},
                expected_output="Outreach drafts created but not sent.",
                reversibility=ReversibilityLevel.DRAFT,
                externality=ExternalityLevel.INTERNAL_LOCAL,
                sensitivity=SensitivityLevel.INTERNAL,
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=refs,
            ),
            "generate_watchlist": MissionAction(
                mission_id=envelope.id,
                action_type="create_watchlist",
                tool="safe_file_writer",
                intent="Generate watchlist file.",
                target=project_path,
                input={"idea": idea_text},
                expected_output="Watchlist created.",
                reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
                externality=ExternalityLevel.INTERNAL_LOCAL,
                sensitivity=SensitivityLevel.INTERNAL,
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=refs,
            ),
            "generate_roadmap": MissionAction(
                mission_id=envelope.id,
                action_type="generate_research_questions",
                tool="safe_file_writer",
                intent="Generate measurable 7-day roadmap.",
                target=project_path,
                input={"idea": idea_text},
                expected_output="7-day roadmap created.",
                reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
                externality=ExternalityLevel.INTERNAL_LOCAL,
                sensitivity=SensitivityLevel.INTERNAL,
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=refs,
            ),
        }

        return MissionPlan(
            mission_id=envelope.id,
            steps=[
                MissionPlanStep(id="prepare_workspace", action=actions["prepare_workspace"], expected_artifact="."),
                MissionPlanStep(
                    id="generate_evidence_pack",
                    depends_on=["prepare_workspace"],
                    action=actions["generate_evidence_pack"],
                    expected_artifact="00_VERDICT.md",
                    required_evidence_refs=refs,
                ),
                MissionPlanStep(
                    id="generate_landing_copy",
                    depends_on=["generate_evidence_pack"],
                    action=actions["generate_landing_copy"],
                    expected_artifact="04_LANDING_PAGE_COPY.md",
                    required_evidence_refs=refs,
                ),
                MissionPlanStep(
                    id="generate_outreach_drafts",
                    depends_on=["generate_evidence_pack"],
                    action=actions["generate_outreach_drafts"],
                    expected_artifact="05_OUTREACH_MESSAGES.md",
                    required_evidence_refs=refs,
                ),
                MissionPlanStep(
                    id="generate_watchlist",
                    depends_on=["generate_evidence_pack"],
                    action=actions["generate_watchlist"],
                    expected_artifact="08_WATCHLIST.md",
                    required_evidence_refs=refs,
                ),
                MissionPlanStep(
                    id="generate_roadmap",
                    depends_on=["generate_evidence_pack"],
                    action=actions["generate_roadmap"],
                    expected_artifact="07_7_DAY_ROADMAP.md",
                    required_evidence_refs=refs,
                ),
            ],
        )
