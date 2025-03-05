#!/bin/bash

# Stop the existing container
echo "Stopping existing pyerp container..."
docker stop pyerp

# Remove the existing container
echo "Removing existing pyerp container..."
docker rm pyerp

# Rebuild the Docker image
echo "Rebuilding Docker image..."
docker build -t docker-pyerp .

# Start a new container
echo "Starting new pyerp container..."
docker run -d --name pyerp docker-pyerp

# Follow the logs
echo "Following container logs..."
docker logs -f pyerp 