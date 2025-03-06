#!/bin/bash
# Script to set up HTTPS for Docker deployment
# Run this script on the Docker host server

# Create SSL directory if it doesn't exist
mkdir -p ./docker/nginx/ssl

# Generate self-signed certificates without SAN extension
# This simpler version will work for testing purposes
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./docker/nginx/ssl/server.key \
  -out ./docker/nginx/ssl/server.crt \
  -subj "/CN=localhost"

echo "SSL certificates generated successfully!"

# Set proper permissions
chmod 644 ./docker/nginx/ssl/server.crt
chmod 600 ./docker/nginx/ssl/server.key

# Display how to restart the Docker services
echo ""
echo "To apply the changes, restart your Docker containers with:"
echo "docker-compose -f docker/docker-compose.prod.yml down"
echo "docker-compose -f docker/docker-compose.prod.yml up -d"
