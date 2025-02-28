# PowerShell script to rebuild and run the Docker container with local settings

# Variables
$CONTAINER_NAME = "pyerp-local"
$IMAGE_NAME = "pyerp:debug"
$PORT = "8000"

Write-Host "Stopping any existing container..."
$running = docker ps -q --filter "name=$CONTAINER_NAME"
if ($running) {
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
}

Write-Host "Rebuilding Docker image..."
docker build -t $IMAGE_NAME -f docker/Dockerfile.minimal .

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

Write-Host "Checking logs..."
docker logs $CONTAINER_NAME

Write-Host "Container is running at: http://localhost:${PORT}"
Write-Host "To see real-time logs, run: docker logs ${CONTAINER_NAME} -f" 