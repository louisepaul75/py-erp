#!/bin/bash
set -e

# Install development dependencies if needed
if [ ! -f /app/.devdeps_installed ]; then
    echo "Installing development dependencies..."
    cd /app && pip install -r requirements/development.txt
    touch /app/.devdeps_installed
fi

# Create necessary directories
mkdir -p /app/logs
chmod -R 777 /app/logs

# Ensure Filebeat is properly set up for logging
if [ -f /usr/bin/filebeat ]; then
    echo "Configuring Filebeat for log shipping to Elasticsearch..."
    
    # Create required directories with proper permissions
    mkdir -p /var/lib/filebeat /var/log/filebeat
    chown root:root /etc/filebeat/filebeat.yml
    chmod go-w /etc/filebeat/filebeat.yml
    
    # Remove any existing lock file that might prevent startup
    rm -f /var/lib/filebeat/filebeat.lock
    rm -f /var/lib/filebeat/registry/filebeat
    rm -f /var/lib/filebeat/registry.old
    
    # Replace environment variables in config
    ES_HOST="${ELASTICSEARCH_HOST:-localhost}"
    sed -i "s/\${ELASTICSEARCH_HOST}/$ES_HOST/g" /etc/filebeat/filebeat.yml
    
    KB_HOST="${KIBANA_HOST:-localhost}"
    sed -i "s/\${KIBANA_HOST}/$KB_HOST/g" /etc/filebeat/filebeat.yml
    
    echo "Filebeat configuration completed for Elasticsearch: $ES_HOST, Kibana: $KB_HOST"
    
    # Filebeat will be managed by supervisord, not started here
    echo "Filebeat will be started by supervisord..."
else
    echo "Warning: Filebeat not found. Logs will not be shipped to Elasticsearch."
    echo "Run fix_elasticsearch_logging.sh to install and configure Filebeat."
fi

# Execute the command passed to the entrypoint
exec "$@" 