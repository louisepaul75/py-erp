#!/bin/bash

# Initialize variables for optional parameters
RUN_TESTS=""
USE_CACHE="yes"
MONITORING_MODE="separate"  # Default is separate monitoring

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
            if [[ "$2" != "none" && "$2" != "separate" && "$2" != "remote" ]]; then
                echo "Error: --monitoring requires one of: none, separate, remote"
                exit 1
            fi
            MONITORING_MODE="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 [--tests ui] [--no-cache] [--monitoring none|separate|remote]"
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

# Check if monitoring containers are already running and stop/remove them if they are
if docker ps | grep -q "pyerp-elastic-kibana"; then
    echo "Stopping existing monitoring container..."
    docker stop pyerp-elastic-kibana || true
    docker rm pyerp-elastic-kibana || true
fi

# Always remove the monitoring container even if not running
if [ "$MONITORING_MODE" == "separate" ]; then
    echo "Removing monitoring container (if exists)..."
    docker stop pyerp-elastic-kibana || true
    docker rm pyerp-elastic-kibana || true
fi

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

# Get hostname for developer identification
HOSTNAME=$(hostname)

# Configure monitoring environment variables based on selected mode
if [ "$MONITORING_MODE" == "none" ]; then
    # No monitoring environment variables needed
    MONITORING_ENV=""
    MONITORING_CMD=""
    MONITORING_PORTS=""
    MONITORING_VOLUMES=""
elif [ "$MONITORING_MODE" == "separate" ]; then
    # Set environment variables to connect to separate monitoring container
    MONITORING_ENV="-e ELASTICSEARCH_HOST=pyerp-elastic-kibana -e ELASTICSEARCH_PORT=9200 -e KIBANA_HOST=pyerp-elastic-kibana -e KIBANA_PORT=5602 -e ELASTICSEARCH_INDEX_PREFIX=pyerp -e PYERP_ENV=dev -e SENTRY_DSN=https://development@sentry.example.com/1"
    MONITORING_CMD=""
    MONITORING_PORTS=""
    MONITORING_VOLUMES=""
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
    MONITORING_CMD=""
    MONITORING_PORTS=""
    MONITORING_VOLUMES=""
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
  $([ "$MONITORING_MODE" == "none" ] && echo "-p 9200:9200 -p 5602:5601") \
  -v $(pwd):/app \
  $([ "$MONITORING_MODE" == "none" ] && echo "-v pyerp_elasticsearch_data:/var/lib/elasticsearch") \
  --network pyerp-network \
  pyerp-dev-image \
  bash -c "cd /app && bash /app/docker/ensure_static_dirs.sh && bash /app/docker/ensure_frontend_deps.sh && $([ "$MONITORING_MODE" == "none" ] && echo "bash /app/docker/install_monitoring.sh &&") /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf"

# Start the separate monitoring container if needed
if [ "$MONITORING_MODE" == "separate" ]; then
    echo "Starting separate monitoring container with docker-compose..."
    docker-compose -f docker/docker-compose.monitoring.yml up -d
fi

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
    echo -e "\nMonitoring services (integrated):"
    echo -e "- Elasticsearch: http://localhost:9200"
    echo -e "- Kibana: http://localhost:5602"
    echo -e "- Sentry: Integrated with Django application"
elif [ "$MONITORING_MODE" == "separate" ]; then
    echo -e "\nMonitoring services (separate container):"
    echo -e "- Elasticsearch: http://localhost:9200"
    echo -e "- Kibana: http://localhost:5602" 
    echo -e "- Sentry: Integrated with Django application"
    echo -e "Monitoring container logs: docker logs pyerp-elastic-kibana"
elif [ "$MONITORING_MODE" == "remote" ]; then
    echo -e "\nMonitoring services (remote connection):"
    echo -e "- Connected to remote Elasticsearch: ${ELASTICSEARCH_HOST:-production-elk-server-address}:${ELASTICSEARCH_PORT:-9200}"
    echo -e "- Connected to remote Kibana: ${KIBANA_HOST:-production-elk-server-address}:${KIBANA_PORT:-5601}"
    echo -e "- Using developer ID: $HOSTNAME"
fi

echo -e "To run frontend tests manually, use: docker exec -it pyerp-dev bash -c 'cd /app/frontend-react && npm test'"
