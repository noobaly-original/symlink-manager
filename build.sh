#!/bin/bash
# Build script for macOS and Linux

set -e

echo "==========================================="
echo "  Symlink Manager - Build Script"
echo "==========================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it with: uv venv"
    exit 1
fi

# Run the build
.venv/bin/python build_executable.py
