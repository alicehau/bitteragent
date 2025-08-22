#!/bin/bash

# Script to run only easy-tagged tasks in terminal-bench
# Usage: ./tbench/run_easy_tasks.sh [model]

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run terminal-bench with easy task filter
echo "Running all easy-tagged tasks..."

# Pass model as first argument if provided, otherwise use script's default
if [ -n "$1" ]; then
    "$SCRIPT_DIR/run_terminal_bench.sh" "" "$1" "easy"
else
    # Just pass empty for task_id and "easy" for filter, let script use default model
    "$SCRIPT_DIR/run_terminal_bench.sh" "" "" "easy"
fi