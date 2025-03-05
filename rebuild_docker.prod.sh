#!/bin/bash

# Stop the existing container
echo "Stopping existing pyerp-prod container..."
docker stop pyerp-prod || true

# Remove the existing container
echo "Removing existing pyerp-prod container..."
docker rm pyerp-prod || true

# Rebuild the Docker image
echo "Rebuilding Docker image..."
docker build -t pyerp-prod-image -f docker/Dockerfile.prod \
  --build-arg DJANGO_SETTINGS_MODULE=pyerp.config.settings.production .

# Start a new container
echo "Starting new pyerp-prod container..."
docker run -d \
  --name pyerp-prod \
  --env-file config/env/.env.prod \
  -p 80:80 \
  -p 443:443 \
  -v $(pwd)/docker/nginx/ssl:/etc/nginx/ssl \
  pyerp-prod-image

# Follow the logs for just 10 seconds to see startup
echo "Showing initial container logs (10 seconds)..."
timeout 10 docker logs -f pyerp-prod || true

echo -e "\nContainer is running in the background. Use 'docker logs pyerp-prod' to view logs again." 