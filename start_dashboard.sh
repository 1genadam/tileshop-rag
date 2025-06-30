#!/bin/bash

# Tileshop Dashboard Startup Script
# This script ensures the dashboard starts with proper virtual environment and dependencies

echo "🚀 Starting Tileshop Admin Dashboard..."

# Navigate to project directory
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)
VENV_DIR="/Users/robertsher/Projects/autogen_env"

echo "📁 Project Directory: $PROJECT_DIR"
echo "🐍 Virtual Environment: $VENV_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "Creating virtual environment..."
    cd /Users/robertsher/Projects
    python -m venv autogen_env
    cd "$PROJECT_DIR"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check and install dependencies
echo "📦 Checking dependencies..."
REQUIRED_PACKAGES=("flask" "flask-socketio" "psycopg2-binary" "docker" "psutil" "requests" "beautifulsoup4" "lxml" "selenium")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python -c "import $package" 2>/dev/null; then
        echo "📥 Installing $package..."
        pip install "$package"
    else
        echo "✅ $package is available"
    fi
done

# Check Docker
echo "🐳 Checking Docker..."
if ! docker ps >/dev/null 2>&1; then
    echo "⚠️  Docker is not running. Please start Docker Desktop."
    echo "   The dashboard will still start but container management will be limited."
fi

# Kill any existing dashboard process
echo "🔄 Stopping any existing dashboard..."
pkill -f "reboot_dashboard.py" 2>/dev/null || true

# Start the dashboard
echo "🌟 Starting dashboard..."
python reboot_dashboard.py > dashboard.log 2>&1 &
DASHBOARD_PID=$!

echo "✅ Dashboard started with PID: $DASHBOARD_PID"
echo "🌐 Access dashboard at: http://localhost:8080"
echo "📊 Environment Status: Virtual environment activated"
echo "📝 Logs: dashboard.log"

# Wait a moment and check if it's running
sleep 3
if kill -0 $DASHBOARD_PID 2>/dev/null; then
    echo "✅ Dashboard is running successfully!"
else
    echo "❌ Dashboard failed to start. Check dashboard.log for errors."
    exit 1
fi