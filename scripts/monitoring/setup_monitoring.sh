#!/bin/bash
set -e

# Configuration
TARGET_IP="192.168.73.65"
TARGET_USER="admin-local"
REMOTE_DIR="/home/admin-local/pyerp-monitoring"

echo "Setting up pyERP monitoring system on $TARGET_IP..."

# Create a temporary directory for the setup files
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Copy necessary files to the temporary directory
cp docker/install_monitoring.sh $TEMP_DIR/
cp docker/docker-compose.dev.yml $TEMP_DIR/
cp rebuild_docker.dev.sh $TEMP_DIR/

# Create a setup script for the remote server
cat > $TEMP_DIR/remote_setup.sh << 'EOF'
#!/bin/bash
set -e

# Create the necessary directories
mkdir -p ~/pyerp-monitoring/docker
mkdir -p ~/pyerp-monitoring/config/env

# Move files to the correct locations
mv install_monitoring.sh ~/pyerp-monitoring/docker/
mv docker-compose.dev.yml ~/pyerp-monitoring/docker/
mv rebuild_docker.dev.sh ~/pyerp-monitoring/

# Make scripts executable
chmod +x ~/pyerp-monitoring/docker/install_monitoring.sh
chmod +x ~/pyerp-monitoring/rebuild_docker.dev.sh

# Create a basic .env.dev file if it doesn't exist
if [ ! -f ~/pyerp-monitoring/config/env/.env.dev ]; then
    mkdir -p ~/pyerp-monitoring/config/env
    cat > ~/pyerp-monitoring/config/env/.env.dev << 'ENVEOF'
DJANGO_SETTINGS_MODULE=pyerp.config.settings.development
DJANGO_DEBUG=True
REDIS_URL=redis://127.0.0.1:6379/0
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pyerp_monitoring
DB_USER=postgres
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
KIBANA_HOST=localhost
KIBANA_PORT=5601
SENTRY_DSN=https://development@sentry.example.com/1
ENVEOF
    echo "Created default .env.dev file"
fi

echo "Setup completed successfully!"
echo "To start the monitoring system, run: cd ~/pyerp-monitoring && ./rebuild_docker.dev.sh"
EOF

# Make the remote setup script executable
chmod +x $TEMP_DIR/remote_setup.sh

# Copy files to the remote server
echo "Copying files to $TARGET_USER@$TARGET_IP..."
scp -r $TEMP_DIR/* $TARGET_USER@$TARGET_IP:~/

# Execute the setup script on the remote server
echo "Executing setup script on $TARGET_USER@$TARGET_IP..."
ssh $TARGET_USER@$TARGET_IP "bash ~/remote_setup.sh"

# Clean up the temporary directory
rm -rf $TEMP_DIR
echo "Cleaned up temporary directory"

echo "Monitoring system setup completed successfully!"
echo "To start the monitoring system, SSH into $TARGET_USER@$TARGET_IP and run:"
echo "cd ~/pyerp-monitoring && ./rebuild_docker.dev.sh" 