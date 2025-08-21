#!/bin/bash
set -e

echo "Installing TinyAgent..."

# Install Python and pip if not available
apt-get update
apt-get install -y python3 python3-pip git

# Install TinyAgent from the mounted directory
# The bitteragent directory should be mounted at /opt/bitteragent by terminal-bench
if [ -d "/opt/bitteragent" ]; then
    cd /opt/bitteragent
    pip install -e .
elif [ -d "/app/bitteragent" ]; then
    cd /app/bitteragent
    pip install -e .
else
    echo "Error: bitteragent directory not found in expected locations"
    echo "Please ensure bitteragent is properly mounted in the container"
    exit 1
fi

echo "TinyAgent installation complete!"