#!/bin/bash
# Script to test the monitoring setup by generating logs
# This script should be run from the project root

set -e

# Determine which container to use
if docker ps | grep -q pyerp-dev; then
    CONTAINER=pyerp-dev
elif docker ps | grep -q pyerp-prod; then
    CONTAINER=pyerp-prod
else
    echo "ERROR: No running pyERP container found."
    echo "Please start the container first with rebuild_docker.dev.sh or rebuild_docker.prod.sh"
    exit 1
fi

# Make the test script executable
chmod +x scripts/test_monitoring.py

# Default values
COUNT=100
DELAY=0.1
NO_ERRORS=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --count=*)
        COUNT="${1#*=}"
        shift
        ;;
        --delay=*)
        DELAY="${1#*=}"
        shift
        ;;
        --no-errors)
        NO_ERRORS="--no-errors"
        shift
        ;;
        *)
        echo "Unknown parameter: $1"
        echo "Usage: $0 [--count=N] [--delay=SECONDS] [--no-errors]"
        exit 1
        ;;
    esac
done

echo "Running monitoring test in $CONTAINER..."
echo "Generating $COUNT log messages with ${DELAY}s delay between each..."

# Run the test script in the container
docker exec -it $CONTAINER python /app/scripts/test_monitoring.py --count=$COUNT --delay=$DELAY $NO_ERRORS

echo "Test completed. Check the logs in the container."
echo "To view logs in Kibana, open http://localhost:5601"

# Check if Elasticsearch is running
ES_HOST=$(docker exec $CONTAINER bash -c 'echo $ELASTICSEARCH_HOST')
ES_PORT=$(docker exec $CONTAINER bash -c 'echo $ELASTICSEARCH_PORT')

echo "Checking if Elasticsearch is available at $ES_HOST:$ES_PORT..."
if docker exec $CONTAINER curl -s "http://$ES_HOST:$ES_PORT" > /dev/null; then
    echo "Elasticsearch is running."
    echo "Checking logs in Elasticsearch..."
    # Show log count by level
    docker exec $CONTAINER curl -s "http://$ES_HOST:$ES_PORT/pyerp-logs-*/_search?pretty" -H 'Content-Type: application/json' -d '{
        "size": 0,
        "aggs": {
            "log_levels": {
                "terms": {
                    "field": "level.keyword",
                    "size": 10
                }
            }
        }
    }' | grep -A 15 "aggregations"
else
    echo "Warning: Elasticsearch is not available. Check the container logs for errors."
fi

echo ""
echo "To analyze logs with more details:"
echo "1. Open Kibana at http://localhost:5601"
echo "2. Navigate to Discover"
echo "3. Create an index pattern 'pyerp-logs-*' if not already created"
echo "4. Explore logs with different filters" 