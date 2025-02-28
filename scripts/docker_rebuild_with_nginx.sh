#!/bin/bash
# Linux shell script to restart Docker containers with latest code
# This version handles separate web and Nginx containers
# Run this script from the root directory of your project

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Configuration
WEB_CONTAINER="pyerp-web"  # Your Django container name
NGINX_CONTAINER="pyerp-nginx"  # Your Nginx container name
COMPOSE_FILE="docker-compose.yml"  # Your compose file path
NGINX_COMPOSE_FILE="docker/docker-compose.yml"  # Nginx compose file if separate

echo -e "${CYAN}===== Docker Container Management Script with Nginx =====${NC}"

# Step 1: Stop and remove existing containers
echo -e "\n${GREEN}[1/5] Stopping and removing existing containers...${NC}"
# Stop the containers if they're running
docker stop $WEB_CONTAINER 2>/dev/null || true
docker stop $NGINX_CONTAINER 2>/dev/null || true

# Remove the containers
docker rm $WEB_CONTAINER 2>/dev/null || true
docker rm $NGINX_CONTAINER 2>/dev/null || true

echo -e "  ${GREEN}✓ Containers successfully stopped and removed${NC}"

# Step 2: Pull latest code from GitHub
echo -e "\n${GREEN}[2/5] Pulling latest code from GitHub...${NC}"
if git pull; then
    echo -e "  ${GREEN}✓ Latest code pulled successfully${NC}"
else
    echo -e "  ${RED}✗ Error pulling code${NC}"
    echo -e "  ${YELLOW}You may need to stash or commit your local changes first${NC}"
    exit 1
fi

# Step 3: Build Django container
echo -e "\n${GREEN}[3/5] Building Django container...${NC}"
if [ -f "$COMPOSE_FILE" ]; then
    if docker-compose -f $COMPOSE_FILE build --no-cache; then
        echo -e "  ${GREEN}✓ Django container rebuilt successfully${NC}"
    else
        echo -e "  ${RED}✗ Error rebuilding Django container${NC}"
        exit 1
    fi
else
    if docker-compose build --no-cache; then
        echo -e "  ${GREEN}✓ Django container rebuilt successfully${NC}"
    else
        echo -e "  ${RED}✗ Error rebuilding Django container${NC}"
        exit 1
    fi
fi

# Step 4: Build Nginx container
echo -e "\n${GREEN}[4/5] Building Nginx container...${NC}"
# Check if we have a separate compose file for Nginx
if [ -f "$NGINX_COMPOSE_FILE" ]; then
    if docker-compose -f $NGINX_COMPOSE_FILE build --no-cache; then
        echo -e "  ${GREEN}✓ Nginx container rebuilt successfully from separate compose file${NC}"
    else
        echo -e "  ${RED}✗ Error rebuilding Nginx container${NC}"
        exit 1
    fi
else
    echo -e "  ${YELLOW}→ No separate Nginx compose file found, assuming it's included in the main compose file${NC}"
fi

# Step 5: Start containers
echo -e "\n${GREEN}[5/5] Starting containers...${NC}"
# Start Django container
if [ -f "$COMPOSE_FILE" ]; then
    if docker-compose -f $COMPOSE_FILE up -d; then
        echo -e "  ${GREEN}✓ Django containers started successfully${NC}"
    else
        echo -e "  ${RED}✗ Error starting Django containers${NC}"
        exit 1
    fi
else
    if docker-compose up -d; then
        echo -e "  ${GREEN}✓ Django containers started successfully${NC}"
    else
        echo -e "  ${RED}✗ Error starting Django containers${NC}"
        exit 1
    fi
fi

# Start Nginx container if separate
if [ -f "$NGINX_COMPOSE_FILE" ]; then
    if docker-compose -f $NGINX_COMPOSE_FILE up -d; then
        echo -e "  ${GREEN}✓ Nginx container started successfully${NC}"
    else
        echo -e "  ${RED}✗ Error starting Nginx container${NC}"
        exit 1
    fi
fi

# Create Docker network if it doesn't exist
echo -e "\n${CYAN}Ensuring Docker network exists...${NC}"
docker network create pyerp-network 2>/dev/null || true
echo -e "  ${GREEN}→ Docker network ready${NC}"

# Connect containers to network if needed
echo -e "\n${CYAN}Ensuring containers are on the same network...${NC}"
docker network connect pyerp-network $WEB_CONTAINER 2>/dev/null || true
docker network connect pyerp-network $NGINX_CONTAINER 2>/dev/null || true
echo -e "  ${GREEN}→ Containers connected to network${NC}"

# Final status check
echo -e "\n${CYAN}Checking container status...${NC}"
docker ps

echo -e "\n${CYAN}===== Process Complete =====${NC}"
echo -e "${GREEN}The web application should now be accessible via HTTPS${NC}"
echo -e "${YELLOW}If you encounter 'too many redirects' errors:${NC}"
echo -e "${YELLOW}  1. Clear your browser cache and cookies${NC}"
echo -e "${YELLOW}  2. Check that settings_https.py is being properly loaded${NC}"
echo -e "${YELLOW}  3. Verify X-Forwarded-Proto header is set to 'https' in Nginx config${NC}"
echo -e "${YELLOW}  4. Check container networking with 'docker network inspect pyerp-network'${NC}" 