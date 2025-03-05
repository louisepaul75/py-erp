#!/bin/bash

# Script to ensure static directories exist and are properly populated
# This script is meant to be run before starting the application

# Create static directories if they don't exist
mkdir -p static/images
mkdir -p staticfiles/images

# Copy frontend assets to static directories if they exist
if [ -d frontend/src/assets ]; then
  echo "Copying frontend assets to static directories..."
  cp -r frontend/src/assets/* static/images/ 2>/dev/null || true
  cp -r frontend/src/assets/* staticfiles/images/ 2>/dev/null || true
  echo "Assets copied successfully."
else
  echo "Frontend assets directory not found. Skipping asset copy."
fi

# Create a no-image placeholder if it doesn't exist
if [ ! -f static/images/no-image.png ] && [ -f frontend/src/assets/wsz_logo.png ]; then
  echo "Creating no-image.png placeholder..."
  cp frontend/src/assets/wsz_logo.png static/images/no-image.png
  cp frontend/src/assets/wsz_logo.png staticfiles/images/no-image.png
  echo "Placeholder created successfully."
fi

echo "Static directories setup completed." 