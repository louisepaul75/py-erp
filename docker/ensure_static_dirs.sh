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
mkdir -p staticfiles/react

# Create directories for logs and data
mkdir -p logs
mkdir -p data
mkdir -p /var/lib/elasticsearch
mkdir -p /var/log/elasticsearch
mkdir -p /app/logs

# Set proper permissions
chown -R root:root /var/lib/elasticsearch /var/log/elasticsearch /app/logs 2>/dev/null || true
chmod -R 755 /var/lib/elasticsearch /var/log/elasticsearch /app/logs 2>/dev/null || true

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

# React frontend handling
if [ -d frontend-react/build ]; then
  echo "Copying React build files to static directories..."
  cp -r frontend-react/build/* staticfiles/react/ 2>/dev/null || true
  echo "React build files copied successfully."
elif [ -d frontend-react/.next ]; then
  echo "Copying Next.js build files to static directories..."
  mkdir -p staticfiles/react/_next
  cp -r frontend-react/.next/static/* staticfiles/react/_next/ 2>/dev/null || true
  cp -r frontend-react/public/* staticfiles/react/ 2>/dev/null || true
  
  # Ensure index.html exists
  if [ ! -f staticfiles/react/index.html ]; then
    echo "Creating fallback index.html..."
    echo '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>pyERP</title><script>window.location.href="/app";</script></head><body><div id="root">Loading pyERP...</div></body></html>' > staticfiles/react/index.html
  fi
  
  echo "Next.js files copied successfully."
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
