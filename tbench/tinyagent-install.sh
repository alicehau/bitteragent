#!/bin/bash
set -e

echo "Installing TinyAgent..."

# Install Python and pip if not available
apt-get update
apt-get install -y python3 python3-pip git

# Create a directory for TinyAgent installation
INSTALL_DIR="/opt/tinyagent"
mkdir -p $INSTALL_DIR

# Clone the TinyAgent repository
git clone https://github.com/alicehau/tinyagent.git $INSTALL_DIR

# Install TinyAgent and its dependencies globally without changing directory
pip install $INSTALL_DIR

echo "TinyAgent installation complete!"