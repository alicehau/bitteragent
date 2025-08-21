"""Base provider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Provider(ABC):
    """Abstract LLM provider."""

    @abstractmethod
    async def complete(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        """Return a completion given conversation messages and tools."""
        raise NotImplementedError
