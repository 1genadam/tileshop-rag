#!/bin/bash

# Exit immediately if any command fails
set -e

# Ensure you're on the main branch
git checkout main

# Add and commit any changes
git add -A
git commit -m "Automated deployment"

# Ensure the Heroku remote is set up (only required once)
git remote add heroku https://git.heroku.com/genadam.git || true

# Push changes to Heroku
git push heroku main --force

# Confirm deployment
echo "Deployed to Heroku successfully!"


