#!/bin/bash

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
    -p 8050:8050 \
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

echo "Container is running in background"
echo "View logs with: docker logs -f pyerp-prod"
