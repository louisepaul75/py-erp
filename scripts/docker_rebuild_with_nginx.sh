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
BRANCH=""  # Will be auto-detected

# Function to display help information
display_help() {
  echo -e "${CYAN}===== Docker Rebuild with Nginx - Help =====${NC}"
  echo -e "${YELLOW}Usage: $0 [OPTIONS]${NC}"
  echo -e "${YELLOW}Options:${NC}"
  echo -e "  ${YELLOW}--help                Display this help message${NC}"
  echo -e "  ${YELLOW}--branch=BRANCH       Specify which Git branch to pull from (auto-detected if not specified)${NC}"
  echo -e "  ${YELLOW}--no-prune            Skip Docker resource cleanup even if space is low${NC}"
  echo -e "${CYAN}===== Examples =====${NC}"
  echo -e "  ${YELLOW}$0 --branch=develop   Pull from develop branch and rebuild containers${NC}"
  echo -e "  ${YELLOW}$0 --no-prune         Skip Docker cleanup${NC}"
  echo -e "${CYAN}===== Notes =====${NC}"
  echo -e "  ${YELLOW}This script will:${NC}"
  echo -e "  ${YELLOW}1. Stop and remove existing containers${NC}"
  echo -e "  ${YELLOW}2. Pull the latest code from GitHub (using SSH)${NC}"
  echo -e "  ${YELLOW}3. Build Django and Nginx containers${NC}"
  echo -e "  ${YELLOW}4. Start all containers${NC}"
  exit 0
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --help)
      display_help
      ;;
    --no-prune)
      SKIP_PRUNE=true
      shift
      ;;
    --branch=*)
      BRANCH="${1#*=}"
      shift
      ;;
    *)
      echo -e "${YELLOW}Unknown option: $1${NC}"
      echo -e "${YELLOW}Use --help for available options${NC}"
      shift
      ;;
  esac
done

# Detect which user is running the script
SCRIPT_USER=$(whoami)
echo -e "${CYAN}Script running as user: $SCRIPT_USER${NC}"

# Adjust commands based on whether running as root/sudo
if [ "$SCRIPT_USER" = "root" ]; then
  ACTUAL_USER=$(logname 2>/dev/null || echo $SUDO_USER)
  if [ -z "$ACTUAL_USER" ]; then
    # Try to find the actual user from environment variables
    ACTUAL_USER=$SUDO_USER
  fi
  
  if [ -n "$ACTUAL_USER" ]; then
    ACTUAL_USER_HOME=$(eval echo ~$ACTUAL_USER)
    echo -e "${YELLOW}Detected actual user: $ACTUAL_USER${NC}"
    SSH_KEY_PATH="$ACTUAL_USER_HOME/.ssh/id_rsa"
  else
    echo -e "${YELLOW}Could not determine actual user, using default paths${NC}"
    SSH_KEY_PATH="/home/admin-local/.ssh/id_rsa"
  fi
else
  SSH_KEY_PATH="$HOME/.ssh/id_rsa"
fi

echo -e "${YELLOW}Using SSH key: $SSH_KEY_PATH${NC}"

# Auto-detect default branch if not specified
if [ -z "$BRANCH" ]; then
  echo -e "${YELLOW}Auto-detecting default branch...${NC}"
  # First check local default branch
  DEFAULT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
  
  if [ -n "$DEFAULT_BRANCH" ]; then
    BRANCH="$DEFAULT_BRANCH"
    echo -e "${GREEN}Using current branch: $BRANCH${NC}"
  else
    # Check if main or master exists on remote
    if GIT_SSH_COMMAND="ssh -i $SSH_KEY_PATH -o IdentitiesOnly=yes" git ls-remote --heads origin main 2>/dev/null | grep -q main; then
      BRANCH="main"
      echo -e "${GREEN}Detected 'main' branch on remote${NC}"
    elif GIT_SSH_COMMAND="ssh -i $SSH_KEY_PATH -o IdentitiesOnly=yes" git ls-remote --heads origin master 2>/dev/null | grep -q master; then
      BRANCH="master"
      echo -e "${GREEN}Detected 'master' branch on remote${NC}"
    else
      echo -e "${RED}Could not detect default branch. Please specify with --branch=${NC}"
      exit 1
    fi
  fi
