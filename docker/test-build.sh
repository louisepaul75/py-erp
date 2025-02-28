#!/bin/bash
set -e

# Run dependency scanner first
echo "Running dependency scanner..."
cd "$(dirname "$0")/.."
python scripts/check_dependencies.py

# Build the Docker image
echo "Building Docker image..."
cd "$(dirname "$0")"
docker build -f test-pdf-deps.dockerfile -t pyerp-pdf-test .

echo "Build completed successfully!"
echo "You can run the container with: docker run --rm pyerp-pdf-test" 