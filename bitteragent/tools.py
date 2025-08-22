"""Tool system for TinyAgent."""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ToolResult:
    """Structured tool execution result."""
    success: bool
    output: str | None = None
    error: str | None = None


class Tool(ABC):
    """Base class for tools."""

    name: str = "tool"
    description: str = ""
    parameters: Dict[str, Any] = {}

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given parameters."""
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
    except TypeError as exc:
        # Handle missing required parameters more gracefully
        error_msg = str(exc)
        if "missing" in error_msg and "required" in error_msg:
            # Extract the parameter name from the error message
            return ToolResult(success=False, error=f"Missing required parameter(s): {error_msg}")
        return ToolResult(success=False, error=str(exc))
    except Exception as exc:
        return ToolResult(success=False, error=str(exc))
