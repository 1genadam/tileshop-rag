#!/bin/bash

# Exit immediately if any command fails
set -e

# Ensure you're in the project directory
cd ~/genadam || exit

# Function to open URLs in the default web browser
open_url() {
    local url=$1
    if command -v open >/dev/null 2>&1; then
        open "$url" # macOS
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$url" # Linux
    else
        echo "Could not determine how to open URLs on this system."
    fi
}

# Function to start a service in a new terminal window
run_in_new_terminal() {
    local command=$1
    osascript <<EOF
tell application "Terminal"
    do script "cd ~/genadam; source autogen_env/bin/activate; $command"
end tell
EOF
}

# Start Flask (5001)
run_in_new_terminal "FLASK_APP=test_flask.py flask run --port=5001"
echo "Flask started on http://127.0.0.1:5001/"
open_url "http://127.0.0.1:5001/"

# Start SQLite-related service (5000)
run_in_new_terminal "python app.py"
echo "SQLite-related service started on http://127.0.0.1:5000/"
open_url "http://127.0.0.1:5000/"

# Open the Heroku app
open_url "https://genadam-2669f82f8579.herokuapp.com/"

# Start Jupyter Notebook
run_in_new_terminal "jupyter lab"
echo "Jupyter Notebook started on http://localhost:8888/lab"
open_url "http://localhost:8888/lab"

# Open GitLab job status page
open_url "https://gitlab.com/genadam/genadam/-/jobs"

# Open Heroku activity dashboard
open_url "https://dashboard.heroku.com/apps/genadam/activity"

# Confirm all services and browser tabs have been started
echo "All services started, and browser tabs opened successfully."

