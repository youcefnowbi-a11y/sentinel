from __future__ import annotations

import hashlib
import json

import pytest

from sentinel.agent import (
    AgentEventType,
    ArtifactCaptureKind,
    ArtifactCaptureSandbox,
    ArtifactCaptureSource,
    ArtifactCaptureStatus,
    EventBus,
)


def test_artifact_capture_writes_text_hashes_and_traces_without_raw_content(tmp_path):
    bus = EventBus("mission_001")
    sandbox = ArtifactCaptureSandbox(mission_id="mission_001", capture_root=tmp_path)

    result = sandbox.capture_text(
        relative_path="reports/summary.md",
        content="secret-free report body",
        artifact_type="mission_report",
        event_bus=bus,
        evidence_refs=["ev_1"],
        provenance_refs=["worker_result_1"],
    )

    assert result.accepted is True
    assert result.status == ArtifactCaptureStatus.CAPTURED
    assert result.artifact is not None
    assert result.artifact.kind == ArtifactCaptureKind.TEXT
    assert result.artifact.source == ArtifactCaptureSource.DIRECT_TEXT
    assert result.artifact.relative_path == "reports/summary.md"
    assert result.artifact.sha256 == hashlib.sha256(b"secret-free report body").hexdigest()
    assert (tmp_path / "reports" / "summary.md").read_text(encoding="utf-8") == "secret-free report body"
    assert bus.events()[-1].event_type == AgentEventType.ARTIFACT_CAPTURED
    assert "secret-free report body" not in json.dumps(bus.events()[-1].payload)
    assert bus.verify_chain() is True


def test_artifact_capture_writes_canonical_json_and_index(tmp_path):
    bus = EventBus("mission_001")
    sandbox = ArtifactCaptureSandbox(mission_id="mission_001", capture_root=tmp_path)

    result = sandbox.capture_json(
        relative_path="data/result.json",
        payload={"b": 2, "a": 1},
        artifact_type="structured_result",
        event_bus=bus,
    )
    index = sandbox.write_index(event_bus=bus)

    assert result.accepted is True
    assert (tmp_path / "data" / "result.json").read_text(encoding="utf-8") == '{\n  "a": 1,\n  "b": 2\n}'
    assert (tmp_path / "captured_artifacts.json").exists()
    assert index.artifacts[0].relative_path == "data/result.json"
    assert bus.events()[-1].event_type == AgentEventType.ARTIFACT_CAPTURE_INDEX_WRITTEN


def test_artifact_capture_rejects_path_escape_and_writes_rejection_trace(tmp_path):
    bus = EventBus("mission_001")
    sandbox = ArtifactCaptureSandbox(mission_id="mission_001", capture_root=tmp_path)

    result = sandbox.capture_text(relative_path="../escape.txt", content="nope", event_bus=bus)

    assert result.accepted is False
    assert result.status == ArtifactCaptureStatus.REJECTED
    assert result.reason == "path_outside_capture_root"
    assert not (tmp_path.parent / "escape.txt").exists()
    assert bus.events()[-1].event_type == AgentEventType.ARTIFACT_CAPTURE_REJECTED


def test_artifact_capture_duplicate_same_hash_is_idempotent(tmp_path):
    sandbox = ArtifactCaptureSandbox(mission_id="mission_001", capture_root=tmp_path)

    first = sandbox.capture_text(relative_path="same.txt", content="same")
    second = sandbox.capture_text(relative_path="same.txt", content="same")

    assert first.accepted is True
    assert second.accepted is True
    assert second.status == ArtifactCaptureStatus.DUPLICATE
    assert second.artifact == first.artifact
    assert len(sandbox.artifacts) == 1


def test_artifact_capture_duplicate_same_hash_writes_duplicate_trace(tmp_path):
    bus = EventBus("mission_001")
    sandbox = ArtifactCaptureSandbox(mission_id="mission_001", capture_root=tmp_path)

    first = sandbox.capture_text(relative_path="same.txt", content="same", event_bus=bus)
    second = sandbox.capture_text(relative_path="same.txt", content="same", event_bus=bus)

    assert first.status == ArtifactCaptureStatus.CAPTURED
    assert second.status == ArtifactCaptureStatus.DUPLICATE
    assert second.trace_event_id == bus.events()[-1].id
    assert bus.events()[-1].event_type == AgentEventType.ARTIFACT_CAPTURE_DUPLICATE
    assert bus.events()[-1].payload["sha256"] == first.artifact.sha256
    assert len(sandbox.artifacts) == 1


def test_artifact_capture_rejects_destructive_overwrite(tmp_path):
    sandbox = ArtifactCaptureSandbox(mission_id="mission_001", capture_root=tmp_path)

    first = sandbox.capture_text(relative_path="same.txt", content="one")
    second = sandbox.capture_text(relative_path="same.txt", content="two")

    assert first.accepted is True
    assert second.accepted is False
    assert second.reason == "artifact_path_already_captured_with_different_hash"
    assert (tmp_path / "same.txt").read_text(encoding="utf-8") == "one"


def test_artifact_capture_rejects_oversize_capture_before_write(tmp_path):
    bus = EventBus("mission_001")
    sandbox = ArtifactCaptureSandbox(mission_id="mission_001", capture_root=tmp_path, max_capture_bytes=4)

    result = sandbox.capture_text(relative_path="too-large.txt", content="too large", event_bus=bus)

    assert result.accepted is False
    assert result.reason == "artifact_too_large"
    assert not (tmp_path / "too-large.txt").exists()
    assert bus.events()[-1].event_type == AgentEventType.ARTIFACT_CAPTURE_REJECTED
    assert bus.events()[-1].payload["reason"] == "artifact_too_large"


def test_artifact_capture_rejects_non_positive_capture_limit(tmp_path):
    with pytest.raises(ValueError, match="max_capture_bytes"):
        ArtifactCaptureSandbox(mission_id="mission_001", capture_root=tmp_path, max_capture_bytes=0)


def test_artifact_capture_stream_helpers_do_not_execute_processes(tmp_path):
    sandbox = ArtifactCaptureSandbox(mission_id="mission_001", capture_root=tmp_path)

    stdout = sandbox.capture_stdout(relative_path="streams/stdout.txt", content="printed output")
    stderr = sandbox.capture_stderr(relative_path="streams/stderr.txt", content="error output")

    assert stdout.accepted is True
    assert stdout.artifact is not None
    assert stdout.artifact.kind == ArtifactCaptureKind.STDOUT
    assert stderr.accepted is True
    assert stderr.artifact is not None
    assert stderr.artifact.kind == ArtifactCaptureKind.STDERR


def test_artifact_capture_rejects_mismatched_trace_mission(tmp_path):
    sandbox = ArtifactCaptureSandbox(mission_id="mission_001", capture_root=tmp_path)

    with pytest.raises(ValueError, match="mission_id"):
        sandbox.capture_text(relative_path="a.txt", content="x", event_bus=EventBus("mission_002"))
