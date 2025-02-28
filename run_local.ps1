# PowerShell script to run the PyERP Docker container in local mode with SQLite

# Variables
$CONTAINER_NAME = "pyerp-local"
$IMAGE_NAME = "pyerp:debug"
$PORT = "8000"

# Check if the Docker image exists
try {
    docker image inspect $IMAGE_NAME | Out-Null
    Write-Host "Docker image $IMAGE_NAME found."
} catch {
    Write-Host "Docker image $IMAGE_NAME not found."
    Write-Host "Building the Docker image from Dockerfile.minimal..."
    docker build -t $IMAGE_NAME -f docker/Dockerfile.minimal .
}

# Check if the container is already running
$running = docker ps -q --filter "name=$CONTAINER_NAME"
if ($running) {
    Write-Host "Container $CONTAINER_NAME is already running. Stopping it..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
}

# Run the container with local settings
Write-Host "Starting PyERP container with local SQLite database..."
docker run -d `
    --name $CONTAINER_NAME `
    -p "${PORT}:8000" `
    -e "USE_LOCAL_ENV=true" `
    -e "DJANGO_SETTINGS_MODULE=pyerp.settings.local" `
    -v "${PWD}/db.sqlite3:/app/db.sqlite3" `
    $IMAGE_NAME

Write-Host "Container is starting..."
Start-Sleep -Seconds 2

# Check if the container is running
$running = docker ps -q --filter "name=$CONTAINER_NAME"
if ($running) {
    Write-Host "Container $CONTAINER_NAME is running."
    Write-Host "View logs with: docker logs $CONTAINER_NAME -f"
    Write-Host "Access the application at: http://localhost:$PORT"
} else {
    Write-Host "Container failed to start. Checking logs..."
    docker logs $CONTAINER_NAME
} 