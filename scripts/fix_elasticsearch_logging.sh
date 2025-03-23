#!/bin/bash
# Script to fix the Elasticsearch logging issue by ensuring Filebeat is properly installed and configured

set -e

# Get the current date and time
timestamp() {
  date +"[%Y-%m-%d %H:%M:%S]"
}

# Find Elasticsearch container
echo "$(timestamp) Checking Elasticsearch container..."
ELASTICSEARCH_CONTAINER="pyerp-elastic-kibana"
if ! docker ps | grep -q "$ELASTICSEARCH_CONTAINER"; then
    echo "$(timestamp) ERROR: Elasticsearch container '$ELASTICSEARCH_CONTAINER' is not running"
    echo "$(timestamp) Please start it with: docker-compose -f docker/docker-compose.monitoring.yml up -d"
    exit 1
fi

# Get Elasticsearch container IP
ELASTICSEARCH_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $ELASTICSEARCH_CONTAINER)
if [ -z "$ELASTICSEARCH_IP" ]; then
    echo "$(timestamp) ERROR: Could not find IP address for $ELASTICSEARCH_CONTAINER"
    exit 1
fi
echo "$(timestamp) Found Elasticsearch at $ELASTICSEARCH_CONTAINER with IP $ELASTICSEARCH_IP"

# Set the container to fix (default to pyerp-dev or use first argument)
CONTAINER=${1:-"pyerp-dev"}
if ! docker ps | grep -q "$CONTAINER"; then
    echo "$(timestamp) ERROR: Container '$CONTAINER' is not running"
    exit 1
fi
echo "$(timestamp) Fixing log synchronization in container: $CONTAINER"

# Install Filebeat in the container if not already installed
echo "$(timestamp) Checking if Filebeat is installed..."
if ! docker exec $CONTAINER which filebeat > /dev/null 2>&1; then
    echo "$(timestamp) Installing Filebeat in the container..."
    docker exec -u root $CONTAINER bash -c "apt-get update && apt-get install -y apt-transport-https wget gnupg procps"
    docker exec -u root $CONTAINER bash -c "wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -"
    docker exec -u root $CONTAINER bash -c "echo 'deb https://artifacts.elastic.co/packages/7.x/apt stable main' > /etc/apt/sources.list.d/elastic-7.x.list"
    docker exec -u root $CONTAINER bash -c "apt-get update && apt-get install -y filebeat"
else
    echo "$(timestamp) Filebeat is already installed"
fi

# Create Filebeat directory structure
echo "$(timestamp) Creating Filebeat directory structure..."
docker exec -u root $CONTAINER mkdir -p /etc/filebeat /var/lib/filebeat /var/log/filebeat /app/logs

# Stop any running filebeat
echo "$(timestamp) Stopping any running Filebeat instances..."
docker exec -u root $CONTAINER bash -c "ps aux | grep filebeat | grep -v grep | awk '{print \$2}' | xargs -r kill -9" || true

# Remove any lock files and old logs
echo "$(timestamp) Removing any Filebeat lock files and old logs..."
docker exec -u root $CONTAINER bash -c "rm -f /var/lib/filebeat/filebeat.lock"
docker exec -u root $CONTAINER bash -c "rm -f /var/log/filebeat/filebeat"

# Copy the filebeat config to the container
echo "$(timestamp) Copying Filebeat configuration file to container..."
docker cp docker/filebeat_config.yml $CONTAINER:/etc/filebeat/filebeat.yml

# Set correct permissions
echo "$(timestamp) Setting correct permissions and ownership..."
docker exec -u root $CONTAINER bash -c "chown root:root /etc/filebeat/filebeat.yml"
docker exec -u root $CONTAINER bash -c "chmod go-w /etc/filebeat/filebeat.yml"

# Update filebeat.yml with correct Elasticsearch IP and Kibana host
echo "$(timestamp) Updating filebeat.yml with correct Elasticsearch IP..."
docker exec -u root $CONTAINER bash -c "sed -i 's/\${ELASTICSEARCH_HOST}/$ELASTICSEARCH_IP/g' /etc/filebeat/filebeat.yml"
docker exec -u root $CONTAINER bash -c "sed -i 's/\${KIBANA_HOST}/$ELASTICSEARCH_IP/g' /etc/filebeat/filebeat.yml"

# Create Elasticsearch index template
echo "$(timestamp) Setting up Elasticsearch index template..."
docker cp scripts/create_elasticsearch_pipeline.sh $CONTAINER:/tmp/
docker exec -u root $CONTAINER bash -c "chmod +x /tmp/create_elasticsearch_pipeline.sh"
docker exec -u root $CONTAINER bash -c "/tmp/create_elasticsearch_pipeline.sh $ELASTICSEARCH_IP"

# Make sure data directory exists with correct permissions
docker exec -u root $CONTAINER bash -c "mkdir -p /var/lib/filebeat && chown root:root /var/lib/filebeat"

# Start filebeat with the updated configuration
echo "$(timestamp) Starting Filebeat with updated configuration..."
docker exec -u root -d $CONTAINER bash -c "nohup /usr/bin/filebeat -e -c /etc/filebeat/filebeat.yml > /app/logs/filebeat_stdout.log 2>&1 &"

# Check if filebeat is running
sleep 5
FILEBEAT_PID=$(docker exec -u root $CONTAINER bash -c "ps aux | grep filebeat | grep -v grep | awk '{print \$2}'")

if [ -z "$FILEBEAT_PID" ]; then
    echo "$(timestamp) ERROR: Filebeat failed to start. Check logs at /app/logs/filebeat_stdout.log"
    exit 1
else
    echo "$(timestamp) Filebeat is running with PID: $FILEBEAT_PID"
    echo "$(timestamp) Log synchronization fix complete!"
    
    # Generate some test logs to verify everything is working
    echo "$(timestamp) Generating test logs to verify the setup..."
    docker exec -u root $CONTAINER bash -c "python /app/scripts/test_monitoring.py --count=5 --delay=0.1"
    
    # Wait for logs to be processed
    sleep 5
    
    # Check if logs appear in Elasticsearch
    echo "$(timestamp) Checking if logs are showing up in Elasticsearch..."
    RESPONSE=$(docker exec -u root $CONTAINER bash -c "curl -s 'http://$ELASTICSEARCH_IP:9200/pyerp-*/_search?pretty' -H 'Content-Type: application/json' -d '{\"size\": 0}'")
    
    # Check if any documents are found
    COUNT=$(echo $RESPONSE | grep -o '"count" : [0-9]*' | awk '{print $3}')
    if [ -z "$COUNT" ] || [ "$COUNT" -eq 0 ]; then
        echo "$(timestamp) WARNING: No logs found in Elasticsearch yet. This may take a few moments."
        echo "$(timestamp) To check manually, run:"
        echo "docker exec -it $CONTAINER curl -s 'http://$ELASTICSEARCH_IP:9200/pyerp-*/_search?pretty'"
    else
        echo "$(timestamp) Success! Found $COUNT log entries in Elasticsearch."
    fi
    
    echo ""
    echo "To verify logs in Kibana:"
    echo "1. Open Kibana at http://localhost:5602"
    echo "2. Navigate to Discover"
    echo "3. Create an index pattern 'pyerp-*' if not already created"
    echo "4. Explore logs with different filters"
fi 