#!/bin/bash

# Stop the existing container
echo "Stopping existing pyerp-prod container..."
docker stop pyerp-prod || true

# Remove the existing container
echo "Removing existing pyerp-prod container..."
docker rm pyerp-prod || true

# Rebuild the Docker image
echo "Rebuilding Docker image..."
docker build -t pyerp-prod-image -f docker/Dockerfile.prod \
  --build-arg DJANGO_SETTINGS_MODULE=pyerp.config.settings.production .

# Add monitoring environment variables
MONITORING_ENV="-e ELASTICSEARCH_HOST=localhost -e ELASTICSEARCH_PORT=9200 -e KIBANA_HOST=localhost -e KIBANA_PORT=5601 -e SENTRY_DSN=https://production@sentry.example.com/1"

# Start a new container
echo "Starting new pyerp-prod container..."
docker run -d \
  --name pyerp-prod \
  --env-file config/env/.env.prod \
  $MONITORING_ENV \
  -p 80:80 \
  -p 443:443 \
  -p 9200:9200 \
  -p 5601:5601 \
  -v $(pwd)/docker/nginx/ssl:/etc/nginx/ssl \
  -v pyerp_elasticsearch_data_prod:/var/lib/elasticsearch \
  pyerp-prod-image

# Follow the logs for just 10 seconds to see startup
echo "Showing initial container logs (10 seconds)..."
timeout 10 docker logs -f pyerp-prod || true

echo -e "\nContainer is running in the background. Use 'docker logs pyerp-prod' to view logs again."
echo -e "\nMonitoring services:"
echo -e "- Elasticsearch: http://localhost:9200"
echo -e "- Kibana: http://localhost:5601"
echo -e "- Sentry: Integrated with Django application"

# Frage den Benutzer, ob das Remote-Monitoring eingerichtet werden soll
echo ""
read -p "Möchten Sie das Monitoring-System auf dem Remote-Server (192.168.73.65) einrichten? (j/n): " setup_remote

if [[ $setup_remote == "j" || $setup_remote == "J" || $setup_remote == "y" || $setup_remote == "Y" ]]; then
    # Führe das setup_monitoring_complete.sh Skript aus
    echo "Starte Remote-Monitoring-Setup..."
    bash ./setup_monitoring_complete.sh
else
    echo "Remote-Monitoring-Setup übersprungen."
fi
