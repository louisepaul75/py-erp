#!/bin/bash
set -e

# Create Kibana configuration
mkdir -p /usr/share/kibana/config
cat > /usr/share/kibana/config/kibana.yml << EOF
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://localhost:9200"]
EOF

# Start supervisor which will manage Elasticsearch and Kibana
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf 