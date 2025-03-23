#!/bin/bash

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
docker build -t pyerp-prod-image -f docker/Dockerfile.prod \
  --build-arg DJANGO_SETTINGS_MODULE=pyerp.config.settings.production .

# Create Docker network if it doesn't exist
echo "Ensuring Docker network exists..."
docker network create pyerp-network 2>/dev/null || true

# Start a new container
echo "Starting new pyerp-prod container..."
docker run -d \
  --name pyerp-prod \
  --env-file config/env/.env.prod \
  -e ELASTICSEARCH_HOST=pyerp-elastic-kibana \
  -e ELASTICSEARCH_PORT=9200 \
  -e KIBANA_HOST=pyerp-elastic-kibana \
  -e KIBANA_PORT=5601 \
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
