#!/bin/bash

echo "Setting up production-like environment with HTTPS locally..."

# Ensure SSL directory exists
mkdir -p ./docker/nginx/ssl

# Generate self-signed certificates if they don't exist
if [ ! -f "./docker/nginx/ssl/server.crt" ] || [ ! -f "./docker/nginx/ssl/server.key" ]; then
  echo "Generating self-signed SSL certificates..."
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ./docker/nginx/ssl/server.key \
    -out ./docker/nginx/ssl/server.crt \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
fi

# Ensure nginx config directories exist
mkdir -p ./docker/nginx/conf.d

# Create Nginx configuration files
echo "Creating Nginx configuration files..."

cat > ./docker/nginx/conf.d/pyerp.conf << EOL
server {
    listen 443 ssl;
    server_name localhost;

    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384';

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /app/static/;
    }

    location /media/ {
        alias /app/media/;
    }
}
EOL

cat > ./docker/nginx/conf.d/pyerp.http.conf << EOL
server {
    listen 80;
    server_name localhost;
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}
EOL

echo "Nginx configuration files created"

# Create a local link to point to the SSL directories
echo "Preparing to run production rebuild script..."

# Make sure the certificate is accessible from where production expects it
mkdir -p ./docker/nginx
cp -r ./docker/nginx/ssl /tmp/
cp -r ./docker/nginx/conf.d /tmp/

# Run the production rebuild with environment pointing to local config
echo "Building and starting production containers locally..."
./rebuild_docker.prod.sh

# Once the container is running, copy the SSL certificates and configs into the container
echo "Copying SSL certificates to the Docker container..."
docker cp /tmp/ssl pyerp-prod:/etc/nginx/
docker cp /tmp/conf.d pyerp-prod:/etc/nginx/

# Restart Nginx in the container
echo "Restarting Nginx in the container..."
docker exec pyerp-prod supervisorctl restart nginx

echo "----------------------------------------"
echo "Local production environment started with HTTPS!"
echo "----------------------------------------"
echo "Frontend: https://localhost"
echo "Backend API: https://localhost/api"
echo "----------------------------------------"
echo "To stop the environment, run: docker-compose -f docker/docker-compose.prod.yml down"
echo "----------------------------------------" 