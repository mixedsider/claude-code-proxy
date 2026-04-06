#!/bin/bash

# anthropic-proxy Execution Script for Linux/macOS
set -e

if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please run ./install.sh first."
    exit 1
fi

echo "🚀 Starting anthropic-proxy..."
uv run uvicorn server:app --host 0.0.0.0 --port 8082
