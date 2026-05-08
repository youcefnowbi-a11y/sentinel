from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from sentinel.mission.artifacts import MissionArtifactIndex
from sentinel.mission.models import MissionAction
from sentinel.mission.trace_timeline import MissionTraceTimeline


def mission_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:64] or "sentinel-mission"


class SafeMissionExecutors:
    ALLOWED_ACTIONS = {
        "create_project_folder",
        "create_markdown_file",
        "export_json",
        "generate_gtm_pack",
        "generate_landing_copy",
        "generate_outreach_drafts_without_sending",
        "create_watchlist",
        "generate_research_questions",
        "write_trace",
    }

    def __init__(self, project_root: str | Path | None = None) -> None:
        self.project_root = Path(project_root or Path.cwd()).resolve()
        self.generated_root = (self.project_root / "data" / "generated_projects").resolve()

    def project_dir_for(self, mission_title: str) -> Path:
        return (self.generated_root / mission_slug(mission_title)).resolve()

    def execute(
        self,
        action: MissionAction,
        project_dir: str | Path,
        artifact_index: MissionArtifactIndex,
        timeline: MissionTraceTimeline | None = None,
    ) -> dict[str, Any]:
        if action.action_type not in self.ALLOWED_ACTIONS:
            raise ValueError(f"No safe mission executor for {action.action_type}.")

        project_path = self._ensure_project_dir(project_dir)

        if action.action_type == "create_project_folder":
            artifact_index.record_folder(project_path)
            return {"status": "created", "folder_path": str(project_path), "type": "project_folder"}
        if action.action_type == "create_markdown_file":
            return self._write_markdown(action, project_path, artifact_index)
        if action.action_type == "export_json":
            return self._write_json(action, project_path, artifact_index)
        if action.action_type == "generate_gtm_pack":
            return self._generate_gtm_pack(action, project_path, artifact_index)
        if action.action_type == "generate_landing_copy":
            return self._generate_landing_copy(action, project_path, artifact_index)
        if action.action_type == "generate_outreach_drafts_without_sending":
            return self._generate_outreach_drafts(action, project_path, artifact_index)
        if action.action_type == "create_watchlist":
            return self._create_watchlist(action, project_path, artifact_index)
        if action.action_type == "generate_research_questions":
            return self._generate_research_questions(action, project_path, artifact_index)
        if action.action_type == "write_trace":
            if timeline:
                timeline.persist()
            return {"status": "written", "path": str(project_path / "mission_timeline.json"), "type": "trace"}

        raise ValueError(f"No safe mission executor for {action.action_type}.")

    def _ensure_project_dir(self, project_dir: str | Path) -> Path:
        path = Path(project_dir)
        if not path.is_absolute():
            path = self.project_root / path
        path = path.resolve()
        if path != self.generated_root and self.generated_root not in path.parents:
            raise ValueError("Mission writes must stay under data/generated_projects.")
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _resolve_file(self, project_dir: Path, filename: str) -> Path:
        path = Path(filename)
        if not path.is_absolute():
            path = project_dir / path
        path = path.resolve()
        if path == project_dir or project_dir not in path.parents:
            raise ValueError("Path traversal outside the mission project folder is blocked.")
        return path

    def _write_markdown(self, action: MissionAction, project_dir: Path, artifact_index: MissionArtifactIndex) -> dict[str, Any]:
        filename = str(action.input.get("filename") or action.input.get("path") or "NOTE.md")
        path = self._resolve_file(project_dir, filename)
        content = str(action.input.get("content") or "")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        artifact_index.record_file(
            str(action.input.get("artifact_type") or "markdown"),
            path,
            evidence_refs=action.evidence_refs,
            action_id=action.id,
        )
        return {"status": "created", "path": str(path), "type": str(action.input.get("artifact_type") or "markdown")}

    def _write_json(self, action: MissionAction, project_dir: Path, artifact_index: MissionArtifactIndex) -> dict[str, Any]:
        filename = str(action.input.get("filename") or action.input.get("path") or "export.json")
        path = self._resolve_file(project_dir, filename)
        payload = action.input.get("payload") or {}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        artifact_index.record_file(
            str(action.input.get("artifact_type") or "json_export"),
            path,
            evidence_refs=action.evidence_refs,
            action_id=action.id,
        )
        return {"status": "created", "path": str(path), "type": str(action.input.get("artifact_type") or "json_export")}

    def _generate_gtm_pack(self, action: MissionAction, project_dir: Path, artifact_index: MissionArtifactIndex) -> dict[str, Any]:
        idea = str(action.input.get("idea") or "the delegated mission")
        refs = self._refs(action)
        sections = {
            "00_VERDICT.md": (
                "gtm_verdict",
                f"# Executive Verdict\n\nDecision: research_more until paid-intent is verified.\n\n{refs}\n\n## Evidence gap\n\nEVIDENCE_GAP: wtp - Confirm willingness to pay before build."
            ),
            "01_EVIDENCE.md": (
                "evidence",
                f"# Evidence\n\nSentinel is operating from mission-scoped local inputs for `{idea}`.\n\n{refs}\n\n## Evidence gap\n\nEVIDENCE_GAP: source_depth - Import CueIdea evidence or live research before claiming certainty."
            ),
            "02_ICP.md": (
                "icp",
                f"# ICP\n\nPrimary segment: specific early-stage SaaS founders validating first customers.\n\n{refs}\n\n## Evidence gap\n\nEVIDENCE_GAP: icp - Replace this with CueIdea-backed buyer segment evidence when available."
            ),
            "03_COMPETITOR_GAPS.md": (
                "competitor_gap",
                f"# Competitor Gaps\n\nCurrent alternative: manual spreadsheets, generic research prompts, and scattered prospect lists.\n\nConcrete wedge: one mission creates a traceable first-customer pack instead of an unverified dashboard.\n\n{refs}"
            ),
        }
        created: list[str] = []
        for filename, (artifact_type, content) in sections.items():
            path = self._resolve_file(project_dir, filename)
            path.write_text(content + "\n", encoding="utf-8")
            artifact_index.record_file(artifact_type, path, evidence_refs=action.evidence_refs, action_id=action.id)
            created.append(str(path))
        return {"status": "created", "paths": created, "type": "gtm_pack"}

    def _generate_landing_copy(self, action: MissionAction, project_dir: Path, artifact_index: MissionArtifactIndex) -> dict[str, Any]:
        idea = str(action.input.get("idea") or "your GTM mission")
        content = (
            "# Landing Page Copy\n\n"
            f"Headline: Turn `{idea}` into a first-customer mission pack.\n\n"
            "Subheadline: Sentinel converts evidence into positioning, outreach drafts, watchlists, and a 7-day validation path with mission authority and traceability.\n\n"
            "CTA: Start a bounded validation mission.\n\n"
            f"{self._refs(action)}\n"
        )
        path = self._resolve_file(project_dir, "04_LANDING_PAGE_COPY.md")
        path.write_text(content, encoding="utf-8")
        artifact_index.record_file("landing_copy", path, evidence_refs=action.evidence_refs, action_id=action.id)
        return {"status": "created", "path": str(path), "type": "landing_copy"}

    def _generate_outreach_drafts(self, action: MissionAction, project_dir: Path, artifact_index: MissionArtifactIndex) -> dict[str, Any]:
        content = (
            "# Outreach Messages\n\n"
            "Status: draft_only\n\n"
            "Subject: Quick question about validating first customers\n\n"
            "Body: I am validating whether founders need a safer way to turn market evidence into first-customer actions. "
            "Would a 10 minute conversation this week be useful? Reply stop if not relevant.\n\n"
            "No email was sent. User approval and contact ownership are required before any future sending version.\n\n"
            f"{self._refs(action)}\n"
        )
        md_path = self._resolve_file(project_dir, "05_OUTREACH_MESSAGES.md")
        md_path.write_text(content, encoding="utf-8")
        artifact_index.record_file("outreach_drafts", md_path, evidence_refs=action.evidence_refs, action_id=action.id)

        json_path = self._resolve_file(project_dir, "outreach_drafts.json")
        json_path.write_text(
            json.dumps(
                {
                    "status": "draft_created",
                    "sent": False,
                    "requires_user_contact_approval": True,
                    "drafts": [
                        {
                            "subject": "Quick question about validating first customers",
                            "body": "Draft only. Reply stop if not relevant.",
                        }
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        artifact_index.record_file("outreach_draft_json", json_path, evidence_refs=action.evidence_refs, action_id=action.id)
        return {"status": "draft_created", "sent": False, "path": str(md_path), "type": "outreach_drafts"}

    def _create_watchlist(self, action: MissionAction, project_dir: Path, artifact_index: MissionArtifactIndex) -> dict[str, Any]:
        content = (
            "# Watchlist\n\n"
            "- Competitors: manual research workflows, generic AI assistants, spreadsheet-first prospect tracking.\n"
            "- Communities: indie hackers, agency owners, SaaS founder forums, CueIdea signal sources.\n"
            "- Objections: weak WTP proof, generic ICP, unverified competitor gap.\n\n"
            f"{self._refs(action)}\n"
        )
        path = self._resolve_file(project_dir, "08_WATCHLIST.md")
        path.write_text(content, encoding="utf-8")
        artifact_index.record_file("watchlist", path, evidence_refs=action.evidence_refs, action_id=action.id)
        return {"status": "created", "path": str(path), "type": "watchlist"}

    def _generate_research_questions(self, action: MissionAction, project_dir: Path, artifact_index: MissionArtifactIndex) -> dict[str, Any]:
        content = (
            "# 7-Day Validation Roadmap\n\n"
            "Day 1: identify 10 reachable prospects and record their source.\n"
            "Day 2: interview 5 prospects about the current workaround.\n"
            "Day 3: collect 3 competitor alternatives and the repeated complaint.\n"
            "Day 4: test 2 landing page headlines against the strongest pain.\n"
            "Day 5: ask for exact paid pilot or budget range.\n"
            "Day 6: summarize objections and update positioning.\n"
            "Day 7: decide build / pivot / niche_down / kill based on WTP, ICP reachability, and competitor gap.\n\n"
            f"{self._refs(action)}\n"
        )
        path = self._resolve_file(project_dir, "07_7_DAY_ROADMAP.md")
        path.write_text(content, encoding="utf-8")
        artifact_index.record_file("roadmap", path, evidence_refs=action.evidence_refs, action_id=action.id)
        return {"status": "created", "path": str(path), "type": "roadmap"}

    @staticmethod
    def _refs(action: MissionAction) -> str:
        if not action.evidence_refs:
            return "## Evidence gap\n\nEVIDENCE_GAP: evidence_refs - No evidence refs attached to this section."
        return "## Evidence refs\n\n" + "\n".join(f"- `{ref}`" for ref in action.evidence_refs)
