class MissionRevokedError(RuntimeError):
    """Raised when a run is attempted after mission authority was revoked."""


class AgentBlockedError(RuntimeError):
    """Raised when the agent core blocks execution before worker dispatch."""
