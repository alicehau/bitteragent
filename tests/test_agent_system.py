"""Tests for agent system prompt handling."""
import asyncio
from typing import Any, Dict, List

from bitteragent.agent import Agent
from bitteragent.providers.base import Provider
from bitteragent.tools import ToolRegistry


class MockProvider(Provider):
    """Mock provider that captures messages."""
    
    def __init__(self):
        self.calls: List[Dict[str, Any]] = []
    
    async def complete(self, messages: List[Dict[str, Any]], tools=None) -> Dict[str, Any]:
        """Capture messages and return text response."""
        self.calls.append({"messages": messages.copy(), "tools": tools})
        return {"content": [{"type": "text", "text": "Response"}]}


def test_agent_system_prompt_handling():
    """Test that system prompt is passed correctly to provider."""
    provider = MockProvider()
    registry = ToolRegistry()
    system_prompt = "You are a helpful assistant."
    
    agent = Agent(
        provider=provider,
        registry=registry,
        system_prompt=system_prompt
    )
    
    # Run the agent
    result = asyncio.run(agent.run("Hello"))
    
    # Check that the provider received the system prompt
    assert len(provider.calls) == 1
    messages = provider.calls[0]["messages"]
    
    # System prompt should be first message
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == system_prompt
    
    # User message should follow
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Hello"
    
    # Result should be the response
    assert result == "Response"


def test_agent_without_system_prompt():
    """Test agent without system prompt."""
    provider = MockProvider()
    registry = ToolRegistry()
    
    agent = Agent(
        provider=provider,
        registry=registry,
        system_prompt=None
    )
    
    result = asyncio.run(agent.run("Hello"))
    
    # Check messages sent to provider
    assert len(provider.calls) == 1
    messages = provider.calls[0]["messages"]
    
    # No system message, just user message
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    
    assert result == "Response"


def test_agent_preserves_conversation_history():
    """Test that agent preserves conversation history correctly."""
    provider = MockProvider()
    registry = ToolRegistry()
    system_prompt = "Test system"
    
    agent = Agent(
        provider=provider,
        registry=registry,
        system_prompt=system_prompt
    )
    
    # First interaction
    asyncio.run(agent.run("First"))
    
    # Second interaction
    asyncio.run(agent.run("Second"))
    
    # Check second call includes history but system prompt is still first
    second_call_messages = provider.calls[1]["messages"]
    
    assert second_call_messages[0]["role"] == "system"
    assert second_call_messages[0]["content"] == system_prompt
    
    assert second_call_messages[1]["role"] == "user"
    assert second_call_messages[1]["content"] == "First"
    
    assert second_call_messages[2]["role"] == "assistant"
    
    assert second_call_messages[3]["role"] == "user"
    assert second_call_messages[3]["content"] == "Second"


def test_agent_system_prompt_not_in_history():
    """Test that system prompt is not stored in message history."""
    provider = MockProvider()
    registry = ToolRegistry()
    system_prompt = "System prompt"
    
    agent = Agent(
        provider=provider,
        registry=registry,
        system_prompt=system_prompt
    )
    
    # System prompt should be stored separately
    assert agent.system_prompt == system_prompt
    
    # Messages list should be empty initially
    assert len(agent.messages) == 0
    
    # Run the agent
    asyncio.run(agent.run("Test"))
    
    # Check internal message history doesn't contain system prompt
    for msg in agent.messages:
        if msg.get("role") == "system":
            assert False, "System prompt should not be in message history"