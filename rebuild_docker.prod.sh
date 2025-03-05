#!/bin/bash

# Stop the existing container
echo "Stopping existing pyerp container..."
docker stop pyerp || true

# Remove the existing container
echo "Removing existing pyerp container..."
docker rm pyerp || true

# Rebuild the Docker image
echo "Rebuilding Docker image..."
docker build -t docker-pyerp -f docker/Dockerfile.prod .

# Start a new container
echo "Starting new pyerp container..."
docker run -d \
  --name pyerp \
  --env-file config/env/.env.prod \
  -p 8050:8050 \
  -p 80:80 \
  -p 443:443 \
  docker-pyerp

# Follow the logs
echo "Following container logs..."
docker logs -f pyerp 