"""Core agent implementation."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Callable, Optional

from .providers.base import Provider
from .tools import ToolRegistry, run_tool, ToolResult


class Agent:
    """Minimal agent handling tool-augmented conversations."""

    def __init__(
        self, 
        provider: Provider, 
        registry: ToolRegistry, 
        system_prompt: str | None = None,
        tool_callback: Optional[Callable[[str, Dict[str, Any], Optional[ToolResult]], None]] = None,
        text_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.system_prompt = system_prompt
        self.messages: List[Dict[str, Any]] = []
        self.tool_callback = tool_callback
        self.text_callback = text_callback

    async def run(self, user_input: str) -> str:
        """Run a single-turn conversation handling tool calls."""
        self.messages.append({"role": "user", "content": user_input})
        while True:
            # Prepare messages with system prompt if available
            messages_with_system = self.messages.copy()
            if self.system_prompt:
                messages_with_system.insert(0, {"role": "system", "content": self.system_prompt})
            response = await self.provider.complete(messages_with_system, self.registry.to_anthropic_schema())
            content = response.get("content", [])
            self.messages.append({"role": "assistant", "content": content})
            tool_calls = [c for c in content if c.get("type") == "tool_use"]
            if not tool_calls:
                texts = [c.get("text", "") for c in content if c.get("type") == "text"]
                return "".join(texts)
            
            # Execute tools one by one for immediate feedback
            tool_results = []
            
            for tool_use in tool_calls:
                tool_name = tool_use.get("name", "unknown")
                params = tool_use.get("input", {})
                
                # Show tool call immediately when we encounter it
                if self.tool_callback:
                    self.tool_callback(tool_name, params, None)  # None indicates start of execution
                
                tool = self.registry.get(tool_name)
                if tool is None:
                    # Unknown tool - show result immediately
                    unknown_result = ToolResult(success=False, error="unknown tool")
                    if self.tool_callback:
                        self.tool_callback(tool_name, params, unknown_result)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.get("id"),
                        "content": "unknown tool",
                    })
                else:
                    # Execute tool immediately and show result
                    result = await run_tool(tool, params)
                    
                    # Show tool result via callback immediately
                    if self.tool_callback:
                        self.tool_callback(tool_name, params, result)
                    
                    content = result.output if result.success else result.error or ""
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.get("id"),
                        "content": content,
                    })
            
            # Add all tool results as a single user message
            if tool_results:
                self.messages.append({
                    "role": "user",
                    "content": tool_results
                })
