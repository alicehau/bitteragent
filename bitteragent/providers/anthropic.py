"""Anthropic provider implementation."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List

try:  # pragma: no cover - optional dependency
    import anthropic
except Exception:  # pragma: no cover - optional dependency
    anthropic = None

from .base import Provider


class AnthropicProvider(Provider):
    """Provider using Anthropic's API."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-sonnet-20240229",
        max_retries: int = 3,
        timeout: int = 120,
    ) -> None:
        if anthropic is None:
            raise RuntimeError("anthropic package not installed")
        self.client = anthropic.AsyncAnthropic(api_key=api_key, timeout=timeout)
        self.model = model
        self.max_retries = max_retries

    async def complete(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                resp = await self.client.messages.create(
                    model=self.model,
                    messages=messages,
                    tools=tools or [],
                )
                return resp
            except Exception as exc:  # pragma: no cover - network errors
                last_exc = exc
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("Anthropic API call failed") from last_exc
