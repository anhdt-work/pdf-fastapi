#!/bin/bash

echo "📊 PDF-to-Text API Status"
echo "========================"

if [ -f logs/app.pid ]; then
    PID=$(cat logs/app.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "✅ Status: RUNNING"
        echo "📋 Process ID: $PID"
        echo "💾 Memory usage: $(ps -o pid,vsz,rss,comm -p $PID | tail -1)"
        echo "⏰ Uptime: $(ps -o pid,etime,comm -p $PID | tail -1)"
    else
        echo "❌ Status: STOPPED (PID file exists but process not running)"
        rm logs/app.pid
    fi
else
    if pgrep -f "python main.py" > /dev/null; then
        echo "⚠️  Status: RUNNING (but no PID file found)"
        echo "📋 Process(es): $(pgrep -f 'python main.py')"
    else
        echo "❌ Status: STOPPED"
    fi
fi

echo ""
echo "📁 Log file size: $(du -h logs/app.log 2>/dev/null || echo 'No log file')"
echo "🌐 API endpoint: http://localhost:8000"
echo "📖 API docs: http://localhost:8000/docs"
