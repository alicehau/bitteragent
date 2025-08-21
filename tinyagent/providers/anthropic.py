"""Anthropic provider implementation."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Callable, Optional

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
        model: str = "claude-sonnet-4-20250514",
        max_retries: int = 3,
        timeout: int = 120,
        text_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        if anthropic is None:
            raise RuntimeError("anthropic package not installed")
        self.client = anthropic.AsyncAnthropic(api_key=api_key, timeout=timeout)
        self.model = model
        self.max_retries = max_retries
        self.text_callback = text_callback
        # Track token usage
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    async def complete(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                # Extract system message if present
                system_message = None
                filtered_messages = []
                for msg in messages:
                    if msg.get("role") == "system":
                        system_message = msg.get("content", "")
                    else:
                        filtered_messages.append(msg)
                
                # Call Anthropic API
                kwargs = {
                    "model": self.model,
                    "messages": filtered_messages,
                    "max_tokens": 4096,
                }
                if system_message:
                    kwargs["system"] = system_message
                if tools:
                    kwargs["tools"] = tools
                
                # Use streaming if we have a text callback
                if self.text_callback:
                    kwargs["stream"] = True
                    stream = await self.client.messages.create(**kwargs)
                    
                    content = []
                    current_text = ""
                    current_tool_use = None
                    current_tool_input_json = ""
                    
                    async for event in stream:
                        if event.type == "content_block_start":
                            if event.content_block.type == "text":
                                current_text = ""
                            elif event.content_block.type == "tool_use":
                                current_tool_use = {
                                    "type": "tool_use",
                                    "id": event.content_block.id,
                                    "name": event.content_block.name,
                                    "input": {}
                                }
                                current_tool_input_json = ""
                        elif event.type == "content_block_delta":
                            if event.delta.type == "text_delta":
                                current_text += event.delta.text
                                self.text_callback(event.delta.text)
                            elif event.delta.type == "input_json_delta":
                                current_tool_input_json += event.delta.partial_json
                        elif event.type == "content_block_stop":
                            if current_text:
                                content.append({"type": "text", "text": current_text})
                                current_text = ""
                            elif current_tool_use:
                                # Parse the accumulated JSON for tool input
                                try:
                                    import json
                                    current_tool_use["input"] = json.loads(current_tool_input_json) if current_tool_input_json else {}
                                except json.JSONDecodeError:
                                    current_tool_use["input"] = {}
                                content.append(current_tool_use)
                                current_tool_use = None
                                current_tool_input_json = ""
                        elif event.type == "message_stop":
                            # Track usage if available
                            if hasattr(event, 'usage'):
                                self.total_input_tokens += getattr(event.usage, 'input_tokens', 0)
                                self.total_output_tokens += getattr(event.usage, 'output_tokens', 0)
                            break
                    
                    return {"content": content}
                else:
                    # Non-streaming version
                    resp = await self.client.messages.create(**kwargs)
                    
                    # Track token usage
                    if hasattr(resp, 'usage'):
                        self.total_input_tokens += getattr(resp.usage, 'input_tokens', 0)
                        self.total_output_tokens += getattr(resp.usage, 'output_tokens', 0)
                    
                    # Convert response content blocks to dictionary format
                    content = []
                    for block in resp.content:
                        # Use block.model_dump() to get all attributes as dict
                        block_dict = block.model_dump()
                        content.append(block_dict)
                    
                    return {"content": content}
            except Exception as exc:  # pragma: no cover - network errors
                last_exc = exc
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        raise RuntimeError(f"Anthropic API call failed: {last_exc}") from last_exc
