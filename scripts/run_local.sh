#!/bin/bash
# Script to run the PyERP Docker container in local mode with SQLite

# Exit on error
set -e

# Variables
CONTAINER_NAME="pyerp-local"
IMAGE_NAME="pyerp:debug"
PORT="8000"

# Check if the Docker image exists
if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
    echo "Docker image $IMAGE_NAME not found."
    echo "Building the Docker image from Dockerfile.minimal..."
    docker build -t $IMAGE_NAME -f docker/Dockerfile.minimal .
fi

# Check if the container is already running
if docker ps -q --filter "name=$CONTAINER_NAME" | grep -q .; then
    echo "Container $CONTAINER_NAME is already running. Stopping it..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Run the container with local settings
echo "Starting PyERP container with local SQLite database..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8000 \
    -e "USE_LOCAL_ENV=true" \
    -e "DJANGO_SETTINGS_MODULE=pyerp.settings.local" \
    -v "$(pwd)/db.sqlite3:/app/db.sqlite3" \
    $IMAGE_NAME

echo "Container is starting..."
sleep 2

# Check if the container is running
if docker ps -q --filter "name=$CONTAINER_NAME" | grep -q .; then
    echo "Container $CONTAINER_NAME is running."
    echo "View logs with: docker logs $CONTAINER_NAME -f"
    echo "Access the application at: http://localhost:$PORT"
else
    echo "Container failed to start. Checking logs..."
    docker logs $CONTAINER_NAME
fi 