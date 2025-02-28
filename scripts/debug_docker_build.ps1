# Debug Docker Build Script
# This script builds a Docker image using the debug Dockerfile 
# to identify dependency issues

# Set error action
$ErrorActionPreference = "Stop"

Write-Host "Building debug Docker image to identify dependency issues..." -ForegroundColor Green

# Navigate to the project root directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Make sure we are in the project root
Set-Location $projectRoot

# Build the Docker image
Write-Host "Building Docker image with debug configuration..." -ForegroundColor Cyan
docker build -f docker/Dockerfile.dev-debug -t pyerp-debug .

# Check if the build succeeded
if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker build succeeded!" -ForegroundColor Green
    Write-Host "This means all dependencies can be installed individually." -ForegroundColor Green
    Write-Host "The issue might be related to conflicts between packages during pip-compile." -ForegroundColor Yellow
    
    # Suggest alternative approach
    Write-Host "`nSuggested workaround:" -ForegroundColor Cyan
    Write-Host "1. Skip pip-compile in the Dockerfile" -ForegroundColor White
    Write-Host "2. Install packages directly from the .in file with pip install -r requirements/development.in" -ForegroundColor White
    Write-Host "3. For production, consider pre-compiling the requirements.txt files locally" -ForegroundColor White
} else {
    Write-Host "Docker build failed." -ForegroundColor Red
    Write-Host "Review the output to identify which package is causing the issue." -ForegroundColor Yellow
} 