#!/bin/bash
set -e

echo "Installing BitterAgent..."

# Install Python and pip if not available
apt-get update
apt-get install -y python3 python3-pip

# Install BitterAgent from PyPI
# Use --break-system-packages to override PEP 668 protection in containers
pip3 install --break-system-packages bitteragent

# Verify installation
python3 -m pip show bitteragent || echo "Warning: BitterAgent module not found after installation"
python3 -c "import bitteragent" || echo "Warning: Cannot import bitteragent module"

echo "BitterAgent installation complete!"