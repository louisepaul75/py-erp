#!/bin/bash
# Direct Install Docker Build Script
# This script builds a Docker image using the direct installation approach (no pip-compile)

set -e  # Exit on error

# ANSI color codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Docker image with direct dependency installation...${NC}"

# Navigate to the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Make sure we are in the project root
cd "$PROJECT_ROOT"

# Build the Docker image
echo -e "${CYAN}Building Docker image using direct dependency installation...${NC}"
docker build -f docker/Dockerfile.dev-direct -t pyerp-dev .
BUILD_EXIT_CODE=$?

# Check if the build succeeded
if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Docker build succeeded!${NC}"
    echo -e "${YELLOW}The direct installation approach worked. Consider updating your main Dockerfile.dev with this approach.${NC}"
    
    # Run the container
    echo -e "\n${CYAN}Do you want to run the container now? (y/n)${NC}"
    read -r response
    
    if [ "$response" = "y" ]; then
        echo -e "${CYAN}Running the Docker container...${NC}"
        docker run --rm -it -p 8000:8000 pyerp-dev
    fi
else
    echo -e "${RED}Docker build failed.${NC}"
    echo -e "${YELLOW}There might be issues with the dependencies themselves.${NC}"
    exit 1
fi 