#!/bin/bash
# docker-prune.sh - Clean up unused Docker resources to free up space

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}===== Docker Resource Cleanup =====${NC}"

# Display current disk space
echo -e "${YELLOW}Current disk space usage:${NC}"
df -h

# Remove stopped containers
echo -e "\n${YELLOW}Removing stopped containers...${NC}"
containers=$(docker ps -a -q -f status=exited -f status=created)
if [ -n "$containers" ]; then
    docker rm $containers
    echo -e "${GREEN}✓ Stopped containers removed${NC}"
else
    echo -e "${GREEN}✓ No stopped containers to remove${NC}"
fi

# Remove unused images
echo -e "\n${YELLOW}Removing dangling images...${NC}"
if docker images prune -f --filter="dangling=true"; then
    echo -e "${GREEN}✓ Dangling images removed${NC}"
else
    echo -e "${RED}✗ Failed to remove dangling images${NC}"
fi

# Remove unused volumes
echo -e "\n${YELLOW}Removing unused volumes...${NC}"
if docker volume prune -f; then
    echo -e "${GREEN}✓ Unused volumes removed${NC}"
else
    echo -e "${RED}✗ Failed to remove unused volumes${NC}"
fi

# Remove unused networks
echo -e "\n${YELLOW}Removing unused networks...${NC}"
if docker network prune -f; then
    echo -e "${GREEN}✓ Unused networks removed${NC}"
else
    echo -e "${RED}✗ Failed to remove unused networks${NC}"
fi

# Remove build cache
echo -e "\n${YELLOW}Removing build cache...${NC}"
if docker builder prune -f; then
    echo -e "${GREEN}✓ Build cache removed${NC}"
else
    echo -e "${RED}✗ Failed to remove build cache${NC}"
fi

# Display freed disk space
echo -e "\n${YELLOW}Updated disk space usage:${NC}"
df -h

echo -e "\n${GREEN}Docker resources cleaned up successfully.${NC}"
echo -e "${YELLOW}You can now proceed with your Docker build.${NC}" 