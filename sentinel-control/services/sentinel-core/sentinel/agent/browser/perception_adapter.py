from __future__ import annotations

from sentinel.agent.browser.ui_observation import BrowserBoundingBox, BrowserUIObservation, BrowserUIObservationSet
from sentinel.agent.browser.visual_observation import BrowserVisualObservation
from sentinel.agent.perception import (
    PerceptionConfidence,
    PerceptionEngine,
    PerceptionEvidence,
    PerceptionEvidenceKind,
    PerceptionFrame,
    PerceptionRegion,
    PerceptionSourceType,
    PerceptionTarget,
    PerceptionText,
    PerceptionTextSource,
)


INTERACTABLE_BROWSER_ROLES = frozenset(
    {
        "button",
        "link",
        "textbox",
        "checkbox",
        "radio",
        "combobox",
        "listbox",
        "option",
        "searchbox",
        "slider",
        "spinbutton",
        "switch",
        "tab",
    }
)


class BrowserPerceptionAdapter:
    """Maps browser-specific observations into the generic P4H-X scene model."""

    def __init__(self, *, engine: PerceptionEngine | None = None) -> None:
        self.engine = engine or PerceptionEngine()

    def build_frame(
        self,
        *,
        ui_observation_set: BrowserUIObservationSet,
        visual_observations: list[BrowserVisualObservation] | None = None,
        action_classes_by_ref: dict[str, list[str]] | None = None,
    ) -> PerceptionFrame:
        visuals = list(visual_observations or [])
        action_hints = action_classes_by_ref or {}
        self._validate_mission_scope(ui_observation_set, visuals)

        evidence: list[PerceptionEvidence] = [
            PerceptionEvidence(
                kind=PerceptionEvidenceKind.STRUCTURAL_OBSERVATION,
                source_type=PerceptionSourceType.BROWSER,
                source_observation_id=ui_observation_set.id,
                source_event_ids=list(ui_observation_set.trace_refs),
                observation_sha256=ui_observation_set.observation_sha256,
                page_sha256=self._first_page_hash(ui_observation_set),
                snapshot_sha256=self._first_snapshot_hash(ui_observation_set),
                note="browser_ui_observation_set",
            )
        ]
        regions: list[PerceptionRegion] = []
        texts: list[PerceptionText] = []
        targets: list[PerceptionTarget] = []
        region_by_ref: dict[str, str] = {}
        evidence_ids_by_ref: dict[str, list[str]] = {}

        for visual in visuals:
            visual_evidence = PerceptionEvidence(
                kind=PerceptionEvidenceKind.VISUAL_ARTIFACT,
                source_type=PerceptionSourceType.BROWSER,
                source_observation_id=visual.id,
                source_event_ids=list(visual.trace_refs),
                artifact_id=visual.artifact_id,
                artifact_sha256=visual.artifact_sha256,
                observation_sha256=visual.observation_sha256,
                page_sha256=visual.page_sha256,
                snapshot_sha256=visual.snapshot_sha256,
                note=visual.kind.value,
            )
            evidence.append(visual_evidence)
            region = PerceptionRegion(
                source_type=PerceptionSourceType.BROWSER,
                bbox=self._bbox_dict(visual.region.bbox),
                source_artifact_sha256=visual.region.source_screenshot_sha256,
                source_observation_id=visual.id,
                runtime_ref_id=visual.region.ref_id,
                confidence_score=0.9 if visual.region.ref_id else 0.45,
            )
            regions.append(region)
            if visual.region.ref_id:
                region_by_ref[visual.region.ref_id] = region.id
                evidence_ids_by_ref.setdefault(visual.region.ref_id, []).append(visual_evidence.id)
            if visual.ocr_text:
                ocr_evidence = PerceptionEvidence(
                    kind=PerceptionEvidenceKind.OCR_HINT,
                    source_type=PerceptionSourceType.BROWSER,
                    source_observation_id=visual.id,
                    source_event_ids=list(visual.trace_refs),
                    artifact_id=visual.artifact_id,
                    artifact_sha256=visual.artifact_sha256,
                    observation_sha256=visual.observation_sha256,
                    page_sha256=visual.page_sha256,
                    snapshot_sha256=visual.snapshot_sha256,
                    note="ocr_fallback_hint_not_authority",
                )
                evidence.append(ocr_evidence)
                texts.append(
                    PerceptionText(
                        source=PerceptionTextSource.OCR,
                        text=visual.ocr_text,
                        region_id=region.id,
                        evidence_id=ocr_evidence.id,
                        confidence_score=0.45,
                        authoritative_for_action=False,
                    )
                )

        structural_evidence_id = evidence[0].id
        for observation in ui_observation_set.observations:
            region_id = region_by_ref.get(observation.ref_id or "")
            if observation.bbox is not None:
                region = PerceptionRegion(
                    source_type=PerceptionSourceType.BROWSER,
                    bbox=self._bbox_dict(observation.bbox),
                    source_artifact_sha256=observation.screenshot_sha256,
                    source_observation_id=observation.id,
                    runtime_ref_id=observation.ref_id,
                    confidence_score=max(0.0, 1.0 - observation.uncertainty_score),
                )
                regions.append(region)
                region_id = region.id
                if observation.ref_id:
                    region_by_ref[observation.ref_id] = region.id

            target = self._target_from_observation(
                observation,
                region_id=region_id,
                evidence_ids=[structural_evidence_id, *evidence_ids_by_ref.get(observation.ref_id or "", [])],
                extra_action_classes=action_hints.get(observation.ref_id or "", []),
            )
            targets.append(target)
            target_text = observation.name or observation.text
            if target_text:
                texts.append(
                    PerceptionText(
                        source=PerceptionTextSource.STRUCTURAL,
                        text=target_text,
                        target_id=target.id,
                        region_id=region_id,
                        evidence_id=structural_evidence_id,
                        confidence_score=target.confidence.text,
                    )
                )

        return self.engine.build_frame(
            mission_id=ui_observation_set.mission_id,
            source_type=PerceptionSourceType.BROWSER,
            source_url=ui_observation_set.url,
            page_sha256=self._first_page_hash(ui_observation_set, visuals),
            snapshot_sha256=self._first_snapshot_hash(ui_observation_set, visuals),
            visual_artifact_sha256=next((visual.artifact_sha256 for visual in visuals if visual.artifact_sha256), None),
            viewport=next((visual.viewport for visual in visuals if visual.viewport), {}),
            regions=regions,
            texts=texts,
            targets=targets,
            evidence=evidence,
            trace_refs=[*ui_observation_set.trace_refs, *[ref for visual in visuals for ref in visual.trace_refs]],
        )

    @staticmethod
    def _validate_mission_scope(
        ui_observation_set: BrowserUIObservationSet,
        visual_observations: list[BrowserVisualObservation],
    ) -> None:
        for visual in visual_observations:
            if visual.mission_id != ui_observation_set.mission_id:
                raise ValueError("browser_visual_observation_mission_mismatch")
            if visual.url != ui_observation_set.url:
                raise ValueError("browser_visual_observation_url_mismatch")

    @staticmethod
    def _target_from_observation(
        observation: BrowserUIObservation,
        *,
        region_id: str | None,
        evidence_ids: list[str],
        extra_action_classes: list[str] | None = None,
    ) -> PerceptionTarget:
        role = (observation.role or "").lower()
        visible = bool(observation.visible)
        understood = bool(observation.role or observation.name or observation.text)
        interactable = bool(observation.interactable) or role in INTERACTABLE_BROWSER_ROLES
        actionable = bool(observation.ref_id and interactable)
        structural_confidence = max(0.0, 1.0 - observation.uncertainty_score)
        text_confidence = structural_confidence if observation.name or observation.text else 0.0
        grounding_confidence = structural_confidence if observation.ref_id else 0.0
        action_classes = ["browser_interaction_limited"] if actionable else []
        action_classes.extend(extra_action_classes or [])
        return PerceptionTarget(
            source_type=PerceptionSourceType.BROWSER,
            runtime_ref_id=observation.ref_id,
            role=observation.role,
            name=observation.name,
            text=observation.text,
            region_id=region_id,
            evidence_ids=list(dict.fromkeys(evidence_ids)),
            source_observation_ids=[observation.id],
            visible=visible,
            understood=understood,
            actionable=actionable,
            authorized=False,
            action_classes=sorted(set(action_classes)),
            page_sha256=observation.page_sha256,
            snapshot_sha256=observation.snapshot_sha256,
            confidence=PerceptionConfidence(
                visual=0.75 if region_id else 0.0,
                structural=structural_confidence,
                text=text_confidence,
                grounding=grounding_confidence,
                overall=(structural_confidence + grounding_confidence + text_confidence) / 3,
            ),
        )

    @staticmethod
    def _bbox_dict(bbox: BrowserBoundingBox) -> dict[str, float]:
        return {"x": bbox.x, "y": bbox.y, "width": bbox.width, "height": bbox.height}

    @staticmethod
    def _first_page_hash(
        ui_observation_set: BrowserUIObservationSet,
        visuals: list[BrowserVisualObservation] | None = None,
    ) -> str | None:
        return next(
            (value for value in [*(observation.page_sha256 for observation in ui_observation_set.observations), *((visual.page_sha256 for visual in visuals or []))] if value),
            None,
        )

    @staticmethod
    def _first_snapshot_hash(
        ui_observation_set: BrowserUIObservationSet,
        visuals: list[BrowserVisualObservation] | None = None,
    ) -> str | None:
        return next(
            (value for value in [*(observation.snapshot_sha256 for observation in ui_observation_set.observations), *((visual.snapshot_sha256 for visual in visuals or []))] if value),
            None,
        )
