#!/bin/bash

# Exit immediately if any command fails
set -e

# Ensure you're on the main branch
git checkout main

# Freeze dependencies to requirements.txt
pip freeze > requirements.txt
echo "Updated requirements.txt with current dependencies."

# Stage the changes in requirements.txt
git add requirements.txt

# Check for staged changes
if git diff --cached --quiet; then
    echo "No changes detected in cache. Aborting deployment."
    exit 0
fi

# List the changes that will be committed
echo "The following changes are staged for commit:"
git diff --cached --name-only

# Commit the staged changes
git commit -m "Automated deployment with staged changes"

# Push changes to Heroku
git push heroku main --force

# Confirm deployment
echo "Deployed to Heroku successfully!"

