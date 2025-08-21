"""Anthropic tool adapter."""
from __future__ import annotations

from typing import Any, Dict

from .base import ToolAdapter
from ..tools import Tool


class AnthropicAdapter(ToolAdapter):
    """Convert tools to Anthropic schema."""

    def to_schema(self, tool: Tool) -> Dict[str, Any]:
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.parameters,
        }
