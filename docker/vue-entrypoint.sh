#!/bin/bash
set -e

# Change to frontend directory
cd /app/frontend

# Install dependencies if node_modules doesn't exist or if package.json has changed
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-json-hash" ] || [ "$(md5sum package.json | cut -d' ' -f1)" != "$(cat node_modules/.package-json-hash)" ]; then
    echo "Installing/updating npm dependencies..."
    npm install
    md5sum package.json | cut -d' ' -f1 > node_modules/.package-json-hash
fi

# Execute the command passed to the script
exec "$@" 