fi

# Show configuration
echo -e "${CYAN}===== Docker Deployment Configuration =====${NC}"
echo -e "${YELLOW}Branch: $BRANCH${NC}"
echo -e "${YELLOW}Skip pruning: ${SKIP_PRUNE:-false}${NC}"

# Check if we're low on disk space - using sudo if needed
LOW_SPACE=false
if [ "$SCRIPT_USER" = "root" ]; then
  DOCKER_DIR=$(docker info 2>/dev/null | grep "Docker Root Dir" | cut -d: -f2 | tr -d '[:space:]')
else
  DOCKER_DIR=$(sudo docker info 2>/dev/null | grep "Docker Root Dir" | cut -d: -f2 | tr -d '[:space:]')
fi

if [ -z "$DOCKER_DIR" ]; then
    DOCKER_DIR="/var/lib/docker"  # Default location
fi

# We need to handle disk space check with or without sudo
if [ "$SCRIPT_USER" = "root" ]; then
  if [ -d "$DOCKER_DIR" ]; then
    FREE_SPACE=$(df -m "$DOCKER_DIR" | tail -1 | awk '{print $4}')
    echo -e "${CYAN}Available space in Docker directory: ${FREE_SPACE}MB${NC}"
    
    if [ "$FREE_SPACE" -lt 1000 ]; then
        echo -e "${YELLOW}Low disk space detected (less than 1GB free).${NC}"
        LOW_SPACE=true
    fi
  else
    echo -e "${YELLOW}Docker directory not found at $DOCKER_DIR, skipping space check${NC}"
  fi
else
  if [ -d "$DOCKER_DIR" ]; then
    FREE_SPACE=$(sudo df -m "$DOCKER_DIR" 2>/dev/null | tail -1 | awk '{print $4}')
    echo -e "${CYAN}Available space in Docker directory: ${FREE_SPACE}MB${NC}"
    
    if [ "$FREE_SPACE" -lt 1000 ]; then
        echo -e "${YELLOW}Low disk space detected (less than 1GB free).${NC}"
        LOW_SPACE=true
    fi
  else
    echo -e "${YELLOW}Docker directory not found at $DOCKER_DIR, skipping space check${NC}"
  fi
fi

# Clean up Docker resources if needed
if [ "$LOW_SPACE" = true ] && [ "$SKIP_PRUNE" != true ]; then
    echo -e "${YELLOW}Running Docker cleanup to free up space...${NC}"
    # Ensure the prune script is executable (works on both Windows and Linux)
    if [ -f ./scripts/docker-prune.sh ]; then
        chmod +x ./scripts/docker-prune.sh || true
        if [ "$SCRIPT_USER" = "root" ]; then
          bash ./scripts/docker-prune.sh
        else
          sudo bash ./scripts/docker-prune.sh
        fi
    else
        echo -e "${RED}Docker prune script not found at ./scripts/docker-prune.sh${NC}"
        echo -e "${YELLOW}Continuing without cleanup...${NC}"
    fi
fi

# Try to find the Docker Compose files
echo -e "${CYAN}===== Docker Container Management Script with Nginx =====${NC}"
echo -e "${YELLOW}Searching for Docker Compose files...${NC}"

# Search for possible Docker Compose files
POSSIBLE_COMPOSE_FILES=(
  "docker-compose.prod.yml"
  "docker-compose.prod.yaml"
  "docker/docker-compose.prod.yml"
  "docker/docker-compose.prod.yaml"
  "docker-compose.yml"
  "docker-compose.yaml"
  "docker/docker-compose.yml"
  "docker/docker-compose.yaml"
  "compose/docker-compose.yml"
  "compose/docker-compose.yaml"
)

