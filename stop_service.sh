#!/bin/bash

echo "Stopping PDF-to-Text API (uvicorn)..."

if [ -f logs/app.pid ]; then
    PID=$(cat logs/app.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping uvicorn process with PID: $PID"
        # Try graceful shutdown first
        kill -TERM $PID
        sleep 2
        
        # Check if still running, force kill if necessary
        if kill -0 $PID 2>/dev/null; then
            echo "⚠️  Process still running, forcing shutdown..."
            kill -KILL $PID
        fi
        
        rm logs/app.pid
        echo "✅ Application stopped successfully!"
    else
        echo "⚠️  Process $PID not found. Cleaning up PID file."
        rm logs/app.pid
    fi
else
    echo "⚠️  No PID file found. Checking for running uvicorn processes..."
    
    # Kill uvicorn processes by name
    pkill -f "uvicorn.*main:app"
    if [ $? -eq 0 ]; then
        echo "✅ Found and stopped running uvicorn processes"
    else
        # Fallback to kill any uvicorn process
        pkill -f "uvicorn"
        if [ $? -eq 0 ]; then
            echo "✅ Found and stopped uvicorn processes"
        else
            echo "ℹ️  No running uvicorn processes found"
        fi
    fi
fi
