"""File operation tools."""
from __future__ import annotations

import os
from typing import Any

from .base import NativeTool
from ..tools import ToolResult


class ReadFileTool(NativeTool):
    name = "read_file"
    description = "Read file contents"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "line_limit": {"type": "integer", "default": 1000},
        },
        "required": ["path"],
    }

    async def execute(self, path: str, line_limit: int = 1000, **_: Any) -> ToolResult:
        if not os.path.exists(path):
            return ToolResult(success=False, error="File not found")
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()[:line_limit]
            return ToolResult(success=True, output="".join(lines))
        except Exception as exc:  # pragma: no cover
            return ToolResult(success=False, error=str(exc))


class WriteFileTool(NativeTool):
    name = "write_file"
    description = "Write content to file"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"},
            "append": {"type": "boolean", "default": False},
        },
        "required": ["path", "content"],
    }

    async def execute(self, path: str, content: str, append: bool = False, **_: Any) -> ToolResult:
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            mode = "a" if append else "w"
            with open(path, mode, encoding="utf-8") as f:
                f.write(content)
            return ToolResult(success=True, output="written")
        except Exception as exc:  # pragma: no cover
            return ToolResult(success=False, error=str(exc))


class EditFileTool(NativeTool):
    name = "edit_file"
    description = "Find and replace within a file"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "find": {"type": "string"},
            "replace": {"type": "string"},
            "dry_run": {"type": "boolean", "default": False},
        },
        "required": ["path", "find", "replace"],
    }

    async def execute(self, path: str, find: str, replace: str, dry_run: bool = False, **_: Any) -> ToolResult:
        if not os.path.exists(path):
            return ToolResult(success=False, error="File not found")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = content.replace(find, replace)
            if not dry_run:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
            return ToolResult(success=True, output=new_content)
        except Exception as exc:  # pragma: no cover
            return ToolResult(success=False, error=str(exc))
