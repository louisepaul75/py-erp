#!/bin/bash

# Default values
RUN_TESTS=true
RUN_MONITORING=true
DEBUG_MODE=false
LOCAL_HTTPS_MODE=false
PROFILE_MEMORY=false

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --no-tests) RUN_TESTS=false; shift ;;
        --no-monitoring) RUN_MONITORING=false; shift ;;
        --debug) DEBUG_MODE=true; shift ;;
        --local-https) LOCAL_HTTPS_MODE=true; shift ;;
        --profile-memory) PROFILE_MEMORY=true; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

# Announce test skipping early if flag is set
if [ "$RUN_TESTS" = false ]; then
    echo "Skipping tests as requested via --no-tests flag."
    echo ""
fi

# Stop and remove existing containers
echo "Stopping existing containers..."
docker stop pyerp-prod || true
docker rm pyerp-prod || true
docker stop pyerp-elastic-kibana || true
docker rm pyerp-elastic-kibana || true

# Build Docker image
echo "Building Docker image..."
docker build -t pyerp-prod-image -f docker/Dockerfile.prod .

# Create network if it doesn't exist
docker network create pyerp-network || true

# Ensure the host directory for memory snapshots exists
mkdir -p ./memory_snapshots_output/memory_snapshots

# Choose environment file based on mode
ENV_FILE="config/env/.env.prod"
if [ "$DEBUG_MODE" = true ]; then
    ENV_FILE="config/env/.env.prod.local"
fi

echo "Starting containers..."
# Construct docker run command parts
DOCKER_RUN_CMD="docker run -d \
    --name pyerp-prod \
    --hostname pyerp-app \
    --network pyerp-network \
    -p 80:80 \
    -p 443:443 \
    -p 3000:3000 \
    -p 6379:6379 \
    -p 8000:8000 \
    --env-file $ENV_FILE \
    -e NODE_ENV=production \
    -e NEXT_TELEMETRY_DISABLED=1"

# Add volume mount for memory snapshots
# NOTE: Assumes snapshots are written to /app/memory_snapshots inside the container. Adjust if necessary.
DOCKER_RUN_CMD="$DOCKER_RUN_CMD \
    -v $(pwd)/memory_snapshots_output/memory_snapshots:/app/data/memory_snapshots"

# Add conditional memory profiling env var
if [ "$PROFILE_MEMORY" = true ]; then
    echo "Memory profiling enabled."
    DOCKER_RUN_CMD="$DOCKER_RUN_CMD \
    -e ENABLE_MEMORY_PROFILING=true"
fi

# Add conditional HTTPS proxy env var
if [ "$LOCAL_HTTPS_MODE" = true ]; then
    DOCKER_RUN_CMD="$DOCKER_RUN_CMD \
    -e USE_LOCAL_HTTPS_PROXY=true"
fi

# Add the image name and execute
DOCKER_RUN_CMD="$DOCKER_RUN_CMD \
    pyerp-prod-image"

echo "Executing: $DOCKER_RUN_CMD" # Optional: echo the command for debugging
eval $DOCKER_RUN_CMD # Execute the constructed command

echo -e "\nContainer pyerp-prod is running in the background. Use 'docker logs pyerp-prod' to view logs."

# --- Check Database Connection Source ---
echo -e "\n--- Verifying Database Connection Source in Logs ---"
# Wait a bit longer initially for the app to start and log the connection source
echo "Waiting 15 seconds for application logs to populate..."
sleep 15

DB_SOURCE_CHECK_SUCCESS=false
DB_SOURCE_LOG_LINE=""

for i in $(seq 1 3); do # Retry a few times in case logs are delayed
    DB_SOURCE_LOG_LINE=$(docker logs pyerp-prod 2>&1 | grep -E 'Database settings source:' | tail -n 1)
    if [[ -n "$DB_SOURCE_LOG_LINE" ]]; then
        if [[ "$DB_SOURCE_LOG_LINE" == *"1Password"* ]]; then
            echo "✅ Database successfully connected using 1Password credentials."
            echo "   Log line found: '$DB_SOURCE_LOG_LINE'"
            DB_SOURCE_CHECK_SUCCESS=true
            break
        elif [[ "$DB_SOURCE_LOG_LINE" == *"environment variables"* ]]; then
            echo "❌ ERROR: Database connected using environment variables, not 1Password!"
            echo "   Log line found: '$DB_SOURCE_LOG_LINE'"
            echo "   Stopping build process as 1Password connection failed."
            exit 1 # Exit script with error
        else
            echo "❓ Unknown database connection source state on attempt $i."
            echo "   Log line found: '$DB_SOURCE_LOG_LINE'"
            # Continue loop to retry
        fi
    else
        echo "⚠️ Database source log line not found yet (attempt $i). Waiting..."
    fi
    if [ "$DB_SOURCE_CHECK_SUCCESS" = false ]; then
        sleep 5 # Wait before retrying
    fi
