from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sentinel.mission.models import MissionArtifact, MissionArtifactReceipt, RollbackMetadata
from sentinel.mission.trace_timeline import MissionTraceTimeline
from sentinel.shared.enums import MissionTraceEventType


class MissionArtifactIndex:
    def __init__(self, project_dir: str | Path, mission_id: str | None = None) -> None:
        self.project_dir = Path(project_dir).resolve()
        self.mission_id = mission_id
        self.artifacts: list[MissionArtifact] = []
        self.artifact_receipts: list[MissionArtifactReceipt] = []
        self.rollback = RollbackMetadata()

    @property
    def index_path(self) -> Path:
        return self.project_dir / "mission_artifacts.json"

    @property
    def rollback_path(self) -> Path:
        return self.project_dir / "artifact_manifest.json"

    def record_folder(self, path: str | Path) -> None:
        relative = self._relative(path)
        if relative not in self.rollback.created_folders:
            self.rollback.created_folders.append(relative)

    def record_file(
        self,
        artifact_type: str,
        path: str | Path,
        *,
        evidence_refs: list[str] | None = None,
        action_id: str | None = None,
        can_rollback: bool = True,
    ) -> MissionArtifact:
        resolved = self._resolve_inside(path)
        if not resolved.is_file():
            raise ValueError("Mission artifact receipt requires an existing file inside the mission project folder.")
        relative = resolved.relative_to(self.project_dir).as_posix()
        data = resolved.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        artifact = MissionArtifact(
            type=artifact_type,
            path=relative,
            evidence_refs=evidence_refs or [],
            created_by_action_id=action_id,
            can_rollback=can_rollback,
            sha256=digest,
            size_bytes=len(data),
            rollback_strategy="delete_created_artifact_after_user_confirmation_if_hash_matches" if can_rollback else "manual_review_required",
        )
        receipt = MissionArtifactReceipt(
            mission_id=self.mission_id,
            artifact_id=artifact.id,
            artifact_type=artifact.type,
            artifact_path=artifact.path,
            artifact_sha256=digest,
            size_bytes=len(data),
            action_id=action_id,
            reversible=can_rollback,
            rollback_strategy=artifact.rollback_strategy or "manual_review_required",
        )
        artifact = artifact.model_copy(update={"receipt_id": receipt.id})
        self.artifacts.append(artifact)
        self.artifact_receipts.append(receipt)
        self.rollback.artifact_receipts = list(self.artifact_receipts)
        if relative not in self.rollback.created_files:
            self.rollback.created_files.append(relative)
        return artifact

    def write(self, timeline: MissionTraceTimeline | None = None) -> None:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        if timeline:
            self._emit_receipts(timeline)
        self.index_path.write_text(
            json.dumps([artifact.model_dump(mode="json") for artifact in self.artifacts], indent=2),
            encoding="utf-8",
        )
        self.rollback_path.write_text(
            json.dumps(self.rollback.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
        if timeline:
            timeline.emit(
                MissionTraceEventType.ARTIFACT_INDEX_WRITTEN,
                "Mission artifact index written.",
                result={"path": str(self.index_path), "artifact_count": len(self.artifacts)},
            )
            timeline.emit(
                MissionTraceEventType.ROLLBACK_AVAILABLE,
                "Rollback metadata available for generated local artifacts.",
                result=self.rollback.model_dump(mode="json"),
            )

    def _relative(self, path: str | Path) -> str:
        return self._resolve_inside(path).relative_to(self.project_dir).as_posix()

    def _resolve_inside(self, path: str | Path) -> Path:
        resolved = Path(path).resolve()
        try:
            resolved.relative_to(self.project_dir)
        except ValueError:
            raise ValueError("Mission artifact path must stay inside the mission project folder.") from None
        return resolved

    def _emit_receipts(self, timeline: MissionTraceTimeline) -> None:
        receipt_by_id = {receipt.id: receipt for receipt in self.artifact_receipts}
        updated_artifacts: list[MissionArtifact] = []
        for artifact in self.artifacts:
            receipt = receipt_by_id.get(artifact.receipt_id or "")
            if receipt is None or receipt.trace_refs:
                updated_artifacts.append(artifact)
                continue
            event = timeline.emit(
                MissionTraceEventType.ACTION_RECEIPT_RECORDED,
                "Mission artifact receipt recorded.",
                action_id=receipt.action_id,
                target=receipt.artifact_path,
                result=receipt.model_dump(mode="json"),
                reversible=receipt.reversible,
            )
            updated_receipt = receipt.model_copy(update={"trace_refs": [event.id]})
            receipt_by_id[receipt.id] = updated_receipt
            updated_artifacts.append(artifact.model_copy(update={"trace_refs": [event.id]}))
        self.artifacts = updated_artifacts
        self.artifact_receipts = [receipt_by_id[receipt.id] for receipt in self.artifact_receipts]
        self.rollback.artifact_receipts = list(self.artifact_receipts)
