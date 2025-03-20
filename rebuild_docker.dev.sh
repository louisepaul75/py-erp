#!/bin/bash

# Initialize variables for optional parameters
RUN_TESTS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --tests)
            if [ -z "$2" ]; then
                echo "Error: --tests requires a parameter (e.g. ui)"
                exit 1
            fi
            RUN_TESTS="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 [--tests ui]"
            exit 1
            ;;
    esac
done

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
  bash -c "cd /app && bash /app/docker/ensure_static_dirs.sh && bash /app/docker/ensure_frontend_deps.sh && /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf"

# Show the last 50 lines of container logs
echo "Showing last 50 lines of container logs..."
docker logs --tail 50 pyerp-dev || true

# Run tests only if the --tests parameter was provided
if [ -n "$RUN_TESTS" ]; then
    case "$RUN_TESTS" in
        "ui")
            echo "Running frontend tests..."
            docker exec pyerp-dev bash -c "cd /app/frontend-react && npm test -- --silent || echo 'Tests may fail initially, but the setup is complete.'"
            ;;
        *)
            echo "Unknown test type: $RUN_TESTS"
            echo "Supported test types: ui"
            ;;
    esac
fi

echo -e "\nContainer is running in the background. Use 'docker logs pyerp-dev' to view logs again."
echo -e "To run frontend tests manually, use: docker exec -it pyerp-dev bash -c 'cd /app/frontend-react && npm test'"
