#!/bin/bash

echo "Starting PDF-to-Text API in background..."

# Activate virtual environment if it exists
if [ -d "env" ]; then
    source env/bin/activate
    echo "Virtual environment activated"
fi

# Start the application in background
nohup python main.py > logs/app.log 2>&1 &

# Get the process ID
PID=$!
echo $PID > logs/app.pid

echo "✅ Application started successfully!"
echo "📋 Process ID: $PID"
echo "📁 Log file: logs/app.log"
echo "🔍 View logs: tail -f logs/app.log"
echo "⏹️  Stop app: ./stop_service.sh"
