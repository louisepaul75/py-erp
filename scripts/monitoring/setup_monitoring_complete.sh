#!/bin/bash
set -e

echo "Setting up ELK Stack monitoring for pyERP production environment..."

# Wait for Elasticsearch to be ready
echo "Waiting for Elasticsearch to become available..."
for i in {1..30}; do
    if curl -s http://localhost:9200 > /dev/null; then
        echo "Elasticsearch is ready!"
        break
    fi
    echo "Waiting for Elasticsearch... attempt $i of 30"
    sleep 5
    
    if [ $i -eq 30 ]; then
        echo "Elasticsearch did not start in time. Check Elasticsearch logs."
        exit 1
    fi
done

# Create index pattern for logs
echo "Creating index template for pyERP logs..."
curl -X PUT "http://localhost:9200/_index_template/pyerp-logs" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["pyerp-logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    },
    "mappings": {
      "properties": {
        "timestamp": { "type": "date" },
        "@timestamp": { "type": "date" },
        "message": { "type": "text" },
        "level": { "type": "keyword" },
        "name": { "type": "keyword" },
        "hostname": { "type": "keyword" },
        "environment": { "type": "keyword" },
        "service": { "type": "keyword" },
        "user_id": { "type": "keyword" },
        "request_id": { "type": "keyword" },
        "ip_address": { "type": "ip" },
        "exception": { "type": "text" },
        "path": { "type": "keyword" },
        "method": { "type": "keyword" },
        "status_code": { "type": "integer" },
        "duration_ms": { "type": "float" },
        "tags": { "type": "keyword" }
      }
    }
  }
}
'

# Wait for Kibana to be ready
echo "Waiting for Kibana to become available..."
for i in {1..30}; do
    if curl -s http://localhost:5601/api/status > /dev/null; then
        echo "Kibana is ready!"
        break
    fi
    echo "Waiting for Kibana... attempt $i of 30"
    sleep 5
    
    if [ $i -eq 30 ]; then
        echo "Kibana did not start in time. Check Kibana logs."
        exit 1
    fi
done

# Configure Filebeat
echo "Configuring Filebeat to ship logs to Elasticsearch..."
if [ ! -f /etc/filebeat/filebeat.yml ]; then
    # If no configuration exists, copy the template
    if [ -f /app/docker/filebeat_config.yml ]; then
        cp /app/docker/filebeat_config.yml /etc/filebeat/filebeat.yml
        echo "Copied Filebeat configuration from template."
    else
        echo "Error: Filebeat configuration template not found."
        exit 1
    fi
fi

# Restart Filebeat to apply configuration
echo "Restarting Filebeat service..."
supervisorctl restart filebeat

echo "ELK Stack monitoring setup complete!"
echo "Elasticsearch: http://localhost:9200"
echo "Kibana: http://localhost:5601" 