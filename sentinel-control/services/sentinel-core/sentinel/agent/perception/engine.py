from __future__ import annotations

from typing import Any

from sentinel.agent.perception.models import (
    PerceptionConfidence,
    PerceptionEvidence,
    PerceptionFrame,
    PerceptionRegion,
    PerceptionSourceType,
    PerceptionTarget,
    PerceptionText,
    hash_perception_payload,
)


class PerceptionEngine:
    """Builds mission-governed scene frames without granting action authority."""

    active_source_types = frozenset({PerceptionSourceType.BROWSER})

    def build_frame(
        self,
        *,
        mission_id: str,
        source_type: PerceptionSourceType,
        source_url: str | None = None,
        page_sha256: str | None = None,
        snapshot_sha256: str | None = None,
        visual_artifact_sha256: str | None = None,
        viewport: dict[str, Any] | None = None,
        regions: list[PerceptionRegion] | None = None,
        texts: list[PerceptionText] | None = None,
        targets: list[PerceptionTarget] | None = None,
        evidence: list[PerceptionEvidence] | None = None,
        trace_refs: list[str] | None = None,
    ) -> PerceptionFrame:
        if source_type not in self.active_source_types:
            raise ValueError(f"perception_source_not_active:{source_type.value}")
        region_list = list(regions or [])
        text_list = list(texts or [])
        target_list = list(targets or [])
        evidence_list = list(evidence or [])
        confidence = self._confidence(region_list, text_list, target_list)
        payload = {
            "mission_id": mission_id,
            "source_type": source_type.value,
            "source_url": source_url,
            "page_sha256": page_sha256,
            "snapshot_sha256": snapshot_sha256,
            "visual_artifact_sha256": visual_artifact_sha256,
            "viewport": dict(viewport or {}),
            "regions": [self._stable_model(region) for region in region_list],
            "texts": [self._stable_model(text) for text in text_list],
            "targets": [self._stable_model(target) for target in target_list],
            "evidence": [self._stable_model(item) for item in evidence_list],
            "confidence": confidence.model_dump(mode="json"),
        }
        return PerceptionFrame(
            mission_id=mission_id,
            source_type=source_type,
            source_url=source_url,
            page_sha256=page_sha256,
            snapshot_sha256=snapshot_sha256,
            visual_artifact_sha256=visual_artifact_sha256,
            viewport=dict(viewport or {}),
            regions=region_list,
            texts=text_list,
            targets=target_list,
            evidence=evidence_list,
            confidence=confidence,
            frame_sha256=hash_perception_payload(payload),
            trace_refs=list(trace_refs or []),
        )

    @staticmethod
    def _stable_model(model: Any) -> dict[str, Any]:
        payload = model.model_dump(mode="json")
        payload.pop("id", None)
        return payload

    @staticmethod
    def _confidence(
        regions: list[PerceptionRegion],
        texts: list[PerceptionText],
        targets: list[PerceptionTarget],
    ) -> PerceptionConfidence:
        visual = max((region.confidence_score for region in regions), default=0.0)
        structural = max((target.confidence.structural for target in targets), default=0.0)
        text = max((item.confidence_score for item in texts), default=0.0)
        grounding = max((target.confidence.grounding for target in targets), default=0.0)
        scores = [score for score in [visual, structural, text, grounding] if score > 0]
        overall = sum(scores) / len(scores) if scores else 0.0
        return PerceptionConfidence(
            visual=visual,
            structural=structural,
            text=text,
            grounding=grounding,
            overall=overall,
        )