COMPOSE_FILE=""
NGINX_COMPOSE_FILE=""

# Find main Docker Compose file
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

# Check if Nginx is in a separate compose file or the same one
if [[ "$COMPOSE_FILE" == *"prod"* ]]; then
  # In production, Nginx should be part of the docker-compose.prod.yml file
  if [ "$SCRIPT_USER" = "root" ]; then
    grep -q "nginx" "$COMPOSE_FILE" 2>/dev/null
  else
    sudo grep -q "nginx" "$COMPOSE_FILE" 2>/dev/null
  fi
  
  if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}Nginx configuration found in production compose file${NC}"
    NGINX_COMPOSE_FILE="$COMPOSE_FILE"
  else
    echo -e "  ${YELLOW}Nginx not found in production compose file. Looking for separate Nginx config...${NC}"
    # Continue with the existing Nginx lookup logic
    if [ -f "docker/docker-compose.prod.yml" ]; then
      if [ "$SCRIPT_USER" = "root" ]; then
        grep -q "nginx" "docker/docker-compose.prod.yml" 2>/dev/null
      else
        sudo grep -q "nginx" "docker/docker-compose.prod.yml" 2>/dev/null
      fi
      
      if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}Found separate Nginx compose file: docker/docker-compose.prod.yml${NC}"
        NGINX_COMPOSE_FILE="docker/docker-compose.prod.yml"
      fi
    fi
  fi
else
  # For development, continue with regular Nginx check
  if [ "$SCRIPT_USER" = "root" ]; then
    grep -q "nginx" "$COMPOSE_FILE" 2>/dev/null
  else
    sudo grep -q "nginx" "$COMPOSE_FILE" 2>/dev/null
  fi
  
  if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}Nginx configuration found in main compose file${NC}"
    NGINX_COMPOSE_FILE="$COMPOSE_FILE"
  else
    # Check docker/docker-compose.yml specifically for Nginx
    if [ -f "docker/docker-compose.yml" ]; then
      if [ "$SCRIPT_USER" = "root" ]; then
        grep -q "nginx" "docker/docker-compose.yml" 2>/dev/null
      else
        sudo grep -q "nginx" "docker/docker-compose.yml" 2>/dev/null
      fi
      
      if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}Found separate Nginx compose file: docker/docker-compose.yml${NC}"
        NGINX_COMPOSE_FILE="docker/docker-compose.yml"
      fi
    fi
  fi
fi

# If still not found, ask user
if [ -z "$NGINX_COMPOSE_FILE" ]; then
  echo -e "  ${YELLOW}Nginx configuration not found. Please specify the path to your Nginx Docker Compose file${NC}"
  echo -e "  ${YELLOW}(or press Enter to skip if Nginx is run separately):${NC}"
  read -p "  Nginx compose file path: " NGINX_COMPOSE_FILE
fi

# Helper function to run docker commands with or without sudo
docker_cmd() {
  if [ "$SCRIPT_USER" = "root" ]; then
    docker "$@"
  else
    sudo docker "$@"
  fi
}

# Helper function for docker-compose commands
docker_compose_cmd() {
  local compose_file="$1"
  shift
  if [ "$SCRIPT_USER" = "root" ]; then
    docker-compose -f "$compose_file" "$@"
  else
    sudo docker-compose -f "$compose_file" "$@"
  fi
}

# Step 1: Stop and remove existing containers
echo -e "\n${GREEN}[1/5] Stopping and removing existing containers...${NC}"
# Stop the containers if they're running
docker_cmd stop $WEB_CONTAINER 2>/dev/null || true
docker_cmd stop $NGINX_CONTAINER 2>/dev/null || true

