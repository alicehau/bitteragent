# Terminal-bench Integration for BitterAgent

This directory contains the terminal-bench adapter for BitterAgent.

## Setup

1. Install required packages:
   ```bash
   pip install terminal-bench
   pip install bitteragent
   ```

2. Set your API key:
   ```bash
   export ANTHROPIC_API_KEY=your-key-here
   ```

## Usage

From the bitteragent repository directory, run:

```bash
# Run all tasks with default model
./tbench/run_terminal_bench.sh

# Run a specific task
./tbench/run_terminal_bench.sh simple-server

# Run with a specific task and model
./tbench/run_terminal_bench.sh simple-server anthropic/claude-3-5-sonnet-20241022
```

## How it Works

BitterAgent runs as an installed agent inside the terminal-bench container. The agent is installed from PyPI and executes directly in the container environment, using its native tools to interact with the system.

## Files

- `terminal_bench_installed_adapter.py` - The BitterAgent adapter that implements the terminal-bench AbstractInstalledAgent interface
- `run_terminal_bench.sh` - Shell script to run terminal-bench with proper environment setup
- `bitteragent-install.sh` - Installation script for BitterAgent in terminal-bench containers (installs from PyPI)

## Requirements

- `ANTHROPIC_API_KEY` environment variable must be set
- Python 3.11+ 
- terminal-bench installed
- bitteragent installed (or available in PYTHONPATH for development)