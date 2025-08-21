"""Shell execution tool."""
from __future__ import annotations

import asyncio
from typing import Any, Dict

from .base import NativeTool
from ..tools import ToolResult


class ShellTool(NativeTool):
    name = "shell"
    description = "Execute shell commands. For file listing, use 'git ls-files' (respects .gitignore) or commands that exclude common unwanted files (.venv/, __pycache__/, .git/, etc.). For searching file contents, prefer 'rg' (ripgrep) for fast, smart searching that respects .gitignore automatically."
    parameters = {
        "type": "object",
        "properties": {
            "cmd": {"type": "string", "description": "Command to execute"},
            "timeout": {"type": "number", "description": "Timeout in seconds", "default": 30},
        },
        "required": ["cmd"],
    }

    async def execute(self, cmd: str, timeout: float | None = 30, **_: Any) -> ToolResult:
        # Auto-improve common file listing commands to respect .gitignore and exclude common unwanted files
        improved_cmd = self._improve_command(cmd)
        
        try:
            proc = await asyncio.create_subprocess_shell(
                improved_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            try:
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                proc.kill()
                return ToolResult(success=False, error="Command timed out")
            output = stdout.decode().strip()
            return ToolResult(success=True, output=output)
        except Exception as exc:  # pragma: no cover - defensive
            return ToolResult(success=False, error=str(exc))
    
    def _improve_command(self, cmd: str) -> str:
        """Improve common commands to exclude unwanted files and respect .gitignore."""
        cmd = cmd.strip()
        
        # Improve basic ls commands to use git ls-files when appropriate
        if cmd in ["ls", "ls .", "ls -la", "ls -la .", "ls -l", "ls -l ."]:
            return "git ls-files 2>/dev/null || find . -maxdepth 1 -type f -not -name '.*' | sort"
        
        # Improve recursive ls to use git ls-files
        if cmd in ["ls -R", "ls -la -R", "ls -laR", "find . -type f", "find . -name '*'"]:
            return "git ls-files 2>/dev/null || find . -type f -not -path './.git/*' -not -path './.venv/*' -not -path './venv/*' -not -path './*/__pycache__/*' -not -name '*.pyc' -not -name '*.pyo' -not -name '.DS_Store' -not -path './node_modules/*' -not -path './.pytest_cache/*' | sort"
        
        # Improve find commands that don't already have exclusions
        if cmd.startswith("find .") and "-not -path" not in cmd and "-prune" not in cmd:
            if "-type f" in cmd:
                # Add common exclusions to find commands looking for files
                base_find = cmd
                exclusions = " -not -path './.git/*' -not -path './.venv/*' -not -path './venv/*' -not -path './*/__pycache__/*' -not -name '*.pyc' -not -name '*.pyo' -not -name '.DS_Store' -not -path './node_modules/*' -not -path './.pytest_cache/*'"
                return base_find + exclusions
        
        return cmd
