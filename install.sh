#!/bin/bash

# anthropic-proxy Installation Script for Linux/macOS
set -e

echo "🔍 Checking for uv..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Refresh PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "✅ uv is already installed."
fi

echo "⚙️  Configuring environment..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
        echo "⚠️  Please edit .env and add your API keys."
    else
        echo "❌ .env.example not found. Please create .env manually."
    fi
else
    echo "ℹ️  .env already exists, skipping."
fi

echo "🚀 Setup complete!"
echo "--------------------------------------------------"
echo "To start the server, run:"
echo "  ./start.sh"
echo "--------------------------------------------------"
