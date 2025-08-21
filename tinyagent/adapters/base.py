"""Base adapter interface for tool schemas."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..tools import Tool


class ToolAdapter(ABC):
    """Base class for tool schema adapters."""

    @abstractmethod
    def to_schema(self, tool: Tool) -> Dict[str, Any]:
        """Return provider-specific schema for a tool."""
        raise NotImplementedError
