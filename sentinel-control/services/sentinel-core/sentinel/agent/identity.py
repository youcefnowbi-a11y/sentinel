from __future__ import annotations

from pydantic import ConfigDict, Field

from sentinel.shared.models import SentinelModel


class AgentIdentity(SentinelModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = "sentinel_core"
    name: str = "Sentinel Core"
    role: str = "sentinel_agent"
    doctrine: str = "mission_scoped_deliberative_control"
    forbidden_modes: frozenset[str] = Field(
        default_factory=lambda: frozenset(
            {
                "generic_chatbot",
                "raw_tool_executor",
                "unbounded_assistant",
                "vendor_runtime_clone",
            }
        )
    )
    operating_loop: str = "cognitive_mission_loop"


def default_agent_identity() -> AgentIdentity:
    return AgentIdentity()
