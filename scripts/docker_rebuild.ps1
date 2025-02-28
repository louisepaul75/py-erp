# PowerShell script to restart Docker containers with latest code
# Run this script from the root directory of your project

$ErrorActionPreference = "Stop"
Write-Host "===== Docker Container Management Script =====" -ForegroundColor Cyan

# Step 1: Stop and remove existing containers
Write-Host "`n[1/4] Stopping and removing existing containers..." -ForegroundColor Green
try {
    docker-compose down
    Write-Host "  ✓ Containers successfully stopped" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error stopping containers: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Pull latest code from GitHub
Write-Host "`n[2/4] Pulling latest code from GitHub..." -ForegroundColor Green
try {
    git pull
    Write-Host "  ✓ Latest code pulled successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error pulling code: $_" -ForegroundColor Red
    Write-Host "    You may need to stash or commit your local changes first" -ForegroundColor Yellow
    exit 1
}

# Step 3: Rebuild Docker images
Write-Host "`n[3/4] Rebuilding Docker images..." -ForegroundColor Green
try {
    # Using docker-compose at the root of the project
    docker-compose build --no-cache
    Write-Host "  ✓ Docker images rebuilt successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error rebuilding Docker images: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Start containers
Write-Host "`n[4/4] Starting containers..." -ForegroundColor Green
try {
    docker-compose up -d
    Write-Host "  ✓ Containers started successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error starting containers: $_" -ForegroundColor Red
    exit 1
}

# Final status check
Write-Host "`nChecking container status..." -ForegroundColor Cyan
docker-compose ps

Write-Host "`n===== Process Complete =====" -ForegroundColor Cyan
Write-Host "The web application should now be accessible via HTTPS" -ForegroundColor Green
Write-Host "If you encounter 'too many redirects' errors:" -ForegroundColor Yellow
Write-Host "  1. Clear your browser cache" -ForegroundColor Yellow
Write-Host "  2. Check that settings_https.py is being properly loaded" -ForegroundColor Yellow
Write-Host "  3. Verify X-Forwarded-Proto header is set to 'https' in Nginx config" -ForegroundColor Yellow 