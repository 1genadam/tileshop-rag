#!/bin/bash

# Tileshop Dashboard Reboot Script
# Stops current dashboard, clears cache, and restarts in autogen_env

echo "🔄 Rebooting Tileshop Dashboard..."

# Stop any existing dashboard processes
echo "⏹️  Stopping existing dashboard processes..."
pkill -f "python.*admin_dashboard.py" 2>/dev/null
sleep 2

# Verify process is stopped
if pgrep -f "admin_dashboard.py" > /dev/null; then
    echo "⚠️  Force killing remaining processes..."
    pkill -9 -f "admin_dashboard.py" 2>/dev/null
    sleep 1
fi

# Start dashboard in autogen_env
echo "🚀 Starting dashboard in autogen_env..."
/Users/robertsher/Projects/autogen_env/bin/python admin_dashboard.py > dashboard.log 2>&1 &

# Wait for startup
sleep 3

# Check if dashboard started successfully
if pgrep -f "admin_dashboard.py" > /dev/null; then
    PID=$(pgrep -f "admin_dashboard.py")
    echo "✅ Dashboard started successfully!"
    echo "   Process ID: $PID"
    echo "   Environment: autogen_env"
    echo "   URL: http://127.0.0.1:8080"
    echo ""
    echo "📋 Recent startup logs:"
    tail -5 dashboard.log | sed 's/^/   /'
    echo ""
    echo "🧹 IMPORTANT: Clear browser cache for UI updates!"
    echo "   Chrome/Safari: Cmd+Shift+R"
    echo "   Firefox: Ctrl+Shift+R or Cmd+Shift+R"
    echo ""
    echo "🔍 Monitor logs: tail -f dashboard.log"
else
    echo "❌ Failed to start dashboard"
    echo "📋 Error logs:"
    tail -10 dashboard.log | sed 's/^/   /'
    exit 1
fi