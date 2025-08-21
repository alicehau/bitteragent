#!/bin/bash
set -e

echo "Installing TinyAgent from GitHub..."

# Install Python, pip, and git if not available
apt-get update
apt-get install -y python3 python3-pip git

# Install TinyAgent directly from GitHub
pip install git+https://github.com/alicehau/tinyagent.git

# Install additional dependencies if needed
pip install anthropic openai

echo "TinyAgent installation complete!"