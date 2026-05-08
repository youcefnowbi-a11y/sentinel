from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any

from pydantic import Field, model_validator

from sentinel.shared.models import SentinelModel, new_id


class PerceptionSourceType(StrEnum):
    BROWSER = "browser"
    DESKTOP = "desktop"
    IMAGE = "image"
    PDF = "pdf"
    VIDEO_FRAME = "video_frame"


class PerceptionTextSource(StrEnum):
    STRUCTURAL = "structural"
    PAGE_TEXT = "page_text"
    OCR = "ocr"


class PerceptionEvidenceKind(StrEnum):
    STRUCTURAL_OBSERVATION = "structural_observation"
    VISUAL_ARTIFACT = "visual_artifact"
    OCR_HINT = "ocr_hint"


class PerceptionRegion(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("preg"))
    source_type: PerceptionSourceType
    bbox: dict[str, float] = Field(default_factory=dict)
    source_artifact_sha256: str | None = None
    source_observation_id: str | None = None
    runtime_ref_id: str | None = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class PerceptionText(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("ptxt"))
    source: PerceptionTextSource
    text: str
    target_id: str | None = None
    region_id: str | None = None
    evidence_id: str | None = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    authoritative_for_action: bool = False

    @model_validator(mode="after")
    def ocr_cannot_be_action_authority(self) -> "PerceptionText":
        if self.source == PerceptionTextSource.OCR and self.authoritative_for_action:
            raise ValueError("ocr_text_cannot_authorize_action")
        return self


class PerceptionConfidence(SentinelModel):
    visual: float = Field(default=0.0, ge=0.0, le=1.0)
    structural: float = Field(default=0.0, ge=0.0, le=1.0)
    text: float = Field(default=0.0, ge=0.0, le=1.0)
    grounding: float = Field(default=0.0, ge=0.0, le=1.0)
    overall: float = Field(default=0.0, ge=0.0, le=1.0)


class PerceptionEvidence(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("pev"))
    kind: PerceptionEvidenceKind
    source_type: PerceptionSourceType
    source_observation_id: str | None = None
    source_event_ids: list[str] = Field(default_factory=list)
    artifact_id: str | None = None
    artifact_sha256: str | None = None
    observation_sha256: str | None = None
    page_sha256: str | None = None
    snapshot_sha256: str | None = None
    note: str = ""


class PerceptionTarget(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("ptgt"))
    source_type: PerceptionSourceType
    runtime_ref_id: str | None = None
    role: str | None = None
    name: str | None = None
    text: str | None = None
    region_id: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    source_observation_ids: list[str] = Field(default_factory=list)
    visible: bool = False
    understood: bool = False
    actionable: bool = False
    authorized: bool = False
    action_classes: list[str] = Field(default_factory=list)
    page_sha256: str | None = None
    snapshot_sha256: str | None = None
    confidence: PerceptionConfidence = Field(default_factory=PerceptionConfidence)

    @model_validator(mode="after")
    def perception_never_authorizes_action(self) -> "PerceptionTarget":
        if self.authorized:
            raise ValueError("perception_target_cannot_be_authorized")
        if self.actionable and not self.runtime_ref_id:
            raise ValueError("actionable_perception_target_requires_runtime_ref")
        return self


class PerceptionFrame(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("pframe"))
    mission_id: str
    source_type: PerceptionSourceType
    source_url: str | None = None
    page_sha256: str | None = None
    snapshot_sha256: str | None = None
    visual_artifact_sha256: str | None = None
    viewport: dict[str, Any] = Field(default_factory=dict)
    regions: list[PerceptionRegion] = Field(default_factory=list)
    texts: list[PerceptionText] = Field(default_factory=list)
    targets: list[PerceptionTarget] = Field(default_factory=list)
    evidence: list[PerceptionEvidence] = Field(default_factory=list)
    confidence: PerceptionConfidence = Field(default_factory=PerceptionConfidence)
    frame_sha256: str
    trace_refs: list[str] = Field(default_factory=list)

    def target_by_id(self, target_id: str) -> PerceptionTarget | None:
        return next((target for target in self.targets if target.id == target_id), None)

    def target_by_ref(self, runtime_ref_id: str) -> PerceptionTarget | None:
        return next((target for target in self.targets if target.runtime_ref_id == runtime_ref_id), None)


def hash_perception_payload(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
