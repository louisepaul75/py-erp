#!/bin/bash
set -e

# Detect architecture for logging purposes
ARCH=$(uname -m)
echo "Container running on architecture: $ARCH"

# Start Elasticsearch in the background
echo "Starting Elasticsearch..."
/usr/local/bin/docker-entrypoint.sh elasticsearch -d

# Wait for Elasticsearch to be ready
echo "Waiting for Elasticsearch to become available..."
for i in {1..60}; do  # Increased timeout for slow machines
    if curl -s http://localhost:9200 > /dev/null; then
        echo "Elasticsearch is ready!"
        break
    fi
    echo "Waiting for Elasticsearch... attempt $i of 60"
    sleep 5
    
    if [ $i -eq 60 ]; then
        echo "Elasticsearch did not start in time. Check Elasticsearch logs."
        # Continue anyway so we can at least try to start Kibana
    fi
done

# Start Kibana with appropriate settings based on architecture
echo "Starting Kibana..."
KIBANA_ARGS="--allow-root"

# Add architecture-specific settings if needed
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    echo "Setting ARM-specific optimizations for Kibana"
    # Add any ARM-specific settings here if needed
    export NODE_OPTIONS="--max-old-space-size=2048"
fi

# Find and run Kibana
if [ -f /usr/share/kibana/bin/kibana ]; then
    echo "Using Kibana from /usr/share/kibana/bin"
    /usr/share/kibana/bin/kibana $KIBANA_ARGS &
elif [ -f /usr/bin/kibana ]; then
    echo "Using Kibana from /usr/bin"
    /usr/bin/kibana $KIBANA_ARGS &
else
    echo "Error: Could not find Kibana executable"
    echo "Directory contents of /usr/share/kibana/bin:"
    ls -la /usr/share/kibana/bin || true
    echo "Directory contents of /usr/bin:"
    ls -la /usr/bin/kibana* || true
    exit 1
fi

echo "Elasticsearch and Kibana are starting up..."
echo "- Elasticsearch: http://localhost:9200"
echo "- Kibana: http://localhost:5601"

# Keep the container running and show log output
tail -f /var/log/elasticsearch/*.log /usr/share/kibana/logs/*.log 2>/dev/null || tail -f /dev/null 