# Remove the containers
docker_cmd rm $WEB_CONTAINER 2>/dev/null || true
docker_cmd rm $NGINX_CONTAINER 2>/dev/null || true

echo -e "  ${GREEN}✓ Containers successfully stopped and removed${NC}"

# Step 2: Pull latest code from GitHub
echo -e "\n${GREEN}[2/5] Pulling latest code from GitHub...${NC}"

# Function to check and fix SSH setup if needed
check_ssh_git_connection() {
    # Get the current repository URL
    REPO_URL=$(git config --get remote.origin.url)
    
    # Only check if it's using SSH format
    if [[ $REPO_URL == git@* ]]; then
        echo -e "  ${YELLOW}Using SSH for GitHub: $REPO_URL${NC}"
        
        # Display the key we're using
        echo -e "  ${YELLOW}Using SSH key: $SSH_KEY_PATH${NC}"
        
        # Check if the key exists
        if [ -f "$SSH_KEY_PATH" ]; then
            echo -e "  ${GREEN}SSH key file exists.${NC}"
            
            # Check key permissions
            KEY_PERMS=$(stat -c "%a" "$SSH_KEY_PATH" 2>/dev/null || stat -f "%Lp" "$SSH_KEY_PATH" 2>/dev/null)
            if [ "$KEY_PERMS" != "600" ]; then
                echo -e "  ${YELLOW}Setting correct permissions on SSH key...${NC}"
                chmod 600 "$SSH_KEY_PATH" || echo -e "  ${RED}Failed to set permissions on SSH key${NC}"
            fi
            
            # Test SSH connection directly with the key
            echo -e "  ${YELLOW}Testing connection to GitHub...${NC}"
            if ssh -i "$SSH_KEY_PATH" -o IdentitiesOnly=yes -T git@github.com -o StrictHostKeyChecking=no -o BatchMode=yes 2>&1 | grep -q "success"; then
                echo -e "  ${GREEN}SSH connection to GitHub successful.${NC}"
            else
                echo -e "  ${RED}Cannot connect to GitHub via SSH.${NC}"
                echo -e "  ${YELLOW}Detailed SSH debugging:${NC}"
                ssh -i "$SSH_KEY_PATH" -vT git@github.com
                
                echo -e "\n  ${YELLOW}SSH troubleshooting:${NC}"
                echo -e "  ${YELLOW}1. Check permissions: chmod 600 $SSH_KEY_PATH${NC}"
                echo -e "  ${YELLOW}2. Make sure known_hosts file exists${NC}"
                echo -e "  ${YELLOW}3. Add GitHub to known_hosts: ssh-keyscan github.com >> ~/.ssh/known_hosts${NC}"
                echo -e "  ${YELLOW}4. Verify key is added to your GitHub account: https://github.com/settings/keys${NC}"
            fi
        else
            echo -e "  ${RED}SSH key not found at $SSH_KEY_PATH${NC}"
            echo -e "  ${YELLOW}Please check the path to your SSH key.${NC}"
        fi
    else
        # Using HTTPS or other protocol
        echo -e "  ${GREEN}Not using SSH URL: $REPO_URL${NC}"
    fi
}

# Check SSH setup
check_ssh_git_connection

# Now try to pull the latest code
echo -e "  ${YELLOW}Pulling from branch: $BRANCH${NC}"
if GIT_SSH_COMMAND="ssh -i $SSH_KEY_PATH -o IdentitiesOnly=yes" git pull origin $BRANCH; then
    echo -e "  ${GREEN}✓ Latest code pulled successfully from $BRANCH${NC}"
