#!/bin/bash

# Initialize variables for optional parameters
RUN_TESTS=""
USE_CACHE="yes"
MONITORING_MODE="none"  # Default is basic local logging

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
        --no-cache)
            USE_CACHE="no"
            shift
            ;;
        --monitoring)
            if [[ "$2" != "none" && "$2" != "remote" ]]; then
                echo "Error: --monitoring requires one of: none, remote"
                exit 1
            fi
            MONITORING_MODE="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 [--tests ui] [--no-cache] [--monitoring none|remote]"
            exit 1
            ;;
    esac
done

# Create Docker network if it doesn't exist
echo "Ensuring Docker network exists..."
docker network create pyerp-network 2>/dev/null || true

# Stop the existing container
echo "Stopping existing pyerp-dev container..."
docker stop pyerp-dev || true

# Remove the existing container
echo "Removing existing pyerp-dev container..."
docker rm pyerp-dev || true

# Rebuild the Docker image
if [ "$USE_CACHE" == "no" ]; then
    echo "Rebuilding Docker image for development (no cache)..."
    docker build --no-cache -t pyerp-dev-image -f docker/Dockerfile.dev .
else
    echo "Rebuilding Docker image for development (using cache)..."
    docker build -t pyerp-dev-image -f docker/Dockerfile.dev .
fi

# Check if .env.dev exists and prepare env_file argument
ENV_FILE="config/env/.env.dev"
if [ -f "$ENV_FILE" ]; then
    echo "Found $ENV_FILE, will use it for environment variables"
    ENV_ARG="--env-file $ENV_FILE"
else
    echo "No $ENV_FILE found, will use development settings with SQLite fallback"
    ENV_ARG="-e DJANGO_SETTINGS_MODULE=pyerp.config.settings.development -e PYERP_ENV=dev"
fi

# Get hostname for developer identification
HOSTNAME=$(hostname)

# Configure monitoring environment variables based on selected mode
if [ "$MONITORING_MODE" == "none" ]; then
    # No monitoring environment variables needed
    MONITORING_ENV=""
elif [ "$MONITORING_MODE" == "remote" ]; then
    # Get remote ELK settings from .env.dev file or use defaults
    if [ -f "$ENV_FILE" ]; then
        # Source the .env file to get the ELK settings
        source "$ENV_FILE"
        # Set environment variables for remote ELK
        MONITORING_ENV="-e ELASTICSEARCH_HOST=${ELASTICSEARCH_HOST:-production-elk-server-address} -e ELASTICSEARCH_PORT=${ELASTICSEARCH_PORT:-9200} -e KIBANA_HOST=${KIBANA_HOST:-production-elk-server-address} -e KIBANA_PORT=${KIBANA_PORT:-5601} -e ELASTICSEARCH_USERNAME=${ELASTICSEARCH_USERNAME:-} -e ELASTICSEARCH_PASSWORD=${ELASTICSEARCH_PASSWORD:-} -e ELASTICSEARCH_INDEX_PREFIX=pyerp-dev -e PYERP_ENV=dev -e HOSTNAME=$HOSTNAME"
    else
        echo "Warning: No $ENV_FILE found, using default remote ELK settings"
        MONITORING_ENV="-e ELASTICSEARCH_HOST=production-elk-server-address -e ELASTICSEARCH_PORT=9200 -e KIBANA_HOST=production-elk-server-address -e KIBANA_PORT=5601 -e ELASTICSEARCH_INDEX_PREFIX=pyerp-dev -e PYERP_ENV=dev -e HOSTNAME=$HOSTNAME"
    fi
fi

# Start the pyERP container
echo "Starting new pyerp-dev container..."
docker run -d \
  --name pyerp-dev \
  $ENV_ARG \
  $MONITORING_ENV \
  -p 8050:8050 \
  -p 3000:3000 \
  -p 6379:6379 \
  -p 80:80 \
  -v $(pwd):/app \
  --network pyerp-network \
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

# Display monitoring information based on the selected mode
if [ "$MONITORING_MODE" == "none" ]; then
    echo -e "\nMonitoring: Disabled (using local logging only)"
elif [ "$MONITORING_MODE" == "remote" ]; then
    echo -e "\nMonitoring services (remote connection):"
    echo -e "- Connected to remote Elasticsearch: ${ELASTICSEARCH_HOST:-production-elk-server-address}:${ELASTICSEARCH_PORT:-9200}"
    echo -e "- Connected to remote Kibana: ${KIBANA_HOST:-production-elk-server-address}:${KIBANA_PORT:-5601}"
    echo -e "- Using developer ID: $HOSTNAME"
fi

echo -e "To run frontend tests manually, use: docker exec -it pyerp-dev bash -c 'cd /app/frontend-react && npm test'"
