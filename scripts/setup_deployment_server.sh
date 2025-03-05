#!/bin/bash

# Script to set up a server for pyERP deployment
# This script should be run on the target deployment server

# Exit on error
set -e

# Check if script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" 
    exit 1
fi

# Configuration variables - modify these as needed
APP_USER=${1:-"pyerp"}
APP_PATH=${2:-"/opt/pyerp"}
ENV_FILE=${3:-"config/env/.env"}
DOCKER_COMPOSE_VERSION="2.24.6"

echo "Setting up deployment server for pyERP..."
echo "App User: $APP_USER"
echo "App Path: $APP_PATH"
echo "Environment File: $ENV_FILE"

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file $ENV_FILE not found!"
    echo "Usage: $0 [app_user] [app_path] [env_file]"
    exit 1
fi

# Load environment variables from .env file
echo "Loading environment variables from $ENV_FILE..."
set -a
source "$ENV_FILE"
set +a

# Verify required environment variables
if [ -z "$GITHUB_USERNAME" ] || [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_USERNAME and GITHUB_TOKEN must be defined in $ENV_FILE"
    echo "Please add the following to your $ENV_FILE file:"
    echo "GITHUB_USERNAME=your-github-username"
    echo "GITHUB_TOKEN=your-github-personal-access-token"
    exit 1
fi

# Create app user if it doesn't exist
if ! id "$APP_USER" &>/dev/null; then
    echo "Creating user $APP_USER..."
    useradd -m -s /bin/bash "$APP_USER"
    # Add user to docker group (will be created later if it doesn't exist)
    usermod -aG docker "$APP_USER" || true
fi

# Create app directory
echo "Creating application directory at $APP_PATH..."
mkdir -p "$APP_PATH"
chown -R "$APP_USER:$APP_USER" "$APP_PATH"

# Install dependencies
echo "Installing dependencies..."
apt-get update
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    python3 \
    python3-pip

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

# Create directories for Docker volumes
echo "Creating directories for Docker volumes..."
mkdir -p "$APP_PATH/data"
mkdir -p "$APP_PATH/logs"
mkdir -p "$APP_PATH/media"
mkdir -p "$APP_PATH/static"
mkdir -p "$APP_PATH/config/env"
chown -R "$APP_USER:$APP_USER" "$APP_PATH"

# Function to get environment variable or default
get_env_var() {
    local var_name=$1
    local default_value=$2
    local var_value=${!var_name}
    
    if [ -n "$var_value" ]; then
        echo "$var_value"
    else
        echo "$default_value"
    fi
}

# Create production environment file
if [ ! -f "$APP_PATH/config/env/.env.prod" ]; then
    echo "Creating production environment file..."
    cat > "$APP_PATH/config/env/.env.prod" << EOF
# Django settings
DEBUG=False
SECRET_KEY=$(get_env_var "SECRET_KEY" "$(openssl rand -hex 32)")
ALLOWED_HOSTS=$(get_env_var "ALLOWED_HOSTS" "$(hostname -I | tr ' ' ','),$(hostname),localhost")

# Database settings
DB_HOST=$(get_env_var "DB_HOST" "localhost")
DB_PORT=$(get_env_var "DB_PORT" "5432")
DB_NAME=$(get_env_var "DB_NAME" "pyerp")
DB_USER=$(get_env_var "DB_USER" "pyerp")
DB_PASSWORD=$(get_env_var "DB_PASSWORD" "$(openssl rand -hex 16)")

# Email settings
EMAIL_HOST=$(get_env_var "EMAIL_HOST" "smtp.example.com")
EMAIL_PORT=$(get_env_var "EMAIL_PORT" "587")
EMAIL_HOST_USER=$(get_env_var "EMAIL_HOST_USER" "no-reply@example.com")
EMAIL_HOST_PASSWORD=$(get_env_var "EMAIL_HOST_PASSWORD" "change-this-password")
EMAIL_USE_TLS=$(get_env_var "EMAIL_USE_TLS" "True")
DEFAULT_FROM_EMAIL=$(get_env_var "DEFAULT_FROM_EMAIL" "no-reply@example.com")

# Datadog settings (optional)
DD_API_KEY=$(get_env_var "DD_API_KEY" "")
DD_SITE=$(get_env_var "DD_SITE" "datadoghq.com")

# GitHub credentials (for container registry)
GITHUB_USERNAME=$GITHUB_USERNAME
GITHUB_TOKEN=$GITHUB_TOKEN

# Legacy ERP connection settings (if applicable)
LEGACY_API_HOST=$(get_env_var "LEGACY_API_HOST" "")
LEGACY_API_PORT=$(get_env_var "LEGACY_API_PORT" "8080")
LEGACY_API_USERNAME=$(get_env_var "LEGACY_API_USERNAME" "")
LEGACY_API_PASSWORD=$(get_env_var "LEGACY_API_PASSWORD" "")

# Additional settings from source environment
$(grep -v "^#" "$ENV_FILE" | grep -v "^$" | grep -v "GITHUB_" | grep -v "SECRET_KEY" | grep -v "ALLOWED_HOSTS" | grep -v "DB_" | grep -v "EMAIL_" | grep -v "DD_" | grep -v "LEGACY_API_" || true)
EOF
    chown "$APP_USER:$APP_USER" "$APP_PATH/config/env/.env.prod"
    chmod 600 "$APP_PATH/config/env/.env.prod"
    echo "Production environment file created at $APP_PATH/config/env/.env.prod"
    echo "Please review and update any missing or incorrect values."
fi

# Set up GitHub Container Registry authentication
echo "Setting up GitHub Container Registry authentication using credentials from $ENV_FILE..."
echo "Using GitHub username: $GITHUB_USERNAME"

# Login to GitHub Container Registry
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin

# Save credentials for the app user
sudo -u "$APP_USER" bash -c "echo '$GITHUB_TOKEN' | docker login ghcr.io -u '$GITHUB_USERNAME' --password-stdin"

# Copy the source environment file to the server for reference
cp "$ENV_FILE" "$APP_PATH/config/env/.env.source"
chown "$APP_USER:$APP_USER" "$APP_PATH/config/env/.env.source"
chmod 600 "$APP_PATH/config/env/.env.source"

echo "Server setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and update the environment file at $APP_PATH/config/env/.env.prod"
echo "2. Set up the CI/CD pipeline in your GitHub repository with the following secrets:"
echo "   - PROD_DEPLOY_HOST: $(hostname -I | awk '{print $1}')"
echo "   - PROD_DEPLOY_USER: $APP_USER"
echo "   - PROD_DEPLOY_PATH: $APP_PATH"
echo "   - PROD_SSH_PRIVATE_KEY: The private key for SSH access to this server"
echo ""
echo "3. Make sure your firewall allows incoming connections to ports 80 and 443"
echo ""
echo "For more information, see the documentation at: https://github.com/your-org/pyERP" 