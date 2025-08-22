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
            "file_path": {
                "type": "string",
                "description": "The absolute path to the file to read (must be absolute, not relative)"
            },
            "limit": {
                "type": "integer", 
                "description": "Optional number of lines to read (default: 1000)",
                "default": 1000
            },
            "offset": {
                "type": "integer",
                "description": "Optional line number to start reading from (default: 0)",
                "default": 0
            },
        },
        "required": ["file_path"],
    }

    async def execute(self, file_path: str, limit: int = 1000, offset: int = 0, **_: Any) -> ToolResult:
        if not os.path.exists(file_path):
            return ToolResult(success=False, error="File not found")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                lines = lines[offset:offset + limit] if offset > 0 else lines[:limit]
            return ToolResult(success=True, output="".join(lines))
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class WriteFileTool(NativeTool):
    name = "write_file"
    description = "Write content to a file (will overwrite existing file)"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The absolute path to the file to write (must be absolute, not relative)"
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file"
            },
        },
        "required": ["file_path", "content"],
    }

    async def execute(self, file_path: str, content: str, **_: Any) -> ToolResult:
        try:
            os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return ToolResult(success=True, output="written")
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class EditFileTool(NativeTool):
    name = "edit_file"
    description = "Perform exact string replacements in a file"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to modify (preferrably absolute path)"
            },
            "old_string": {
                "type": "string",
                "description": "The exact text to replace (must match exactly including whitespace)"
            },
            "new_string": {
                "type": "string",
                "description": "The text to replace it with (must be different from old_string)"
            },
            "replace_all": {
                "type": "boolean",
                "description": "Replace all occurrences of old_string (default: false - replaces only first occurrence)",
                "default": False
            },
        },
        "required": ["file_path", "old_string", "new_string"],
    }

    async def execute(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False, **_: Any) -> ToolResult:
        if not os.path.exists(file_path):
            return ToolResult(success=False, error="File not found")
        if old_string == new_string:
            return ToolResult(success=False, error="old_string and new_string cannot be the same")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if old_string not in content:
                return ToolResult(success=False, error="old_string not found in file")
            
            if replace_all:
                new_content = content.replace(old_string, new_string)
            else:
                new_content = content.replace(old_string, new_string, 1)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            count = content.count(old_string)
            replaced = count if replace_all else 1
            return ToolResult(success=True, output=f"Replaced {replaced} occurrence(s)")
        except Exception as exc: 
            return ToolResult(success=False, error=str(exc))