else
    echo -e "  ${RED}✗ Error pulling code from $BRANCH${NC}"
    echo -e "  ${YELLOW}SSH authentication may have failed. Here's some debugging info:${NC}"
    echo -e "  ${YELLOW}1. SSH key being used: $SSH_KEY_PATH${NC}"
    echo -e "  ${YELLOW}2. Make sure this key is added to your GitHub account${NC}"
    echo -e "  ${YELLOW}3. Try testing with: ssh -i $SSH_KEY_PATH -T git@github.com${NC}"
    echo -e "  ${YELLOW}4. Check if you have local changes that need to be stashed/committed${NC}"
    
    # Show available branches
    echo -e "  ${YELLOW}Available remote branches:${NC}"
    GIT_SSH_COMMAND="ssh -i $SSH_KEY_PATH -o IdentitiesOnly=yes" git ls-remote --heads origin
    
    # Ask if user wants to continue
    read -p "  Continue with deployment anyway? (y/n): " continue_anyway
    if [[ "$continue_anyway" != "y" && "$continue_anyway" != "Y" ]]; then
        echo -e "  ${RED}Aborting deployment.${NC}"
        exit 1
    fi
    echo -e "  ${YELLOW}Continuing without pulling latest code...${NC}"
fi

# Step 3: Build Django container
echo -e "\n${GREEN}[3/5] Building Django container...${NC}"
if [ -n "$COMPOSE_FILE" ]; then
    # Check if we have a production file - prefer that over development
    PROD_FILE=""
    if [[ "$COMPOSE_FILE" == *"prod"* ]]; then
        PROD_FILE="$COMPOSE_FILE"
    elif [ -f "docker/docker-compose.prod.yml" ]; then
        PROD_FILE="docker/docker-compose.prod.yml"
    elif [ -f "docker-compose.prod.yml" ]; then
        PROD_FILE="docker-compose.prod.yml"
    fi
    
    if [ -n "$PROD_FILE" ]; then
        echo -e "  ${YELLOW}Using production compose file: $PROD_FILE${NC}"
        if docker_compose_cmd "$PROD_FILE" build --no-cache; then
            echo -e "  ${GREEN}✓ Django container rebuilt successfully${NC}"
            # Update COMPOSE_FILE to use production for starting containers
            COMPOSE_FILE="$PROD_FILE"
        else
            echo -e "  ${RED}✗ Error rebuilding Django container${NC}"
            exit 1
        fi
    else
        echo -e "  ${YELLOW}Using compose file: $COMPOSE_FILE${NC}"
        echo -e "  ${YELLOW}Warning: This may be a development configuration file.${NC}"
        if docker_compose_cmd "$COMPOSE_FILE" build --no-cache; then
            echo -e "  ${GREEN}✓ Django container rebuilt successfully${NC}"
        else
            echo -e "  ${RED}✗ Error rebuilding Django container${NC}"
            exit 1
        fi
    fi
else
    echo -e "  ${RED}No Docker Compose file specified for Django${NC}"
    exit 1
fi

# Step 4: Build Nginx container
echo -e "\n${GREEN}[4/5] Building Nginx container...${NC}"
# Check if we have a separate compose file for Nginx
if [ -n "$NGINX_COMPOSE_FILE" ] && [ "$NGINX_COMPOSE_FILE" != "$COMPOSE_FILE" ]; then
    echo -e "  ${YELLOW}Using Nginx compose file: $NGINX_COMPOSE_FILE${NC}"
    if docker_compose_cmd "$NGINX_COMPOSE_FILE" build --no-cache; then
        echo -e "  ${GREEN}✓ Nginx container rebuilt successfully from separate compose file${NC}"
    else
        echo -e "  ${RED}✗ Error rebuilding Nginx container${NC}"
        exit 1
    fi
elif [ -n "$NGINX_COMPOSE_FILE" ]; then
    echo -e "  ${YELLOW}Nginx is in the same compose file as Django${NC}"
else
    echo -e "  ${YELLOW}No Nginx compose file specified, skipping Nginx build${NC}"
fi

