#!/bin/bash

# Stop the existing container
echo "Stopping existing pyerp-dev container..."
docker stop pyerp-dev || true

# Remove the existing container
echo "Removing existing pyerp-dev container..."
docker rm pyerp-dev || true

# Rebuild the Docker image
echo "Rebuilding Docker image for development..."
docker build -t pyerp-dev-image -f docker/Dockerfile.dev .

# Start a new container
echo "Starting new pyerp-dev container..."
docker run -d \
  --name pyerp-dev \
  --env-file config/env/.env.dev \
  -p 8050:8050 \
  -p 3000:3000 \
  -p 6379:6379 \
  -v $(pwd):/app \
  pyerp-dev-image \
  /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf

# Follow the logs
echo "Following container logs..."
docker logs -f pyerp-dev 