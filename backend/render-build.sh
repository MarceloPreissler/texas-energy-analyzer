#!/usr/bin/env bash
# Render.com build script for Texas Energy Analyzer backend

set -e  # Exit on error

echo "=== Render Build Script ==="
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright..."
playwright install chromium

echo "Installing Playwright system dependencies..."
playwright install-deps chromium

echo "Build complete!"
