#!/bin/bash

echo "Starting pyERP in debug mode with live editing"
echo "-------------------------------------------"
echo "This will mount the frontend code for live editing and disable minification"
echo ""

# Run the rebuild script with both debug and live-edit flags
./rebuild_docker.prod.sh --debug --live-edit

echo ""
echo "Starting monitoring containers..."
docker-compose -f docker/docker-compose.monitoring.yml up -d

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
        echo "Elasticsearch did not start in time. Please check Elasticsearch logs."
        echo "You can check logs with: docker logs pyerp-elastic-kibana"
    fi
done

echo ""
echo "Development setup completed!"
echo "-------------------------------------------"
echo "Access the app with non-minified code at: http://localhost:3000"
echo "You can now edit files in the frontend-react directory and see changes immediately"
echo "Changes to the following files will be applied instantly:"
echo "  - frontend-react/src/**/*"
echo ""
echo "Monitoring services:"
echo "- Elasticsearch: http://localhost:9200"
echo "- Kibana: http://localhost:5601"
echo ""
echo "View application logs with: docker logs -f pyerp-prod"
echo "View monitoring logs with: docker logs -f pyerp-elastic-kibana" 