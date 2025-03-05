#!/bin/bash

# Script to ensure static directories exist and are properly populated
# This script is meant to be run before starting the application

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Get the project root directory (parent of script directory)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# Change to project root directory
cd "$PROJECT_ROOT"

# Create static directories if they don't exist
mkdir -p static/images
mkdir -p staticfiles/images
mkdir -p pyerp/static/images

# Copy frontend assets to static directories if they exist
if [ -d frontend/src/assets ]; then
  echo "Copying frontend assets to static directories..."
  cp -r frontend/src/assets/* static/images/ 2>/dev/null || true
  cp -r frontend/src/assets/* staticfiles/images/ 2>/dev/null || true
  cp -r frontend/src/assets/* pyerp/static/images/ 2>/dev/null || true
  echo "Assets copied successfully."
else
  echo "Frontend assets directory not found. Skipping asset copy."
fi

# Create a no-image placeholder using wsz_logo.png
if [ -f frontend/src/assets/wsz_logo.png ]; then
  echo "Creating no-image.png placeholder using WSZ logo..."
  cp frontend/src/assets/wsz_logo.png static/images/no-image.png
  cp frontend/src/assets/wsz_logo.png staticfiles/images/no-image.png
  cp frontend/src/assets/wsz_logo.png pyerp/static/images/no-image.png
  echo "WSZ logo placeholder created successfully."
fi

# Run collectstatic to ensure all static files are collected
if command -v python &> /dev/null; then
  echo "Running collectstatic..."
  python "$PROJECT_ROOT/manage.py" collectstatic --noinput
  echo "Collectstatic completed."
fi

echo "Static directories setup completed." 