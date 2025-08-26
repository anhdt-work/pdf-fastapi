#!/bin/bash

echo "Stopping PDF-to-Text API..."

if [ -f logs/app.pid ]; then
    PID=$(cat logs/app.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping process with PID: $PID"
        kill $PID
        rm logs/app.pid
        echo "✅ Application stopped successfully!"
    else
        echo "⚠️  Process $PID not found. Cleaning up PID file."
        rm logs/app.pid
    fi
else
    echo "⚠️  No PID file found. Checking for running processes..."
    pkill -f "python main.py"
    if [ $? -eq 0 ]; then
        echo "✅ Found and stopped running python processes"
    else
        echo "ℹ️  No running processes found"
    fi
fi
