from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import UTC, datetime
from collections.abc import Iterable
from typing import Any

from sentinel.agent.events import AgentEventType
from sentinel.agent.models import AgentEvent
from sentinel.agent.phases import AgentPhase
from sentinel.shared.models import new_id


class EventBus:
    def __init__(self, mission_id: str) -> None:
        self.mission_id = mission_id
        self._events: list[AgentEvent] = []
        self._last_hash: str | None = None

    def append(
        self,
        event_type: AgentEventType,
        summary: str,
        *,
        phase_before: AgentPhase | None = None,
        phase_after: AgentPhase | None = None,
        payload: dict[str, Any] | None = None,
        trace_refs: list[str] | None = None,
        parent_event_id: str | None = None,
        actor: str = "sentinel_agent",
    ) -> AgentEvent:
        sequence = len(self._events)
        event_data = {
            "id": new_id("aev"),
            "mission_id": self.mission_id,
            "sequence": sequence,
            "logical_time": sequence,
            "event_type": event_type,
            "phase_before": phase_before,
            "phase_after": phase_after,
            "actor": actor,
            "summary": summary,
            "payload": deepcopy(payload) if payload is not None else {},
            "trace_refs": list(trace_refs) if trace_refs is not None else [],
            "parent_event_id": parent_event_id,
            "previous_hash": self._last_hash,
            "event_hash": "",
            "created_at": datetime.now(UTC),
        }
        event_hash = self._hash_payload(event_data)
        event = AgentEvent(**{**event_data, "event_hash": event_hash})
        self._events.append(event)
        self._last_hash = event_hash
        return event

    def events(self) -> tuple[AgentEvent, ...]:
        return tuple(self._events)

    def last(self) -> AgentEvent | None:
        return self._events[-1] if self._events else None

    def verify_chain(self) -> bool:
        return self.verify_events(self._events)

    @classmethod
    def verify_events(cls, events: Iterable[AgentEvent]) -> bool:
        previous_hash: str | None = None
        for index, event in enumerate(events):
            if event.sequence != index or event.logical_time != index:
                return False
            if event.previous_hash != previous_hash:
                return False
            event_data = event.model_dump()
            event_hash = event_data.pop("event_hash")
            if cls._hash_payload(event_data) != event_hash:
                return False
            previous_hash = event_hash
        return True

    @staticmethod
    def _hash_payload(payload: dict[str, Any]) -> str:
        serializable = dict(payload)
        serializable.pop("event_hash", None)
        canonical = json.dumps(serializable, sort_keys=True, default=str, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
