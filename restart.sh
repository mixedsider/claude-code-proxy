#!/bin/bash

# anthropic-proxy Restart Script for Linux/macOS/Bash
set -e

echo "🔍 Finding and stopping existing anthropic-proxy processes on port 8082..."

# Find PID using port 8082 (handles multiple OS variants)
if command -v lsof >/dev/null 2>&1; then
    PID=$(lsof -t -i:8082)
elif command -v fuser >/dev/null 2>&1; then
    PID=$(fuser 8082/tcp 2>/dev/null)
else
    # Fallback to netstat/awk if others aren't available
    PID=$(netstat -anop | grep :8082 | grep LISTEN | awk '{print $7}' | cut -d/ -f1)
fi

if [ -n "$PID" ]; then
    echo "🛑 Stopping process (PID: $PID)..."
    kill -9 $PID
    echo "✅ Existing process stopped."
else
    echo "ℹ️ No existing process found on port 8082."
fi

# Start the server using start.sh
./start.sh
