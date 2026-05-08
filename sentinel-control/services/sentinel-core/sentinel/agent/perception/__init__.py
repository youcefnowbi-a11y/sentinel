"""Mission-governed perception models.

P4H-X v0 keeps browser as the only active backend. Future source types are
modeled but rejected by the active PerceptionEngine until their own authority
and runner contracts exist.
"""

from sentinel.agent.perception.engine import PerceptionEngine
from sentinel.agent.perception.models import (
    PerceptionConfidence,
    PerceptionEvidence,
    PerceptionEvidenceKind,
    PerceptionFrame,
    PerceptionRegion,
    PerceptionSourceType,
    PerceptionTarget,
    PerceptionText,
    PerceptionTextSource,
    hash_perception_payload,
)

__all__ = [
    "PerceptionConfidence",
    "PerceptionEngine",
    "PerceptionEvidence",
    "PerceptionEvidenceKind",
    "PerceptionFrame",
    "PerceptionRegion",
    "PerceptionSourceType",
    "PerceptionTarget",
    "PerceptionText",
    "PerceptionTextSource",
    "hash_perception_payload",
]
