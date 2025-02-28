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
BRANCH="main"  # Default branch to pull from

# Function to display help information
display_help() {
  echo -e "${CYAN}===== Docker Rebuild with Nginx - Help =====${NC}"
  echo -e "${YELLOW}Usage: $0 [OPTIONS]${NC}"
  echo -e "${YELLOW}Options:${NC}"
  echo -e "  ${YELLOW}--help                Display this help message${NC}"
  echo -e "  ${YELLOW}--branch=BRANCH       Specify which Git branch to pull from (default: main)${NC}"
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

# Show configuration
echo -e "${CYAN}===== Docker Deployment Configuration =====${NC}"
echo -e "${YELLOW}Branch: $BRANCH${NC}"
echo -e "${YELLOW}Skip pruning: ${SKIP_PRUNE:-false}${NC}"

# Check if we're low on disk space
LOW_SPACE=false
DOCKER_DIR=$(docker info | grep "Docker Root Dir" | cut -d: -f2 | tr -d '[:space:]')
if [ -z "$DOCKER_DIR" ]; then
    DOCKER_DIR="/var/lib/docker"  # Default location
fi

FREE_SPACE=$(df -m "$DOCKER_DIR" | tail -1 | awk '{print $4}')
echo -e "${CYAN}Available space in Docker directory: ${FREE_SPACE}MB${NC}"

if [ "$FREE_SPACE" -lt 1000 ]; then
    echo -e "${YELLOW}Low disk space detected (less than 1GB free).${NC}"
    LOW_SPACE=true
fi

# Clean up Docker resources if needed
if [ "$LOW_SPACE" = true ] && [ "$SKIP_PRUNE" = false ]; then
    echo -e "${YELLOW}Running Docker cleanup to free up space...${NC}"
    # Ensure the prune script is executable (works on both Windows and Linux)
    if [ -f ./scripts/docker-prune.sh ]; then
        chmod +x ./scripts/docker-prune.sh || true
        bash ./scripts/docker-prune.sh
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
  grep -q "nginx" "$COMPOSE_FILE" 2>/dev/null
  if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}Nginx configuration found in production compose file${NC}"
    NGINX_COMPOSE_FILE="$COMPOSE_FILE"
  else
    echo -e "  ${YELLOW}Nginx not found in production compose file. Looking for separate Nginx config...${NC}"
    # Continue with the existing Nginx lookup logic
    if [ -f "docker/docker-compose.prod.yml" ]; then
      grep -q "nginx" "docker/docker-compose.prod.yml" 2>/dev/null
      if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}Found separate Nginx compose file: docker/docker-compose.prod.yml${NC}"
        NGINX_COMPOSE_FILE="docker/docker-compose.prod.yml"
      fi
    fi
  fi
else
  # For development, continue with regular Nginx check
  grep -q "nginx" "$COMPOSE_FILE" 2>/dev/null
  if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}Nginx configuration found in main compose file${NC}"
    NGINX_COMPOSE_FILE="$COMPOSE_FILE"
  else
    # Check docker/docker-compose.yml specifically for Nginx
    if [ -f "docker/docker-compose.yml" ]; then
      grep -q "nginx" "docker/docker-compose.yml" 2>/dev/null
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

