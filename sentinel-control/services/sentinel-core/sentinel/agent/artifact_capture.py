from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any

from pydantic import Field

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.agent.phases import AgentPhase
from sentinel.shared.models import SentinelModel, new_id


DEFAULT_MAX_CAPTURE_BYTES = 50 * 1024 * 1024


class ArtifactCaptureKind(StrEnum):
    TEXT = "text"
    JSON = "json"
    TABLE = "table"
    HTML = "html"
    IMAGE = "image"
    PLOT = "plot"
    STDOUT = "stdout"
    STDERR = "stderr"
    BINARY = "binary"


class ArtifactCaptureStatus(StrEnum):
    CAPTURED = "captured"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"


class ArtifactCaptureSource(StrEnum):
    DIRECT_TEXT = "direct_text"
    DIRECT_JSON = "direct_json"
    DIRECT_BYTES = "direct_bytes"
    STDOUT_STREAM = "stdout_stream"
    STDERR_STREAM = "stderr_stream"
    FUTURE_SANDBOX = "future_sandbox"


class CapturedArtifact(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("capt"))
    mission_id: str
    kind: ArtifactCaptureKind
    source: ArtifactCaptureSource
    artifact_type: str
    relative_path: str
    content_type: str
    sha256: str
    size_bytes: int = Field(ge=0)
    evidence_refs: list[str] = Field(default_factory=list)
    provenance_refs: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class ArtifactCaptureResult(SentinelModel):
    accepted: bool
    status: ArtifactCaptureStatus
    artifact: CapturedArtifact | None = None
    reason: str
    trace_event_id: str | None = None


