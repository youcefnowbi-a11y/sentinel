from __future__ import annotations

from sentinel.agent.models import AgentContext, MethodRef
from sentinel.shared.enums import MissionType


class MethodSelector:
    def select(self, context: AgentContext) -> list[MethodRef]:
        mission_type = context.mission.mission_type
        if mission_type == MissionType.GTM:
            return [
                MethodRef(id="evidence_ladder", name="Evidence Ladder", reason="GTM decisions need proof quality ranking.", required_before=["plan_review"]),
                MethodRef(id="contradiction_mining", name="Contradiction Mining", reason="GTM output must expose evidence gaps.", required_before=["success_evaluation"]),
                MethodRef(id="premortem", name="Premortem", reason="Launch plans need failure anticipation.", required_before=["success_evaluation"]),
                MethodRef(id="roi_tree", name="ROI Tree", reason="Roadmap actions must connect to measurable outcomes.", required_before=["plan_review"]),
            ]
        if mission_type == MissionType.RESEARCH_SUMMARY:
            return [
                MethodRef(id="source_ranking", name="Source Ranking", reason="Research summaries need source quality control.", required_before=["plan_review"]),
                MethodRef(id="contradiction_mining", name="Contradiction Mining", reason="Research must look for disconfirming evidence.", required_before=["success_evaluation"]),
                MethodRef(id="evidence_ladder", name="Evidence Ladder", reason="Research output should classify proof strength.", required_before=["success_evaluation"]),
            ]
        return [
            MethodRef(id="mission_decomposition", name="Mission Decomposition", reason="Unknown mission type requires conservative decomposition.", required_before=["plan_review"]),
        ]
