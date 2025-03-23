#!/bin/bash
set -e

# Start Elasticsearch in the background
/usr/local/bin/docker-entrypoint.sh elasticsearch -d

# Start Kibana
/usr/share/kibana/bin/kibana --allow-root &

# Wait for Elasticsearch and Kibana to start
echo "Waiting for Elasticsearch and Kibana to start..."
sleep 30

# Run the Kibana setup script to create dashboard
echo "Setting up Kibana dashboards for developer filtering..."
python3 /usr/local/bin/kibana_setup.py

# Keep the container running
echo "Elasticsearch and Kibana are running."
tail -f /dev/null 