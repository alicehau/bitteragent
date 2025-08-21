# Terminal-bench Integration for TinyAgent

This directory contains the terminal-bench adapter for TinyAgent.

## Setup

1. Ensure terminal-bench is installed in a sibling directory (`../terminal-bench`) or set the `TERMINAL_BENCH_DIR` environment variable to point to your terminal-bench installation.

2. Ensure terminal-bench has a Python 3.12+ virtual environment set up:
   ```bash
   cd ../terminal-bench
   python3.12 -m venv .venv
   .venv/bin/pip install -e .
   ```

3. Create a `.env` file in the bitteragent root directory with your API key:
   ```bash
   echo "ANTHROPIC_API_KEY=your-key-here" > ../.env
   ```

## Usage

From the bitteragent directory, run:

```bash
# Run with default task (hello-world) and model (external mode)
./tbench/run_terminal_bench.sh

# Run with a specific task
./tbench/run_terminal_bench.sh simple-server

# Run with a specific task and model
./tbench/run_terminal_bench.sh simple-server anthropic/claude-3-5-sonnet-20241022

# Run in installed mode (agent runs inside container)
ADAPTER_TYPE=installed ./tbench/run_terminal_bench.sh hello-world

# Run in external mode (default - agent runs on host)
ADAPTER_TYPE=external ./tbench/run_terminal_bench.sh hello-world
```

## Adapter Modes

TinyAgent can run in two modes:

1. **External Mode** (default): TinyAgent runs on the host and sends commands to the container via tmux. This is easier to debug but requires the TmuxShellTool wrapper.

2. **Installed Mode**: TinyAgent is installed inside the container from GitHub and runs directly. This is more realistic but harder to debug. The agent's native tools work directly in the container.

## Files

- `terminal_bench_adapter.py` - The TinyAgent adapter that implements the terminal-bench BaseAgent interface
- `run_terminal_bench.sh` - Shell script to run terminal-bench with proper environment setup
- `tinyagent-setup.sh` - Installation script for TinyAgent in terminal-bench containers (for installed agent mode)

## Environment Variables

- `TERMINAL_BENCH_DIR` - Path to terminal-bench installation (defaults to `../terminal-bench`)
- `ANTHROPIC_API_KEY` - Your Anthropic API key (loaded from `.env` file)