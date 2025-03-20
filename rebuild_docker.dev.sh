#!/bin/bash

# Initialize variables for optional parameters
RUN_TESTS=""
USE_CACHE="yes"

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
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 [--tests ui] [--no-cache]"
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

# Add monitoring environment variables
MONITORING_ENV="-e ELASTICSEARCH_HOST=localhost -e ELASTICSEARCH_PORT=9200 -e KIBANA_HOST=localhost -e KIBANA_PORT=5601 -e SENTRY_DSN=https://development@sentry.example.com/1"

# Start a new container
echo "Starting new pyerp-dev container..."
docker run -d \
  --name pyerp-dev \
  $ENV_ARG \
  $MONITORING_ENV \
  -p 8050:8050 \
  -p 3000:3000 \
  -p 6379:6379 \
  -p 80:80 \
  -p 9200:9200 \
  -p 5601:5601 \
  -v $(pwd):/app \
  -v pyerp_elasticsearch_data:/var/lib/elasticsearch \
  pyerp-dev-image \
  bash -c "cd /app && bash /app/docker/ensure_static_dirs.sh && bash /app/docker/ensure_frontend_deps.sh && bash /app/docker/install_monitoring.sh && /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf"

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
echo -e "\nMonitoring services:"
echo -e "- Elasticsearch: http://localhost:9200"
echo -e "- Kibana: http://localhost:5601"
echo -e "- Sentry: Integrated with Django application"
echo -e "To run frontend tests manually, use: docker exec -it pyerp-dev bash -c 'cd /app/frontend-react && npm test'"

# Ask the user if they want to set up remote monitoring
echo ""
read -p "Would you like to set up the monitoring system on the remote server (192.168.73.65)? (y/n): " setup_remote

if [[ $setup_remote == "j" || $setup_remote == "J" || $setup_remote == "y" || $setup_remote == "Y" ]]; then
    # Run the setup_monitoring_complete.sh script
    echo "Starting remote monitoring setup..."
    bash ./setup_monitoring_complete.sh
else
    echo "Remote monitoring setup skipped."
fi
