#!/bin/bash
# Run Linux Container Script
# This script builds and runs the Linux-optimized Docker container

set -e  # Exit on error

# ANSI color codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Make sure we are in the project root
cd "$PROJECT_ROOT"

# Parse command-line arguments
BUILD=true
DETACH=false
PORT=8000
DOCKER_COMPOSE=false

# Function to show usage information
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help            Show this help message and exit"
    echo "  -n, --no-build        Skip building the Docker image"
    echo "  -d, --detach          Run container in detached mode"
    echo "  -p, --port PORT       Specify port (default: 8000)"
    echo "  -c, --compose         Use docker-compose instead of docker run"
    echo ""
    exit 0
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_usage
            ;;
        -n|--no-build)
            BUILD=false
            shift
            ;;
        -d|--detach)
            DETACH=true
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -c|--compose)
            DOCKER_COMPOSE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            ;;
    esac
done

# Build the Docker image if requested
if [ "$BUILD" = true ]; then
    echo -e "${CYAN}Building Docker image...${NC}"
    docker build -f docker/Dockerfile.dev-linux -t pyerp-linux .
    
    # Check if build was successful
    if [ $? -ne 0 ]; then
        echo -e "${RED}Docker build failed!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Docker build successful!${NC}"
fi

# Run the container using docker-compose or docker run
if [ "$DOCKER_COMPOSE" = true ]; then
    echo -e "${CYAN}Running container with docker-compose...${NC}"
    
    # Create a docker-compose override file
    cat > docker-compose.override.yml <<EOF
version: '3.8'
services:
  web:
    image: pyerp-linux
    ports:
      - "${PORT}:8000"
EOF
    
    # Run docker-compose
    if [ "$DETACH" = true ]; then
        docker-compose up -d
    else
        docker-compose up
    fi
else
    echo -e "${CYAN}Running container with docker run...${NC}"
    
    # Set detach mode if requested
    DETACH_ARG=""
    if [ "$DETACH" = true ]; then
        DETACH_ARG="-d"
    fi
    
    # Run the container
    docker run --rm -it $DETACH_ARG -p ${PORT}:8000 \
        -v "$(pwd):/app" \
        --name pyerp-linux-container \
        pyerp-linux
fi

echo -e "${GREEN}Container is running!${NC}"
if [ "$DETACH" = true ]; then
    echo -e "${CYAN}Access the application at http://localhost:${PORT}${NC}"
    echo -e "${CYAN}To view logs: docker logs -f pyerp-linux-container${NC}"
    echo -e "${CYAN}To stop container: docker stop pyerp-linux-container${NC}"
fi 