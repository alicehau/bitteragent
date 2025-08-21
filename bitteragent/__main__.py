"""Command line interface for BitterAgent."""
import asyncio
import os

import click
from dotenv import load_dotenv

from .agent import Agent
from .tools import ToolRegistry
from .native_tools.shell import ShellTool
from .native_tools.file_ops import ReadFileTool, WriteFileTool, EditFileTool
from .providers.anthropic import AnthropicProvider

load_dotenv()


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ShellTool())
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(EditFileTool())
    return registry


@click.group()
def cli() -> None:
    """BitterAgent CLI."""
    pass


@cli.command()
@click.argument("prompt")
def run(prompt: str) -> None:
    """Run a single prompt and print the response."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise click.UsageError("ANTHROPIC_API_KEY environment variable is required")
    provider = AnthropicProvider(api_key=api_key)
    agent = Agent(provider=provider, registry=build_registry())
    result = asyncio.run(agent.run(prompt))
    click.echo(result)


@cli.command()
def tools() -> None:
    """List available tools."""
    registry = build_registry()
    for tool in registry.tools.values():
        click.echo(f"{tool.name}: {tool.description}")


if __name__ == "__main__":
    cli()
