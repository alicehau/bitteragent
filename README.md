# TinyAgent - Minimal Python CLI Agent

A ultra-minimal, extensible Python CLI agent with native tools for shell execution and file operations.

## Architecture Overview

### Design Principles
- **Single-file core** with modular extensions
- **Async-aware** for parallel tool execution and streaming
- **Tool-first architecture** with simple registry pattern
- **Direct Anthropic API integration** (no abstraction layers initially)
- **Minimal dependencies** (anthropic, click, rich for UI, asyncio)

### Project Structure

```
tinyagent/
├── pyproject.toml          # Modern Python packaging with uv
├── uv.lock                 # Lock file for reproducible builds
├── README.md               # This file
├── .env.example            # API key configuration
├── .python-version        # Python version for uv
├── system.md               # Default system prompt (optional)
├── tinyagent/
│   ├── __init__.py
│   ├── __main__.py        # CLI entry point
│   ├── agent.py           # Core agent loop & conversation
│   ├── tools.py           # Tool base class & registry
│   ├── providers/         # LLM providers
│   │   ├── __init__.py
│   │   ├── base.py        # Base provider interface
│   │   ├── anthropic.py   # Anthropic Claude provider
│   │   └── openai.py      # OpenAI provider (future)
│   ├── adapters/          # Tool format adapters
│   │   ├── __init__.py
│   │   ├── anthropic.py   # Anthropic tool format
│   │   ├── openai.py      # OpenAI function format
│   │   └── base.py        # Base adapter interface
│   └── native_tools/      # Built-in tools
│       ├── __init__.py
│       ├── shell.py       # Shell execution tool
│       ├── file_ops.py    # Read/write file tools
│       └── base.py        # Base tool implementation
└── tests/
    └── test_agent.py
```

## Core Components

### 1. Tool System
- **Base Tool Class**: Abstract class defining tool interface
  - `name`: Tool identifier
  - `description`: Human-readable description
  - `parameters`: JSON Schema for tool parameters
  - `execute()`: Method to run the tool
- **ToolRegistry**: Manages tool registration and discovery
  - Register built-in tools on startup
  - Lookup tools by name
  - **Format adapters** for different tool schemas:
    - `to_anthropic_schema()`: Convert to Anthropic tool format
    - `to_openai_schema()`: Convert to OpenAI function format
    - `to_mcp_schema()`: Convert to MCP tool format
    - `to_langchain_schema()`: Convert to LangChain tool format
  - Extensible adapter pattern for new formats
- **ToolResult**: Structured response from tool execution
  - `success`: Boolean status
  - `output`: Tool output/result
  - `error`: Error message if failed

### 2. Provider Interface
- **Provider ABC**: Abstract base for LLM providers in `providers/base.py`
  - `complete(messages, tools)`: Generate completion with tool support
  - Provider-specific configuration
  - **Built-in retry logic** with exponential backoff
  - **Error handling** for rate limits, timeouts, API errors
- **AnthropicProvider**: Implementation using Anthropic SDK in `providers/anthropic.py`
  - Handle streaming responses
  - Process tool use blocks
  - Return structured responses
  - Auto-retry on 429/500/502/503 errors
  - Configurable max retries and timeout
- **Extensible**: Easy to add OpenAI, Ollama, or other providers

### 3. Agent Core
- **Conversation Management**
  - Maintain message history
  - Handle user input
  - Process model responses
  - **System prompt loading** from `system.md` file
- **Tool Execution Loop**
  - Parse tool calls from model
  - **Parallel execution** for multiple tool calls (using asyncio/threads)
  - Execute tools with parameters
  - Return results to model in order

### 4. Native Tools

#### ShellTool
- Execute shell commands
- Features:
  - Timeout support (default 30s)
  - Streaming output capture
  - Working directory management

#### ReadFileTool
- Read file contents
- Features:
  - Line limit support (default 1000)
  - Binary file detection
  - Error handling for missing files

#### WriteFileTool
- Write content to files
- Features:
  - Create parent directories
  - Overwrite/append modes

#### EditFileTool
- Simple find-and-replace in files
- Features:
  - Exact string matching
  - Multiple replacements
  - Dry-run mode

### 5. CLI Interface
- **Commands**
  - `chat`: Interactive conversation mode
  - `run`: Execute single command
  - `tools`: List available tools
- **Options**
  - `--api-key`: Anthropic API key
  - `--model`: Model selection (claude-3-opus, etc.)
  - `--system-prompt`: Path to system.md file (default: ./system.md if exists)
  - `--verbose`: Debug logging

## Implementation Plan

### Phase 1: Core Foundation ✓
1. Design minimal architecture
2. Create project structure
3. Setup packaging (pyproject.toml)

### Phase 2: Basic Implementation
1. Implement Tool base class and registry
2. Create Anthropic provider
3. Build agent conversation loop
4. Add CLI entry point

### Phase 3: Native Tools
1. Implement ShellTool
2. Add file read/write tools
3. Create edit/replace tool

### Phase 4: Polish
1. Add error handling and retries
2. Implement logging system
3. Create configuration management
4. Write basic tests

### Phase 5: Extensions (Future)
1. Plugin system for custom tools
2. MCP client support
3. Additional providers (OpenAI, Ollama)
4. Conversation persistence

## Key Design Decisions

### Why Minimal?
- **Simplicity**: Easy to understand and modify
- **Debuggability**: Clear execution flow
- **Extensibility**: Clean interfaces for adding features
- **Performance**: No unnecessary abstractions

### Tool-First Approach
Following patterns from analyzed agents (Codex, Gemini CLI, Goose):
- Tools are first-class citizens
- Registry pattern for discovery
- Structured tool results
- Clear tool/agent separation

### Native Tools Only (Initially)
- Start with essential tools (shell, file ops)
- No MCP dependency initially
- Focus on core functionality
- MCP can be added later as plugin

### Async for Parallelism
- Tools execute in parallel when multiple are called
- Better performance for I/O bound operations
- Maintains order of results for model
- Uses asyncio for concurrency

## Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/tinyagent.git
cd tinyagent

# Install dependencies with uv
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API key
```

## Usage Examples

```bash
# Interactive chat
uv run python -m tinyagent chat

# Run single command
uv run python -m tinyagent run "Create a Python hello world script"

# List available tools
uv run python -m tinyagent tools

# With specific model
uv run python -m tinyagent chat --model claude-3-opus-20240229

# With custom system prompt
uv run python -m tinyagent chat --system-prompt ./custom-prompt.md
```

## Configuration

```bash
# .env file
ANTHROPIC_API_KEY=your-api-key-here
TINYAGENT_MODEL=claude-3-opus-20240229
TINYAGENT_SYSTEM_PROMPT=./system.md
TINYAGENT_MAX_RETRIES=3
TINYAGENT_TIMEOUT=120
```

### System Prompt (system.md)

Create a `system.md` file in your project root to customize the agent's behavior:

```markdown
# System Prompt

You are a helpful AI assistant with access to tools for file operations and shell commands.

## Guidelines
- Be concise and clear in responses
- Execute tasks efficiently
- Provide helpful explanations when needed

## Capabilities
- File system operations (read, write, edit)
- Shell command execution
- Parallel tool execution for efficiency
```

## Requirements

- Python 3.11+
- uv (package manager)
- anthropic SDK
- click (CLI framework)
- rich (terminal formatting)
- python-dotenv (configuration)

## License

MIT

## Contributing

This is a minimal reference implementation. Feel free to fork and extend!