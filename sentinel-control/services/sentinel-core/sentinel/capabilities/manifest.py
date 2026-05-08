from __future__ import annotations

from sentinel.capabilities.fixtures.static_catalog import load_static_fixture_manifests
from sentinel.capabilities.registry import ToolRegistry


def default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for manifest in load_static_fixture_manifests():
        registry.register(manifest)
    return registry
