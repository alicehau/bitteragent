#!/bin/bash

# Script to run terminal-bench with bitteragent from within bitteragent directory
# Usage: ./tbench/run_terminal_bench.sh [task-id] [model]

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BITTERAGENT_DIR="$(dirname "$SCRIPT_DIR")"

# Parse arguments - all are optional
TASK_ID=""
MODEL="anthropic/claude-sonnet-4-20250514"
TASK_FILTER=""

# Process arguments
if [ $# -ge 1 ] && [ -n "$1" ]; then
    TASK_ID="$1"
fi

if [ $# -ge 2 ] && [ -n "$2" ]; then
    MODEL="$2"
fi

if [ $# -ge 3 ] && [ -n "$3" ]; then
    TASK_FILTER="$3"
fi

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

echo "Model: $MODEL"
echo "Adapter: $ADAPTER_TYPE"

# Build the tb run command
TB_CMD="tb run --dataset terminal-bench-core==head --agent-import-path $ADAPTER_PATH --model $MODEL --n-concurrent 1"

# Handle task filtering
if [ -n "$TASK_FILTER" ]; then
    if [ "$TASK_FILTER" = "easy" ]; then
        echo "Getting list of easy tasks..."
        EASY_TASKS=$(python3 "$SCRIPT_DIR/get_easy_tasks.py")
        echo "Found easy tasks: $EASY_TASKS"
        for task in $EASY_TASKS; do
            TB_CMD="$TB_CMD --task-id $task"
        done
    else
        echo "Unknown task filter: $TASK_FILTER"
        exit 1
    fi
elif [ -n "$TASK_ID" ]; then
    echo "Task ID: $TASK_ID"
    TB_CMD="$TB_CMD --task-id $TASK_ID"
else
    echo "Running all tasks..."
fi

# Execute the command
eval $TB_CMD
