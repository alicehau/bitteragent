"""Tool system for BitterAgent."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ToolResult:
    """Structured tool execution result."""
    success: bool
    output: str | None = None
    error: str | None = None


class Tool:
    """Base class for tools."""

    name: str = "tool"
    description: str = ""
    parameters: Dict[str, Any] = {}

    async def execute(self, **kwargs: Any) -> ToolResult:  # pragma: no cover - override
        raise NotImplementedError


class ToolRegistry:
    """Registry for tools."""

    def __init__(self) -> None:
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def to_anthropic_schema(self) -> List[Dict[str, Any]]:
        """Return tools in Anthropic tool format."""
        result = []
        for tool in self.tools.values():
            result.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.parameters,
                }
            )
        return result

    def list(self) -> List[str]:
        return list(self.tools.keys())


async def run_tool(tool: Tool, params: Dict[str, Any]) -> ToolResult:
    """Run a tool and ensure it respects ToolResult structure."""
    try:
        return await tool.execute(**params)
    except Exception as exc:  # pragma: no cover - defensive
        return ToolResult(success=False, error=str(exc))
