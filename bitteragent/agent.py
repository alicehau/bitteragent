"""Core agent implementation."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from .providers.base import Provider
from .tools import ToolRegistry, run_tool


class Agent:
    """Minimal agent handling tool-augmented conversations."""

    def __init__(self, provider: Provider, registry: ToolRegistry, system_prompt: str | None = None) -> None:
        self.provider = provider
        self.registry = registry
        self.messages: List[Dict[str, Any]] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    async def run(self, user_input: str) -> str:
        """Run a single-turn conversation handling tool calls."""
        self.messages.append({"role": "user", "content": user_input})
        while True:
            response = await self.provider.complete(self.messages, self.registry.to_anthropic_schema())
            content = response.get("content", [])
            self.messages.append({"role": "assistant", "content": content})
            tool_calls = [c for c in content if c.get("type") == "tool_use"]
            if not tool_calls:
                texts = [c.get("text", "") for c in content if c.get("type") == "text"]
                return "".join(texts)
            # Execute tools in parallel
            tasks = []
            for call in tool_calls:
                tool = self.registry.get(call.get("name"))
                if tool is None:
                    # Unknown tool
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_use_id": call.get("id"),
                            "content": "unknown tool",
                        }
                    )
                    continue
                params = call.get("input", {})
                tasks.append(run_tool(tool, params))
            results = await asyncio.gather(*tasks)
            for call, result in zip(tool_calls, results):
                content = result.output if result.success else result.error or ""
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_use_id": call.get("id"),
                        "content": content,
                    }
                )
