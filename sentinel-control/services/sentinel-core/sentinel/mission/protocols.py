from __future__ import annotations

from pathlib import Path
from typing import Protocol

from sentinel.mission.artifacts import MissionArtifactIndex
from sentinel.mission.models import MissionAction, MissionArtifact, MissionAuthorityEnvelope, MissionPlan, ReviewResult
from sentinel.mission.trace_timeline import MissionTraceTimeline


class MissionPlannerProtocol(Protocol):
    def create_plan(
        self,
        envelope: MissionAuthorityEnvelope,
        *,
        idea: str | None = None,
        evidence_refs: list[str] | None = None,
    ) -> MissionPlan:
        ...


class MissionExecutorProtocol(Protocol):
    def execute(
        self,
        action: MissionAction,
        project_dir: str | Path,
        artifact_index: MissionArtifactIndex,
        timeline: MissionTraceTimeline | None = None,
    ) -> dict:
        ...


class MissionReviewerProtocol(Protocol):
    def review(
        self,
        envelope: MissionAuthorityEnvelope,
        project_dir: str | Path,
        artifacts: list[MissionArtifact],
        *,
        unresolved_critical_escalations: int = 0,
    ) -> ReviewResult:
        ...


class MissionSuccessEvaluatorProtocol(Protocol):
    def evaluate(
        self,
        project_dir: str | Path,
        review: ReviewResult,
        *,
        unresolved_critical_escalations: int = 0,
    ) -> tuple[bool, list[str]]:
        ...
