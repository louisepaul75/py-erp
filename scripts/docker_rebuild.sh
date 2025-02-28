#!/bin/bash
# Linux shell script to restart Docker containers with latest code
# Run this script from the root directory of your project

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}===== Docker Container Management Script =====${NC}"

# Try to find the Docker Compose file
echo -e "${YELLOW}Searching for Docker Compose file...${NC}"

# Search for possible Docker Compose files
POSSIBLE_COMPOSE_FILES=(
  "docker-compose.yml"
  "docker-compose.yaml"
  "docker/docker-compose.yml"
  "docker/docker-compose.yaml"
  "compose/docker-compose.yml"
  "compose/docker-compose.yaml"
)

COMPOSE_FILE=""

# Find Docker Compose file
for file in "${POSSIBLE_COMPOSE_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo -e "  ${GREEN}Found Docker Compose file: $file${NC}"
    COMPOSE_FILE="$file"
    break
  fi
done

# Check if we found a compose file
if [ -z "$COMPOSE_FILE" ]; then
  echo -e "  ${RED}No Docker Compose file found in standard locations${NC}"
  echo -e "  ${YELLOW}Please specify the path to your Docker Compose file:${NC}"
  read -p "  Docker Compose file path: " COMPOSE_FILE
  
  if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "  ${RED}File not found: $COMPOSE_FILE${NC}"
    exit 1
  fi
fi

# Step 1: Stop and remove existing containers
echo -e "\n${GREEN}[1/4] Stopping and removing existing containers...${NC}"
if docker-compose -f "$COMPOSE_FILE" down; then
    echo -e "  ${GREEN}✓ Containers successfully stopped${NC}"
else
    echo -e "  ${RED}✗ Error stopping containers${NC}"
    exit 1
fi

# Step 2: Pull latest code from GitHub
echo -e "\n${GREEN}[2/4] Pulling latest code from GitHub...${NC}"
if git pull; then
    echo -e "  ${GREEN}✓ Latest code pulled successfully${NC}"
else
    echo -e "  ${RED}✗ Error pulling code${NC}"
    echo -e "  ${YELLOW}You may need to stash or commit your local changes first${NC}"
    exit 1
fi

# Step 3: Rebuild Docker images
echo -e "\n${GREEN}[3/4] Rebuilding Docker images...${NC}"
if docker-compose -f "$COMPOSE_FILE" build --no-cache; then
    echo -e "  ${GREEN}✓ Docker images rebuilt successfully${NC}"
else
    echo -e "  ${RED}✗ Error rebuilding Docker images${NC}"
    exit 1
fi

# Step 4: Start containers
echo -e "\n${GREEN}[4/4] Starting containers...${NC}"
if docker-compose -f "$COMPOSE_FILE" up -d; then
    echo -e "  ${GREEN}✓ Containers started successfully${NC}"
else
    echo -e "  ${RED}✗ Error starting containers${NC}"
    exit 1
fi

# Final status check
echo -e "\n${CYAN}Checking container status...${NC}"
docker-compose -f "$COMPOSE_FILE" ps

echo -e "\n${CYAN}===== Process Complete =====${NC}"
echo -e "${GREEN}The web application should now be accessible via HTTPS${NC}"
echo -e "${YELLOW}If you encounter 'too many redirects' errors:${NC}"
echo -e "${YELLOW}  1. Clear your browser cache${NC}"
echo -e "${YELLOW}  2. Check that settings_https.py is being properly loaded${NC}"
echo -e "${YELLOW}  3. Verify X-Forwarded-Proto header is set to 'https' in Nginx config${NC}" 