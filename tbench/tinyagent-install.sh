#!/bin/bash
set -e

echo "Installing TinyAgent..."

# Install Python and pip if not available
apt-get update
apt-get install -y python3 python3-pip git

# Install TinyAgent directly from GitHub (until published to PyPI)
# Use --break-system-packages to override PEP 668 protection in containers
pip3 install --break-system-packages "git+https://github.com/alicehau/tinyagent.git"

# Alternative: When published to PyPI, use:
# pip3 install --break-system-packages tinyagent

# Verify installation
python3 -m pip show tinyagent || echo "Warning: TinyAgent module not found after installation"
python3 -c "import tinyagent" || echo "Warning: Cannot import tinyagent module"

echo "TinyAgent installation complete!"