# Check for port conflicts before starting containers
check_port() {
    local port=$1
    local service=$2
    
    # Check if the port is in use
    if command -v nc >/dev/null 2>&1; then
        if nc -z localhost $port >/dev/null 2>&1; then
            echo -e "  ${RED}Port $port is already in use! This will conflict with $service.${NC}"
            echo -e "  ${YELLOW}You can:${NC}"
            echo -e "  ${YELLOW}1. Stop the service using this port${NC}"
            echo -e "  ${YELLOW}2. Modify the docker-compose file to use a different port${NC}"
            echo -e "  ${YELLOW}3. Continue anyway (may fail)${NC}"
            read -p "  Continue anyway? (y/n): " continue_anyway
            if [[ "$continue_anyway" != "y" && "$continue_anyway" != "Y" ]]; then
                echo -e "  ${RED}Aborting deployment.${NC}"
                exit 1
            fi
        fi
    fi
}

# Check for port conflicts before starting containers
check_for_port_conflicts() {
    echo -e "\n${YELLOW}Checking for potential port conflicts...${NC}"
    
    # Extract ports from the docker-compose file
    if [[ "$COMPOSE_FILE" == *"prod"* ]]; then
        check_port 80 "Nginx (HTTP)"
        check_port 443 "Nginx (HTTPS)"
    else
        # Development setup typically uses port 8000
        check_port 8000 "Django development server"
    fi
}

# Step 5: Start containers
echo -e "\n${GREEN}[5/5] Starting containers...${NC}"

# Check for port conflicts first
check_for_port_conflicts

# Start Django container
if [ -n "$COMPOSE_FILE" ]; then
    echo -e "  ${YELLOW}Starting containers using: $COMPOSE_FILE${NC}"
    if docker_compose_cmd "$COMPOSE_FILE" up -d; then
        echo -e "  ${GREEN}✓ Django containers started successfully${NC}"
    else
        echo -e "  ${RED}✗ Error starting Django containers${NC}"
        exit 1
    fi
else
    echo -e "  ${RED}No Docker Compose file specified for Django${NC}"
    exit 1
fi

# Start Nginx container if separate
if [ -n "$NGINX_COMPOSE_FILE" ] && [ "$NGINX_COMPOSE_FILE" != "$COMPOSE_FILE" ]; then
    echo -e "  ${YELLOW}Starting Nginx using: $NGINX_COMPOSE_FILE${NC}"
    if docker_compose_cmd "$NGINX_COMPOSE_FILE" up -d; then
        echo -e "  ${GREEN}✓ Nginx container started successfully${NC}"
    else
        echo -e "  ${RED}✗ Error starting Nginx container${NC}"
        exit 1
    fi
fi

# Create Docker network if it doesn't exist
echo -e "\n${CYAN}Ensuring Docker network exists...${NC}"
docker_cmd network create pyerp-network 2>/dev/null || true
echo -e "  ${GREEN}→ Docker network ready${NC}"

# Connect containers to network if needed
echo -e "\n${CYAN}Ensuring containers are on the same network...${NC}"
docker_cmd network connect pyerp-network $WEB_CONTAINER 2>/dev/null || true
docker_cmd network connect pyerp-network $NGINX_CONTAINER 2>/dev/null || true
echo -e "  ${GREEN}→ Containers connected to network${NC}"

# Final status check
echo -e "\n${CYAN}Checking container status...${NC}"
docker_cmd ps

echo -e "\n${CYAN}===== Process Complete =====${NC}"
echo -e "${GREEN}The web application should now be accessible via HTTPS${NC}"
echo -e "${YELLOW}If you encounter 'too many redirects' errors:${NC}"
echo -e "${YELLOW}  1. Clear your browser cache and cookies${NC}"
echo -e "${YELLOW}  2. Check that settings_https.py is being properly loaded${NC}"
echo -e "${YELLOW}  3. Verify X-Forwarded-Proto header is set to 'https' in Nginx config${NC}"
echo -e "${YELLOW}  4. Check container networking with 'docker network inspect pyerp-network'${NC}" 