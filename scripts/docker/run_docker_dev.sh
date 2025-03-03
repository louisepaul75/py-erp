#!/bin/bash

# Script to run the pyERP Docker container in development mode
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if .env.dev exists
if [ ! -f ".env.dev" ]; then
    echo "Creating .env.dev file from example..."
    cp docker/docker.env.dev.example .env.dev
    echo "Please edit .env.dev with your development settings and run this script again."
    exit 1
fi

# Build and start the container
echo "Building and starting the Docker container..."
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml up -d

echo "Container is starting up..."
echo "You can view logs with: docker-compose -f docker/docker-compose.yml logs -f"
echo "Application should be available at http://localhost:8000" 