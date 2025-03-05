#!/bin/bash

# Stop the existing container
echo "Stopping existing pyerp-dev container..."
docker stop pyerp-dev || true

# Remove the existing container
echo "Removing existing pyerp-dev container..."
docker rm pyerp-dev || true

# Rebuild the Docker image
echo "Rebuilding Docker image for development..."
docker build -t docker-pyerp-dev -f docker/Dockerfile.dev .

# Start a new container
echo "Starting new pyerp-dev container..."
docker run -d \
  --name pyerp-dev \
  --env-file config/env/.env.dev \
  -p 8051:8050 \
  -v $(pwd):/app \
  --entrypoint /bin/bash \
  docker-pyerp-dev \
  -c "/app/docker/entrypoint.dev.sh"

# Follow the logs
echo "Following container logs..."
docker logs -f pyerp-dev 