#!/bin/bash

# Script to run terminal-bench with bitteragent
# Usage: ./tbench/run_terminal_bench.sh [task-id] [model]
#
# Requires:
#   - terminal-bench installed: pip install terminal-bench
#   - bitteragent installed: pip install bitteragent
#   - ANTHROPIC_API_KEY environment variable set

# Parse arguments - all are optional
TASK_ID=""
MODEL="anthropic/claude-sonnet-4-20250514"

# Process arguments
if [ $# -ge 1 ] && [ -n "$1" ]; then
    TASK_ID="$1"
fi

if [ $# -ge 2 ] && [ -n "$2" ]; then
    MODEL="$2"
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable is not set"
    echo "Please set it with: export ANTHROPIC_API_KEY=your-key-here"
    exit 1
fi

# Run terminal-bench with the BitterAgent installed adapter
echo "Running terminal-bench with BitterAgent..."
echo "Model: $MODEL"

# Add current directory's parent to PYTHONPATH so tbench module can be imported
# This assumes the script is run from within the bitteragent repo
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$(dirname "$SCRIPT_DIR"):$PYTHONPATH"

ADAPTER_PATH="tbench.terminal_bench_installed_adapter:BitterAgentInstalledAdapter"

# Build the tb run command
TB_CMD="tb run --dataset terminal-bench-core==head --agent-import-path $ADAPTER_PATH --model $MODEL --n-concurrent 1"

# Add task ID if specified
if [ -n "$TASK_ID" ]; then
    echo "Task ID: $TASK_ID"
    TB_CMD="$TB_CMD --task-id $TASK_ID"
else
    echo "Running all tasks..."
fi

# Execute the command
eval $TB_CMD