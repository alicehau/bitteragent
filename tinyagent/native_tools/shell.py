"""Shell execution tool."""
from __future__ import annotations

import asyncio
from typing import Any, Dict

from .base import NativeTool
from ..tools import ToolResult


class ShellTool(NativeTool):
    name = "shell"
    description = """Execute shell commands. Best practices:
- For file listing: use 'git ls-files' (respects .gitignore) or 'find' with exclusions for .venv/, __pycache__/, .git/, node_modules/, .pytest_cache/, etc.
- For searching file contents: prefer 'rg' (ripgrep) which is fast and automatically respects .gitignore
- For directory traversal: exclude common build/cache directories to avoid noise
- Use specific file extensions or patterns when possible to narrow results
- Consider using tools like 'fd' for file finding as an alternative to 'find'"""
    parameters = {
        "type": "object",
        "properties": {
            "cmd": {"type": "string", "description": "Command to execute"},
            "timeout": {"type": "number", "description": "Timeout in seconds", "default": 30},
        },
        "required": ["cmd"],
    }

    async def execute(self, cmd: str, timeout: float | None = 30, **_: Any) -> ToolResult:
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
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

