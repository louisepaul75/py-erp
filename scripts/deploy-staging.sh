#!/bin/bash
set -e

# Script to deploy the pyERP application to staging environment

echo "Setting up staging deployment for pyERP..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Pull the latest code if needed
# git pull origin dev

# Deploy with Docker Compose
echo "Deploying with Docker Compose..."
docker-compose -f docker/docker-compose.prod.yml --env-file config/env/.env.prod up -d

# Run migrations
echo "Running database migrations..."
docker-compose -f docker/docker-compose.prod.yml --env-file config/env/.env.prod exec -T pyerp python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
docker-compose -f docker/docker-compose.prod.yml --env-file config/env/.env.prod exec -T pyerp python manage.py collectstatic --noinput

# Check if deployment was successful
echo "Checking deployment status..."
docker-compose -f docker/docker-compose.prod.yml --env-file config/env/.env.prod ps

echo "Deployment completed successfully!" 