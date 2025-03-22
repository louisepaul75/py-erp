#!/bin/bash
# Script to create Elasticsearch pipeline for handling JSON parsing errors

# Use the provided Elasticsearch IP or default to localhost
ELASTIC_IP=${1:-"localhost"}
ELASTIC_PORT=${2:-"9200"}

echo "Using Elasticsearch at $ELASTIC_IP:$ELASTIC_PORT"

echo "Creating Elasticsearch JSON error handling pipeline..."

# Delete the existing pipeline if it exists
curl -X DELETE "http://$ELASTIC_IP:$ELASTIC_PORT/_ingest/pipeline/json-error-pipeline" -H 'Content-Type: application/json'

# Delete old indices to avoid mapping conflicts
curl -X DELETE "http://$ELASTIC_IP:$ELASTIC_PORT/pyerp-*" -H 'Content-Type: application/json'

# Create an index template for pyERP logs
curl -X PUT "http://$ELASTIC_IP:$ELASTIC_PORT/_template/pyerp-template" -H 'Content-Type: application/json' -d '
{
  "index_patterns": ["pyerp-*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "dynamic": true,
    "properties": {
      "@timestamp": { "type": "date" },
      "message": { "type": "text" },
      "service": { 
        "type": "object",
        "dynamic": true,
        "properties": {
          "name": { "type": "keyword" },
          "type": { "type": "keyword" }
        }
      },
      "error": { "type": "object", "dynamic": true }
    }
  }
}'

echo "Setup of Elasticsearch indices and templates complete" 