"""Command line interface for TinyAgent."""
import asyncio
import os
import json
import logging
from typing import Any, Dict, Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.logging import RichHandler

from .agent import Agent
from .tools import ToolRegistry, ToolResult
from .native_tools.shell import ShellTool
from .native_tools.file_ops import ReadFileTool, WriteFileTool, EditFileTool
from .providers.anthropic import AnthropicProvider

load_dotenv()

console = Console()

# Setup logging with Rich handler for pretty output
logging.basicConfig(
    level=logging.ERROR,
    format="%(message)s",
    handlers=[RichHandler(console=console, show_time=False, show_path=False)]
)


def create_tool_callback() -> callable:
    """Create a callback function to display tool execution in real-time."""
    def tool_callback(tool_name: str, params: Dict[str, Any], result: Optional[ToolResult]) -> None:
        if result is None:
            # Tool call starting
            params_str = json.dumps(params, indent=2) if params else "{}"
            console.print(f"\n[bold blue]🔧 Calling tool:[/bold blue] {tool_name}")
            if params:
                console.print(Panel(
                    Syntax(params_str, "json", theme="monokai", line_numbers=False),
                    title="Parameters",
                    border_style="blue"
                ))
        else:
            # Tool execution completed
            if result.success:
                console.print(f"[bold green]✅ Tool completed successfully[/bold green]")
                if result.output:
                    # Determine if output looks like code/structured data
                    output = result.output.strip()
                    if (output.startswith('{') and output.endswith('}')) or \
                       (output.startswith('[') and output.endswith(']')):
                        # JSON-like output
                        console.print(Panel(
                            Syntax(output, "json", theme="monokai", line_numbers=False),
                            title="Result",
                            border_style="green"
                        ))
                    elif '\n' in output and len(output) > 100:
                        # Multi-line output
                        console.print(Panel(
                            output,
                            title="Result",
                            border_style="green"
                        ))
                    else:
                        # Short output
                        console.print(f"[green]Result: {output}[/green]")
            else:
                console.print(f"[bold red]❌ Tool failed[/bold red]")
                if result.error:
                    console.print(f"[red]Error: {result.error}[/red]")
    
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
    console.print(f"\n[bold]Agent:[/bold] {result}")


@cli.command()
def chat() -> None:
    """Start an interactive chat session."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise click.UsageError("ANTHROPIC_API_KEY environment variable is required")
    
    provider = AnthropicProvider(api_key=api_key)
    agent = Agent(provider=provider, registry=build_registry(), tool_callback=create_tool_callback())
    
    console.print("[bold]Starting chat session[/bold] (type 'exit' or 'quit' to end)")
    console.print("-" * 50)
    
    while True:
        try:
            # Use rich console for consistent formatting
            user_input = console.input("\n[bold cyan]You:[/bold cyan] ")
            
            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold]Goodbye![/bold]")
                break
            
            if not user_input.strip():
                continue
                
            result = asyncio.run(agent.run(user_input))
            console.print(f"\n[bold]Agent:[/bold] {result}")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold]Goodbye![/bold]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}")


@cli.command()
def tools() -> None:
    """List available tools."""
    registry = build_registry()
    for tool in registry.tools.values():
        click.echo(f"{tool.name}: {tool.description}")


if __name__ == "__main__":
    cli()
