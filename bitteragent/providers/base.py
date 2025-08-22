"""Base provider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..tools import ToolRegistry


class Provider(ABC):
    """Abstract LLM provider."""

    @abstractmethod
    async def complete(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        """Return a completion given conversation messages and tools."""
        raise NotImplementedError
    
    def get_tools_schema(self, registry: ToolRegistry) -> List[Dict[str, Any]]:
        """Convert tool registry to provider-specific schema format.
        
        Default implementation returns Anthropic format.
        Override in subclasses for provider-specific formats.
        """
        # Default to Anthropic format
        result = []
        for tool in registry.tools.values():
            result.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters,
            })
        return result
