#!/usr/bin/env python3
"""Command-line interface for TinyAgent."""
import argparse
import asyncio
import os
import sys
from pathlib import Path

from .agent import Agent
from .providers.anthropic import AnthropicProvider
from .tools import ToolRegistry
from .native_tools.shell import ShellTool
from .native_tools.file_ops import ReadFileTool, WriteFileTool, EditFileTool


async def main_async(task: str):
    """Main async function to run the agent."""
    # Get configuration from environment
    provider_name = os.getenv("TINYAGENT_PROVIDER", "anthropic")
    model = os.getenv("TINYAGENT_MODEL", "claude-3-5-sonnet-20241022")
    
    # Initialize provider
    if provider_name == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
            sys.exit(1)
        provider = AnthropicProvider(api_key=api_key, model=model)
    else:
        print(f"Error: Unsupported provider: {provider_name}", file=sys.stderr)
        sys.exit(1)
    
    # Create tool registry
    registry = ToolRegistry()
    
    # Register tools
    registry.register(ShellTool())
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(EditFileTool())
    
    # Create system prompt
    system_prompt = """You are an AI assistant helping to complete a task in a terminal environment.
You have access to bash commands and file operations. Complete the task efficiently and directly.
Focus on completing the task successfully. Use the tools available to you."""
    
    # Create and run agent
    agent = Agent(
        provider=provider,
        registry=registry,
        system_prompt=system_prompt
    )
    
    try:
        # Run the agent
        response = await agent.run(task)
        print(f"Task completed. Final response: {response}")
        return 0
    except Exception as e:
        print(f"Error executing task: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Run TinyAgent with a task")
    parser.add_argument(
        "--task",
        type=str,
        help="Task instruction to execute"
    )
    parser.add_argument(
        "--task-file",
        type=str,
        help="File containing the task instruction"
    )
    
    args = parser.parse_args()
    
    # Get task from arguments
    if args.task:
        task = args.task
    elif args.task_file:
        with open(args.task_file, 'r') as f:
            task = f.read().strip()
    else:
        print("Error: Either --task or --task-file must be provided", file=sys.stderr)
        sys.exit(1)
    
    # Run the async main
    exit_code = asyncio.run(main_async(task))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()