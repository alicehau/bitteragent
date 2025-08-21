"""Terminal-bench installed agent adapter for TinyAgent."""
import os
import shlex
from pathlib import Path

from terminal_bench.agents.installed_agents.abstract_installed_agent import (
    AbstractInstalledAgent,
)
from terminal_bench.terminal.models import TerminalCommand


class TinyAgentInstalledAdapter(AbstractInstalledAgent):
    """Adapter to run TinyAgent as an installed agent in terminal-bench."""
    
    @staticmethod
    def name() -> str:
        return "tinyagent-installed"
    
    def __init__(self, model_name: str = "claude-3-5-haiku-20241022", **kwargs):
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
        
        self._provider = provider_str
        self._model = model
    
    @property
    def _env(self) -> dict[str, str]:
        """Environment variables to use when running the agent."""
        env = {}
        
        # Set API key based on provider
        if self._provider == "anthropic":
            env["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_API_KEY"]
            env["TINYAGENT_MODEL"] = self._model
            env["TINYAGENT_PROVIDER"] = "anthropic"
        elif self._provider == "openai":
            env["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]
            env["TINYAGENT_MODEL"] = self._model
            env["TINYAGENT_PROVIDER"] = "openai"
        else:
            raise ValueError(f"Unsupported provider: {self._provider}")
        
        return env
    
    @property
    def _install_agent_script_path(self) -> Path:
        """Script to install the agent in the container."""
        return Path(__file__).parent / "tinyagent-install.sh"
    
    def _run_agent_commands(self, instruction: str) -> list[TerminalCommand]:
        """Commands to run the agent with the given task instruction."""
        escaped_instruction = shlex.quote(instruction)
        
        # Run TinyAgent directly with the instruction using the 'run' command
        run_agent_command = TerminalCommand(
            command=f"python -m tinyagent run {escaped_instruction}",
            min_timeout_sec=0.0,
            max_timeout_sec=float("inf"),
            block=True,
            append_enter=True,
        )
        
        return [run_agent_command]