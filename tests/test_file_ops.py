"""Tests for file operation tools."""
import asyncio
import os
import tempfile
from pathlib import Path

import pytest

from bitteragent.native_tools.file_ops import ReadFileTool, WriteFileTool, EditFileTool


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Line 1\nLine 2\nLine 3\n")
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_read_file_success(temp_file):
    """Test successful file reading."""
    tool = ReadFileTool()
    result = asyncio.run(tool.execute(file_path=temp_file))
    assert result.success
    assert result.output == "Line 1\nLine 2\nLine 3\n"


def test_read_file_with_limit(temp_file):
    """Test file reading with line limit."""
    tool = ReadFileTool()
    result = asyncio.run(tool.execute(file_path=temp_file, limit=2))
    assert result.success
    assert result.output == "Line 1\nLine 2\n"


def test_read_file_with_offset(temp_file):
    """Test file reading with offset."""
    tool = ReadFileTool()
    result = asyncio.run(tool.execute(file_path=temp_file, offset=1, limit=2))
    assert result.success
    assert result.output == "Line 2\nLine 3\n"


def test_read_file_not_found():
    """Test reading non-existent file."""
    tool = ReadFileTool()
    result = asyncio.run(tool.execute(file_path="/nonexistent/file.txt"))
    assert not result.success
    assert result.error == "File not found"


def test_write_file_success(temp_dir):
    """Test successful file writing."""
    tool = WriteFileTool()
    file_path = os.path.join(temp_dir, "test.txt")
    result = asyncio.run(tool.execute(file_path=file_path, content="Hello World"))
    
    assert result.success
    assert result.output == "written"
    
    # Verify file contents
    with open(file_path) as f:
        assert f.read() == "Hello World"


def test_write_file_creates_directory(temp_dir):
    """Test that write creates parent directories."""
    tool = WriteFileTool()
    file_path = os.path.join(temp_dir, "subdir", "test.txt")
    result = asyncio.run(tool.execute(file_path=file_path, content="Test"))
    
    assert result.success
    assert os.path.exists(file_path)


def test_write_file_overwrites(temp_file):
    """Test that write overwrites existing file."""
    tool = WriteFileTool()
    result = asyncio.run(tool.execute(file_path=temp_file, content="New content"))
    
    assert result.success
    with open(temp_file) as f:
        assert f.read() == "New content"


def test_edit_file_success(temp_file):
    """Test successful file editing."""
    tool = EditFileTool()
    result = asyncio.run(tool.execute(
        file_path=temp_file,
        old_string="Line 2",
        new_string="Modified Line"
    ))
    
    assert result.success
    assert "Replaced 1 occurrence(s)" in result.output
    
    with open(temp_file) as f:
        content = f.read()
        assert "Modified Line" in content
        assert "Line 2" not in content


def test_edit_file_replace_all(temp_file):
    """Test editing with replace_all."""
    # Create file with repeated content
    with open(temp_file, 'w') as f:
        f.write("foo bar\nfoo baz\nfoo qux")
    
    tool = EditFileTool()
    result = asyncio.run(tool.execute(
        file_path=temp_file,
        old_string="foo",
        new_string="hello",
        replace_all=True
    ))
    
    assert result.success
    assert "Replaced 3 occurrence(s)" in result.output
    
    with open(temp_file) as f:
        content = f.read()
        assert "foo" not in content
        assert content.count("hello") == 3


def test_edit_file_not_found():
    """Test editing non-existent file."""
    tool = EditFileTool()
    result = asyncio.run(tool.execute(
        file_path="/nonexistent/file.txt",
        old_string="old",
        new_string="new"
    ))
    
    assert not result.success
    assert result.error == "File not found"


def test_edit_file_string_not_found(temp_file):
    """Test editing when old_string not in file."""
    tool = EditFileTool()
    result = asyncio.run(tool.execute(
        file_path=temp_file,
        old_string="Nonexistent",
        new_string="New"
    ))
    
    assert not result.success
    assert "old_string not found in file" in result.error


def test_edit_file_same_strings(temp_file):
    """Test editing with identical old and new strings."""
    tool = EditFileTool()
    result = asyncio.run(tool.execute(
        file_path=temp_file,
        old_string="same",
        new_string="same"
    ))
    
    assert not result.success
    assert "cannot be the same" in result.error