# Function to check and fix SSH setup if needed
check_ssh_git_connection() {
    # Get the current repository URL
    REPO_URL=$(git config --get remote.origin.url)
    
    # Only check if it's using SSH format
    if [[ $REPO_URL == git@* ]]; then
        echo -e "  ${YELLOW}Using SSH for GitHub: $REPO_URL${NC}"
        
        # List SSH directory contents for debugging
        echo -e "  ${YELLOW}Checking SSH directory contents:${NC}"
        ls -la ~/.ssh/ 2>/dev/null || echo -e "  ${RED}Cannot access ~/.ssh directory${NC}"
        
        # Try SSH agent - see if we have any keys loaded
        echo -e "  ${YELLOW}Checking for keys in ssh-agent...${NC}"
        if ! ssh-add -l &>/dev/null; then
            echo -e "  ${RED}No SSH keys found in ssh-agent.${NC}"
            echo -e "  ${YELLOW}Checking for SSH key files...${NC}"
            
            # Create SSH directory if it doesn't exist
            if [ ! -d ~/.ssh ]; then
                echo -e "  ${YELLOW}Creating ~/.ssh directory...${NC}"
                mkdir -p ~/.ssh
                chmod 700 ~/.ssh
            fi
            
            # Look for any SSH key files (expanded search)
            SSH_KEYS=( $(find ~/.ssh -name "id_*" ! -name "*.pub" 2>/dev/null) )
            
            if [ ${#SSH_KEYS[@]} -gt 0 ]; then
                echo -e "  ${GREEN}Found SSH key files:${NC}"
                for key in "${SSH_KEYS[@]}"; do
                    echo -e "  ${GREEN}- $key${NC}"
                done
                
                echo -e "  ${YELLOW}Starting ssh-agent and adding keys...${NC}"
                # Start ssh-agent if not running
                eval "$(ssh-agent -s)" || echo -e "  ${RED}Failed to start ssh-agent${NC}"
                
                # Try to add each key found
                for key in "${SSH_KEYS[@]}"; do
                    echo -e "  ${YELLOW}Adding key: $key${NC}"
                    ssh-add "$key" || echo -e "  ${RED}Failed to add key: $key${NC}"
                done
                
                # Check if successful
                if ssh-add -l &>/dev/null; then
                    echo -e "  ${GREEN}SSH key(s) added to agent.${NC}"
                else
                    echo -e "  ${RED}Failed to add SSH keys to agent.${NC}"
                fi
            else
                echo -e "  ${RED}No SSH key files found in ~/.ssh/${NC}"
                echo -e "  ${YELLOW}Would you like to generate a new SSH key? (y/n)${NC}"
                read -p "  Generate new SSH key? " generate_key
                
                if [[ "$generate_key" == "y" || "$generate_key" == "Y" ]]; then
                    echo -e "  ${YELLOW}Enter your email address:${NC}"
                    read -p "  Email: " user_email
                    
                    echo -e "  ${YELLOW}Generating new SSH key...${NC}"
                    ssh-keygen -t ed25519 -C "$user_email" || ssh-keygen -t rsa -b 4096 -C "$user_email"
                    
                    echo -e "  ${GREEN}SSH key generated. Adding to ssh-agent...${NC}"
                    eval "$(ssh-agent -s)"
                    
                    # Try to add the newly generated key
                    if [ -f ~/.ssh/id_ed25519 ]; then
                        ssh-add ~/.ssh/id_ed25519
                    elif [ -f ~/.ssh/id_rsa ]; then
                        ssh-add ~/.ssh/id_rsa
                    fi
                    
                    echo -e "  ${YELLOW}Please add this key to your GitHub account:${NC}"
                    cat ~/.ssh/id_ed25519.pub 2>/dev/null || cat ~/.ssh/id_rsa.pub 2>/dev/null
                    echo -e "  ${YELLOW}Visit: https://github.com/settings/keys${NC}"
                    
                    echo -e "  ${YELLOW}Press Enter when you've added the key to GitHub...${NC}"
                    read -p "  " _
                else
                    echo -e "  ${YELLOW}Please manually generate an SSH key with:${NC}"
                    echo -e "  ${YELLOW}ssh-keygen -t ed25519 -C \"your_email@example.com\"${NC}"
                    echo -e "  ${YELLOW}Then add to GitHub: https://github.com/settings/keys${NC}"
                fi
            fi
        else
            echo -e "  ${GREEN}SSH keys found in ssh-agent.${NC}"
            ssh-add -l
        fi
        
        # Try a basic SSH connection test to GitHub
        echo -e "  ${YELLOW}Testing connection to GitHub...${NC}"
        if ssh -T git@github.com -o StrictHostKeyChecking=no -o BatchMode=yes 2>&1 | grep -q "success"; then
            echo -e "  ${GREEN}SSH connection to GitHub successful.${NC}"
        else
            echo -e "  ${RED}Cannot connect to GitHub via SSH.${NC}"
            echo -e "  ${YELLOW}Detailed SSH debugging:${NC}"
            echo -e "  ${YELLOW}Running: ssh -vT git@github.com${NC}"
            ssh -vT git@github.com
            
            echo -e "\n  ${YELLOW}Linux SSH troubleshooting:${NC}"
            echo -e "  ${YELLOW}1. Check permissions: chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_*${NC}"
            echo -e "  ${YELLOW}2. Make sure known_hosts file exists: touch ~/.ssh/known_hosts${NC}"
            echo -e "  ${YELLOW}3. Add GitHub to known_hosts: ssh-keyscan github.com >> ~/.ssh/known_hosts${NC}"
            echo -e "  ${YELLOW}4. Restart the SSH agent: eval \$(ssh-agent -s) && ssh-add${NC}"
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
if git pull origin $BRANCH; then
    echo -e "  ${GREEN}✓ Latest code pulled successfully from $BRANCH${NC}"
else
    echo -e "  ${RED}✗ Error pulling code from $BRANCH${NC}"
    echo -e "  ${YELLOW}SSH authentication failed. Please check your SSH keys.${NC}"
    echo -e "  ${YELLOW}You may need to:${NC}"
    echo -e "  ${YELLOW}1. Add your SSH key to the ssh-agent: ssh-add ~/.ssh/id_rsa${NC}"
    echo -e "  ${YELLOW}2. Make sure your SSH key is added to your GitHub account${NC}"
    echo -e "  ${YELLOW}3. Test with: ssh -T git@github.com${NC}"
    echo -e "  ${YELLOW}4. Stash or commit your local changes first${NC}"
    
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
        if docker-compose -f "$PROD_FILE" build --no-cache; then
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
        if docker-compose -f "$COMPOSE_FILE" build --no-cache; then
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
    if docker-compose -f "$NGINX_COMPOSE_FILE" build --no-cache; then
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
    if docker-compose -f "$COMPOSE_FILE" up -d; then
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
    if docker-compose -f "$NGINX_COMPOSE_FILE" up -d; then
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