done

if [ "$DB_SOURCE_CHECK_SUCCESS" = false ]; then
    echo "❌ ERROR: Failed to verify database connection source after multiple attempts."
    echo "   Could not find the 'Database settings source:' log line or it indicated failure."
    echo "   Last checked line (if any): '$DB_SOURCE_LOG_LINE'"
    echo "   Stopping build process."
    # Optional: Dump last logs for debugging
    # echo "--- Last 50 lines of pyerp-prod logs ---"
    # docker logs --tail 50 pyerp-prod || true
    # echo "---------------------------------------"
    exit 1 # Exit script with error
fi
echo "--- Database Check Complete ---"

# Start the monitoring container unless skipped
if [ "$RUN_MONITORING" = true ]; then
    echo "Starting monitoring container..."
    docker-compose -f docker/docker-compose.monitoring.yml up -d

    echo -e "\nMonitoring services:"
    echo -e "- Elasticsearch: http://localhost:9200"
    echo -e "- Kibana: http://localhost:5601"
    echo -e "Monitoring container logs: docker logs pyerp-elastic-kibana"

    # Wait for Elasticsearch to be ready before running setup
    echo "Waiting for Elasticsearch to become available..."
    for i in {1..30}; do
        if curl -s http://localhost:9200 > /dev/null; then
            echo "Elasticsearch is ready!"
            break
        fi
        echo "Waiting for Elasticsearch... attempt $i of 30"
        sleep 5

        if [ $i -eq 30 ]; then
            echo "Elasticsearch did not start in time. Please check Elasticsearch logs."
            echo "You can check logs with: docker logs pyerp-elastic-kibana"
        fi
    done

    echo "Waiting 10 seconds before starting health checks..."
    sleep 10
else
    echo "Skipping monitoring setup as requested."
fi

# --- Health Checks ---
echo -e "\n--- Running Health Checks ---"
MAX_RETRIES=12
RETRY_DELAY=5
APP_URL="http://localhost:80" # Nginx serves the app on port 80

# Check Main Application Endpoint
echo "Checking main application endpoint ($APP_URL)..."
APP_SUCCESS=false
for i in $(seq 1 $MAX_RETRIES); do
    # Using --head and -L to follow redirects if any (e.g., HTTP to HTTPS)
    if curl -fsSL --head $APP_URL > /dev/null; then
        echo "✅ Main application endpoint is responsive."
        APP_SUCCESS=true
        break
    fi
    # Check if container is still running
    if ! docker ps --filter "name=pyerp-prod" --filter "status=running" --format "{{.Names}}" | grep -q pyerp-prod; then
        echo "❌ Error: Container pyerp-prod seems to have stopped."
        break # No point retrying if container is down
    fi
    echo "Attempt $i/$MAX_RETRIES failed. Retrying in $RETRY_DELAY seconds..."
    sleep $RETRY_DELAY
done

if [ "$APP_SUCCESS" = false ]; then
    if docker ps --filter "name=pyerp-prod" --filter "status=running" --format "{{.Names}}" | grep -q pyerp-prod; then
        echo "❌ Error: Main application endpoint failed to respond after $MAX_RETRIES attempts."
    fi
    echo "Please check container logs: docker logs pyerp-prod"
fi

echo "--- Health Checks Complete ---"

# Run tests inside the container if requested and main app is healthy
if [ "$RUN_TESTS" = true ]; then
  if [ "$APP_SUCCESS" = true ]; then
      echo -e "\n--- Running Tests Inside Container ---"
      echo "Executing tests within the pyerp-prod container..."
      # Assuming ./run_all_tests.sh is executable and in the default working dir of the container
      docker exec pyerp-prod ./run_all_tests.sh
      if [ $? -ne 0 ]; then
          echo "❌ Tests failed inside the container. Check container logs or run manually:"
          echo "   docker exec -it pyerp-prod /bin/bash"
          echo "   (cd to appropriate directory if needed)"
          echo "   ./run_all_tests.sh"
          # Consider adding 'exit 1' here if test failure should stop the script
      else
          echo "✅ Tests passed inside the container."
      fi
      echo "--- Test Execution Complete ---"
  else
      # This message is printed only if tests were supposed to run but health check failed
      echo -e "\nSkipping tests because the main application health check failed."
  fi
fi
