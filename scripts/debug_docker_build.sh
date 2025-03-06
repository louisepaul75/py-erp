#!/bin/bash
# Debug Docker Build Script
# This script builds a Docker image using the debug Dockerfile
# to identify dependency issues

set -e  # Exit on error

# ANSI color codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building debug Docker image to identify dependency issues...${NC}"

# Navigate to the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Make sure we are in the project root
cd "$PROJECT_ROOT"

# Build the Docker image
echo -e "${CYAN}Building Docker image with debug configuration...${NC}"
docker build -f docker/Dockerfile.dev-debug -t pyerp-debug .
BUILD_EXIT_CODE=$?

# Check if the build succeeded
if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Docker build succeeded!${NC}"
    echo -e "${GREEN}This means all dependencies can be installed individually.${NC}"
    echo -e "${YELLOW}The issue might be related to conflicts between packages during pip-compile.${NC}"

    # Suggest alternative approach
    echo -e "\n${CYAN}Suggested workaround:${NC}"
    echo "1. Skip pip-compile in the Dockerfile"
    echo "2. Install packages directly from the .in file with pip install -r requirements/development.in"
    echo "3. For production, consider pre-compiling the requirements.txt files locally"
else
    echo -e "${RED}Docker build failed.${NC}"
    echo -e "${YELLOW}Review the output to identify which package is causing the issue.${NC}"
    exit 1
fi
