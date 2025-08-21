"""OpenAI tool adapter (placeholder)."""
from __future__ import annotations

from typing import Any, Dict

from .base import ToolAdapter
from ..tools import Tool


class OpenAIAdapter(ToolAdapter):
    """Convert tools to OpenAI function schema."""

    def to_schema(self, tool: Tool) -> Dict[str, Any]:  # pragma: no cover - placeholder
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        }
