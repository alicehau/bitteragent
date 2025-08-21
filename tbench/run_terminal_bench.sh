#!/bin/bash

# Script to run terminal-bench with bitteragent from within bitteragent directory
# Usage: ./tbench/run_terminal_bench.sh [task-id] [model]

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BITTERAGENT_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
TASK_ID="${1:-hello-world}"
MODEL="${2:-anthropic/claude-3-5-haiku-20241022}"

# Allow user to set TERMINAL_BENCH_DIR or default to ../terminal-bench
TERMINAL_BENCH_DIR="${TERMINAL_BENCH_DIR:-$(cd "$BITTERAGENT_DIR/../terminal-bench" 2>/dev/null && pwd)}"

if [ -z "$TERMINAL_BENCH_DIR" ] || [ ! -d "$TERMINAL_BENCH_DIR" ]; then
    echo "Error: terminal-bench directory not found. Please set TERMINAL_BENCH_DIR environment variable."
    exit 1
fi

# Source .env file from bitteragent to get API key
if [ -f "$BITTERAGENT_DIR/.env" ]; then
    source "$BITTERAGENT_DIR/.env"
else
    echo "Warning: .env file not found at $BITTERAGENT_DIR/.env"
fi

# Activate the terminal-bench virtual environment (Python 3.12)
if [ -f "$TERMINAL_BENCH_DIR/.venv/bin/activate" ]; then
    source "$TERMINAL_BENCH_DIR/.venv/bin/activate"
else
    echo "Error: terminal-bench venv not found at $TERMINAL_BENCH_DIR/.venv"
    echo "Please ensure terminal-bench is installed with Python 3.12+"
    exit 1
fi

# Add bitteragent to Python path so tinyagent and tbench can be imported
export PYTHONPATH="$BITTERAGENT_DIR:$PYTHONPATH"

# Change to terminal-bench directory (required for terminal-bench to work properly)
cd "$TERMINAL_BENCH_DIR"

# Run terminal-bench with the TinyAgent adapter
# Default to external adapter, but allow override with ADAPTER_TYPE env var
ADAPTER_TYPE="${ADAPTER_TYPE:-external}"

if [ "$ADAPTER_TYPE" = "installed" ]; then
    echo "Running terminal-bench with TinyAgent (installed mode)..."
    ADAPTER_PATH="tbench.terminal_bench_installed_adapter:TinyAgentInstalledAdapter"
else
    echo "Running terminal-bench with TinyAgent (external mode)..."
    ADAPTER_PATH="tbench.terminal_bench_adapter:TinyAgentAdapter"
fi

echo "Task: $TASK_ID"
echo "Model: $MODEL"
echo "Adapter: $ADAPTER_TYPE"

tb run \
    --agent-import-path "$ADAPTER_PATH" \
    --model "$MODEL" \
    --task-id "$TASK_ID" \
    --n-concurrent 1