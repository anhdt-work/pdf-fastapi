#!/bin/bash

# Ensure logs directory exists
mkdir -p logs

# Truncate log if larger than 100MB
if [ -f logs/app.log ] && [ $(stat -c%s "logs/app.log") -gt $((100*1024*1024)) ]; then
    echo "Log file too large (>100MB), truncating..."
    : > logs/app.log
fi

echo "Starting PDF-to-Text API with uvicorn in background..."

# Activate virtual environment if it exists
if [ -d "env" ]; then
    source env/bin/activate
    echo "Virtual environment activated"
fi

# Start the application with uvicorn in background
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > logs/app.log 2>&1 &

# Get the process ID
PID=$!
echo $PID > logs/app.pid

echo "✅ Application started successfully with uvicorn!"
echo "📋 Process ID: $PID"
echo "📁 Log file: logs/app.log"
echo "🌐 API: http://localhost:8000"
echo "📖 Docs: http://localhost:8000/docs"
echo "🔄 Auto-reload: Enabled"
echo "🔍 View logs: tail -f logs/app.log"
echo "⏹️  Stop app: ./stop_service.sh"
echo "ℹ️  For dependency installation, run setup.sh once before using this script."
echo "ℹ️  For production log rotation, consider using 'logrotate' on logs/app.log."
