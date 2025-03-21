#!/bin/bash
set -e

# Konfiguration
TARGET_IP="192.168.73.65"
TARGET_USER="admin-local"
REMOTE_DIR="/home/admin-local/pyerp-monitoring"

echo "=== pyERP Monitoring-System Setup ==="
echo "Ziel: $TARGET_USER@$TARGET_IP:$REMOTE_DIR"
echo "======================================="

# Temporäres Verzeichnis für die Setup-Dateien erstellen
TEMP_DIR=$(mktemp -d)
echo "Temporäres Verzeichnis erstellt: $TEMP_DIR"

# Docker-Compose-Datei für das Monitoring-System erstellen
cat > $TEMP_DIR/docker-compose.monitoring.yml << 'EOF'
# WARNING: NEVER ADD CREDENTIALS DIRECTLY TO THIS FILE
# All sensitive information should be stored in the environment files in config/env directory
# This file should be safe to commit to version control

version: '3.8'

services:
  pyerp-monitoring:
    image: docker.io/library/python:3.12-slim
    container_name: pyerp-monitoring
    ports:
      - "9200:9200"  # Elasticsearch
      - "5601:5601"  # Kibana
    volumes:
      - ./logs:/app/logs
      - elasticsearch_data:/var/lib/elasticsearch
    environment:
      - ELASTICSEARCH_HOST=localhost
      - ELASTICSEARCH_PORT=9200
      - KIBANA_HOST=localhost
      - KIBANA_PORT=5601
      - SENTRY_DSN=https://development@sentry.example.com/1
    command: >
      bash -c "
        cd /app &&
        bash /app/install_monitoring.sh &&
        /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
      "

volumes:
  elasticsearch_data:
EOF

# Installation-Skript für das Monitoring-System erstellen
cat > $TEMP_DIR/install_monitoring.sh << 'EOF'
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
EOF

# Start-Skript für das Monitoring-System erstellen
cat > $TEMP_DIR/start_monitoring.sh << 'EOF'
#!/bin/bash
set -e

# Stop and remove existing container if it exists
echo "Stopping existing pyerp-monitoring container..."
docker stop pyerp-monitoring || true
echo "Removing existing pyerp-monitoring container..."
docker rm pyerp-monitoring || true

# Create logs directory if it doesn't exist
mkdir -p ./logs

# Start the monitoring container
echo "Starting pyERP monitoring system..."
docker-compose -f docker-compose.monitoring.yml up -d

# Show container status
echo "Container status:"
docker ps | grep pyerp-monitoring

echo -e "\nMonitoring system is running in the background."
echo -e "Services available at:"
echo -e "- Elasticsearch: http://localhost:9200"
echo -e "- Kibana: http://localhost:5601"
echo -e "\nTo view logs, run: docker logs pyerp-monitoring"
EOF

# Remote-Setup-Skript erstellen
cat > $TEMP_DIR/remote_setup.sh << 'EOF'
#!/bin/bash
set -e

# Create the necessary directories
mkdir -p ~/pyerp-monitoring/logs

# Move files to the correct locations
mv docker-compose.monitoring.yml ~/pyerp-monitoring/
mv install_monitoring.sh ~/pyerp-monitoring/
mv start_monitoring.sh ~/pyerp-monitoring/

# Make scripts executable
chmod +x ~/pyerp-monitoring/install_monitoring.sh
chmod +x ~/pyerp-monitoring/start_monitoring.sh

# Create a README file
cat > ~/pyerp-monitoring/README.md << 'EOFREADME'
# pyERP Monitoring System

Dieses Verzeichnis enthält die Konfiguration für das pyERP Monitoring-System.

## Komponenten

Das Monitoring-System besteht aus drei Hauptkomponenten:

1. **Elasticsearch**: Zentrale Datenbank für alle Logs
2. **Kibana**: Visualisierung und Analyse der Log-Daten
3. **Filebeat**: Sammelt und strukturiert Logs
4. **Sentry**: Fehler-Tracking und Performance-Monitoring

## Starten des Systems

Um das Monitoring-System zu starten, führen Sie folgenden Befehl aus:

```
cd ~/pyerp-monitoring
./start_monitoring.sh
```

## Zugriff auf die Dienste

- Elasticsearch: http://192.168.73.65:9200
- Kibana: http://192.168.73.65:5601

## Logs

Die Logs des Monitoring-Systems werden im Verzeichnis `~/pyerp-monitoring/logs` gespeichert.
EOFREADME

echo "Setup completed successfully!"
echo "To start the monitoring system, run: cd ~/pyerp-monitoring && ./start_monitoring.sh"
EOF

# Skripte ausführbar machen
chmod +x $TEMP_DIR/install_monitoring.sh
chmod +x $TEMP_DIR/start_monitoring.sh
chmod +x $TEMP_DIR/remote_setup.sh

# Dateien auf den Remote-Server kopieren
echo "Kopiere Dateien auf $TARGET_USER@$TARGET_IP..."
scp -r $TEMP_DIR/* $TARGET_USER@$TARGET_IP:~/

# Setup-Skript auf dem Remote-Server ausführen
echo "Führe Setup-Skript auf $TARGET_USER@$TARGET_IP aus..."
ssh $TARGET_USER@$TARGET_IP "bash ~/remote_setup.sh"

# Temporäres Verzeichnis aufräumen
rm -rf $TEMP_DIR
echo "Temporäres Verzeichnis aufgeräumt"

echo "=== Monitoring-System-Setup abgeschlossen! ==="
echo "Um das Monitoring-System zu starten, verbinde dich mit $TARGET_USER@$TARGET_IP und führe aus:"
echo "cd ~/pyerp-monitoring && ./start_monitoring.sh"
echo ""
echo "Dienste werden verfügbar sein unter:"
echo "- Elasticsearch: http://$TARGET_IP:9200"
echo "- Kibana: http://$TARGET_IP:5601" 