"""Command line interface for TinyAgent."""
import asyncio
import os
import json
import logging
from typing import Any, Dict, Optional

import click
from dotenv import load_dotenv

from .agent import Agent
from .tools import ToolRegistry, ToolResult
from .native_tools.shell import ShellTool
from .native_tools.file_ops import ReadFileTool, WriteFileTool, EditFileTool
from .providers.anthropic import AnthropicProvider

load_dotenv()

# Setup simple logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(message)s"
)


def create_tool_callback() -> callable:
    """Create a callback function to display tool execution in real-time."""
    def tool_callback(tool_name: str, params: Dict[str, Any], result: Optional[ToolResult]) -> None:
        if result is None:
            # Tool call starting - be concise
            params_str = json.dumps(params) if params else ""
            if params_str:
                print(f"{tool_name}: {params_str}")
            else:
                print(f"{tool_name}")
        else:
            # Tool execution completed - show failures and short outputs
            if not result.success:
                print(f"Tool call failed: {result.error}")
            elif result.output and len(result.output.strip()) < 200:
                # Only show short outputs inline
                print(result.output.strip())
    
    return tool_callback


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ShellTool())
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(EditFileTool())
    return registry


@click.group()
def cli() -> None:
    """TinyAgent CLI."""
    pass


@cli.command()
@click.argument("prompt")
def run(prompt: str) -> None:
    """Run a single prompt and print the response."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise click.UsageError("ANTHROPIC_API_KEY environment variable is required")
    provider = AnthropicProvider(api_key=api_key)
    agent = Agent(provider=provider, registry=build_registry(), tool_callback=create_tool_callback())
    result = asyncio.run(agent.run(prompt))
    print(f"\nAgent: {result}")


@cli.command()
def chat() -> None:
    """Start an interactive chat session."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise click.UsageError("ANTHROPIC_API_KEY environment variable is required")
    
    provider = AnthropicProvider(api_key=api_key)
    agent = Agent(provider=provider, registry=build_registry(), tool_callback=create_tool_callback())
    
    print("Starting chat session (type 'exit' or 'quit' to end)")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue
                
            result = asyncio.run(agent.run(user_input))
            print(f"\nAgent: {result}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


@cli.command()
def tools() -> None:
    """List available tools."""
    registry = build_registry()
    for tool in registry.tools.values():
        click.echo(f"{tool.name}: {tool.description}")


if __name__ == "__main__":
    cli()
