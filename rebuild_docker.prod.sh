#!/bin/bash

echo "Running all tests..."
./run_all_tests.sh
if [ $? -ne 0 ]; then
    echo "Tests failed. Aborting build."
    exit 1
fi
echo "All tests passed. Proceeding with build..."
echo "" # Add a newline for spacing

# Parse command line arguments
DEBUG_MODE=false
LIVE_EDIT=false

for arg in "$@"
do
    case $arg in
        --debug)
        DEBUG_MODE=true
        shift
        ;;
        --live-edit)
        LIVE_EDIT=true
        shift
        ;;
    esac
done

# Stop and remove existing containers
echo "Stopping existing containers..."
docker stop pyerp-prod || true
docker rm pyerp-prod || true
docker stop pyerp-elastic-kibana || true
docker rm pyerp-elastic-kibana || true

# Only rebuild if not in live edit mode
if [ "$LIVE_EDIT" = false ]; then
    echo "Building Docker image..."
    docker build -t pyerp-prod-image -f docker/Dockerfile.prod .
fi

# Create network if it doesn't exist
docker network create pyerp-network || true

# Prepare volume mounts
VOLUME_MOUNTS=""
if [ "$LIVE_EDIT" = true ]; then
    VOLUME_MOUNTS="-v $(pwd)/frontend-react:/app/frontend-react"
fi

# Choose environment file based on mode
ENV_FILE="config/env/.env.prod"
if [ "$DEBUG_MODE" = true ]; then
    ENV_FILE="config/env/.env.prod.local"
fi

echo "Starting containers..."
docker run -d \
    --name pyerp-prod \
    --network pyerp-network \
    -p 80:80 \
    -p 443:443 \
    -p 3000:3000 \
    -p 5432:5432 \
    -p 6379:6379 \
    -p 8000:8000 \
    --env-file $ENV_FILE \
    -e NODE_ENV=development \
    -e NEXT_TELEMETRY_DISABLED=1 \
    $VOLUME_MOUNTS \
    pyerp-prod-image

# If in live edit mode, start the Next.js development server
if [ "$LIVE_EDIT" = true ]; then
    echo "Starting Next.js development server..."
    # Give the container a moment to start up
    sleep 2
    docker exec pyerp-prod bash -c "cd /app/frontend-react && NODE_ENV=development NEXT_TELEMETRY_DISABLED=1 npm run dev -- --port 3000 --hostname 0.0.0.0"
fi

echo -e "\nContainer is running in the background. Use 'docker logs pyerp-prod' to view logs again."

# Start the monitoring container
echo "Starting monitoring container..."
docker-compose -f docker/docker-compose.monitoring.yml up -d

echo -e "\nMonitoring services:"
echo -e "- Elasticsearch: http://localhost:9200"
echo -e "- Kibana: http://localhost:5601"
echo -e "Monitoring container logs: docker logs pyerp-elastic-kibana"

# Wait for Elasticsearch to be ready before running setup
echo "Waiting for Elasticsearch to become available..."
for i in {1..30}; do
    if curl -s http://localhost:9200 > /dev/null; then
        echo "Elasticsearch is ready!"
        break
    fi
    echo "Waiting for Elasticsearch... attempt $i of 30"
    sleep 5
    
    if [ $i -eq 30 ]; then
        echo "Elasticsearch did not start in time. Please check Elasticsearch logs."
        echo "You can check logs with: docker logs pyerp-elastic-kibana"
    fi
done

echo "Waiting 10 seconds before starting health checks..."
sleep 10

# --- Health Checks ---
echo -e "\n--- Running Health Checks ---"
MAX_RETRIES=12
RETRY_DELAY=5
APP_URL="http://localhost:80" # Nginx serves the app on port 80

# Check Main Application Endpoint
echo "Checking main application endpoint ($APP_URL)..."
APP_SUCCESS=false
for i in $(seq 1 $MAX_RETRIES); do
    # Using --head and -L to follow redirects if any (e.g., HTTP to HTTPS)
    if curl -fsSL --head $APP_URL > /dev/null; then
        echo "✅ Main application endpoint is responsive."
        APP_SUCCESS=true
        break
    fi
    # Check if container is still running
    if ! docker ps --filter "name=pyerp-prod" --filter "status=running" --format "{{.Names}}" | grep -q pyerp-prod; then
        echo "❌ Error: Container pyerp-prod seems to have stopped."
        break # No point retrying if container is down
    fi
    echo "Attempt $i/$MAX_RETRIES failed. Retrying in $RETRY_DELAY seconds..."
    sleep $RETRY_DELAY
done

if [ "$APP_SUCCESS" = false ]; then
    if docker ps --filter "name=pyerp-prod" --filter "status=running" --format "{{.Names}}" | grep -q pyerp-prod; then
        echo "❌ Error: Main application endpoint failed to respond after $MAX_RETRIES attempts."
    fi
    echo "Please check container logs: docker logs pyerp-prod"
fi

echo "--- Health Checks Complete ---"
