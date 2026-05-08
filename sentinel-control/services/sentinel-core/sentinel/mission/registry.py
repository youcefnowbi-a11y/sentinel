from __future__ import annotations

from dataclasses import dataclass

from sentinel.mission.models import MissionArtifactSchema
from sentinel.mission.protocols import (
    MissionExecutorProtocol,
    MissionPlannerProtocol,
    MissionReviewerProtocol,
    MissionSuccessEvaluatorProtocol,
)
from sentinel.shared.enums import MissionType


@dataclass(frozen=True)
class MissionDefinition:
    mission_type: MissionType | str
    planner: MissionPlannerProtocol
    executor: MissionExecutorProtocol
    reviewer: MissionReviewerProtocol
    success_evaluator: MissionSuccessEvaluatorProtocol
    artifact_schema: MissionArtifactSchema


class MissionRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, MissionDefinition] = {}

    def register(self, definition: MissionDefinition) -> None:
        key = self._key(definition.mission_type)
        self._definitions[key] = definition

    def get(self, mission_type: MissionType | str) -> MissionDefinition:
        key = self._key(mission_type)
        if key not in self._definitions:
            raise KeyError(f"Unknown mission type: {key}")
        return self._definitions[key]

    def list_types(self) -> list[str]:
        return sorted(self._definitions)

    @staticmethod
    def _key(value: MissionType | str) -> str:
        return value.value if isinstance(value, MissionType) else str(value)


def default_mission_registry(project_root: str | None = None) -> MissionRegistry:
    from sentinel.missions.gtm import create_gtm_definition
    from sentinel.missions.research_summary import create_research_summary_definition

    registry = MissionRegistry()
    registry.register(create_gtm_definition(project_root=project_root))
    registry.register(create_research_summary_definition(project_root=project_root))
    return registry
