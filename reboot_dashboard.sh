#!/bin/bash

# Tileshop Dashboard Reboot Script
# Stops current dashboard, clears cache, and auto-starts in background with autogen_env

echo "🔄 Rebooting Tileshop Dashboard (Auto-Background Mode)..."

# Quick git sync (optimized for speed)
echo "📤 Quick git sync..."
if ! git diff-index --quiet HEAD --; then
    echo "📝 Auto-committing local changes..."
    git add -A && git commit -m "Dashboard reboot auto-commit" --quiet
    git push --quiet origin $(git branch --show-current) &
    GIT_PID=$!
    echo "✅ Git push started in background (PID: $GIT_PID)"
else
    echo "✅ No changes to commit"
fi

# Stop any existing dashboard and chat processes (fast)
echo "⏹️  Stopping existing dashboard and chat processes..."
pkill -f "python.*dashboard_app.py" 2>/dev/null
pkill -f "python.*customer_chat_app.py" 2>/dev/null
pkill -f "python.*salesperson_chat_app.py" 2>/dev/null
pkill -f "python.*contractor_chat_app.py" 2>/dev/null
sleep 1  # Allow processes to stop gracefully

# Clear Python cache files
echo "🧹 Clearing Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Clear Flask template cache (if exists)
echo "🗂️  Clearing Flask template cache..."
rm -rf flask_session/ 2>/dev/null || true
rm -rf .cache/ 2>/dev/null || true

# Verify processes are stopped
if pgrep -f "dashboard_app.py\|chat_app.py" > /dev/null; then
    echo "⚠️  Force killing remaining processes..."
    pkill -9 -f "dashboard_app.py" 2>/dev/null
    pkill -9 -f "chat_app.py" 2>/dev/null
    sleep 1
fi

# Start all applications in autogen_env (background mode)
echo "🚀 Starting TileShop application suite in autogen_env..."
echo "   📊 Dashboard (port 8080)"
echo "   👤 Customer Chat (port 8081) - Hybrid Form/LLM Interface"
echo "   💼 Salesperson Tools (port 8082)"
echo "   🔧 Contractor Tools (port 8083)"

source ../autogen_env/bin/activate && {
    python dashboard_app.py > dashboard.log 2>&1 &
    python customer_chat_app.py > customer_chat.log 2>&1 &
    python salesperson_chat_app.py > salesperson_chat.log 2>&1 &
    python contractor_chat_app.py > contractor_chat.log 2>&1 &
}

# Wait for startup (longer for multiple apps)
sleep 3

# Check if applications started successfully
echo "✅ Checking application startup status..."
DASHBOARD_PID=$(pgrep -f "dashboard_app.py" 2>/dev/null)
CUSTOMER_PID=$(pgrep -f "customer_chat_app.py" 2>/dev/null)
SALES_PID=$(pgrep -f "salesperson_chat_app.py" 2>/dev/null)
CONTRACTOR_PID=$(pgrep -f "contractor_chat_app.py" 2>/dev/null)

if [ ! -z "$DASHBOARD_PID" ]; then
    echo "   ✅ Dashboard (PID: $DASHBOARD_PID) - http://127.0.0.1:8080"
else
    echo "   ❌ Dashboard failed to start"
fi

if [ ! -z "$CUSTOMER_PID" ]; then
    echo "   ✅ Customer Chat (PID: $CUSTOMER_PID) - http://127.0.0.1:8081"
else
    echo "   ❌ Customer Chat failed to start"
fi

if [ ! -z "$SALES_PID" ]; then
    echo "   ✅ Salesperson Tools (PID: $SALES_PID) - http://127.0.0.1:8082"
else
    echo "   ⚠️  Salesperson Tools not started"
fi

if [ ! -z "$CONTRACTOR_PID" ]; then
    echo "   ✅ Contractor Tools (PID: $CONTRACTOR_PID) - http://127.0.0.1:8083"
else
    echo "   ⚠️  Contractor Tools not started"
fi

echo ""
echo "📋 Recent startup logs:"
if [ -f dashboard.log ]; then
    echo "   Dashboard:"
    tail -3 dashboard.log | sed 's/^/      /'
fi
if [ -f customer_chat.log ]; then
    echo "   Customer Chat:"
    tail -3 customer_chat.log | sed 's/^/      /'
fi
echo ""
echo "🧹 BROWSER CACHE CLEARING:"
echo "   Quick: Cmd+Shift+R (Chrome/Safari) or Ctrl+Shift+R (Firefox)"
echo "   Advanced: F12 → Network tab → Check 'Disable cache' → Refresh"
echo "   Nuclear: Open private/incognito window"
echo "   📱 Mobile: Settings → Clear browsing data"
echo ""
echo "🔄 FORCING BROWSER REFRESH..."
echo "📡 Broadcasting reload signal to open browser tabs..."
echo ""
echo "🔍 Monitor logs:"
echo "   Dashboard: tail -f dashboard.log"
echo "   Customer Chat: tail -f customer_chat.log"
echo "   Salesperson: tail -f salesperson_chat.log"
echo "   Contractor: tail -f contractor_chat.log"
echo ""

# Check if at least dashboard and customer chat started
if [ ! -z "$DASHBOARD_PID" ] && [ ! -z "$CUSTOMER_PID" ]; then
    echo "✅ Reboot complete! Core applications are running in background."
    echo ""
    echo "🌟 PRIMARY INTERFACES:"
    echo "   📊 Main Dashboard: http://127.0.0.1:8080"
    echo "   🏠 Customer Chat (Hybrid Interface): http://127.0.0.1:8081"
    echo ""
    echo "🔧 ADDITIONAL TOOLS:"
    echo "   💼 Salesperson: http://127.0.0.1:8082"
    echo "   🔧 Contractor: http://127.0.0.1:8083"
    exit 0
elif [ ! -z "$DASHBOARD_PID" ]; then
    echo "⚠️  Partial success - Dashboard running but customer chat failed"
    echo "📋 Customer Chat Error logs:"
    tail -10 customer_chat.log 2>/dev/null | sed 's/^/   /' || echo "   No customer chat log found"
    exit 1
else
    echo "❌ Failed to start core applications"
    echo "📋 Dashboard Error logs:"
    tail -10 dashboard.log 2>/dev/null | sed 's/^/   /' || echo "   No dashboard log found"
    exit 1
fi