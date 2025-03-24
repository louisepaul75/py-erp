#!/bin/bash

# Check if running in debug mode
DEBUG_MODE=false
if [[ "$1" == "--debug" ]]; then
  DEBUG_MODE=true
  echo "Running in debug mode - optimizing for localhost testing"
fi

# Stop the existing container
echo "Stopping existing pyerp-prod container..."
docker stop pyerp-prod || true

# Remove the existing container
echo "Removing existing pyerp-prod container..."
docker rm pyerp-prod || true

# Stop the existing monitoring container if it exists
echo "Stopping existing monitoring container..."
docker stop pyerp-elastic-kibana || true
docker rm pyerp-elastic-kibana || true

# Rebuild the Docker image
echo "Rebuilding Docker image..."

if [ "$DEBUG_MODE" = true ]; then
  # Debug mode build with special flags
  docker build -t pyerp-prod-image -f docker/Dockerfile.prod \
    --build-arg DJANGO_SETTINGS_MODULE=pyerp.config.settings.production \
    --build-arg DEBUG_MODE=true .
else
  # Normal production build
  docker build -t pyerp-prod-image -f docker/Dockerfile.prod \
    --build-arg DJANGO_SETTINGS_MODULE=pyerp.config.settings.production .
fi

# Create Docker network if it doesn't exist
echo "Ensuring Docker network exists..."
docker network create pyerp-network 2>/dev/null || true

# Start a new container
echo "Starting new pyerp-prod container..."

# Determine which env file to use based on mode
ENV_FILE="config/env/.env.prod"
if [ "$DEBUG_MODE" = true ]; then
  ENV_FILE="config/env/.env.prod.local"
  # Create local env file if it doesn't exist
  if [ ! -f "$ENV_FILE" ]; then
    echo "Creating local debugging env file..."
    cp config/env/.env.prod "$ENV_FILE"
    echo "DEBUG=True" >> "$ENV_FILE"
    echo "ALLOWED_HOSTS=localhost,127.0.0.1" >> "$ENV_FILE"
  fi
fi

docker run -d \
  --name pyerp-prod \
  --env-file $ENV_FILE \
  -e ELASTICSEARCH_HOST=pyerp-elastic-kibana \
  -e ELASTICSEARCH_PORT=9200 \
  -e KIBANA_HOST=pyerp-elastic-kibana \
  -e KIBANA_PORT=5601 \
  -e DEBUG_MODE=${DEBUG_MODE} \
  -p 80:80 \
  -p 443:443 \
  -v $(pwd)/docker/nginx/ssl:/etc/nginx/ssl \
  --network pyerp-network \
  --restart unless-stopped \
  pyerp-prod-image

# Follow the logs for just 10 seconds to see startup
echo "Showing initial container logs (10 seconds)..."
# Use a macOS compatible approach instead of timeout command
(docker logs -f pyerp-prod & PID=$!; sleep 10; kill $PID) || true

echo -e "\nContainer is running in the background. Use 'docker logs pyerp-prod' to view logs again."

# Start the monitoring container
echo "Starting monitoring container..."
docker-compose -f docker/docker-compose.monitoring.yml up -d

echo -e "\nMonitoring services:"
echo -e "- Elasticsearch: http://localhost:9200"
echo -e "- Kibana: http://localhost:5601"
echo -e "Monitoring container logs: docker logs pyerp-elastic-kibana"

# Wait for Elasticsearch to be ready before running setup
echo "Waiting for Elasticsearch to become available..."
for i in {1..30}; do
    if curl -s http://localhost:9200 > /dev/null; then
        echo "Elasticsearch is ready!"
        break
    fi
    echo "Waiting for Elasticsearch... attempt $i of 30"
    sleep 5
    
    if [ $i -eq 30 ]; then
        echo "Elasticsearch did not start in time. Please check Elasticsearch logs."
        echo "You can check logs with: docker logs pyerp-elastic-kibana"
    fi
done

if [ "$DEBUG_MODE" = true ]; then
  echo -e "\nDebug mode is active. Access the application at:"
  echo -e "- http://localhost (HTTP)"
  echo -e "- https://localhost (HTTPS - you may need to accept the self-signed certificate)"
  echo -e "\nTo check for frontend issues, open browser devtools (F12) and check the console"
fi
