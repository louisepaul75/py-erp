#!/bin/bash

# Simplified Docker deployment script for all-in-one container setup
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "Creating .env.prod file from example..."
    cp docker/docker.env.example .env.prod
    echo "Please edit .env.prod with your production settings and run this script again."
    exit 1
fi

# Build and start the containers
echo "Building and starting the all-in-one Docker container..."
docker-compose -f docker/docker-compose.prod.yml build
docker-compose -f docker/docker-compose.prod.yml up -d

echo "Container is starting up..."
echo "You can view logs with: docker-compose -f docker/docker-compose.prod.yml logs -f"
echo "Application should be available at https://localhost (or your server's IP/domain)"