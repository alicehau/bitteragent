"""Tests for tool system and registry."""
import asyncio
from typing import Any

import pytest

from bitteragent.tools import Tool, ToolRegistry, ToolResult, run_tool


class MockTool(Tool):
    """Mock tool for testing."""
    
    name = "mock_tool"
    description = "A mock tool"
    parameters = {
        "type": "object",
        "properties": {
            "param1": {"type": "string"},
            "param2": {"type": "integer"}
        },
        "required": ["param1"]
    }
    
    async def execute(self, param1: str, param2: int = 0, **kwargs: Any) -> ToolResult:
        return ToolResult(success=True, output=f"{param1}:{param2}")


class FailingTool(Tool):
    """Tool that always fails."""
    
    name = "failing_tool"
    description = "Always fails"
    parameters = {}
    
    async def execute(self, **kwargs: Any) -> ToolResult:
        raise ValueError("Intentional failure")


def test_tool_registry_register_and_get():
    """Test registering and retrieving tools."""
    registry = ToolRegistry()
    tool = MockTool()
    
    registry.register(tool)
    
    retrieved = registry.get("mock_tool")
    assert retrieved is tool
    
    # Test getting non-existent tool
    assert registry.get("nonexistent") is None


def test_tool_registry_list():
    """Test listing registered tools."""
    registry = ToolRegistry()
    tool1 = MockTool()
    tool2 = FailingTool()
    
    registry.register(tool1)
    registry.register(tool2)
    
    tools_list = registry.list()
    assert "mock_tool" in tools_list
    assert "failing_tool" in tools_list
    assert len(tools_list) == 2


def test_tool_registry_to_anthropic_schema():
    """Test converting tools to Anthropic schema."""
    registry = ToolRegistry()
    tool = MockTool()
    registry.register(tool)
    
    schema = registry.to_anthropic_schema()
    
    assert len(schema) == 1
    assert schema[0]["name"] == "mock_tool"
    assert schema[0]["description"] == "A mock tool"
    assert schema[0]["input_schema"] == tool.parameters


def test_run_tool_success():
    """Test successful tool execution."""
    tool = MockTool()
    result = asyncio.run(run_tool(tool, {"param1": "test", "param2": 42}))
    
    assert result.success
    assert result.output == "test:42"
    assert result.error is None


def test_run_tool_with_default_params():
    """Test tool execution with default parameters."""
    tool = MockTool()
    result = asyncio.run(run_tool(tool, {"param1": "test"}))
    
    assert result.success
    assert result.output == "test:0"


def test_run_tool_missing_required_param():
    """Test tool execution with missing required parameter."""
    tool = MockTool()
    result = asyncio.run(run_tool(tool, {"param2": 42}))
    
    assert not result.success
    assert result.error is not None
    assert "Missing required parameter" in result.error


def test_run_tool_exception_handling():
    """Test exception handling in tool execution."""
    tool = FailingTool()
    result = asyncio.run(run_tool(tool, {}))
    
    assert not result.success
    assert result.error == "Intentional failure"


def test_tool_result_dataclass():
    """Test ToolResult dataclass."""
    # Success result
    result = ToolResult(success=True, output="Success")
    assert result.success
    assert result.output == "Success"
    assert result.error is None
    
    # Failure result
    result = ToolResult(success=False, error="Failed")
    assert not result.success
    assert result.output is None
    assert result.error == "Failed"
    
    # Both output and error
    result = ToolResult(success=False, output="partial", error="error")
    assert not result.success
    assert result.output == "partial"
    assert result.error == "error"


def test_abstract_tool_cannot_be_instantiated():
    """Test that Tool base class cannot be instantiated directly."""
    with pytest.raises(TypeError) as exc_info:
        Tool()
    
    assert "Can't instantiate abstract class" in str(exc_info.value)