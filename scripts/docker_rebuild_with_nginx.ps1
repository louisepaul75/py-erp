# PowerShell script to restart Docker containers with latest code
# This version handles separate web and Nginx containers
# Run this script from the root directory of your project

$ErrorActionPreference = "Stop"
Write-Host "===== Docker Container Management Script with Nginx =====" -ForegroundColor Cyan

# Configuration
$webContainerName = "pyerp-web"  # Your Django container name
$nginxContainerName = "pyerp-nginx"  # Your Nginx container name
$composeFile = "docker-compose.yml"  # Your compose file path
$nginxComposeFile = "docker/docker-compose.yml"  # Nginx compose file if separate

# Step 1: Stop and remove existing containers
Write-Host "`n[1/5] Stopping and removing existing containers..." -ForegroundColor Green
try {
    # Stop the containers if they're running
    docker stop $webContainerName 2>$null
    docker stop $nginxContainerName 2>$null
    
    # Remove the containers
    docker rm $webContainerName 2>$null
    docker rm $nginxContainerName 2>$null
    
    Write-Host "  ✓ Containers successfully stopped and removed" -ForegroundColor Green
} catch {
    Write-Host "  ! Warning when stopping containers: $_" -ForegroundColor Yellow
    Write-Host "  → Continuing anyway..." -ForegroundColor Yellow
}

# Step 2: Pull latest code from GitHub
Write-Host "`n[2/5] Pulling latest code from GitHub..." -ForegroundColor Green
try {
    git pull
    Write-Host "  ✓ Latest code pulled successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error pulling code: $_" -ForegroundColor Red
    Write-Host "    You may need to stash or commit your local changes first" -ForegroundColor Yellow
    exit 1
}

# Step 3: Build Django container
Write-Host "`n[3/5] Building Django container..." -ForegroundColor Green
try {
    # Using docker-compose at the root of the project
    if (Test-Path $composeFile) {
        docker-compose -f $composeFile build --no-cache
    } else {
        docker-compose build --no-cache
    }
    Write-Host "  ✓ Django container rebuilt successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error rebuilding Django container: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Build Nginx container
Write-Host "`n[4/5] Building Nginx container..." -ForegroundColor Green
try {
    # Check if we have a separate compose file for Nginx
    if (Test-Path $nginxComposeFile) {
        docker-compose -f $nginxComposeFile build --no-cache
        Write-Host "  ✓ Nginx container rebuilt successfully from separate compose file" -ForegroundColor Green
    } else {
        Write-Host "  → No separate Nginx compose file found, assuming it's included in the main compose file" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Error rebuilding Nginx container: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Start containers
Write-Host "`n[5/5] Starting containers..." -ForegroundColor Green
try {
    # Start Django container
    if (Test-Path $composeFile) {
        docker-compose -f $composeFile up -d
    } else {
        docker-compose up -d
    }
    
    # Start Nginx container if separate
    if (Test-Path $nginxComposeFile) {
        docker-compose -f $nginxComposeFile up -d
    }
    
    Write-Host "  ✓ Containers started successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error starting containers: $_" -ForegroundColor Red
    exit 1
}

# Create Docker network if it doesn't exist
Write-Host "`nEnsuring Docker network exists..." -ForegroundColor Cyan
docker network create pyerp-network 2>$null
Write-Host "  → Docker network ready" -ForegroundColor Green

# Connect containers to network if needed
Write-Host "`nEnsuring containers are on the same network..." -ForegroundColor Cyan
docker network connect pyerp-network $webContainerName 2>$null
docker network connect pyerp-network $nginxContainerName 2>$null
Write-Host "  → Containers connected to network" -ForegroundColor Green

# Final status check
Write-Host "`nChecking container status..." -ForegroundColor Cyan
docker ps

Write-Host "`n===== Process Complete =====" -ForegroundColor Cyan
Write-Host "The web application should now be accessible via HTTPS" -ForegroundColor Green
Write-Host "If you encounter 'too many redirects' errors:" -ForegroundColor Yellow
Write-Host "  1. Clear your browser cache and cookies" -ForegroundColor Yellow
Write-Host "  2. Check that settings_https.py is being properly loaded" -ForegroundColor Yellow
Write-Host "  3. Verify X-Forwarded-Proto header is set to 'https' in Nginx config" -ForegroundColor Yellow
Write-Host "  4. Check container networking with 'docker network inspect pyerp-network'" -ForegroundColor Yellow 