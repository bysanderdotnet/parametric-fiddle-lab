#!/usr/bin/env sh
set -e

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MARKER_FILE="$SCRIPT_DIR/.deps_installed"

if [ -f "$MARKER_FILE" ]; then
  # We cannot use "exit 0" directly if sourced, but here it is executed.
  # So exit 0 is fine, but to avoid shell block, we will just use if-else.
  echo "Dependencies already installed. Skipping..."
else
  echo "Installing system dependencies..."

  sudo apt-get update
  sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    gmsh \
    libfuse2t64 \
    libwebkit2gtk-4.1-0

  touch "$MARKER_FILE"
  echo "System dependencies installed successfully."
fi
