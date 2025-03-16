#!/bin/bash

# Stop the existing container
echo "Stopping existing pyerp-dev container..."
docker stop pyerp-dev || true

# Remove the existing container
echo "Removing existing pyerp-dev container..."
docker rm pyerp-dev || true

# Uncomment to clean up build cache if needed
# docker buildx prune -a

# Rebuild the Docker image without using cache
echo "Rebuilding Docker image for development (no cache)..."
docker build --no-cache -t pyerp-dev-image -f docker/Dockerfile.dev .

# Check if .env.dev exists and prepare env_file argument
ENV_FILE="config/env/.env.dev"
if [ -f "$ENV_FILE" ]; then
    echo "Found $ENV_FILE, will use it for environment variables"
    ENV_ARG="--env-file $ENV_FILE"
else
    echo "No $ENV_FILE found, will use development settings with SQLite fallback"
    ENV_ARG="-e DJANGO_SETTINGS_MODULE=pyerp.config.settings.development -e PYERP_ENV=dev"
fi

# Start a new container
echo "Starting new pyerp-dev container..."
docker run -d \
  --name pyerp-dev \
  $ENV_ARG \
  -p 8050:8050 \
  -p 3000:3000 \
  -p 6379:6379 \
  -p 5173:5173 \
  -p 80:80 \
  -v $(pwd):/app \
  pyerp-dev-image \
  bash -c "cd /app && bash /app/docker/ensure_static_dirs.sh && /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf"

# Show the last 50 lines of container logs
echo "Showing last 50 lines of container logs..."
docker logs --tail 50 pyerp-dev || true

echo -e "\nContainer is running in the background. Use 'docker logs pyerp-dev' to view logs again."
