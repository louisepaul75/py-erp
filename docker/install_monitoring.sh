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

# Configure Elasticsearch
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

# Configure Kibana
cat > /etc/kibana/kibana.yml << EOFKIB
server.port: 5601
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://localhost:9200"]
EOFKIB

# Configure Filebeat
cat > /etc/filebeat/filebeat.yml << EOFFB
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /app/logs/*.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "pyerp-logs-%{+yyyy.MM.dd}"

setup.kibana:
  host: "localhost:5601"

setup.template.name: "pyerp"
setup.template.pattern: "pyerp-*"
setup.ilm.enabled: false
EOFFB

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

echo "Installation and configuration of monitoring tools completed." 