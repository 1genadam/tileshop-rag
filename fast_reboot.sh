#!/bin/bash

# Fast Dashboard Reboot - Minimal operations for quick restart

echo "⚡ Fast Rebooting Dashboard..."

# Stop dashboard
echo "⏹️  Stopping dashboard..."
pkill -f "python.*dashboard_app.py" 2>/dev/null

# Clear Python cache (background)
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null &

# Start dashboard immediately
echo "🚀 Starting dashboard..."
source ../autogen_env/bin/activate && python dashboard_app.py > dashboard.log 2>&1 &

# Quick check
if pgrep -f "dashboard_app.py" > /dev/null; then
    PID=$(pgrep -f "dashboard_app.py")
    echo "✅ Dashboard restarted! PID: $PID"
    echo "🌐 URL: http://127.0.0.1:8080"
    echo "⚡ Fast reboot complete!"
    exit 0
else
    echo "❌ Fast reboot failed"
    exit 1
fi