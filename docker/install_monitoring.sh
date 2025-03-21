#!/bin/bash
set -e

echo "Installing Elasticsearch, Kibana, Filebeat, and Sentry dependencies..."

# Install system dependencies
apt-get update
apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    supervisor \
    nginx \
    apt-transport-https \
    wget \
    gnupg \
    openjdk-17-jre-headless

# Add Elasticsearch GPG key and repository
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-8.x.list

# Update package lists
apt-get update

# Install Elasticsearch, Kibana, and Filebeat
apt-get install -y elasticsearch kibana filebeat

# Create directories for Elasticsearch data and logs
mkdir -p /var/lib/elasticsearch
mkdir -p /var/log/elasticsearch
mkdir -p /app/logs
chown -R elasticsearch:elasticsearch /var/lib/elasticsearch
chown -R elasticsearch:elasticsearch /var/log/elasticsearch

# Configure Elasticsearch with dynamic host
ES_HOST="${ELASTICSEARCH_HOST:-localhost}"
ES_PORT="${ELASTICSEARCH_PORT:-9200}"
KB_HOST="${KIBANA_HOST:-localhost}"
KB_PORT="${KIBANA_PORT:-5601}"

cat > /etc/elasticsearch/elasticsearch.yml << EOFELS
cluster.name: pyerp-monitoring
node.name: pyerp-node
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node
xpack.security.enabled: false
EOFELS

# Configure Kibana with dynamic Elasticsearch host
cat > /etc/kibana/kibana.yml << EOFKIB
server.port: 5601
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://${ES_HOST}:${ES_PORT}"]
EOFKIB

# Check if our custom Filebeat config exists and use it, otherwise create default
if [ -f /app/docker/filebeat_config.yml ]; then
    echo "Using custom Filebeat configuration from /app/docker/filebeat_config.yml"
    cp /app/docker/filebeat_config.yml /etc/filebeat/filebeat.yml
else
    # Configure Filebeat with dynamic hosts
    cat > /etc/filebeat/filebeat.yml << EOFFB
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /app/logs/*.log
  json.keys_under_root: true
  json.add_error_key: true
  json.message_key: message
  # Handle multiline stack traces
  multiline.pattern: '^[[:space:]]+(at|...)|^Caused by:'
  multiline.negate: false
  multiline.match: after

processors:
  - add_host_metadata: ~
  - add_docker_metadata: ~
  # Add custom tags
  - add_tags:
      tags: ["pyerp", "${PYERP_ENV:-development}"]

output.elasticsearch:
  hosts: ["${ES_HOST}:${ES_PORT}"]
  index: "pyerp-logs-%{+yyyy.MM.dd}"

setup.kibana:
  host: "${KB_HOST}:${KB_PORT}"

setup.template.name: "pyerp"
setup.template.pattern: "pyerp-*"
setup.template.settings:
  index.number_of_shards: 1
  index.number_of_replicas: 0
setup.ilm.enabled: false
EOFFB
fi

# Create Elasticsearch index templates for better field mapping
sleep 5  # Give Elasticsearch time to start up before creating templates

# Function to check if Elasticsearch is running
wait_for_elasticsearch() {
    echo "Waiting for Elasticsearch to start..."
    for i in {1..30}; do
        if curl -s "http://${ES_HOST}:${ES_PORT}" > /dev/null; then
            echo "Elasticsearch is ready!"
            return 0
        fi
        echo "Elasticsearch not ready yet, retrying in 5 seconds..."
        sleep 5
    done
    echo "Elasticsearch did not start in time"
    return 1
}

# Install pip and Python dependencies
apt-get install -y python3-pip
pip install --no-cache-dir sentry-sdk

# Create supervisord configurations for Elasticsearch, Kibana, and Filebeat
mkdir -p /etc/supervisor/conf.d

# Only create a supervisord.conf if it doesn't exist
if [ ! -f /etc/supervisor/conf.d/supervisord.conf ]; then
    cat > /etc/supervisor/conf.d/supervisord.conf << EOFSUP
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[unix_http_server]
file=/var/run/supervisor.sock
chmod=0700
username=root
password=root

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock
username=root
password=root
EOFSUP
fi

cat > /etc/supervisor/conf.d/elasticsearch.conf << EOFEL
[program:elasticsearch]
command=/usr/share/elasticsearch/bin/elasticsearch
user=elasticsearch
autostart=true
autorestart=true
startretries=3
stderr_logfile=/app/logs/elasticsearch-err.log
stdout_logfile=/app/logs/elasticsearch-out.log
priority=35
EOFEL

cat > /etc/supervisor/conf.d/kibana.conf << EOFKIB
[program:kibana]
command=/usr/share/kibana/bin/kibana
autostart=true
autorestart=true
startretries=3
stderr_logfile=/app/logs/kibana-err.log
stdout_logfile=/app/logs/kibana-out.log
priority=40
EOFKIB

cat > /etc/supervisor/conf.d/filebeat.conf << EOFFB
[program:filebeat]
command=/usr/share/filebeat/bin/filebeat -c /etc/filebeat/filebeat.yml -e
user=root
autostart=true
autorestart=true
startretries=3
stderr_logfile=/app/logs/filebeat-err.log
stdout_logfile=/app/logs/filebeat-out.log
priority=45
EOFFB

# Create directories for supervisor logs
mkdir -p /var/log/supervisor
mkdir -p /var/run

# Add a script to create Elasticsearch index templates that will run after Elasticsearch starts
cat > /app/create_es_templates.sh << 'EOF'
#!/bin/bash
set -e

ES_HOST="${ELASTICSEARCH_HOST:-localhost}"
ES_PORT="${ELASTICSEARCH_PORT:-9200}"

echo "Waiting for Elasticsearch to be ready..."
for i in {1..30}; do
    if curl -s "http://${ES_HOST}:${ES_PORT}" > /dev/null; then
        echo "Elasticsearch is ready!"
        break
    fi
    echo "Waiting for Elasticsearch... ($i/30)"
    sleep 5
    if [ $i -eq 30 ]; then
        echo "Elasticsearch did not start in time"
        exit 1
    fi
done

echo "Creating index template for pyerp logs..."
curl -X PUT "http://${ES_HOST}:${ES_PORT}/_index_template/pyerp-logs" -H 'Content-Type: application/json' -d'
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

echo "Creating security dashboard in Kibana..."
sleep 10  # Give Kibana some time to connect to Elasticsearch

# Try to create a basic dashboard for security logs
curl -X POST "http://${KB_HOST}:${KB_PORT}/api/saved_objects/index-pattern/pyerp-logs-*" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{"attributes":{"title":"pyerp-logs-*","timeFieldName":"timestamp"}}'

echo "Elasticsearch and Kibana setup completed."
EOF

chmod +x /app/create_es_templates.sh

# Add the template creation script to supervisor to run after Elasticsearch starts
cat > /etc/supervisor/conf.d/es_templates.conf << EOFET
[program:es_templates]
command=/app/create_es_templates.sh
user=root
autostart=true
autorestart=false
startsecs=0
startretries=3
stderr_logfile=/app/logs/es-templates-err.log
stdout_logfile=/app/logs/es-templates-out.log
priority=50
EOFET

echo "Installation and configuration of monitoring tools completed." 