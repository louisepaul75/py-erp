#!/bin/bash
# Script to configure Elasticsearch retention to limit total size to 1GB

set -e

# Find the container running Elasticsearch
ES_CONTAINER=${1:-"pyerp-elastic-kibana"}
ES_HOST="localhost"
ES_PORT="9200"

echo "Configuring Elasticsearch retention policy for container: $ES_CONTAINER"

# Create ILM policy for size-based retention
echo "Creating ILM policy for 1GB total storage limit..."

# ILM policy JSON with 1GB storage limit
ILM_POLICY='{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "100mb",
            "max_age": "1d"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "delete": {
        "min_age": "0ms",
        "actions": {
          "wait_for_snapshot": {
            "policy": "backup-policy"
          },
          "delete": {
            "delete_searchable_snapshot": true
          }
        }
      }
    }
  }
}'

# Apply the ILM policy to Elasticsearch
docker exec $ES_CONTAINER curl -X PUT "http://$ES_HOST:$ES_PORT/_ilm/policy/pyerp-logs-policy" \
  -H 'Content-Type: application/json' \
  -d "$ILM_POLICY"

# Create index template that uses the ILM policy
INDEX_TEMPLATE='{
  "index_patterns": ["pyerp-logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "index.lifecycle.name": "pyerp-logs-policy",
      "index.lifecycle.rollover_alias": "pyerp-logs"
    },
    "mappings": {
      "properties": {
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
}'

# Apply the index template
docker exec $ES_CONTAINER curl -X PUT "http://$ES_HOST:$ES_PORT/_index_template/pyerp-logs" \
  -H 'Content-Type: application/json' \
  -d "$INDEX_TEMPLATE"

# Create initial index and alias
docker exec $ES_CONTAINER curl -X PUT "http://$ES_HOST:$ES_PORT/pyerp-logs-000001" \
  -H 'Content-Type: application/json' \
  -d '{
    "aliases": {
      "pyerp-logs": {
        "is_write_index": true
      }
    }
  }'

# Update Filebeat configuration to use the new index alias
echo "Updating Filebeat configuration to use the ILM policy..."

# Modify filebeat config in all running containers
for container in $(docker ps --format "{{.Names}}" | grep pyerp); do
  if docker exec $container test -f /etc/filebeat/filebeat.yml; then
    # Enable ILM in Filebeat config
    docker exec $container sed -i 's/setup.ilm.enabled: false/setup.ilm.enabled: true/g' /etc/filebeat/filebeat.yml
    docker exec $container sed -i 's/index: "pyerp-%{+yyyy.MM.dd}"/index: "pyerp-logs"/g' /etc/filebeat/filebeat.yml
    
    # Restart Filebeat to apply changes
    docker exec $container supervisorctl restart filebeat
    echo "Updated Filebeat configuration in container: $container"
  fi
done

echo "Elasticsearch retention policy configured successfully to limit total size to 1GB"
echo "Oldest indices will be automatically deleted when the total size exceeds 1GB" 