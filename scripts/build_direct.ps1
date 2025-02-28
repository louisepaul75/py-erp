# Direct Install Docker Build Script
# This script builds a Docker image using the direct installation approach (no pip-compile)

# Set error action
$ErrorActionPreference = "Stop"

Write-Host "Building Docker image with direct dependency installation..." -ForegroundColor Green

# Navigate to the project root directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Make sure we are in the project root
Set-Location $projectRoot

# Build the Docker image
Write-Host "Building Docker image using direct dependency installation..." -ForegroundColor Cyan
docker build -f docker/Dockerfile.dev-direct -t pyerp-dev .

# Check if the build succeeded
if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker build succeeded!" -ForegroundColor Green
    Write-Host "The direct installation approach worked. Consider updating your main Dockerfile.dev with this approach." -ForegroundColor Yellow
    
    # Run the container
    Write-Host "`nDo you want to run the container now? (y/n)" -ForegroundColor Cyan
    $response = Read-Host
    
    if ($response -eq "y") {
        Write-Host "Running the Docker container..." -ForegroundColor Cyan
        docker run --rm -it -p 8000:8000 pyerp-dev
    }
} else {
    Write-Host "Docker build failed." -ForegroundColor Red
    Write-Host "There might be issues with the dependencies themselves." -ForegroundColor Yellow
} 