# BitterAgent - Minimal Python CLI Agent

A ultra-minimal, extensible Python CLI agent with native tools for shell execution and file operations.

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
- ShellTool
- ReadFileTool
- WriteFileTool
- EditFileTool

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

## Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/bitteragent.git
cd bitteragent

# Install dependencies with uv
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API key
```

## Usage Examples

```bash
# Interactive chat
uv run python -m bitteragent chat

# Run single command
uv run python -m bitteragent run "Create a Python hello world script"

# List available tools
uv run python -m bitteragent tools

# With specific model
uv run python -m bitteragent chat --model claude-3-opus-20240229

# With custom system prompt
uv run python -m bitteragent chat --system-prompt ./custom-prompt.md
```

## Configuration

```bash
# .env file
ANTHROPIC_API_KEY=your-api-key-here
```

## License

MIT

## Contributing

This is a minimal reference implementation. Feel free to fork and extend!