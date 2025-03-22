#!/bin/bash
# Script to fix the log synchronization issue between pyERP and Elasticsearch

# Get the current date and time
timestamp() {
  date +"[%Y-%m-%d %H:%M:%S]"
}

# Find Elasticsearch container
ELASTICSEARCH_CONTAINER="pyerp-elastic-kibana"
ELASTICSEARCH_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $ELASTICSEARCH_CONTAINER)

if [ -z "$ELASTICSEARCH_IP" ]; then
    echo "$(timestamp) Could not find Elasticsearch container at $ELASTICSEARCH_CONTAINER"
    exit 1
fi

echo "$(timestamp) Found Elasticsearch at $ELASTICSEARCH_CONTAINER with IP $ELASTICSEARCH_IP"

# Set the container to fix
CONTAINER=${1:-"pyerp-dev"}
echo "$(timestamp) Fixing log synchronization in container: $CONTAINER"

# Create Filebeat directory structure
echo "$(timestamp) Creating Filebeat directory structure..."
docker exec -u root $CONTAINER mkdir -p /etc/filebeat /var/lib/filebeat /var/log/filebeat

# Install procps for ps command
echo "$(timestamp) Installing procps for process management..."
docker exec -u root $CONTAINER apt-get update
docker exec -u root $CONTAINER apt-get install -y procps

# Check if Filebeat is installed
FILEBEAT_PATH=$(docker exec $CONTAINER which filebeat || echo "")

if [ -z "$FILEBEAT_PATH" ]; then
    echo "$(timestamp) Error: Filebeat is not installed in the container"
    exit 1
else
    echo "$(timestamp) Filebeat is already installed at: $FILEBEAT_PATH"
fi

# Stop any running filebeat
echo "$(timestamp) Stopping any running Filebeat instances..."
docker exec -u root $CONTAINER bash -c "ps aux | grep filebeat | grep -v grep | awk '{print \$2}' | xargs -r kill -9"

# Remove any lock files and old logs
echo "$(timestamp) Removing any Filebeat lock files and old logs..."
docker exec -u root $CONTAINER bash -c "rm -f /var/lib/filebeat/filebeat.lock"
docker exec -u root $CONTAINER bash -c "rm -f /var/log/filebeat/filebeat"

# Copy the local filebeat config to the container
echo "$(timestamp) Copying Filebeat configuration file to container..."
docker cp docker/filebeat_config.yml $CONTAINER:/etc/filebeat/filebeat.yml

# Set correct permissions
echo "$(timestamp) Setting correct permissions and ownership..."
docker exec -u root $CONTAINER bash -c "chown root:root /etc/filebeat/filebeat.yml"
docker exec -u root $CONTAINER bash -c "chmod go-w /etc/filebeat/filebeat.yml"

# Check file size
FILE_SIZE=$(docker exec -u root $CONTAINER bash -c "ls -l /etc/filebeat/filebeat.yml | awk '{print \$5}'")
FILE_SIZE_HUMAN=$(docker exec -u root $CONTAINER bash -c "ls -lh /etc/filebeat/filebeat.yml | awk '{print \$5}'")
echo "$(timestamp) Filebeat configuration file size: $FILE_SIZE_HUMAN"

# Update filebeat.yml with correct Elasticsearch IP and Kibana host
echo "$(timestamp) Updating filebeat.yml with correct Elasticsearch IP..."
docker exec -u root $CONTAINER bash -c "sed -i 's/\${ELASTICSEARCH_HOST}/$ELASTICSEARCH_IP/g' /etc/filebeat/filebeat.yml"
docker exec -u root $CONTAINER bash -c "sed -i 's/\${KIBANA_HOST}/$ELASTICSEARCH_IP/g' /etc/filebeat/filebeat.yml"

# Set up Elasticsearch pipeline and template
echo "$(timestamp) Setting up Elasticsearch pipeline and template..."
docker cp scripts/create_elasticsearch_pipeline.sh $CONTAINER:/tmp/
docker exec -u root $CONTAINER bash -c "chmod +x /tmp/create_elasticsearch_pipeline.sh"
docker exec -u root $CONTAINER bash -c "/tmp/create_elasticsearch_pipeline.sh $ELASTICSEARCH_IP"

# Make sure data directory exists with correct permissions
docker exec -u root $CONTAINER bash -c "mkdir -p /var/lib/filebeat && chown root:root /var/lib/filebeat"

# Start filebeat with the updated configuration
echo "$(timestamp) Starting Filebeat with updated configuration..."
docker exec -u root -d $CONTAINER bash -c "nohup /usr/share/filebeat/bin/filebeat --path.home /usr/share/filebeat --path.config /etc/filebeat --path.data /var/lib/filebeat --path.logs /var/log/filebeat -e -c /etc/filebeat/filebeat.yml > /app/logs/filebeat_stdout.log 2>&1 &"

# Check if filebeat is running
sleep 2
FILEBEAT_PID=$(docker exec -u root $CONTAINER bash -c "ps aux | grep filebeat | grep -v grep | awk '{print \$2}'")

if [ -z "$FILEBEAT_PID" ]; then
    echo "$(timestamp) Error: Filebeat failed to start"
    exit 1
else
    echo "$(timestamp) Filebeat is running with PID: $FILEBEAT_PID"
    echo "$(timestamp) Log synchronization setup complete!"
    echo ""
    echo "Run the monitoring test script to generate logs:"
    echo "  python scripts/monitoring_test.py"
    echo ""
    echo "View logs in Kibana: http://localhost:5601"
fi 