#!/bin/bash

echo "Setting up production-like environment with HTTPS locally..."

# Remove old memory snapshots if they exist
echo "Removing old memory snapshots..."
rm -rf ./memory_snapshots_output/memory_snapshots
# Ensure the base output directory exists for potential later use (like copying)
mkdir -p ./memory_snapshots_output

# Ensure SSL directory exists
mkdir -p ./docker/nginx/ssl

# Generate self-signed certificates if they don't exist
if [ ! -f "./docker/nginx/ssl/server.crt" ] || [ ! -f "./docker/nginx/ssl/server.key" ]; then
  echo "Generating self-signed SSL certificates..."
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ./docker/nginx/ssl/server.key \
    -out ./docker/nginx/ssl/server.crt \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
fi

# Ensure nginx config directories exist
mkdir -p ./docker/nginx/conf.d

# Create Nginx configuration files
# echo "Creating Nginx configuration files..." <-- Removed

# Removed cat > ./docker/nginx/conf.d/pyerp.conf block

# Removed cat > ./docker/nginx/conf.d/pyerp.http.conf block

# echo "Nginx configuration files created" <-- Removed

# Create a local link to point to the SSL directories
echo "Preparing to run production rebuild script..."

# Make sure the certificate AND the correct config are accessible from where production expects it
mkdir -p ./docker/nginx # Ensure base dir exists
rm -rf /tmp/ssl /tmp/conf.d # Clean up previous temp copies
cp -r ./docker/nginx/ssl /tmp/
cp -r ./docker/nginx/conf.d /tmp/ # Copy the conf.d directory which should contain the corrected pyerp.prod.conf

# Run the production rebuild script with flags for this specific setup
echo "Building and starting production containers locally via rebuild script..."
./rebuild_docker.prod.sh --no-monitoring --no-tests --local-https --profile-memory

# Check if the rebuild script was successful
if [ $? -ne 0 ]; then
  echo "Error: rebuild_docker.prod.sh failed. Aborting setup."
  exit 1
fi

# Give container a moment to start up before copying files
sleep 5

# Once the container is running, copy the SSL certificates and configs into the container
# Ensure Nginx is using the correct config for HTTPS
echo "Copying SSL certificates and Nginx config to the Docker container..."
docker cp /tmp/ssl pyerp-prod:/etc/nginx/
docker cp /tmp/conf.d/pyerp.prod.conf pyerp-prod:/etc/nginx/conf.d/default.conf

# Restart Nginx in the container
echo "Restarting Nginx in the container..."
docker exec pyerp-prod supervisorctl restart nginx

echo "----------------------------------------"
echo "Local production environment started with HTTPS!"
echo "----------------------------------------"
echo "Frontend: https://localhost"
echo "Backend API: https://localhost/api"
echo "----------------------------------------"
echo "To stop the environment, run: docker-compose -f docker/docker-compose.prod.yml down"
echo "----------------------------------------" 