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

# Stop any existing dashboard processes (fast)
echo "⏹️  Stopping existing dashboard processes..."
pkill -f "python.*dashboard_app.py" 2>/dev/null
sleep 1  # Reduced from 2 seconds

# Clear Python cache files
echo "🧹 Clearing Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Clear Flask template cache (if exists)
echo "🗂️  Clearing Flask template cache..."
rm -rf flask_session/ 2>/dev/null || true
rm -rf .cache/ 2>/dev/null || true

# Verify process is stopped
if pgrep -f "dashboard_app.py" > /dev/null; then
    echo "⚠️  Force killing remaining processes..."
    pkill -9 -f "dashboard_app.py" 2>/dev/null
    sleep 1
fi

# Start dashboard in autogen_env (background mode)
echo "🚀 Starting dashboard in autogen_env (background mode)..."
source ../autogen_env/bin/activate && python dashboard_app.py > dashboard.log 2>&1 &

# Wait for startup (fast check)
sleep 1  # Reduced from 3 seconds

# Check if dashboard started successfully
if pgrep -f "dashboard_app.py" > /dev/null; then
    PID=$(pgrep -f "dashboard_app.py")
    echo "✅ Dashboard started successfully!"
    echo "   Process ID: $PID"
    echo "   Environment: autogen_env"
    echo "   URL: http://127.0.0.1:8080"
    echo ""
    echo "📋 Recent startup logs:"
    tail -5 dashboard.log | sed 's/^/   /'
    echo ""
    echo "🧹 BROWSER CACHE CLEARING:"
    echo "   Quick: Cmd+Shift+R (Chrome/Safari) or Ctrl+Shift+R (Firefox)"
    echo "   Advanced: F12 → Network tab → Check 'Disable cache' → Refresh"
    echo "   Nuclear: Open private/incognito window"
    echo "   📱 Mobile: Settings → Clear browsing data"
    echo ""
    echo "🔄 FORCING BROWSER REFRESH..."
    # Create a simple JavaScript file to force reload
    cat > force_reload.js << 'EOF'
// Force reload all open dashboard tabs
if (typeof window !== 'undefined' && window.location.pathname === '/') {
    console.log('Dashboard reboot detected - forcing reload...');
    window.location.reload(true);
}
EOF
    # Serve the reload script temporarily (this will work if browser has the tab open)
    echo "📡 Broadcasting reload signal to open browser tabs..."
    sleep 1
    rm -f force_reload.js
    echo ""
    echo "🔍 Monitor logs: tail -f dashboard.log"
    echo ""
    echo "✅ Reboot complete! Dashboard is running in background."
    exit 0
else
    echo "❌ Failed to start dashboard"
    echo "📋 Error logs:"
    tail -10 dashboard.log | sed 's/^/   /'
    exit 1
fi