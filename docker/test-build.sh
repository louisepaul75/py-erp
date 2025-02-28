#!/bin/bash
# Test script to identify Docker build issues

# Copy our modified requirements file
cp requirements/production.in.testing requirements/production.in.test

# Try building with modified requirements
echo "Testing build without PDF libraries..."
DOCKER_BUILDKIT=1 docker build -f docker/Dockerfile.prod . 2>&1 | tee build-log.txt

# Restore original requirements
echo "Build test complete. See build-log.txt for details." 