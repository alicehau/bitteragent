"""Terminal-bench adapter for TinyAgent."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict

from terminal_bench.agents.base_agent import AgentResult, BaseAgent
from terminal_bench.agents.failure_mode import FailureMode
from terminal_bench.terminal.tmux_session import TmuxSession

from tinyagent.agent import Agent
from tinyagent.providers.anthropic import AnthropicProvider
from tinyagent.tools import ToolRegistry, Tool, ToolResult
from tinyagent.native_tools.file_ops import ReadFileTool, WriteFileTool, EditFileTool


class TinyAgentAdapter(BaseAgent):
    """Adapter to run TinyAgent in Terminal-bench."""
    
    @staticmethod
    def name() -> str:
        return "tinyagent"
    
    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", **kwargs):
        """Initialize the TinyAgent adapter.
        
        Args:
            model_name: Model to use (format: provider/model or just model)
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(**kwargs)
        
        # Parse model name
        if "/" in model_name:
            provider_str, model = model_name.split("/", 1)
        else:
            # Default to anthropic
            provider_str = "anthropic"
            model = model_name
        
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        # Initialize provider (currently only Anthropic supported)
        if provider_str == "anthropic":
            self.provider = AnthropicProvider(api_key=api_key, model=model)
        else:
            raise ValueError(f"Unsupported provider: {provider_str}")
        
        # Track tokens
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def perform_task(
        self,
        instruction: str,
        session: TmuxSession,
        logging_dir: Path | None = None,
    ) -> AgentResult:
        """Perform a task using TinyAgent.
        
        Args:
            instruction: The task instruction
            session: The tmux session to interact with
            logging_dir: Optional directory for logging
            
        Returns:
            AgentResult with token counts and failure mode
        """
        # Reset token counts
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        
        # Create tool registry with shell tool that uses tmux session
        registry = ToolRegistry()
        
        # Create a shell tool that interacts with the tmux session
        class TmuxShellTool(Tool):
            def __init__(self, tmux_session: TmuxSession):
                self.name = "bash"
                self.description = "Execute a bash command in the terminal"
                self.parameters = {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute"
                        }
                    },
                    "required": ["command"]
                }
                self.session = tmux_session
            
            async def execute(self, command: str) -> ToolResult:
                """Execute a command in the tmux session."""
                try:
                    # Send command to tmux session
                    self.session.send_keys([command, "Enter"], block=True)
                    
                    # Get output from the session
                    # Note: This is a simplified version - in production you'd want
                    # to capture the actual output from the session
                    output = self.session.capture_pane()
                    
                    return ToolResult(success=True, output=output)
                except Exception as e:
                    return ToolResult(success=False, error=str(e))
        
        # Register the tmux shell tool
        registry.register(TmuxShellTool(session))
        
        # Also register file operation tools
        registry.register(ReadFileTool())
        registry.register(WriteFileTool())
        registry.register(EditFileTool())
        
        # Create system prompt
        system_prompt = f"""You are an AI assistant helping to complete a task in a terminal environment.
        
Task: {instruction}

You have access to bash commands and file operations. Complete the task by using the available tools.
Be efficient and direct in your approach."""
        
        # Create agent
        agent = Agent(
            provider=self.provider,
            registry=registry,
            system_prompt=system_prompt
        )
        
        try:
            # Run the agent synchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Start the agent with the task
                response = loop.run_until_complete(agent.run("Please complete this task."))
                
                # Log if requested
                if logging_dir:
                    log_file = logging_dir / "agent_log.json"
                    log_data = {
                        "instruction": instruction,
                        "messages": agent.messages,
                        "response": response
                    }
                    log_file.write_text(json.dumps(log_data, indent=2))
                
                # Extract token counts from provider if available
                if hasattr(self.provider, 'total_input_tokens'):
                    self.total_input_tokens = self.provider.total_input_tokens
                if hasattr(self.provider, 'total_output_tokens'):
                    self.total_output_tokens = self.provider.total_output_tokens
                
                return AgentResult(
                    total_input_tokens=self.total_input_tokens,
                    total_output_tokens=self.total_output_tokens,
                    failure_mode=FailureMode.NONE
                )
                
            finally:
                loop.close()
                
        except Exception as e:
            # Log error if requested
            if logging_dir:
                error_file = logging_dir / "error.txt"
                error_file.write_text(str(e))
            
            return AgentResult(
                total_input_tokens=self.total_input_tokens,
                total_output_tokens=self.total_output_tokens,
                failure_mode=FailureMode.FATAL_ERROR
            )