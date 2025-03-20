#!/bin/bash

# Script to ensure all necessary frontend dependencies are installed
# This runs every time the container starts

cd /app/frontend-react

echo "Checking for missing frontend dependencies..."

# Install @testing-library/dom if not already installed
if ! npm list @testing-library/dom --depth=0 --silent > /dev/null 2>&1; then
  echo "Installing @testing-library/dom..."
  npm install @testing-library/dom --save-dev
else
  echo "@testing-library/dom is already installed."
fi

# Add any other missing dependencies here
# For example:
# if ! npm list some-package --depth=0 --silent > /dev/null 2>&1; then
#   echo "Installing some-package..."
#   npm install some-package --save-dev
# fi

echo "Frontend dependencies check completed."

# Return to app directory
cd /app 