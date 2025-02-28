#!/bin/bash
# Script to set up HTTPS for Docker deployment
# Run this script on the Docker host server

# Create SSL directory if it doesn't exist
mkdir -p ./docker/nginx/ssl

# Generate self-signed certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./docker/nginx/ssl/server.key \
  -out ./docker/nginx/ssl/server.crt \
  -subj "/CN=localhost" \
  -addext "subjectAltName = DNS:localhost,DNS:yourdomain.com,IP:your_server_ip"

echo "SSL certificates generated successfully!"
echo "Please replace 'yourdomain.com' and 'your_server_ip' in the script with your actual domain and IP"

# Display how to restart the Docker services
echo ""
echo "To apply the changes, restart your Docker containers with:"
echo "docker-compose -f docker/docker-compose.prod.yml down"
echo "docker-compose -f docker/docker-compose.prod.yml up -d" 