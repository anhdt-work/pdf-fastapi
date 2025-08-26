#!/bin/bash

echo "📊 PDF-to-Text API Status (uvicorn)"
echo "=================================="

if [ -f logs/app.pid ]; then
    PID=$(cat logs/app.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "✅ Status: RUNNING (uvicorn)"
        echo "📋 Process ID: $PID"
        echo "💾 Memory usage: $(ps -o pid,vsz,rss,comm -p $PID | tail -1)"
        echo "⏰ Uptime: $(ps -o pid,etime,comm -p $PID | tail -1)"
        echo "🔄 Auto-reload: Enabled"
        
        # Check if it's actually uvicorn
        PROC_CMD=$(ps -o pid,comm,args -p $PID | tail -1)
        if echo "$PROC_CMD" | grep -q "uvicorn"; then
            echo "✅ Confirmed: uvicorn process"
        else
            echo "⚠️  Warning: Process may not be uvicorn"
        fi
    else
        echo "❌ Status: STOPPED (PID file exists but process not running)"
        rm logs/app.pid
    fi
else
    # Check for uvicorn processes
    UVICORN_PIDS=$(pgrep -f "uvicorn.*main:app")
    if [ ! -z "$UVICORN_PIDS" ]; then
        echo "⚠️  Status: RUNNING (but no PID file found)"
        echo "📋 uvicorn Process(es): $UVICORN_PIDS"
        for pid in $UVICORN_PIDS; do
            echo "   PID $pid: $(ps -o pid,etime,comm -p $pid | tail -1)"
        done
    else
        # Fallback check for any uvicorn
        if pgrep -f "uvicorn" > /dev/null; then
            echo "⚠️  Status: uvicorn running (different app)"
            echo "📋 uvicorn Process(es): $(pgrep -f 'uvicorn')"
        else
            echo "❌ Status: STOPPED"
        fi
    fi
fi

echo ""
echo "📁 Log file size: $(du -h logs/app.log 2>/dev/null || echo 'No log file')"
echo "🌐 API endpoint: http://localhost:8000"
echo "📖 API docs: http://localhost:8000/docs"
echo "🔄 Auto-reload: $([ -f logs/app.pid ] && echo 'Enabled' || echo 'N/A')"

# Test if API is responding
echo ""
echo "🏥 Health Check:"
if command -v curl >/dev/null 2>&1; then
    if curl -s -f http://localhost:8000/docs >/dev/null 2>&1; then
        echo "✅ API is responding"
    else
        echo "❌ API not responding"
    fi
else
    echo "ℹ️  curl not available for health check"
fi