class ArtifactCaptureIndex(SentinelModel):
    mission_id: str
    artifacts: list[CapturedArtifact] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class ArtifactCaptureSandbox:
    """Captures already-produced outputs as artifacts without running code."""

    def __init__(
        self,
        *,
        mission_id: str,
        capture_root: str | Path,
        max_capture_bytes: int = DEFAULT_MAX_CAPTURE_BYTES,
    ) -> None:
        if max_capture_bytes <= 0:
            raise ValueError("ArtifactCaptureSandbox.max_capture_bytes must be positive.")
        self.mission_id = mission_id
        self.capture_root = Path(capture_root).resolve()
        self.max_capture_bytes = max_capture_bytes
        self._artifacts: list[CapturedArtifact] = []
        self._by_path: dict[str, CapturedArtifact] = {}

    @property
    def artifacts(self) -> tuple[CapturedArtifact, ...]:
        return tuple(self._artifacts)

    def capture_text(
        self,
        *,
        relative_path: str,
        content: str,
        artifact_type: str = "text",
        kind: ArtifactCaptureKind = ArtifactCaptureKind.TEXT,
        source: ArtifactCaptureSource = ArtifactCaptureSource.DIRECT_TEXT,
        content_type: str = "text/plain; charset=utf-8",
        event_bus: EventBus | None = None,
        evidence_refs: list[str] | None = None,
        provenance_refs: list[str] | None = None,
        phase: AgentPhase = AgentPhase.ARTIFACT_REVIEWING,
    ) -> ArtifactCaptureResult:
        return self._capture_bytes(
            relative_path=relative_path,
            data=content.encode("utf-8"),
            artifact_type=artifact_type,
            kind=kind,
            source=source,
            content_type=content_type,
            event_bus=event_bus,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            phase=phase,
        )

    def capture_json(
        self,
        *,
        relative_path: str,
        payload: dict[str, Any] | list[Any],
        artifact_type: str = "json",
        event_bus: EventBus | None = None,
        evidence_refs: list[str] | None = None,
        provenance_refs: list[str] | None = None,
        phase: AgentPhase = AgentPhase.ARTIFACT_REVIEWING,
    ) -> ArtifactCaptureResult:
        data = json.dumps(payload, sort_keys=True, indent=2, default=str).encode("utf-8")
        return self._capture_bytes(
            relative_path=relative_path,
            data=data,
            artifact_type=artifact_type,
            kind=ArtifactCaptureKind.JSON,
            source=ArtifactCaptureSource.DIRECT_JSON,
            content_type="application/json; charset=utf-8",
            event_bus=event_bus,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            phase=phase,
        )

    def capture_binary(
        self,
        *,
        relative_path: str,
        data: bytes,
        artifact_type: str = "binary",
        kind: ArtifactCaptureKind = ArtifactCaptureKind.BINARY,
        content_type: str = "application/octet-stream",
        event_bus: EventBus | None = None,
        evidence_refs: list[str] | None = None,
        provenance_refs: list[str] | None = None,
        phase: AgentPhase = AgentPhase.ARTIFACT_REVIEWING,
    ) -> ArtifactCaptureResult:
        return self._capture_bytes(
            relative_path=relative_path,
            data=data,
            artifact_type=artifact_type,
            kind=kind,
            source=ArtifactCaptureSource.DIRECT_BYTES,
            content_type=content_type,
            event_bus=event_bus,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            phase=phase,
        )

    def capture_stdout(
        self,
        *,
        relative_path: str,
        content: str,
        event_bus: EventBus | None = None,
        provenance_refs: list[str] | None = None,
        phase: AgentPhase = AgentPhase.ARTIFACT_REVIEWING,
    ) -> ArtifactCaptureResult:
        return self.capture_text(
            relative_path=relative_path,
            content=content,
            artifact_type="stdout",
            kind=ArtifactCaptureKind.STDOUT,
            source=ArtifactCaptureSource.STDOUT_STREAM,
            event_bus=event_bus,
            provenance_refs=provenance_refs,
            phase=phase,
        )

    def capture_stderr(
        self,
        *,
        relative_path: str,
        content: str,
        event_bus: EventBus | None = None,
        provenance_refs: list[str] | None = None,
        phase: AgentPhase = AgentPhase.ARTIFACT_REVIEWING,
    ) -> ArtifactCaptureResult:
        return self.capture_text(
            relative_path=relative_path,
            content=content,
            artifact_type="stderr",
            kind=ArtifactCaptureKind.STDERR,
            source=ArtifactCaptureSource.STDERR_STREAM,
            event_bus=event_bus,
            provenance_refs=provenance_refs,
            phase=phase,
        )

    def write_index(self, *, event_bus: EventBus | None = None) -> ArtifactCaptureIndex:
        self.capture_root.mkdir(parents=True, exist_ok=True)
        index = ArtifactCaptureIndex(mission_id=self.mission_id, artifacts=list(self._artifacts))
        index_path = self.capture_root / "captured_artifacts.json"
        index_path.write_text(
            json.dumps(index.model_dump(mode="json"), sort_keys=True, indent=2),
            encoding="utf-8",
        )
        if event_bus is None:
            return index
        self._ensure_event_bus(event_bus)
        event = event_bus.append(
            AgentEventType.ARTIFACT_CAPTURE_INDEX_WRITTEN,
            "Artifact capture index written without invoking external tools.",
            phase_before=AgentPhase.ARTIFACT_REVIEWING,
            phase_after=AgentPhase.ARTIFACT_REVIEWING,
            payload={
                "artifact_count": len(self._artifacts),
                "index_path": "captured_artifacts.json",
            },
        )
        return index.model_copy(update={"trace_refs": [event.id]})

    def _capture_bytes(
        self,
        *,
        relative_path: str,
        data: bytes,
        artifact_type: str,
        kind: ArtifactCaptureKind,
        source: ArtifactCaptureSource,
        content_type: str,
        event_bus: EventBus | None,
        evidence_refs: list[str] | None,
        provenance_refs: list[str] | None,
        phase: AgentPhase,
    ) -> ArtifactCaptureResult:
        if event_bus is not None:
            self._ensure_event_bus(event_bus)
        if len(data) > self.max_capture_bytes:
            return self._rejected(relative_path, "artifact_too_large", event_bus, phase)
        resolved = self._resolve_capture_path(relative_path)
        if resolved is None:
            return self._rejected(relative_path, "path_outside_capture_root", event_bus, phase)

        digest = hashlib.sha256(data).hexdigest()
        normalized_relative = resolved.relative_to(self.capture_root).as_posix()
        existing = self._by_path.get(normalized_relative)
        if existing is not None:
            if existing.sha256 == digest:
                event_id = existing.trace_refs[-1] if existing.trace_refs else None
                if event_bus is not None:
                    event = event_bus.append(
                        AgentEventType.ARTIFACT_CAPTURE_DUPLICATE,
                        "Duplicate artifact capture request accepted without rewriting content.",
                        phase_before=phase,
                        phase_after=phase,
                        payload=self._artifact_payload(existing),
                    )
                    event_id = event.id
                return ArtifactCaptureResult(
                    accepted=True,
                    status=ArtifactCaptureStatus.DUPLICATE,
                    artifact=existing,
                    reason="artifact_already_captured_with_same_hash",
                    trace_event_id=event_id,
                )
            return self._rejected(normalized_relative, "artifact_path_already_captured_with_different_hash", event_bus, phase)

        if resolved.exists():
            existing_digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
            if existing_digest != digest:
                return self._rejected(normalized_relative, "artifact_path_already_exists_with_different_hash", event_bus, phase)

        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_bytes(data)
        artifact = CapturedArtifact(
            mission_id=self.mission_id,
            kind=kind,
            source=source,
            artifact_type=artifact_type,
            relative_path=normalized_relative,
            content_type=content_type,
            sha256=digest,
            size_bytes=len(data),
            evidence_refs=evidence_refs or [],
            provenance_refs=provenance_refs or [],
        )
        event_id: str | None = None
        if event_bus is not None:
            event = event_bus.append(
                AgentEventType.ARTIFACT_CAPTURED,
                "Artifact content captured and indexed without executing code.",
                phase_before=phase,
                phase_after=phase,
                payload=self._artifact_payload(artifact),
            )
            event_id = event.id
            artifact = artifact.model_copy(update={"trace_refs": [event_id]})

        self._artifacts.append(artifact)
        self._by_path[normalized_relative] = artifact
        return ArtifactCaptureResult(
            accepted=True,
            status=ArtifactCaptureStatus.CAPTURED,
            artifact=artifact,
            reason="artifact_captured",
            trace_event_id=event_id,
        )

    def _rejected(
        self,
        relative_path: str,
        reason: str,
        event_bus: EventBus | None,
        phase: AgentPhase,
    ) -> ArtifactCaptureResult:
        event_id: str | None = None
        if event_bus is not None:
            self._ensure_event_bus(event_bus)
            event = event_bus.append(
                AgentEventType.ARTIFACT_CAPTURE_REJECTED,
                "Artifact capture request rejected before writing.",
                phase_before=phase,
                phase_after=phase,
                payload={
                    "relative_path": relative_path,
                    "reason": reason,
                },
            )
            event_id = event.id
        return ArtifactCaptureResult(
            accepted=False,
            status=ArtifactCaptureStatus.REJECTED,
            reason=reason,
            trace_event_id=event_id,
        )

    def _resolve_capture_path(self, relative_path: str) -> Path | None:
        if not relative_path or "\x00" in relative_path:
            return None
        pure = PurePosixPath(relative_path.replace("\\", "/"))
        if pure.is_absolute() or ".." in pure.parts:
            return None
        resolved = (self.capture_root / pure).resolve()
        try:
            resolved.relative_to(self.capture_root)
        except ValueError:
            return None
        return resolved

    def _ensure_event_bus(self, event_bus: EventBus) -> None:
        if event_bus.mission_id != self.mission_id:
            raise ValueError("Artifact capture trace mission_id must match the capture sandbox mission_id.")

    @staticmethod
    def _artifact_payload(artifact: CapturedArtifact) -> dict[str, Any]:
        return {
            "artifact_id": artifact.id,
            "kind": artifact.kind,
            "source": artifact.source,
            "artifact_type": artifact.artifact_type,
            "relative_path": artifact.relative_path,
            "content_type": artifact.content_type,
            "sha256": artifact.sha256,
            "size_bytes": artifact.size_bytes,
            "evidence_refs": artifact.evidence_refs,
            "provenance_refs": artifact.provenance_refs,
        }
